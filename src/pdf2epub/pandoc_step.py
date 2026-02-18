"""Pandoc step for converting Markdown to EPUB."""

import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)


class PandocError(Exception):
    """Exception raised when Pandoc conversion fails."""
    pass


def run_pandoc(
    markdown_path: str,
    output_path: str,
    images_dir: str,
    title: str | None = None,
    author: str | None = None,
    cover: str | None = None,
    math_format: str = "svg",
    language: str = "en"
) -> str:
    """Convert Markdown to EPUB using pandoc.
    
    Args:
        markdown_path: Path to the input Markdown file.
        output_path: Path where the EPUB file will be saved.
        images_dir: Directory containing images to embed.
        title: Optional title for the EPUB metadata.
        author: Optional author for the EPUB metadata.
        cover: Optional path to cover image.
        math_format: Format for rendering LaTeX math ('svg' or 'mathml').
        language: BCP 47 language tag for the EPUB (default: 'en').
        
    Returns:
        Path to the generated EPUB file.
        
    Raises:
        PandocError: If pandoc conversion fails.
        ImportError: If pypandoc is not installed.
    """
    try:
        import pypandoc
    except ImportError as e:
        raise ImportError(
            "pypandoc is not installed. "
            "Install it with: pip install pypandoc"
        ) from e
    
    logger.info(f"Converting Markdown to EPUB: {markdown_path} -> {output_path}")
    
    markdown_path_obj = Path(markdown_path)
    output_path_obj = Path(output_path)
    images_dir_obj = Path(images_dir)
    
    # Ensure output directory exists
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Build pandoc extra arguments
    extra_args = []
    
    # Set resource path for images
    if images_dir_obj.exists():
        extra_args.extend(["--resource-path", str(images_dir_obj)])
        logger.debug(f"Using resource path: {images_dir_obj}")
    
    # Configure math rendering
    if math_format == "mathml":
        extra_args.append("--mathml")
        logger.debug("Using MathML for math rendering")
    elif math_format == "svg":
        extra_args.extend(["--webtex"])
        logger.debug("Using SVG/WebTeX for math rendering")
    else:
        logger.warning(f"Unknown math format: {math_format}, using default")
    
    # Add metadata
    if title:
        extra_args.extend(["--metadata", f"title={title}"])
        logger.debug(f"Setting title: {title}")
    
    if author:
        extra_args.extend(["--metadata", f"author={author}"])
        logger.debug(f"Setting author: {author}")

    # Set language (required by EPUB spec; missing language causes Kindle errors)
    extra_args.extend(["--metadata", f"lang={language}"])
    logger.debug(f"Setting language: {language}")

    # Set publication date in ISO 8601 format. Pandoc only emits dc:date when
    # this variable is explicitly provided; without it the field is absent.
    # dc:date is recommended by the EPUB spec and its absence can cause
    # validation errors when sending EPUBs to Kindle via Send to Kindle.
    today = date.today().isoformat()
    extra_args.extend(["--metadata", f"date={today}"])
    logger.debug(f"Setting date: {today}")
    
    # Add cover image
    if cover:
        cover_path = Path(cover)
        if cover_path.exists():
            extra_args.extend(["--epub-cover-image", str(cover_path)])
            logger.debug(f"Using cover image: {cover}")
        else:
            logger.warning(f"Cover image not found: {cover}")
    
    # Additional EPUB-specific options
    extra_args.extend([
        "--standalone",
        "--toc",  # Table of contents
    ])
    
    try:
        logger.debug(f"Running pandoc with args: {extra_args}")
        
        # Convert using pypandoc
        pypandoc.convert_file(
            str(markdown_path_obj),
            "epub",
            outputfile=str(output_path_obj),
            extra_args=extra_args
        )
        
        logger.info(f"Pandoc conversion complete: {output_path}")
        
        if not output_path_obj.exists():
            raise PandocError(f"EPUB file was not created: {output_path}")
        
        return str(output_path_obj)
        
    except Exception as e:
        logger.error(f"Pandoc conversion failed: {e}")
        raise PandocError(f"Failed to convert Markdown to EPUB: {e}") from e
