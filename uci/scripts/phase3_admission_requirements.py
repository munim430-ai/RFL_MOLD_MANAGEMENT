#!/usr/bin/env python3
"""Phase 3 — Admission requirements scraping from university websites."""

import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"
UNIS_FILE = DATA_DIR / "universities_deduplicated.json"
OUTPUT_FILE = DATA_DIR / "programs_scraped.json"
FIN_REFS_FILE = DATA_DIR / "financial_refs_for_human_review.json"
MAX_UNIVERSITIES = 500
DELAY = 1
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# Patterns for extracting requirements from text
IELTS_PAT = re.compile(r"IELTS[^\d]*(\d+(?:\.\d+)?)", re.IGNORECASE)
TOEFL_PAT = re.compile(r"TOEFL[^\d]*(\d{2,3})", re.IGNORECASE)
TOPIK_PAT = re.compile(r"TOPIK[^\d]*(\d)", re.IGNORECASE)
GPA_PAT = re.compile(
    r"(?:minimum\s+)?(?:GPA|grade\s+point)[^\d]*(\d+(?:\.\d+)?)\s*(?:/\s*(\d+(?:\.\d+)?))?",
    re.IGNORECASE,
)
# 4.0 scale implied when no denominator; detect percentage GPAs
PERCENT_GPA_PAT = re.compile(r"(\d{2,3})\s*%\s*(?:or\s+above|minimum|required)?", re.IGNORECASE)
TUITION_PAT = re.compile(
    r"(?:tuition|fee)[^\d£$€¥₩]{0,30}([\$£€¥₩]?\s*\d[\d,\.]+)\s*(USD|GBP|EUR|AUD|CAD|KRW|JPY|MYR|TRY|CNY|NZD)?",
    re.IGNORECASE,
)
WAIVER_PAT = re.compile(
    r"(?:no\s+(?:english|IELTS|TOEFL)\s+(?:test|score|requirement)s?|english\s+waiver|"
    r"exempt(?:ion|ed)\s+from\s+english|IELTS\s+waiv(?:er|ed))",
    re.IGNORECASE,
)
CONDITIONAL_PAT = re.compile(
    r"conditional(?:ly)?\s+(?:offer|admission|accept(?:ance)?|enrolment)",
    re.IGNORECASE,
)
BANK_BAL_PAT = re.compile(
    r"(?:bank\s+balance|proof\s+of\s+funds|financial\s+(?:guarantee|proof|statement)|"
    r"bank\s+statement|show\s+funds|minimum\s+fund)",
    re.IGNORECASE,
)
INTAKE_PAT = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.IGNORECASE,
)
MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
PROGRAM_TYPE_MAP = {
    "foundation": "foundation_eap",
    "pathway": "foundation_eap",
    "bachelor": "bachelor",
    "undergraduate": "bachelor",
    "bsc": "bachelor",
    "ba ": "bachelor",
    "beng": "bachelor",
    "master": "master",
    "msc": "master",
    "mba": "master",
    "ma ": "master",
    "meng": "master",
    "postgraduate": "master",
    "doctoral": "master",
    "phd": "master",
}


def fetch(url: str, timeout: int = 5) -> str | None:
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


def domain_reachable(domain: str) -> bool:
    """Quick TCP connect check before spending time on full HTTP."""
    import socket
    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo(domain, 443)
        return True
    except Exception:
        return False


def robots_allows(domain: str) -> bool:
    """Return False if robots.txt disallows all scraping."""
    url = f"https://{domain}/robots.txt"
    rb = fetch(url, timeout=3)
    if rb and "disallow: /" in rb.lower():
        # Check for a blanket Disallow: /
        for line in rb.lower().splitlines():
            if line.startswith("disallow: /") and line.strip() == "disallow: /":
                return False
    return True


def infer_program_type(name: str) -> str:
    nl = name.lower()
    for kw, ptype in PROGRAM_TYPE_MAP.items():
        if kw in nl:
            return ptype
    return "bachelor"  # default assumption


def parse_gpa(text: str) -> tuple[float | None, float | None, bool]:
    """Return (min_gpa_raw, min_gpa_scale, gpa_scale_unknown)."""
    m = GPA_PAT.search(text)
    if m:
        raw = float(m.group(1))
        scale = float(m.group(2)) if m.group(2) else None
        if scale is None:
            if raw <= 4.0:
                scale = 4.0
            elif raw <= 5.0:
                scale = 5.0
            elif raw <= 7.0:
                scale = 7.0
            elif raw <= 10.0:
                scale = 10.0
            else:
                scale = None
        unknown = scale is None
        return raw, scale, unknown

    # Percentage GPA
    m2 = PERCENT_GPA_PAT.search(text)
    if m2:
        raw = float(m2.group(1))
        return raw, 100.0, False

    return None, None, False


