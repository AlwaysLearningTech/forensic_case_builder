"""Scanner module to scan directories, compute SHA256, and copy files."""

import hashlib
import logging
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def compute_sha256(file_path):
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error computing SHA256 for {file_path}: {e}")
        return None


def init_database(db_path):
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Evidence table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT NOT NULL,
            processing_path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            file_size INTEGER,
            created_time TEXT,
            modified_time TEXT,
            accessed_time TEXT,
            file_type TEXT,
            scan_timestamp TEXT NOT NULL
        )
    """)
    
    # Extracted content table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS extracted_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER NOT NULL,
            content_type TEXT,
            extracted_text TEXT,
            extraction_timestamp TEXT NOT NULL,
            FOREIGN KEY (evidence_id) REFERENCES evidence(id)
        )
    """)
    
    # FTS5 virtual table for full-text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(
            evidence_id UNINDEXED,
            original_path,
            extracted_text
        )
    """)
    
    conn.commit()
    conn.close()


def scan_directory(source_path, processing_path, db_path):
    """
    Scan directory, compute SHA256, copy to processing area.
    Never modifies original files.
    """
    source = Path(source_path).resolve()
    processing = Path(processing_path).resolve()
    
    # Initialize database
    init_database(db_path)
    
    # Create processing directory if it doesn't exist
    processing.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    file_count = 0
    error_count = 0
    
    logger.info(f"Scanning directory: {source}")
    
    # Walk through all files in source directory
    for file_path in source.rglob('*'):
        if file_path.is_file():
            try:
                # Compute SHA256
                sha256 = compute_sha256(file_path)
                if sha256 is None:
                    error_count += 1
                    continue
                
                # Get file stats
                stat = file_path.stat()
                file_size = stat.st_size
                created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                accessed_time = datetime.fromtimestamp(stat.st_atime).isoformat()
                
                # Determine relative path
                rel_path = file_path.relative_to(source)
                
                # Create processing path maintaining directory structure
                proc_file = processing / rel_path
                proc_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file to processing area (never modify original)
                shutil.copy2(file_path, proc_file)
                
                # Detect file type
                suffix = file_path.suffix.lower()
                if suffix == '.txt':
                    file_type = 'text'
                elif suffix == '.pdf':
                    file_type = 'pdf'
                elif suffix in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                    file_type = 'image'
                elif suffix in ['.eml', '.msg']:
                    file_type = 'email'
                else:
                    file_type = 'other'
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO evidence (
                        original_path, processing_path, sha256, file_size,
                        created_time, modified_time, accessed_time, file_type,
                        scan_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(file_path), str(proc_file), sha256, file_size,
                    created_time, modified_time, accessed_time, file_type,
                    datetime.now().isoformat()
                ))
                
                file_count += 1
                logger.info(f"Processed: {file_path} -> SHA256: {sha256}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                error_count += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Scan completed: {file_count} files processed, {error_count} errors")
