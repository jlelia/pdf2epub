"""Tests for utility functions."""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pdf2epub.utils import (
    get_model_cache_dir,
    clean_incomplete_model_downloads,
)


class TestGetModelCacheDir:
    """Tests for get_model_cache_dir function."""
    
    def test_get_model_cache_dir_with_env_var(self):
        """Test that DATALAB_MODELS_HOME environment variable is respected."""
        with patch.dict(os.environ, {'DATALAB_MODELS_HOME': '/custom/cache'}):
            cache_dir = get_model_cache_dir()
            assert cache_dir == Path('/custom/cache')
    
    def test_get_model_cache_dir_windows(self):
        """Test default cache directory on Windows."""
        with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\test\\AppData\\Local'}, clear=True):
            with patch('sys.platform', 'win32'):
                cache_dir = get_model_cache_dir()
                expected = Path('C:\\Users\\test\\AppData\\Local') / 'datalab' / 'datalab' / 'Cache' / 'models'
                assert cache_dir == expected
    
    def test_get_model_cache_dir_unix(self):
        """Test default cache directory on Unix-like systems."""
        with patch.dict(os.environ, {'XDG_CACHE_HOME': '/home/user/.cache'}, clear=True):
            with patch('sys.platform', 'linux'):
                cache_dir = get_model_cache_dir()
                expected = Path('/home/user/.cache') / 'datalab' / 'models'
                assert cache_dir == expected
    
    def test_get_model_cache_dir_unix_no_xdg(self):
        """Test default cache directory on Unix-like systems without XDG_CACHE_HOME."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.platform', 'linux'):
                with patch('os.path.expanduser') as mock_expand:
                    mock_expand.return_value = '/home/user/.cache'
                    cache_dir = get_model_cache_dir()
                    expected = Path('/home/user/.cache') / 'datalab' / 'models'
                    assert cache_dir == expected


class TestCleanIncompleteModelDownloads:
    """Tests for clean_incomplete_model_downloads function."""
    
    def test_clean_incomplete_model_downloads_no_cache_dir(self, tmp_path, caplog):
        """Test behavior when cache directory doesn't exist."""
        import logging
        non_existent_cache = tmp_path / "non_existent"
        
        with caplog.at_level(logging.DEBUG):
            with patch('pdf2epub.utils.get_model_cache_dir', return_value=non_existent_cache):
                clean_incomplete_model_downloads()
            
        assert "does not exist" in caplog.text
    
    def test_clean_incomplete_model_downloads_empty_dir(self, tmp_path):
        """Test cleaning an empty model directory."""
        cache_dir = tmp_path / "cache"
        model_type_dir = cache_dir / "layout"
        model_version_dir = model_type_dir / "2025_09_23"
        model_version_dir.mkdir(parents=True)
        
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            clean_incomplete_model_downloads()
        
        # Empty directory should be removed
        assert not model_version_dir.exists()
    
    def test_clean_incomplete_model_downloads_only_git_files(self, tmp_path, caplog):
        """Test cleaning a directory with only git-related files."""
        cache_dir = tmp_path / "cache"
        model_type_dir = cache_dir / "layout"
        model_version_dir = model_type_dir / "2025_09_23"
        model_version_dir.mkdir(parents=True)
        
        # Create only git-related files
        (model_version_dir / ".gitattributes").write_text("test")
        (model_version_dir / ".gitignore").write_text("test")
        (model_version_dir / "README.md").write_text("test")
        
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            clean_incomplete_model_downloads()
        
        # Directory with only git files should be removed
        assert not model_version_dir.exists()
        assert "Removing incomplete model download" in caplog.text
    
    def test_clean_incomplete_model_downloads_few_files(self, tmp_path, caplog):
        """Test cleaning a directory with very few non-git files."""
        cache_dir = tmp_path / "cache"
        model_type_dir = cache_dir / "layout"
        model_version_dir = model_type_dir / "2025_09_23"
        model_version_dir.mkdir(parents=True)
        
        # Create git files + only 2 real files (less than threshold of 3)
        (model_version_dir / ".gitattributes").write_text("test")
        (model_version_dir / "model.pt").write_text("test")
        (model_version_dir / "config.json").write_text("test")
        
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            clean_incomplete_model_downloads()
        
        # Directory should be removed (< 3 non-git files)
        assert not model_version_dir.exists()
        assert "Removing incomplete model download" in caplog.text
    
    def test_clean_incomplete_model_downloads_complete_dir(self, tmp_path, caplog):
        """Test that complete directories are not removed."""
        cache_dir = tmp_path / "cache"
        model_type_dir = cache_dir / "layout"
        model_version_dir = model_type_dir / "2025_09_23"
        model_version_dir.mkdir(parents=True)
        
        # Create git files + enough real files to be considered complete
        (model_version_dir / ".gitattributes").write_text("test")
        (model_version_dir / "model.pt").write_text("test")
        (model_version_dir / "config.json").write_text("test")
        (model_version_dir / "processor_config.json").write_text("test")
        (model_version_dir / "tokenizer.json").write_text("test")
        
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            clean_incomplete_model_downloads()
        
        # Directory should NOT be removed (>= 3 non-git files)
        assert model_version_dir.exists()
        assert "Removing incomplete model download" not in caplog.text
    
    def test_clean_incomplete_model_downloads_multiple_models(self, tmp_path, caplog):
        """Test cleaning multiple model directories."""
        cache_dir = tmp_path / "cache"
        
        # Create incomplete layout model
        layout_dir = cache_dir / "layout" / "2025_09_23"
        layout_dir.mkdir(parents=True)
        (layout_dir / ".gitattributes").write_text("test")
        
        # Create complete detection model
        detection_dir = cache_dir / "detection" / "2025_09_23"
        detection_dir.mkdir(parents=True)
        for i in range(5):
            (detection_dir / f"model_{i}.pt").write_text("test")
        
        # Create incomplete ocr model
        ocr_dir = cache_dir / "ocr" / "2025_09_23"
        ocr_dir.mkdir(parents=True)
        (ocr_dir / "README.md").write_text("test")
        
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            clean_incomplete_model_downloads()
        
        # Incomplete directories should be removed
        assert not layout_dir.exists()
        assert not ocr_dir.exists()
        # Complete directory should remain
        assert detection_dir.exists()
    
    def test_clean_incomplete_model_downloads_permission_error(self, tmp_path, caplog):
        """Test graceful handling of permission errors during cleanup."""
        cache_dir = tmp_path / "cache"
        model_type_dir = cache_dir / "layout"
        model_version_dir = model_type_dir / "2025_09_23"
        model_version_dir.mkdir(parents=True)
        
        (model_version_dir / ".gitattributes").write_text("test")
        
        # Mock shutil.rmtree to raise a permission error
        with patch('pdf2epub.utils.get_model_cache_dir', return_value=cache_dir):
            with patch('shutil.rmtree', side_effect=PermissionError("Access denied")):
                clean_incomplete_model_downloads()
        
        assert "Failed to remove" in caplog.text
