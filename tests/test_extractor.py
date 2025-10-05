"""Tests for extractor module."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from forensic_case_builder.extractor import (
    extract_plain_text,
    extract_pdf_text,
    extract_email_content
)


def test_extract_plain_text():
    """Test plain text extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is test content\nWith multiple lines")
        temp_path = f.name
    
    try:
        text = extract_plain_text(temp_path)
        assert text is not None
        assert "test content" in text
        assert "multiple lines" in text
    finally:
        Path(temp_path).unlink()


def test_extract_email_content():
    """Test email content extraction."""
    email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000

This is the email body.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
        f.write(email_content)
        temp_path = f.name
    
    try:
        text = extract_email_content(temp_path)
        assert text is not None
        assert "sender@example.com" in text
        assert "Test Email" in text
        assert "email body" in text
    finally:
        Path(temp_path).unlink()
