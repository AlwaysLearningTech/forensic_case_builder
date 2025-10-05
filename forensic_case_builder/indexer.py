"""Indexer module for SQLite FTS5 full-text search."""

import logging
import sqlite3

logger = logging.getLogger(__name__)


def index_evidence(db_path):
    """Index extracted content in SQLite FTS5 virtual table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing FTS index
    cursor.execute("DELETE FROM evidence_fts")
    
    # Index all extracted content
    cursor.execute("""
        SELECT ec.id, ec.evidence_id, e.original_path, ec.extracted_text
        FROM extracted_content ec
        JOIN evidence e ON ec.evidence_id = e.id
    """)
    
    rows = cursor.fetchall()
    indexed_count = 0
    
    for row_id, evidence_id, original_path, extracted_text in rows:
        try:
            cursor.execute("""
                INSERT INTO evidence_fts (rowid, evidence_id, original_path, extracted_text)
                VALUES (?, ?, ?, ?)
            """, (row_id, evidence_id, original_path, extracted_text))
            indexed_count += 1
        except Exception as e:
            logger.error(f"Error indexing evidence {evidence_id}: {e}")
    
    conn.commit()
    conn.close()
    
    logger.info(f"Indexing completed: {indexed_count} items indexed in FTS5")
