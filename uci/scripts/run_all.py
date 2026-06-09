#!/usr/bin/env python3
"""Run the full UCI OSINT data collection pipeline (Phases 1–4 + report)."""

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent

PIPELINE = [
    ("Phase 1 — Agency discovery", SCRIPTS / "phase1_agency_discovery.py"),
    ("Phase 2 — University extraction", SCRIPTS / "phase2_university_extraction.py"),
    ("Phase 3 — Admission requirements", SCRIPTS / "phase3_admission_requirements.py"),
    ("Phase 4 — Schema export", SCRIPTS / "phase4_schema_export.py"),
    ("Report generation", SCRIPTS / "generate_collection_report.py"),
]

for label, script in PIPELINE:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}\n")
    result = subprocess.run([sys.executable, str(script)])
    if result.returncode != 0:
        print(f"\n❌ {label} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

print("\n✅ Full pipeline complete.")
