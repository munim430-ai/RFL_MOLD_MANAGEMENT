#!/usr/bin/env python3
"""Phase 4 — Schema-ready Supabase export."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
IMPORT_DIR = DATA_DIR / "import"
UNIS_FILE = DATA_DIR / "universities_deduplicated.json"
PROGRAMS_FILE = DATA_DIR / "programs_scraped.json"
FIN_REFS_FILE = DATA_DIR / "financial_refs_for_human_review.json"
META_FILE = DATA_DIR / "phase3_meta.json"


def run() -> None:
    print("=== Phase 4: Schema-Ready Supabase Export ===\n")
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()

    # --- Universities import ---
    print("[1/3] Building universities_import.json...")
    unis = json.loads(UNIS_FILE.read_text(encoding="utf-8"))

    unis_import = []
    uni_id_map: dict[str, str] = {}  # university_id slug → uuid

    for u in unis:
        new_id = str(uuid.uuid4())
        uni_id_map[u["university_id"]] = new_id
        unis_import.append({
            "id": new_id,
            "name": u["canonical_name"],
            "country_code": u.get("country_code", "XX"),
            "domain": u.get("domain"),
            "source": "osint_scrape",
            "created_at": ts,
        })

    with open(IMPORT_DIR / "universities_import.json", "w", encoding="utf-8") as f:
        json.dump(unis_import, f, indent=2, ensure_ascii=False)
    print(f"  {len(unis_import)} universities written")

    # --- Programs import ---
    print("[2/3] Building programs_import.json and programs_needs_review.json...")
    programs_raw = json.loads(PROGRAMS_FILE.read_text(encoding="utf-8"))

    programs_ok = []
    programs_review = []

    for p in programs_raw:
        uni_slug = p.get("university_id")
        uni_uuid = uni_id_map.get(uni_slug)

        mapped = {
            "id": str(uuid.uuid4()),
            "university_id": uni_uuid,
            "program_name": p.get("program_name"),
            "program_type": p.get("program_type"),
            "field_of_study": p.get("field_of_study"),
            "min_gpa_raw": p.get("min_gpa_raw"),
            "min_gpa_scale": p.get("min_gpa_scale"),
            "gpa_scale_unknown": p.get("gpa_scale_unknown", False),
            "ielts_min": p.get("ielts_min"),
            "ielts_min_null_reason": p.get("ielts_min_null_reason"),
            "toefl_min": p.get("toefl_min"),
            "no_ielts": p.get("no_ielts", False),
            "conditional_admission": p.get("conditional_admission", False),
            "topik_min": p.get("topik_min"),
            "work_exp_months_required": p.get("work_exp_months_required"),
            "tuition_annual_local": p.get("tuition_annual_local"),
            "tuition_currency": p.get("tuition_currency"),
            "intake_months": p.get("intake_months", []),
            "application_deadline": p.get("application_deadline"),
            "source_url": p.get("source_url"),
            "data_confidence": p.get("data_confidence"),
            "human_verified": False,
            "created_at": ts,
        }

        if p.get("data_confidence") in ("high", "medium"):
            programs_ok.append(mapped)
        else:
            programs_review.append(mapped)

    with open(IMPORT_DIR / "programs_import.json", "w", encoding="utf-8") as f:
        json.dump(programs_ok, f, indent=2, ensure_ascii=False)
    with open(IMPORT_DIR / "programs_needs_review.json", "w", encoding="utf-8") as f:
        json.dump(programs_review, f, indent=2, ensure_ascii=False)
    print(f"  {len(programs_ok)} programs ready to import")
    print(f"  {len(programs_review)} programs need review (low confidence)")

    # --- Financial refs (pass-through) ---
    print("[3/3] Copying financial_refs_for_human_review.json...")
    if FIN_REFS_FILE.exists():
        fin_refs = json.loads(FIN_REFS_FILE.read_text(encoding="utf-8"))
        with open(IMPORT_DIR / "financial_refs_for_human_review.json", "w", encoding="utf-8") as f:
            json.dump(fin_refs, f, indent=2, ensure_ascii=False)
        print(f"  {len(fin_refs)} financial refs written")
    else:
        (IMPORT_DIR / "financial_refs_for_human_review.json").write_text("[]")
        print("  No financial refs file found — wrote empty array")

    print(f"\n✅ Export complete → {IMPORT_DIR}")
    print(f"   universities_import.json:           {len(unis_import)}")
    print(f"   programs_import.json:               {len(programs_ok)}")
    print(f"   programs_needs_review.json:         {len(programs_review)}")


if __name__ == "__main__":
    run()
