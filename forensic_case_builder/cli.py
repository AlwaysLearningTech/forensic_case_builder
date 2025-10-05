"""CLI interface for forensic case builder."""

import click
import logging
from pathlib import Path
from .scanner import scan_directory
from .extractor import extract_all
from .indexer import index_evidence
from .reporter import generate_reports
from .builder import build_case
from .synthesizer import synthesize_case

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Forensic Case Builder - Local-first evidence pipeline."""
    pass


@cli.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.argument('processing_path', type=click.Path())
@click.option('--db-path', default='evidence.db', help='Database file path')
def scan(source_path, processing_path, db_path):
    """Scan local root directory, compute SHA256, and copy to processing area."""
    logger.info(f"Scanning {source_path} and copying to {processing_path}")
    scan_directory(source_path, processing_path, db_path)
    logger.info("Scan completed")


@cli.command()
@click.argument('processing_path', type=click.Path(exists=True))
@click.option('--db-path', default='evidence.db', help='Database file path')
def extract(processing_path, db_path):
    """Extract text from plain/PDF/images via Tesseract and parse emails."""
    logger.info(f"Extracting text from evidence in {processing_path}")
    extract_all(processing_path, db_path)
    logger.info("Extraction completed")


@cli.command()
@click.option('--db-path', default='evidence.db', help='Database file path')
def index(db_path):
    """Index extracted content in SQLite with FTS5."""
    logger.info(f"Indexing evidence in {db_path}")
    index_evidence(db_path)
    logger.info("Indexing completed")


@cli.command()
@click.option('--db-path', default='evidence.db', help='Database file path')
@click.option('--output-dir', default='.', help='Output directory for reports')
def report(db_path, output_dir):
    """Generate Evidence Log (XLSX) and timeline (CSV/XLSX)."""
    logger.info(f"Generating reports from {db_path}")
    generate_reports(db_path, output_dir)
    logger.info("Reports generated")


@cli.command()
@click.option('--db-path', default='evidence.db', help='Database file path')
@click.option('--output-dir', default='.', help='Output directory for declaration')
def build(db_path, output_dir):
    """Generate Declaration (DOCX)."""
    logger.info(f"Building declaration from {db_path}")
    build_case(db_path, output_dir)
    logger.info("Declaration built")


@cli.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.argument('processing_path', type=click.Path())
@click.option('--db-path', default='evidence.db', help='Database file path')
@click.option('--output-dir', default='.', help='Output directory for all outputs')
def synthesize(source_path, processing_path, db_path, output_dir):
    """Run complete pipeline: scan, extract, index, report, and build."""
    logger.info("Starting complete evidence pipeline")
    synthesize_case(source_path, processing_path, db_path, output_dir)
    logger.info("Pipeline completed")


if __name__ == '__main__':
    cli()
