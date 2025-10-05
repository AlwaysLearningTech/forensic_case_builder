"""Synthesizer module to run the complete evidence pipeline."""

import logging
from .scanner import scan_directory
from .extractor import extract_all
from .indexer import index_evidence
from .reporter import generate_reports
from .builder import build_case

logger = logging.getLogger(__name__)


def synthesize_case(source_path, processing_path, db_path, output_dir):
    """
    Run complete evidence pipeline:
    1. Scan source directory and copy to processing area
    2. Extract text from all files
    3. Index content in FTS5
    4. Generate reports (Evidence Log, Timeline)
    5. Build Declaration document
    """
    logger.info("Starting complete evidence pipeline")
    
    # Step 1: Scan
    logger.info("Step 1/5: Scanning and copying evidence...")
    scan_directory(source_path, processing_path, db_path)
    
    # Step 2: Extract
    logger.info("Step 2/5: Extracting text content...")
    extract_all(processing_path, db_path)
    
    # Step 3: Index
    logger.info("Step 3/5: Indexing content in FTS5...")
    index_evidence(db_path)
    
    # Step 4: Report
    logger.info("Step 4/5: Generating reports...")
    generate_reports(db_path, output_dir)
    
    # Step 5: Build
    logger.info("Step 5/5: Building declaration document...")
    build_case(db_path, output_dir)
    
    logger.info("Complete evidence pipeline finished successfully")
