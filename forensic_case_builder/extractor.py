"""Text extraction module for plain text, PDF, images, and emails."""

import logging
import sqlite3
import os
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_plain_text(file_path):
    """Extract text from plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading plain text from {file_path}: {e}")
        return None


def extract_pdf_text(file_path):
    """Extract text from PDF file."""
    try:
        import PyPDF2
        text_parts = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return '\n'.join(text_parts)
    except Exception as e:
        logger.error(f"Error extracting PDF text from {file_path}: {e}")
        return None


def extract_image_text(file_path):
    """Extract text from image using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        
        # Check for TESSDATA_PREFIX environment variable
        tessdata_prefix = os.environ.get('TESSDATA_PREFIX')
        if tessdata_prefix:
            logger.info(f"Using TESSDATA_PREFIX: {tessdata_prefix}")
        
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {e}")
        return None


def extract_email_content(file_path):
    """Extract content from email file (.eml)."""
    try:
        import email
        from email import policy
        
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
        
        parts = []
        parts.append(f"From: {msg.get('From', 'Unknown')}")
        parts.append(f"To: {msg.get('To', 'Unknown')}")
        parts.append(f"Subject: {msg.get('Subject', 'No Subject')}")
        parts.append(f"Date: {msg.get('Date', 'Unknown')}")
        parts.append("")
        
        # Extract body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        parts.append(payload.decode('utf-8', errors='ignore'))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                parts.append(payload.decode('utf-8', errors='ignore'))
        
        return '\n'.join(parts)
    except Exception as e:
        logger.error(f"Error extracting email content from {file_path}: {e}")
        return None


def extract_all(processing_path, db_path):
    """Extract text from all evidence files in processing directory."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all evidence files
    cursor.execute("SELECT id, processing_path, file_type FROM evidence")
    evidence_files = cursor.fetchall()
    
    extracted_count = 0
    error_count = 0
    
    for evidence_id, proc_path, file_type in evidence_files:
        file_path = Path(proc_path)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            error_count += 1
            continue
        
        extracted_text = None
        content_type = file_type
        
        try:
            if file_type == 'text':
                extracted_text = extract_plain_text(file_path)
            elif file_type == 'pdf':
                extracted_text = extract_pdf_text(file_path)
            elif file_type == 'image':
                extracted_text = extract_image_text(file_path)
            elif file_type == 'email':
                extracted_text = extract_email_content(file_path)
            else:
                # Try to read as text anyway
                extracted_text = extract_plain_text(file_path)
                content_type = 'unknown'
            
            if extracted_text:
                # Insert extracted content
                cursor.execute("""
                    INSERT INTO extracted_content (
                        evidence_id, content_type, extracted_text, extraction_timestamp
                    ) VALUES (?, ?, ?, ?)
                """, (evidence_id, content_type, extracted_text, datetime.now().isoformat()))
                
                extracted_count += 1
                logger.info(f"Extracted text from {file_path} ({len(extracted_text)} chars)")
            else:
                logger.warning(f"No text extracted from {file_path}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"Error extracting from {file_path}: {e}")
            error_count += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"Extraction completed: {extracted_count} files extracted, {error_count} errors")
