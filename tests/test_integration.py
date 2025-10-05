"""Integration tests for the complete forensic case builder pipeline."""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from forensic_case_builder.synthesizer import synthesize_case


def test_complete_pipeline():
    """Test the complete evidence pipeline end-to-end."""
    # Create temporary directories
    source_dir = tempfile.mkdtemp()
    processing_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Create test evidence files
        test_txt = Path(source_dir) / "evidence.txt"
        test_txt.write_text("This is critical evidence for the investigation.")
        
        test_email = Path(source_dir) / "communication.eml"
        test_email.write_text("""From: witness@example.com
To: investigator@example.com
Subject: Evidence Report
Date: Mon, 1 Jan 2024 12:00:00 +0000

This email contains important information.
""")
        
        # Create subdirectory with file
        subdir = Path(source_dir) / "documents"
        subdir.mkdir()
        (subdir / "report.txt").write_text("Investigation report content.")
        
        # Run complete pipeline
        synthesize_case(source_dir, processing_dir, db_path, output_dir)
        
        # Verify originals unchanged
        assert test_txt.exists()
        assert test_txt.read_text() == "This is critical evidence for the investigation."
        
        # Verify processing copies exist
        assert (Path(processing_dir) / "evidence.txt").exists()
        assert (Path(processing_dir) / "communication.eml").exists()
        assert (Path(processing_dir) / "documents" / "report.txt").exists()
        
        # Verify database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM evidence")
        assert cursor.fetchone()[0] == 3
        
        cursor.execute("SELECT COUNT(*) FROM extracted_content")
        assert cursor.fetchone()[0] == 3
        
        cursor.execute("SELECT COUNT(*) FROM evidence_fts")
        assert cursor.fetchone()[0] == 3
        
        # Test FTS search
        cursor.execute("SELECT COUNT(*) FROM evidence_fts WHERE extracted_text MATCH 'evidence'")
        assert cursor.fetchone()[0] >= 1
        
        conn.close()
        
        # Verify output files
        output_files = list(Path(output_dir).glob("*"))
        assert len(output_files) == 4  # evidence_log, timeline csv, timeline xlsx, declaration
        
        assert len(list(Path(output_dir).glob("evidence_log_*.xlsx"))) == 1
        assert len(list(Path(output_dir).glob("timeline_*.csv"))) == 1
        assert len(list(Path(output_dir).glob("timeline_*.xlsx"))) == 1
        assert len(list(Path(output_dir).glob("declaration_*.docx"))) == 1
        
    finally:
        shutil.rmtree(source_dir)
        shutil.rmtree(processing_dir)
        shutil.rmtree(output_dir)
        Path(db_path).unlink()


def test_sha256_integrity():
    """Test that SHA256 hashes are correctly computed and stored."""
    source_dir = tempfile.mkdtemp()
    processing_dir = tempfile.mkdtemp()
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Create test file with known content
        test_file = Path(source_dir) / "test.txt"
        test_content = "test content"
        test_file.write_text(test_content)
        
        # Expected SHA256 of "test content"
        expected_sha256 = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
        
        # Import and run scanner
        from forensic_case_builder.scanner import scan_directory
        scan_directory(source_dir, processing_dir, db_path)
        
        # Verify SHA256 in database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sha256 FROM evidence WHERE original_path = ?", (str(test_file),))
        sha256 = cursor.fetchone()[0]
        conn.close()
        
        assert sha256 == expected_sha256
        
    finally:
        shutil.rmtree(source_dir)
        shutil.rmtree(processing_dir)
        Path(db_path).unlink()
