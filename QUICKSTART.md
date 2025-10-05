# Forensic Case Builder - Quick Reference

## Installation

```bash
pip install -e .
```

## Environment Setup

Set Tesseract data path (required for OCR):
```bash
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
```

## Quick Start

### Complete Pipeline (Recommended)

```bash
forensic-case-builder synthesize \
  /path/to/evidence \
  /path/to/processing \
  --db-path case.db \
  --output-dir ./reports
```

### Step-by-Step Workflow

#### 1. Scan Evidence
```bash
forensic-case-builder scan /path/to/evidence /path/to/processing
```
- Computes SHA256 for each file
- Copies files to processing area
- Stores metadata in database
- **Never modifies originals**

#### 2. Extract Text
```bash
forensic-case-builder extract /path/to/processing
```
- Extracts from plain text files
- Extracts from PDFs
- OCR on images (requires Tesseract)
- Parses email files (.eml)

#### 3. Index Content
```bash
forensic-case-builder index
```
- Creates FTS5 full-text search index
- Enables fast content searching

#### 4. Generate Reports
```bash
forensic-case-builder report --output-dir ./reports
```
Generates:
- `evidence_log_<timestamp>.xlsx` - Complete evidence inventory
- `timeline_<timestamp>.csv` - Timeline in CSV format
- `timeline_<timestamp>.xlsx` - Timeline in Excel format

#### 5. Build Declaration
```bash
forensic-case-builder build --output-dir ./reports
```
Generates:
- `declaration_<timestamp>.docx` - Formal declaration document

## Common Options

All commands support:
- `--db-path <path>` - Database file location (default: evidence.db)
- `--help` - Show command help

## Example Workflows

### Basic Investigation
```bash
# Scan evidence
forensic-case-builder scan /evidence /processing

# Extract and index
forensic-case-builder extract /processing
forensic-case-builder index

# Generate reports
forensic-case-builder report --output-dir ./output
forensic-case-builder build --output-dir ./output
```

### Searching Evidence
Use SQLite to search indexed content:
```bash
sqlite3 evidence.db "SELECT original_path FROM evidence_fts WHERE extracted_text MATCH 'keyword'"
```

### Database Queries

View all evidence:
```sql
SELECT id, original_path, sha256, file_size FROM evidence;
```

Search content:
```sql
SELECT e.original_path, ec.extracted_text 
FROM evidence e 
JOIN extracted_content ec ON e.id = ec.evidence_id 
WHERE ec.extracted_text LIKE '%search term%';
```

Full-text search:
```sql
SELECT evidence_id, original_path 
FROM evidence_fts 
WHERE extracted_text MATCH 'keyword1 OR keyword2';
```

## File Type Support

- **Text**: .txt, .md, .log
- **PDF**: .pdf
- **Images**: .jpg, .jpeg, .png, .tiff, .bmp (requires Tesseract)
- **Email**: .eml
- **Other**: Attempts text extraction

## Output Files

### Evidence Log (XLSX)
Columns:
- ID, Original Path, Processing Path
- SHA256, File Size, File Type
- Created/Modified/Accessed Times
- Scan Timestamp

### Timeline (CSV/XLSX)
Columns:
- Evidence ID, File Path, File Type
- Created/Modified/Accessed Times
- Scan Timestamp

### Declaration (DOCX)
Sections:
- Executive Summary
- Declaration Statement
- Evidence Inventory
- Certification

## Tips

1. **Always backup** originals before processing
2. **Use absolute paths** for reliability
3. **Set TESSDATA_PREFIX** before running OCR
4. **Check logs** in case of errors
5. **Use synthesize** for complete workflow
6. **Database is portable** - can be analyzed separately

## Troubleshooting

### Tesseract not found
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr

# Set environment variable
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
```

### Permission errors
Ensure you have read access to source and write access to processing/output directories.

### Database locked
Close any other connections to the database file.

## Performance

- **Scanning**: Fast, limited by disk I/O
- **Extraction**: 
  - Text/Email: Very fast
  - PDF: Moderate
  - OCR: Slow (depends on image size/quality)
- **Indexing**: Fast
- **Reports**: Fast

## Security Considerations

1. Evidence files are copied, never modified
2. SHA256 ensures integrity
3. All operations are logged
4. Database stores complete audit trail
5. Timestamps recorded at each step
