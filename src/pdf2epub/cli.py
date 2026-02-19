"""Command-line interface for pdf2epub."""

import sys
import logging
from pathlib import Path

import click

from pdf2epub import __version__
from pdf2epub.converter import convert
from pdf2epub.utils import setup_logging, get_default_output_path

logger = logging.getLogger(__name__)


@click.command()
@click.argument(
    "input_pdf",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    metavar="INPUT_PDF"
)
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Output EPUB file path (default: same name as input with .epub extension)"
)
@click.option(
    "--title",
    type=str,
    default=None,
    help="EPUB title metadata"
)
@click.option(
    "--author",
    type=str,
    default=None,
    help="EPUB author metadata"
)
@click.option(
    "--cover",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Path to cover image for the EPUB"
)
@click.option(
    "--math-format",
    type=click.Choice(["mathml", "svg"], case_sensitive=False),
    default="svg",
    help="Format for rendering LaTeX math (default: svg)"
)
@click.option(
    "--save-markdown",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Save the intermediate Markdown file to this path (useful for debugging)"
)
@click.option(
    "--language",
    type=str,
    default="en",
    show_default=True,
    help="BCP 47 language tag for the EPUB (e.g. 'en', 'fr', 'de')"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose/debug logging"
)
@click.version_option(version=__version__, prog_name="pdf2epub")
def main(
    input_pdf: str,
    output: str | None,
    title: str | None,
    author: str | None,
    cover: str | None,
    math_format: str,
    save_markdown: str | None,
    language: str,
    verbose: bool
) -> None:
    """Convert PDF files to EPUB format.
    
    pdf2epub uses a two-phase pipeline:
    1. Marker (marker-pdf) converts PDF to Markdown with images
    2. Pandoc converts Markdown to well-formatted EPUB
    
    Examples:
    
        pdf2epub input.pdf
        
        pdf2epub input.pdf -o output.epub --title "My Book" --author "Author Name"
        
        pdf2epub paper.pdf --math-format mathml --verbose    """
    # Setup logging
    setup_logging(verbose=verbose)
    
    try:
        # Validate input is a PDF
        input_path = Path(input_pdf)
        if input_path.suffix.lower() != ".pdf":
            click.echo(f"Error: Input file must be a PDF, got: {input_path.suffix}", err=True)
            sys.exit(1)
        
        # Determine output path
        if output is None:
            output = get_default_output_path(input_pdf)
        
        click.echo(f"Converting PDF to EPUB: {input_pdf}")
        click.echo(f"Output: {output}")
        
        # Run conversion
        result = convert(
            pdf_path=input_pdf,
            output_path=output,
            title=title,
            author=author,
            cover=cover,
            math_format=math_format.lower(),
            save_markdown=save_markdown,
            language=language
        )
        
        click.echo(f"✓ Conversion complete: {result}")
        sys.exit(0)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease ensure all dependencies are installed:", err=True)
        click.echo("  pip install pdf2epub", err=True)
        click.echo("  # Install pandoc separately: apt install pandoc (or brew install pandoc)", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: Conversion failed - {e}", err=True)
        if verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)


if __name__ == "__main__":
    main()
