#!/usr/bin/env python3
"""Generate data/COLLECTION_REPORT.md after all phases complete."""

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
IMPORT_DIR = DATA_DIR / "import"


def run() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    agencies = json.loads((DATA_DIR / "agencies_raw.json").read_text())
    unis = json.loads((DATA_DIR / "universities_deduplicated.json").read_text())
    programs = json.loads((DATA_DIR / "programs_scraped.json").read_text())
    meta = json.loads((DATA_DIR / "phase3_meta.json").read_text()) if (DATA_DIR / "phase3_meta.json").exists() else {}

    fin_refs_path = DATA_DIR / "financial_refs_for_human_review.json"
    fin_refs = json.loads(fin_refs_path.read_text()) if fin_refs_path.exists() else []

    # Country breakdown
    by_country: dict[str, int] = {}
    for u in unis:
        c = u.get("country", "Unknown")
        by_country[c] = by_country.get(c, 0) + 1

    # Confidence breakdown
    confidence: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    for p in programs:
        c = p.get("data_confidence", "low")
        confidence[c] = confidence.get(c, 0) + 1

    # Top 20 universities
    top20 = sorted(unis, key=lambda u: u.get("agency_mention_count", 0), reverse=True)[:20]

    # No requirements list
    no_reqs = meta.get("no_requirements", [])

    lines = [
        f"# UCI OSINT Data Collection Report",
        f"**Generated:** {ts}  ",
        f"",
        f"---",
        f"",
        f"## Summary Counts",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| **Agencies discovered** | {len(agencies)} |",
        f"| **Unique universities** | {len(unis)} |",
        f"| **Programs scraped** | {len(programs)} |",
        f"| **Financial refs for review** | {len(fin_refs)} |",
        f"",
        f"---",
        f"",
        f"## Programs by Confidence Level",
        f"",
        f"| Confidence | Count |",
        f"|-----------|-------|",
        f"| High | {confidence['high']} |",
        f"| Medium | {confidence['medium']} |",
        f"| Low | {confidence['low']} |",
        f"",
        f"---",
        f"",
        f"## Universities by Country",
        f"",
        f"| Country | Universities |",
        f"|---------|-------------|",
    ]

    for country, count in sorted(by_country.items(), key=lambda x: -x[1]):
        lines.append(f"| {country} | {count} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Top 20 Universities by Agency Mention Count",
        f"",
        f"| Rank | University | Country | Agency Mentions | Hipo Matched |",
        f"|------|-----------|---------|----------------|-------------|",
    ]
    for i, u in enumerate(top20, 1):
        hipo = "✅" if u.get("hipo_matched") else "❌"
        lines.append(
            f"| {i} | {u['canonical_name']} | {u.get('country', 'Unknown')} "
            f"| {u.get('agency_mention_count', 0)} | {hipo} |"
        )

    lines += [
        f"",
        f"---",
        f"",
        f"## Universities Without Scraped Admission Requirements",
        f"({len(no_reqs)} universities — manual follow-up required)",
        f"",
    ]
    for uid in no_reqs[:50]:  # cap at 50 for readability
        uni = next((u for u in unis if u["university_id"] == uid), None)
        name = uni["canonical_name"] if uni else uid
        lines.append(f"- {name}")
    if len(no_reqs) > 50:
        lines.append(f"- *(and {len(no_reqs) - 50} more — see phase3_meta.json)*")

    lines += [
        f"",
        f"---",
        f"",
        f"## Notes",
        f"- Scraping performed on publicly accessible pages only",
        f"- robots.txt respected for all university domains",
        f"- No personal data stored (testimonials/names skipped)",
        f"- Bank balance / proof-of-funds URLs logged separately in `financial_refs_for_human_review.json`",
        f"- Rate limit: 2-second delay per domain, exponential backoff on 429/503",
        f"",
    ]

    report = "\n".join(lines)
    out = DATA_DIR / "COLLECTION_REPORT.md"
    out.write_text(report, encoding="utf-8")
    print(f"✅ Written {out}")
    print(report[:1000])


if __name__ == "__main__":
    run()
