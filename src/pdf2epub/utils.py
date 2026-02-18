"""Utility functions for pdf2epub."""

import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application.
    
    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


@contextmanager
def temporary_directory(prefix: str = "pdf2epub_") -> Generator[Path, None, None]:
    """Create a temporary directory that is cleaned up after use.
    
    Args:
        prefix: Prefix for the temporary directory name.
        
    Yields:
        Path to the temporary directory.
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    temp_path = Path(temp_dir)
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path, ignore_errors=True)


def validate_pdf_file(file_path: str) -> Path:
    """Validate that a file exists and is a PDF.
    
    Args:
        file_path: Path to the file to validate.
        
    Returns:
        Path object for the validated file.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a PDF.
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {file_path}")
    
    return path


def get_default_output_path(input_path: str, extension: str = ".epub") -> str:
    """Generate default output path by changing the extension.
    
    Args:
        input_path: Path to the input file.
        extension: Extension for the output file (with dot).
        
    Returns:
        Output path with new extension.
    """
    path = Path(input_path)
    return str(path.with_suffix(extension))


def ensure_directory_exists(path: str | Path) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory.
        
    Returns:
        Path object for the directory.
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
