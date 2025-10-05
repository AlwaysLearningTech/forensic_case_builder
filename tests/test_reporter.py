"""Tests for reporter module."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from forensic_case_builder.scanner import init_database
from forensic_case_builder.reporter import (
    generate_evidence_log_xlsx,
    generate_timeline_csv,
    generate_timeline_xlsx
)


def test_generate_evidence_log_xlsx():
    """Test Evidence Log XLSX generation."""
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
        
        # Generate report
        output_path = Path(output_dir) / "evidence_log.xlsx"
        generate_evidence_log_xlsx(db_path, output_path)
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
    finally:
        Path(db_path).unlink()
        import shutil
        shutil.rmtree(output_dir)


def test_generate_timeline_csv():
    """Test timeline CSV generation."""
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
        
        # Generate timeline
        output_path = Path(output_dir) / "timeline.csv"
        generate_timeline_csv(db_path, output_path)
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verify content
        content = output_path.read_text()
        assert "Evidence ID" in content
        assert "/test/file.txt" in content
        
    finally:
        Path(db_path).unlink()
        import shutil
        shutil.rmtree(output_dir)