def parse_tuition(text: str) -> tuple[float | None, str | None]:
    m = TUITION_PAT.search(text)
    if not m:
        return None, None
    raw_num = re.sub(r"[^\d.]", "", m.group(1))
    try:
        amount = float(raw_num)
    except ValueError:
        return None, None
    currency = m.group(2) if m.group(2) else _infer_currency_from_text(text)
    return amount, currency


def _infer_currency_from_text(text: str) -> str | None:
    if "£" in text:
        return "GBP"
    if "€" in text:
        return "EUR"
    if "$" in text:
        return "USD"  # crude; may be AUD/CAD
    if "¥" in text:
        return "JPY"
    if "₩" in text:
        return "KRW"
    return None


def scrape_program_page(url: str, university_id: str, country_code: str) -> list[dict]:
    """Scrape a single page and extract program information."""
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ")

    # Check for bank balance / financial references → log separately
    has_bank = bool(BANK_BAL_PAT.search(text))

    # Extract scalar requirements
    ielts_m = IELTS_PAT.search(text)
    ielts_min = float(ielts_m.group(1)) if ielts_m else None

    toefl_m = TOEFL_PAT.search(text)
    toefl_min = float(toefl_m.group(1)) if toefl_m else None

    topik_m = TOPIK_PAT.search(text) if country_code == "KR" else None
    topik_min = int(topik_m.group(1)) if topik_m else None

    min_gpa, gpa_scale, gpa_unknown = parse_gpa(text)
    tuition, currency = parse_tuition(text)
    no_ielts = bool(WAIVER_PAT.search(text))
    conditional = bool(CONDITIONAL_PAT.search(text))

    # Intake months
    intakes = []
    for m in INTAKE_PAT.finditer(text):
        mo = MONTH_MAP.get(m.group(1).lower())
        if mo and mo not in intakes:
            intakes.append(mo)
    intakes.sort()

    # Data confidence
    page_lower = url.lower()
    if "international" in page_lower and ("admission" in page_lower or "apply" in page_lower):
        confidence = "high"
    elif "admission" in page_lower or "apply" in page_lower or "entry" in page_lower:
        confidence = "medium"
    else:
        confidence = "low"

    # Try to find program names from headings
    programs_found = []
    headings = soup.find_all(["h1", "h2", "h3"])
    program_names = []
    for h in headings:
        ht = h.get_text(strip=True)
        if len(ht) > 8 and len(ht) < 100:
            for kw in PROGRAM_TYPE_MAP:
                if kw in ht.lower():
                    program_names.append(ht)
                    break

    if not program_names:
        # Fallback: create one generic entry for this page
        program_names = ["International Programs"]

    ts = datetime.now(timezone.utc).isoformat()
    for pname in program_names[:10]:  # cap at 10 per page
        programs_found.append({
            "university_id": university_id,
            "program_name": pname,
            "program_type": infer_program_type(pname),
            "field_of_study": _infer_field(pname),
            "min_gpa_raw": min_gpa,
            "min_gpa_scale": gpa_scale,
            "gpa_scale_unknown": gpa_unknown,
            "ielts_min": ielts_min,
            "ielts_min_null_reason": "not stated" if ielts_min is None else None,
            "toefl_min": toefl_min,
            "no_ielts": no_ielts,
            "conditional_admission": conditional,
            "topik_min": topik_min,
            "work_exp_months_required": None,
            "tuition_annual_local": tuition,
            "tuition_currency": currency,
            "intake_months": intakes,
            "application_deadline": None,
            "source_url": url,
            "data_confidence": confidence,
            "human_verified": False,
            "scraped_at": ts,
            "_has_bank_balance_ref": has_bank,
        })

    return programs_found


INTL_PAGE_PATHS = [
    "/international-students",
    "/admissions/international",
    "/international/admissions",
    "/apply",
    "/admissions",
]

