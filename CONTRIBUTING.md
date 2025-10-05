# Contributing to Forensic Case Builder

Thank you for your interest in contributing to the Forensic Case Builder!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/AlwaysLearningTech/forensic_case_builder.git
cd forensic_case_builder
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Install Tesseract OCR (for image text extraction):
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

4. Set up environment:
```bash
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=forensic_case_builder --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_scanner.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Add type hints where appropriate

## Project Structure

```
forensic_case_builder/
├── forensic_case_builder/      # Main package
│   ├── __init__.py
│   ├── cli.py                  # Command-line interface
│   ├── scanner.py              # Directory scanning and hashing
│   ├── extractor.py            # Text extraction
│   ├── indexer.py              # FTS5 indexing
│   ├── reporter.py             # Report generation
│   ├── builder.py              # Declaration builder
│   └── synthesizer.py          # Pipeline orchestration
├── tests/                      # Test suite
│   ├── test_scanner.py
│   ├── test_extractor.py
│   ├── test_indexer.py
│   ├── test_reporter.py
│   ├── test_builder.py
│   └── test_integration.py
├── pyproject.toml              # Project configuration
├── README.md                   # Documentation
└── example.py                  # Example usage
```

## Key Principles

1. **Never modify originals**: All operations on copies only
2. **Clear logging**: Log all operations and errors
3. **Data integrity**: Use SHA256 for verification
4. **Comprehensive testing**: Test all functionality

## Adding New Features

1. Write tests first (TDD approach)
2. Implement the feature
3. Update documentation
4. Submit a pull request

## Testing Checklist

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage remains high (>70%)
- [ ] Integration tests pass
- [ ] Example script still works

## Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Open an issue on GitHub for any questions or discussions.
