"""Tests for the main converter."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from pdf2epub.converter import convert
from pdf2epub.marker_step import MarkerError
from pdf2epub.pandoc_step import PandocError


class TestConverter:
    """Tests for the main PDF to EPUB converter."""
    
    def test_convert_success(self, tmp_path):
        """Test successful end-to-end conversion."""
        # Create a fake PDF
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        output_path = tmp_path / "output.epub"
        
        # Mock marker and pandoc
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                # Setup mocks
                mock_marker.return_value = ("/tmp/test.md", "/tmp/images")
                mock_pandoc.return_value = str(output_path)
                
                # Run conversion
                result = convert(str(pdf_path), str(output_path))
                
                # Verify
                assert result == str(output_path)
                assert mock_marker.called
                assert mock_pandoc.called
    
    def test_convert_default_output_path(self, tmp_path):
        """Test conversion with default output path."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                mock_marker.return_value = ("/tmp/test.md", "/tmp/images")
                mock_pandoc.return_value = str(tmp_path / "test.epub")
                
                # Call without output_path
                result = convert(str(pdf_path))
                
                # Verify default path was generated
                assert result.endswith(".epub")
                assert mock_pandoc.called
    
    def test_convert_with_metadata(self, tmp_path):
        """Test conversion with title and author metadata."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                mock_marker.return_value = ("/tmp/test.md", "/tmp/images")
                mock_pandoc.return_value = str(output_path)
                
                result = convert(
                    str(pdf_path),
                    str(output_path),
                    title="Test Book",
                    author="Test Author",
                    math_format="svg"
                )
                
                # Verify pandoc was called with metadata
                call_kwargs = mock_pandoc.call_args[1]
                assert call_kwargs["title"] == "Test Book"
                assert call_kwargs["author"] == "Test Author"
                assert call_kwargs["math_format"] == "svg"
    
    def test_convert_invalid_pdf(self, tmp_path):
        """Test conversion with non-PDF file."""
        txt_path = tmp_path / "test.txt"
        txt_path.write_text("not a pdf")
        
        with pytest.raises(ValueError, match="Not a PDF file"):
            convert(str(txt_path))
    
    def test_convert_missing_file(self):
        """Test conversion with missing file."""
        with pytest.raises(FileNotFoundError):
            convert("/nonexistent/file.pdf")
    
    def test_convert_marker_error(self, tmp_path):
        """Test that MarkerError propagates."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            mock_marker.side_effect = MarkerError("Marker failed")
            
            with pytest.raises(MarkerError, match="Marker failed"):
                convert(str(pdf_path))
    
    def test_convert_pandoc_error(self, tmp_path):
        """Test that PandocError propagates."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                mock_marker.return_value = ("/tmp/test.md", "/tmp/images")
                mock_pandoc.side_effect = PandocError("Pandoc failed")
                
                with pytest.raises(PandocError, match="Pandoc failed"):
                    convert(str(pdf_path))
    
    def test_convert_with_cover(self, tmp_path):
        """Test conversion with cover image."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        cover_path = tmp_path / "cover.jpg"
        cover_path.write_bytes(b"fake cover")
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                mock_marker.return_value = ("/tmp/test.md", "/tmp/images")
                mock_pandoc.return_value = str(output_path)
                
                convert(
                    str(pdf_path),
                    str(output_path),
                    cover=str(cover_path)
                )
                
                # Verify cover was passed to pandoc
                call_kwargs = mock_pandoc.call_args[1]
                assert call_kwargs["cover"] == str(cover_path)

    def test_convert_save_markdown(self, tmp_path):
        """Test that save_markdown copies the intermediate Markdown file."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf")
        
        output_path = tmp_path / "output.epub"
        save_md_path = tmp_path / "saved" / "output.md"
        
        # Create a real markdown file that run_marker will "produce"
        marker_output_dir = tmp_path / "marker_out"
        marker_output_dir.mkdir()
        md_file = marker_output_dir / "test.md"
        md_file.write_text("# Test Document\n\nSome content.")
        
        with patch("pdf2epub.converter.run_marker") as mock_marker:
            with patch("pdf2epub.converter.run_pandoc") as mock_pandoc:
                mock_marker.return_value = (str(md_file), str(marker_output_dir / "images"))
                mock_pandoc.return_value = str(output_path)
                
                convert(
                    str(pdf_path),
                    str(output_path),
                    save_markdown=str(save_md_path)
                )
                
                # Verify the markdown was saved
                assert save_md_path.exists()
                assert save_md_path.read_text() == "# Test Document\n\nSome content."
