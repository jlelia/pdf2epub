"""Tests for the marker step."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf2epub.marker_step import run_marker, MarkerError


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
