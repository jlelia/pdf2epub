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


def get_model_cache_dir() -> Path:
    """Get the directory where marker/surya models are cached.
    
    Returns:
        Path to the model cache directory.
    """
    # Check for environment variable first
    if cache_home := os.environ.get('DATALAB_MODELS_HOME'):
        return Path(cache_home)
    
    # Use platform-specific cache directories
    if sys.platform == 'win32':
        # Windows: %LOCALAPPDATA%/datalab/datalab/Cache/models
        local_app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local'))
        return Path(local_app_data) / 'datalab' / 'datalab' / 'Cache' / 'models'
    else:
        # Unix-like: $XDG_CACHE_HOME/datalab/models or ~/.cache/datalab/models
        cache_home = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
        return Path(cache_home) / 'datalab' / 'models'


def clean_incomplete_model_downloads(logger: logging.Logger | None = None) -> None:
    """Clean up incomplete model downloads that may cause conflicts.
    
    This function removes partially downloaded model directories that can cause
    'Destination path already exists' errors during model downloads.
    
    Args:
        logger: Optional logger for reporting cleanup actions.
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    cache_dir = get_model_cache_dir()
    
    if not cache_dir.exists():
        logger.debug(f"Model cache directory does not exist: {cache_dir}")
        return
    
    # Look for model subdirectories
    for model_type_dir in cache_dir.iterdir():
        if not model_type_dir.is_dir():
            continue
            
        # Check each model version directory
        for model_version_dir in model_type_dir.iterdir():
            if not model_version_dir.is_dir():
                continue
            
            # A complete download should have multiple files. If it only has a few
            # files like .gitattributes or .gitignore, it's likely incomplete.
            files = list(model_version_dir.iterdir())
            
            # Consider it incomplete if:
            # 1. It's empty
            # 2. It only has git-related files
            # 3. It has very few files (< 3)
            git_files = {'.gitattributes', '.gitignore', 'README.md'}
            non_git_files = [f for f in files if f.name not in git_files]
            
            if len(files) == 0 or len(non_git_files) < 3:
                logger.warning(
                    f"Removing incomplete model download: {model_version_dir} "
                    f"({len(files)} total files, {len(non_git_files)} non-git files)"
                )
                try:
                    shutil.rmtree(model_version_dir)
                    logger.info(f"Successfully removed incomplete download: {model_version_dir}")
                except Exception as e:
                    logger.warning(f"Failed to remove {model_version_dir}: {e}")
