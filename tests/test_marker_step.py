"""Tests for the marker step."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf2epub.marker_step import run_marker, MarkerError, _log_device_info


class TestMarkerStep:
    """Tests for marker PDF to Markdown conversion."""
    
    def test_run_marker_success(self, tmp_path):
        """Test successful marker conversion."""
        # Mock the marker imports and conversion
        mock_rendered = Mock()
        mock_rendered.markdown = "# Test Document\n\nThis is a test."
        mock_rendered.images = {
            "image1.png": b"fake_image_data"
        }
        
        mock_converter = Mock()
        mock_converter.return_value = mock_rendered
        
        with patch("marker.converters.pdf.PdfConverter", return_value=mock_converter):
            with patch("marker.models.create_model_dict", return_value={}):
                # Create a fake PDF file
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                output_dir = tmp_path / "output"
                
                # Run marker
                markdown_path, images_dir = run_marker(str(pdf_path), str(output_dir))
                
                # Verify outputs
                assert Path(markdown_path).exists()
                assert Path(images_dir).exists()
                assert Path(markdown_path).name == "test.md"
                
                # Verify markdown content
                with open(markdown_path, "r") as f:
                    content = f.read()
                assert "Test Document" in content
    
    def test_run_marker_no_images(self, tmp_path):
        """Test marker conversion with no images."""
        mock_rendered = Mock()
        mock_rendered.markdown = "# Test Document"
        mock_rendered.images = {}
        
        mock_converter = Mock()
        mock_converter.return_value = mock_rendered
        
        with patch("marker.converters.pdf.PdfConverter", return_value=mock_converter):
            with patch("marker.models.create_model_dict", return_value={}):
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                output_dir = tmp_path / "output"
                
                markdown_path, images_dir = run_marker(str(pdf_path), str(output_dir))
                
                assert Path(markdown_path).exists()
                assert Path(images_dir).exists()
    
    def test_run_marker_import_error(self, tmp_path):
        """Test that ImportError is raised when marker is not installed."""
        # Mock the import to raise an ImportError
        import sys
        with patch.dict(sys.modules, {'marker': None, 'marker.converters': None, 'marker.converters.pdf': None}):
            pdf_path = tmp_path / "test.pdf"
            pdf_path.write_text("fake pdf")
            
            with pytest.raises(ImportError, match="marker-pdf is not installed"):
                run_marker(str(pdf_path), str(tmp_path))
    
    def test_run_marker_conversion_error(self, tmp_path):
        """Test that MarkerError is raised on conversion failure."""
        mock_converter = Mock()
        mock_converter.side_effect = Exception("Conversion failed")
        
        with patch("marker.converters.pdf.PdfConverter", return_value=mock_converter):
            with patch("marker.models.create_model_dict", return_value={}):
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                with pytest.raises(MarkerError, match="Failed to convert PDF"):
                    run_marker(str(pdf_path), str(tmp_path))
    
    def test_run_marker_model_download_retry_success(self, tmp_path):
        """Test that model download is retried successfully after cleanup on 'Destination path already exists' error."""
        mock_rendered = Mock()
        mock_rendered.markdown = "# Test"
        mock_rendered.images = {}
        
        mock_converter = Mock()
        mock_converter.return_value = mock_rendered
        
        # First call to create_model_dict fails with the specific error
        # Second call succeeds
        call_count = [0]
        def create_model_dict_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Destination path 'C:\\Users\\test\\models\\layout\\.gitattributes' already exists")
            return {}
        
        with patch("marker.converters.pdf.PdfConverter", return_value=mock_converter):
            with patch("marker.models.create_model_dict", side_effect=create_model_dict_side_effect):
                with patch("pdf2epub.marker_step.clean_incomplete_model_downloads") as mock_cleanup:
                    pdf_path = tmp_path / "test.pdf"
                    pdf_path.write_text("fake pdf")
                    
                    output_dir = tmp_path / "output"
                    
                    # Should succeed after retry
                    markdown_path, images_dir = run_marker(str(pdf_path), str(output_dir))
                    
                    # Verify cleanup was called
                    mock_cleanup.assert_called_once()
                    # Verify create_model_dict was called twice
                    assert call_count[0] == 2
                    # Verify output was created
                    assert Path(markdown_path).exists()
    
    def test_run_marker_model_download_retry_failure(self, tmp_path):
        """Test that error is raised if model download fails even after cleanup."""
        # Both calls to create_model_dict fail with the specific error
        def create_model_dict_side_effect():
            raise Exception("Destination path 'C:\\Users\\test\\models\\layout\\.gitattributes' already exists")
        
        with patch("marker.models.create_model_dict", side_effect=create_model_dict_side_effect):
            with patch("pdf2epub.marker_step.clean_incomplete_model_downloads") as mock_cleanup:
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                with pytest.raises(MarkerError, match="already exists"):
                    run_marker(str(pdf_path), str(tmp_path))
                
                # Verify cleanup was called
                mock_cleanup.assert_called_once()
    
    def test_run_marker_model_download_different_error(self, tmp_path):
        """Test that different errors are not treated as incomplete download errors."""
        def create_model_dict_side_effect():
            raise Exception("Network error: could not connect")
        
        with patch("marker.models.create_model_dict", side_effect=create_model_dict_side_effect):
            with patch("pdf2epub.marker_step.clean_incomplete_model_downloads") as mock_cleanup:
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                with pytest.raises(MarkerError, match="Network error"):
                    run_marker(str(pdf_path), str(tmp_path))
                
                # Verify cleanup was NOT called for different error
                mock_cleanup.assert_not_called()
    
    def test_run_marker_with_pil_images(self, tmp_path):
        """Test marker conversion with PIL Image objects."""
        mock_image = MagicMock()
        mock_image.save = Mock()
        
        mock_rendered = Mock()
        mock_rendered.markdown = "# Test"
        mock_rendered.images = {
            "image1.png": mock_image
        }
        
        mock_converter = Mock()
        mock_converter.return_value = mock_rendered
        
        with patch("marker.converters.pdf.PdfConverter", return_value=mock_converter):
            with patch("marker.models.create_model_dict", return_value={}):
                pdf_path = tmp_path / "test.pdf"
                pdf_path.write_text("fake pdf")
                
                output_dir = tmp_path / "output"
                
                markdown_path, images_dir = run_marker(str(pdf_path), str(output_dir))
                
                # Verify the PIL image save was called
                assert mock_image.save.called


class TestLogDeviceInfo:
    """Tests for the GPU/CPU device detection helper."""

    def test_log_device_info_gpu_available(self, caplog):
        """Test logging when a GPU is available."""
        mock_props = Mock()
        mock_props.total_memory = 8 * (1024 ** 3)  # 8 GB

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA GeForce RTX 3080"
        mock_torch.cuda.get_device_properties.return_value = mock_props

        with patch.dict("sys.modules", {"torch": mock_torch}):
            import logging
            with caplog.at_level(logging.INFO, logger="pdf2epub.marker_step"):
                _log_device_info()

        assert any("NVIDIA GeForce RTX 3080" in m for m in caplog.messages)

    def test_log_device_info_low_vram_warning(self, caplog):
        """Test that a warning is emitted for GPUs with insufficient VRAM."""
        mock_props = Mock()
        mock_props.total_memory = 2 * (1024 ** 3)  # 2 GB — below the 4 GB threshold

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "Some GPU"
        mock_torch.cuda.get_device_properties.return_value = mock_props

        with patch.dict("sys.modules", {"torch": mock_torch}):
            import logging
            with caplog.at_level(logging.WARNING, logger="pdf2epub.marker_step"):
                _log_device_info()

        assert any("VRAM" in m for m in caplog.messages)

    def test_log_device_info_cpu_only_warning(self, caplog):
        """Test that a warning is emitted when no GPU is available."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        with patch.dict("sys.modules", {"torch": mock_torch}):
            import logging
            with caplog.at_level(logging.WARNING, logger="pdf2epub.marker_step"):
                _log_device_info()

        assert any("CPU" in m for m in caplog.messages)

    def test_log_device_info_no_torch(self, caplog):
        """Test graceful handling when torch is not installed."""
        import sys
        with patch.dict(sys.modules, {"torch": None}):
            import logging
            with caplog.at_level(logging.DEBUG, logger="pdf2epub.marker_step"):
                _log_device_info()
        # Should not raise; debug message about torch not being available

