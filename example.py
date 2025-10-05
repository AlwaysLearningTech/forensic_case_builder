#!/usr/bin/env python3
"""
Example script demonstrating the Forensic Case Builder.

This script creates sample evidence files and runs the complete pipeline.
"""

import tempfile
import shutil
from pathlib import Path
from forensic_case_builder.synthesizer import synthesize_case


def create_sample_evidence(evidence_dir):
    """Create sample evidence files for demonstration."""
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample text document
    (evidence_dir / "witness_statement.txt").write_text("""
Witness Statement
Date: January 15, 2024
Time: 14:30

I observed the incident at approximately 2:00 PM near the intersection
of Main Street and Oak Avenue. The suspect was wearing a dark jacket
and appeared to be in a hurry.

Signed: John Doe
    """)
    
    # Sample email
    (evidence_dir / "evidence_email.eml").write_text("""From: witness@example.com
To: investigator@example.com
Subject: Incident Report
Date: Mon, 15 Jan 2024 15:00:00 +0000

Dear Investigator,

I am writing to provide additional information about the incident
that occurred on Main Street. I have attached my detailed observations.

Best regards,
Jane Smith
    """)
    
    # Sample investigation notes
    notes_dir = evidence_dir / "investigation_notes"
    notes_dir.mkdir(exist_ok=True)
    
    (notes_dir / "initial_assessment.txt").write_text("""
Initial Assessment Report

Case Number: 2024-001
Date: January 15, 2024
Investigator: Detective Smith

Summary:
- Incident occurred at 14:00 hours
- Multiple witnesses present
- Evidence collected from scene
- Suspect identified from CCTV footage

Next Steps:
- Interview additional witnesses
- Review forensic evidence
- Prepare case documentation
    """)
    
    (notes_dir / "evidence_log.txt").write_text("""
Evidence Log

Item 1: Witness statements (collected)
Item 2: CCTV footage (under review)
Item 3: Physical evidence (sent to lab)
Item 4: Photographs (processed)
    """)
    
    print(f"Created sample evidence in: {evidence_dir}")
    print(f"  - 2 text documents")
    print(f"  - 1 email file")
    print(f"  - 2 investigation notes")


def main():
    """Run the complete forensic case builder pipeline with sample data."""
    print("=" * 70)
    print("Forensic Case Builder - Example Demonstration")
    print("=" * 70)
    print()
    
    # Create temporary directories
    base_dir = Path(tempfile.mkdtemp(prefix="forensic_demo_"))
    evidence_dir = base_dir / "evidence"
    processing_dir = base_dir / "processing"
    output_dir = base_dir / "output"
    db_path = str(base_dir / "evidence.db")
    
    try:
        # Create sample evidence
        print("Step 1: Creating sample evidence files...")
        create_sample_evidence(evidence_dir)
        print()
        
        # Run the complete pipeline
        print("Step 2: Running complete forensic pipeline...")
        print("-" * 70)
        synthesize_case(
            str(evidence_dir),
            str(processing_dir),
            db_path,
            str(output_dir)
        )
        print("-" * 70)
        print()
        
        # Display results
        print("Step 3: Pipeline completed successfully!")
        print()
        print(f"Evidence files processed:")
        for f in sorted(processing_dir.rglob("*")):
            if f.is_file():
                print(f"  - {f.relative_to(processing_dir)}")
        print()
        
        print(f"Generated reports in: {output_dir}")
        for f in sorted(output_dir.glob("*")):
            size = f.stat().st_size
            print(f"  - {f.name} ({size:,} bytes)")
        print()
        
        print(f"Database created: {db_path}")
        
        # Query database statistics
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM evidence")
        evidence_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM extracted_content")
        extracted_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(file_size) FROM evidence")
        total_size = cursor.fetchone()[0]
        
        conn.close()
        
        print()
        print("Statistics:")
        print(f"  - Evidence files: {evidence_count}")
        print(f"  - Files with extracted text: {extracted_count}")
        print(f"  - Total evidence size: {total_size:,} bytes")
        print()
        
        print("=" * 70)
        print("Demo completed successfully!")
        print(f"All files are in: {base_dir}")
        print("You can inspect the output files to see the results.")
        print("=" * 70)
        
        return base_dir
        
    except Exception as e:
        print(f"Error: {e}")
        shutil.rmtree(base_dir)
        raise


if __name__ == "__main__":
    demo_dir = main()
    print()
    print(f"Note: Demo files are in {demo_dir}")
    print("Remember to clean up when done.")
