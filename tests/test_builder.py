"""Tests for builder module."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from forensic_case_builder.scanner import init_database
from forensic_case_builder.builder import build_case


def test_build_case():
    """Test Declaration document generation."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    output_dir = tempfile.mkdtemp()
    
    try:
        # Initialize database and add test data
        init_database(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO evidence (
                original_path, processing_path, sha256, file_size,
                created_time, modified_time, accessed_time, file_type,
                scan_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "/test/file.txt", "/proc/file.txt", "abc123", 100,
            "2024-01-01", "2024-01-01", "2024-01-01", "text",
            "2024-01-01"
        ))
        
        conn.commit()
        conn.close()
        
        # Build declaration
        build_case(db_path, output_dir)
        
        # Verify file was created
        output_files = list(Path(output_dir).glob("declaration_*.docx"))
        assert len(output_files) == 1
        assert output_files[0].stat().st_size > 0
        
    finally:
        Path(db_path).unlink()
        import shutil
        shutil.rmtree(output_dir)