FIELD_KEYWORDS = {
    "Computer Science": ["computer science", "computing", "software", "information technology", "it"],
    "Engineering": ["engineering", "mechanical", "electrical", "civil", "chemical"],
    "Business": ["business", "management", "commerce", "mba", "administration"],
    "Medicine": ["medicine", "medical", "mbbs", "health science", "nursing", "pharmacy"],
    "Law": ["law", "legal"],
    "Economics": ["economics", "econom"],
    "Arts & Humanities": ["arts", "humanities", "history", "philosophy", "literature"],
    "Social Sciences": ["social science", "sociology", "political", "psychology"],
    "Mathematics": ["mathematics", "math", "statistics"],
    "Physics": ["physics"],
    "Chemistry": ["chemistry"],
    "Biology": ["biology", "biological", "life science"],
    "Architecture": ["architecture", "urban planning"],
    "Education": ["education", "teaching"],
}


def _infer_field(program_name: str) -> str | None:
    pnl = program_name.lower()
    for field, keywords in FIELD_KEYWORDS.items():
        for kw in keywords:
            if kw in pnl:
                return field
    return None


def scrape_university(uni: dict, fin_refs: list) -> list[dict]:
    """Scrape all relevant pages for a single university."""
    domain = uni.get("domain")
    if not domain:
        return []

    # Fast DNS pre-check — skip immediately if domain unresolvable/unreachable
    if not domain_reachable(domain):
        print(f"    Domain unreachable (DNS/TCP): {domain}")
        return []

    base_url = f"https://{domain}"

    # Check robots.txt
    if not robots_allows(domain):
        print(f"    robots.txt blocks scraping for {domain}")
        return []

    programs = []
    tried_urls = set()
    consecutive_empty = 0

    for path in INTL_PAGE_PATHS:
        url = base_url + path
        if url in tried_urls:
            continue
        tried_urls.add(url)

        page_programs = scrape_program_page(url, uni["university_id"], uni.get("country_code", "XX"))

        if not page_programs:
            consecutive_empty += 1
            if consecutive_empty >= 2:
                # Two consecutive empty fetches: domain not serving scrapable content
                break
        else:
            consecutive_empty = 0

        # Separate out financial refs
        for prog in page_programs:
            if prog.pop("_has_bank_balance_ref", False):
                fin_refs.append({
                    "university_id": uni["university_id"],
                    "url": url,
                    "note": "Bank balance / proof-of-funds mention detected",
                })

        programs.extend(page_programs)
        time.sleep(DELAY)

        if programs:
            high_conf = [p for p in programs if p["data_confidence"] == "high"]
            if high_conf:
                break

    return programs


def run() -> None:
    print("=== Phase 3: Admission Requirements Scraping ===\n")

    unis = json.loads(UNIS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(unis)} universities")

    # Process in order of agency_mention_count descending (already sorted)
    target = unis[:MAX_UNIVERSITIES]
    print(f"Processing top {len(target)} universities by agency mention count\n")

    all_programs: list[dict] = []
    fin_refs: list[dict] = []
    no_requirements: list[str] = []
    blocked: list[str] = []

    for i, uni in enumerate(target):
        name = uni["canonical_name"]
        domain = uni.get("domain")
        print(f"[{i+1}/{len(target)}] {name} ({domain or 'no domain'})")

        if not domain:
            print("  Skipped — no domain")
            no_requirements.append(uni["university_id"])
            continue

        programs = scrape_university(uni, fin_refs)

        if programs:
            print(f"  Found {len(programs)} program entries")
            all_programs.extend(programs)
        else:
            print(f"  No requirements scraped")
            no_requirements.append(uni["university_id"])

    # Write programs output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_programs, f, indent=2, ensure_ascii=False)

    # Write financial refs
    with open(FIN_REFS_FILE, "w", encoding="utf-8") as f:
        json.dump(fin_refs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(all_programs)} program entries")
    print(f"✅ Financial refs for human review: {len(fin_refs)}")
    print(f"   No requirements: {len(no_requirements)}")
    print(f"   Blocked by robots.txt: {len(blocked)}")

    # Confidence breakdown
    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    for p in all_programs:
        confidence_counts[p["data_confidence"]] = confidence_counts.get(p["data_confidence"], 0) + 1
    print(f"\nConfidence: high={confidence_counts['high']}, "
          f"medium={confidence_counts['medium']}, low={confidence_counts['low']}")

    # Persist metadata for Phase 4
    meta = {
        "no_requirements": no_requirements,
        "blocked": blocked,
        "total_programs": len(all_programs),
        "confidence": confidence_counts,
    }
    (DATA_DIR / "phase3_meta.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    run()
