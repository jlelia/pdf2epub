"""Main converter orchestration for pdf2epub."""

import logging
import shutil
from pathlib import Path

from pdf2epub.marker_step import run_marker
from pdf2epub.pandoc_step import run_pandoc
from pdf2epub.utils import temporary_directory, validate_pdf_file, get_default_output_path

logger = logging.getLogger(__name__)


def convert(
    pdf_path: str,
    output_path: str | None = None,
    title: str | None = None,
    author: str | None = None,
    cover: str | None = None,
    math_format: str = "svg",
    save_markdown: str | None = None,
    language: str = "en",
    **kwargs
) -> str:
    """Convert a PDF file to EPUB format.
    
    This is the main orchestration function that:
    1. Validates the input PDF
    2. Converts PDF to Markdown using marker
    3. Converts Markdown to EPUB using pandoc
    4. Cleans up temporary files
    
    Args:
        pdf_path: Path to the input PDF file.
        output_path: Path for the output EPUB file. If None, uses the same
                    name as the input with .epub extension.
        title: Optional title for the EPUB metadata.
        author: Optional author for the EPUB metadata.
        cover: Optional path to a cover image.
        math_format: Format for rendering LaTeX math ('svg' or 'mathml').
        save_markdown: Optional path to save the intermediate Markdown file.
        language: BCP 47 language tag for the EPUB (default: 'en').
        **kwargs: Additional keyword arguments (for future extensibility).
        
    Returns:
        Path to the generated EPUB file.
        
    Raises:
        FileNotFoundError: If the input PDF does not exist.
        ValueError: If the input is not a valid PDF file.
        MarkerError: If PDF to Markdown conversion fails.
        PandocError: If Markdown to EPUB conversion fails.
    """
    logger.info(f"Starting PDF to EPUB conversion: {pdf_path}")
    
    # Validate input
    pdf_path_obj = validate_pdf_file(pdf_path)
    
    # Determine output path
    if output_path is None:
        output_path = get_default_output_path(str(pdf_path_obj))
    
    output_path_obj = Path(output_path)
    logger.info(f"Output will be saved to: {output_path}")
    
    # Use a temporary directory for intermediate files
    with temporary_directory() as temp_dir:
        logger.debug(f"Using temporary directory: {temp_dir}")
        
        try:
            # Phase 1: PDF to Markdown using marker
            logger.info("Phase 1: Converting PDF to Markdown with marker...")
            markdown_path, images_dir = run_marker(str(pdf_path_obj), str(temp_dir))
            logger.info(f"Markdown generated: {markdown_path}")
            
            # Save intermediate Markdown if requested
            if save_markdown:
                save_markdown_path = Path(save_markdown)
                save_markdown_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(markdown_path, save_markdown_path)
                logger.info(f"Markdown saved to: {save_markdown_path}")
            
            # Phase 2: Markdown to EPUB using pandoc
            logger.info("Phase 2: Converting Markdown to EPUB with pandoc...")
            epub_path = run_pandoc(
                markdown_path=markdown_path,
                output_path=str(output_path_obj),
                images_dir=images_dir,
                title=title,
                author=author,
                cover=cover,
                math_format=math_format,
                language=language
            )
            logger.info(f"EPUB generated: {epub_path}")
            
            return epub_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise
        
        # Temporary directory is automatically cleaned up
