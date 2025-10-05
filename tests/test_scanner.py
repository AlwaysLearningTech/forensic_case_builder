"""Tests for scanner module."""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from forensic_case_builder.scanner import (
    compute_sha256,
    init_database,
    scan_directory
)


def test_compute_sha256():
    """Test SHA256 computation."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        f.flush()
        temp_path = f.name
    
    try:
        sha256 = compute_sha256(temp_path)
        assert sha256 is not None
        assert len(sha256) == 64
        # SHA256 of "test content"
        assert sha256 == "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
    finally:
        Path(temp_path).unlink()


def test_init_database():
    """Test database initialization."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        init_database(db_path)
        
        # Verify tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'evidence' in tables
        assert 'extracted_content' in tables
        assert 'evidence_fts' in tables
        
        conn.close()
    finally:
        Path(db_path).unlink()


def test_scan_directory():
    """Test directory scanning and copying."""
    # Create temporary directories
    source_dir = tempfile.mkdtemp()
    processing_dir = tempfile.mkdtemp()
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Create test files
        test_file = Path(source_dir) / "test.txt"
        test_file.write_text("Test content")
        
        # Scan directory
        scan_directory(source_dir, processing_dir, db_path)
        
        # Verify file was copied
        copied_file = Path(processing_dir) / "test.txt"
        assert copied_file.exists()
        assert copied_file.read_text() == "Test content"
        
        # Verify database entry
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM evidence")
        count = cursor.fetchone()[0]
        assert count == 1
        
        cursor.execute("SELECT sha256, file_type FROM evidence")
        sha256, file_type = cursor.fetchone()
        assert len(sha256) == 64
        assert file_type == 'text'
        
        conn.close()
        
        # Verify original is unchanged
        assert test_file.exists()
        assert test_file.read_text() == "Test content"
        
    finally:
        shutil.rmtree(source_dir)
        shutil.rmtree(processing_dir)
        Path(db_path).unlink()
