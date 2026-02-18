"""Marker step for converting PDF to Markdown."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkerError(Exception):
    """Exception raised when Marker conversion fails."""
    pass


def run_marker(pdf_path: str, output_dir: str) -> tuple[str, str]:
    """Convert PDF to Markdown using marker-pdf.
    
    Args:
        pdf_path: Path to the input PDF file.
        output_dir: Directory where output files will be saved.
        
    Returns:
        Tuple of (markdown_file_path, images_directory_path).
        
    Raises:
        MarkerError: If marker conversion fails.
        ImportError: If marker-pdf is not installed.
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
    except ImportError as e:
        raise ImportError(
            "marker-pdf is not installed. "
            "Install it with: pip install marker-pdf"
        ) from e
    
    logger.info(f"Converting PDF to Markdown: {pdf_path}")
    
    pdf_path_obj = Path(pdf_path)
    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create model dictionary for marker
        model_dict = create_model_dict()
        
        # Initialize the PDF converter
        converter = PdfConverter(artifact_dict=model_dict)
        
        # Convert the PDF
        logger.debug("Initializing marker conversion...")
        rendered = converter(pdf_path)
        
        # Get the markdown content and images
        markdown_content = rendered.markdown
        images = rendered.images
        
        # Save markdown to file
        markdown_filename = pdf_path_obj.stem + ".md"
        markdown_path = output_dir_obj / markdown_filename
        
        logger.debug(f"Writing markdown to: {markdown_path}")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # Save images to subdirectory
        images_dir = output_dir_obj / "images"
        images_dir.mkdir(exist_ok=True)
        
        if images:
            logger.debug(f"Saving {len(images)} images to: {images_dir}")
            for image_name, image_data in images.items():
                image_path = images_dir / image_name
                # Save image data (PIL Image or bytes)
                if hasattr(image_data, 'save'):
                    # It's a PIL Image
                    image_data.save(image_path)
                else:
                    # It's bytes
                    with open(image_path, "wb") as f:
                        f.write(image_data)
        else:
            logger.debug("No images found in PDF")
        
        logger.info(f"Marker conversion complete: {markdown_path}")
        
        return str(markdown_path), str(images_dir)
        
    except Exception as e:
        logger.error(f"Marker conversion failed: {e}")
        raise MarkerError(f"Failed to convert PDF with marker: {e}") from e
