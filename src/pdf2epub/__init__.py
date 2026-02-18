"""pdf2epub - Convert PDF books and scientific papers to EPUB format.

This package provides a two-phase pipeline:
1. Marker (marker-pdf): Converts PDF to Markdown with images
2. Pandoc: Converts Markdown to EPUB with proper formatting
"""

__version__ = "0.1.0"

from pdf2epub.converter import convert

__all__ = ["convert", "__version__"]
