# Forensic Case Builder

A local-first evidence pipeline for Python 3.11 that provides comprehensive forensic case building capabilities.

## Features

- **Evidence Scanning**: Scan local directories, compute SHA256 hashes, and copy to processing area
- **Text Extraction**: Extract text from plain text, PDF, and images (via Tesseract OCR)
- **Email Parsing**: Parse and extract content from email files (.eml)
- **Full-Text Search**: Index content in SQLite with FTS5 for fast searching
- **Report Generation**: 
  - Evidence Log (XLSX)
  - Timeline (CSV/XLSX)
  - Declaration Document (DOCX)
- **Original Preservation**: Never modifies original files
- **Clear Logging**: Comprehensive logging throughout the pipeline
- **Testing**: Full pytest test suite

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Requirements

- Python 3.11+
- Tesseract OCR (for image text extraction)
  - Set `TESSDATA_PREFIX` environment variable to your Tesseract data directory

## CLI Commands

### scan
Scan local root directory, compute SHA256, and copy to processing area.

```bash
forensic-case-builder scan <source_path> <processing_path> [--db-path evidence.db]
```

### extract
Extract text from plain/PDF/images via Tesseract and parse emails.

```bash
forensic-case-builder extract <processing_path> [--db-path evidence.db]
```

### index
Index extracted content in SQLite with FTS5.

```bash
forensic-case-builder index [--db-path evidence.db]
```

### report
Generate Evidence Log (XLSX) and timeline (CSV/XLSX).

```bash
forensic-case-builder report [--db-path evidence.db] [--output-dir .]
```

### build
Generate Declaration (DOCX).

```bash
forensic-case-builder build [--db-path evidence.db] [--output-dir .]
```

### synthesize
Run complete pipeline: scan, extract, index, report, and build.

```bash
forensic-case-builder synthesize <source_path> <processing_path> [--db-path evidence.db] [--output-dir .]
```

## Usage Example

### Complete Pipeline

```bash
# Run the complete pipeline
forensic-case-builder synthesize /path/to/evidence /path/to/processing --output-dir ./reports

# This will:
# 1. Scan and copy evidence files
# 2. Extract text content
# 3. Index in SQLite FTS5
# 4. Generate evidence log and timeline
# 5. Build declaration document
```

### Step-by-Step

```bash
# Step 1: Scan evidence
forensic-case-builder scan /path/to/evidence /path/to/processing

# Step 2: Extract text
forensic-case-builder extract /path/to/processing

# Step 3: Index content
forensic-case-builder index

# Step 4: Generate reports
forensic-case-builder report --output-dir ./reports

# Step 5: Build declaration
forensic-case-builder build --output-dir ./reports
```

## Environment Variables

- `TESSDATA_PREFIX`: Path to Tesseract training data (required for OCR)

Example:
```bash
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
```

## Testing

Run tests with pytest:

```bash
pytest
```

With coverage:

```bash
pytest --cov=forensic_case_builder --cov-report=html
```

## Output Files

- `evidence_log_<timestamp>.xlsx`: Comprehensive evidence log with SHA256 hashes
- `timeline_<timestamp>.csv`: Timeline of evidence in CSV format
- `timeline_<timestamp>.xlsx`: Timeline of evidence in XLSX format
- `declaration_<timestamp>.docx`: Formal declaration document
- `evidence.db`: SQLite database with all evidence and extracted content

## Architecture

### Modules

- `scanner.py`: Directory scanning and file hashing
- `extractor.py`: Text extraction from various file types
- `indexer.py`: SQLite FTS5 indexing
- `reporter.py`: Report generation (XLSX, CSV)
- `builder.py`: Declaration document generation (DOCX)
- `synthesizer.py`: Complete pipeline orchestration
- `cli.py`: Command-line interface

### Database Schema

**evidence table:**
- id, original_path, processing_path, sha256, file_size
- created_time, modified_time, accessed_time, file_type, scan_timestamp

**extracted_content table:**
- id, evidence_id, content_type, extracted_text, extraction_timestamp

**evidence_fts (FTS5 virtual table):**
- evidence_id, original_path, extracted_text

## Principles

1. **Never modify originals**: All operations are performed on copies
2. **Clear logging**: Every operation is logged
3. **Data integrity**: SHA256 verification for all files
4. **Comprehensive testing**: Full test coverage with pytest
