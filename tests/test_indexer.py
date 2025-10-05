"""Tests for indexer module."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from forensic_case_builder.scanner import init_database
from forensic_case_builder.indexer import index_evidence


def test_index_evidence():
    """Test FTS5 indexing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Initialize database
        init_database(db_path)
        
        # Insert test data
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
        
        evidence_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO extracted_content (
                evidence_id, content_type, extracted_text, extraction_timestamp
            ) VALUES (?, ?, ?, ?)
        """, (evidence_id, "text", "This is test content for searching", "2024-01-01"))
        
        conn.commit()
        conn.close()
        
        # Index evidence
        index_evidence(db_path)
        
        # Verify indexing
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM evidence_fts")
        count = cursor.fetchone()[0]
        assert count == 1
        
        # Test search
        cursor.execute("SELECT * FROM evidence_fts WHERE extracted_text MATCH 'searching'")
        results = cursor.fetchall()
        assert len(results) == 1
        
        conn.close()
        
    finally:
        Path(db_path).unlink()
