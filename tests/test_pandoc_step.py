"""Tests for the pandoc step."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from pdf2epub.pandoc_step import run_pandoc, PandocError


class TestPandocStep:
    """Tests for pandoc Markdown to EPUB conversion."""
    
    def test_run_pandoc_success(self, tmp_path):
        """Test successful pandoc conversion."""
        # Create test files
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test Document\n\nThis is a test.")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        output_path = tmp_path / "output.epub"
        
        # Mock pypandoc
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            # Make the output file exist after conversion
            def create_epub(*args, **kwargs):
                output_path.write_bytes(b"fake epub")
            
            mock_pypandoc.convert_file.side_effect = create_epub
            
            # Run pandoc
            result = run_pandoc(
                str(markdown_path),
                str(output_path),
                str(images_dir),
                title="Test Title",
                author="Test Author",
                math_format="mathml"
            )
            
            # Verify
            assert result == str(output_path)
            assert mock_pypandoc.convert_file.called
            
            # Check call arguments
            call_args = mock_pypandoc.convert_file.call_args
            assert call_args[0][0] == str(markdown_path)
            assert call_args[1]["outputfile"] == str(output_path)
            
            extra_args = call_args[1]["extra_args"]
            assert "--mathml" in extra_args
            assert any("title=Test Title" in arg for arg in extra_args)
            assert any("author=Test Author" in arg for arg in extra_args)
    
    def test_run_pandoc_with_cover(self, tmp_path):
        """Test pandoc conversion with cover image."""
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        cover_path = tmp_path / "cover.jpg"
        cover_path.write_bytes(b"fake cover")
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            def create_epub(*args, **kwargs):
                output_path.write_bytes(b"fake epub")
            
            mock_pypandoc.convert_file.side_effect = create_epub
            
            result = run_pandoc(
                str(markdown_path),
                str(output_path),
                str(images_dir),
                cover=str(cover_path)
            )
            
            # Verify cover was included
            extra_args = mock_pypandoc.convert_file.call_args[1]["extra_args"]
            assert "--epub-cover-image" in extra_args
            assert str(cover_path) in extra_args
    
    def test_run_pandoc_svg_math(self, tmp_path):
        """Test pandoc with SVG math format."""
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            def create_epub(*args, **kwargs):
                output_path.write_bytes(b"fake epub")
            
            mock_pypandoc.convert_file.side_effect = create_epub
            
            run_pandoc(
                str(markdown_path),
                str(output_path),
                str(images_dir),
                math_format="svg"
            )
            
            # Verify SVG/webtex was used
            extra_args = mock_pypandoc.convert_file.call_args[1]["extra_args"]
            assert "--webtex" in extra_args
    
    def test_run_pandoc_import_error(self, tmp_path):
        """Test that ImportError is raised when pypandoc is not installed."""
        with patch("pdf2epub.pandoc_step.pypandoc", side_effect=ImportError):
            with pytest.raises(ImportError, match="pypandoc is not installed"):
                run_pandoc("test.md", "test.epub", "images")
    
    def test_run_pandoc_conversion_error(self, tmp_path):
        """Test that PandocError is raised on conversion failure."""
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            mock_pypandoc.convert_file.side_effect = Exception("Pandoc failed")
            
            with pytest.raises(PandocError, match="Failed to convert Markdown to EPUB"):
                run_pandoc(str(markdown_path), str(output_path), str(images_dir))
    
    def test_run_pandoc_missing_output(self, tmp_path):
        """Test that PandocError is raised if output file is not created."""
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            # Don't create the output file
            mock_pypandoc.convert_file.return_value = None
            
            with pytest.raises(PandocError, match="EPUB file was not created"):
                run_pandoc(str(markdown_path), str(output_path), str(images_dir))
    
    def test_run_pandoc_no_metadata(self, tmp_path):
        """Test pandoc conversion without title/author metadata."""
        markdown_path = tmp_path / "test.md"
        markdown_path.write_text("# Test")
        
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        
        output_path = tmp_path / "output.epub"
        
        with patch("pdf2epub.pandoc_step.pypandoc") as mock_pypandoc:
            def create_epub(*args, **kwargs):
                output_path.write_bytes(b"fake epub")
            
            mock_pypandoc.convert_file.side_effect = create_epub
            
            run_pandoc(str(markdown_path), str(output_path), str(images_dir))
            
            # Verify no title/author in extra args
            extra_args = mock_pypandoc.convert_file.call_args[1]["extra_args"]
            assert not any("title=" in str(arg) for arg in extra_args)
            assert not any("author=" in str(arg) for arg in extra_args)
