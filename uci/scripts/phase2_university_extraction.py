#!/usr/bin/env python3
"""Phase 2 — University extraction, deduplication, and Hipo cross-reference."""

import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).parent.parent / "data"
REFS_DIR = Path(__file__).parent.parent / "docs" / "references"
HIPO_FILE = REFS_DIR / "hipo_universities.json"
AGENCIES_FILE = DATA_DIR / "agencies_raw.json"
OUTPUT_FILE = DATA_DIR / "universities_deduplicated.json"

DELAY = 2
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept-Language": "en-US,en;q=0.9",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# --- University name patterns for extraction from text ---
KNOWN_KEYWORDS = [
    "university", "université", "universität", "universiteit",
    "institute of technology", "college of", "polytechnic",
    "school of", "academy of", "faculty of",
]

# Regex: consecutive title-cased words followed by University/College/Institute keyword
UNI_PATTERN = re.compile(
    r"\b([A-Z][a-z]+(?:\s+(?:of|the|and|&|de|der|van|for|in|at|'s)?\s*[A-Z][a-z]+){0,5}"
    r"\s*(?:University|Université|Universität|Universiteit|College|Institute(?:\s+of\s+Technology)?|"
    r"Polytechnic|Academy|School(?:\s+of\s+\w+)?|Hochschule|Fachhochschule|Universidad|Università))\b"
)


def normalize(name: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^\w\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def slugify(name: str) -> str:
    s = normalize(name)
    s = re.sub(r"\s+", "-", s)
    return s[:80]


def fetch(url: str, timeout: int = 15) -> str | None:
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


def extract_uni_names(text: str) -> list[str]:
    """Extract university names from arbitrary text."""
    names = UNI_PATTERN.findall(text)
    # Also find names ending with common suffixes after "of"
    seen = set()
    result = []
    for n in names:
        n = n.strip()
        if len(n) < 8 or len(n) > 120:
            continue
        key = normalize(n)
        if key not in seen:
            seen.add(key)
            result.append(n)
    return result


def scrape_agency_website(agency: dict) -> list[str]:
    """Scrape agency website for university mentions."""
    website = agency.get("website")
    if not website:
        return []

    unis = []
    # Check robots.txt first
    try:
        rb_url = website.rstrip("/") + "/robots.txt"
        rb = fetch(rb_url, timeout=8)
        if rb and "disallow: /" in rb.lower():
            print(f"    robots.txt disallows scraping {website}")
            return []
    except Exception:
        pass

    # Try common university-listing paths
    paths_to_try = [
        "",
        "/universities",
        "/partner-universities",
        "/our-universities",
        "/programs",
        "/courses",
        "/study-destinations",
    ]

    seen_unis = set()
    for path in paths_to_try:
        url = website.rstrip("/") + path
        html = fetch(url)
        if html:
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(separator=" ")
            found = extract_uni_names(text)
            for u in found:
                key = normalize(u)
                if key not in seen_unis:
                    seen_unis.add(key)
                    unis.append(u)
        time.sleep(DELAY)

    return unis


# ---------------------------------------------------------------------------
# Load Hipo university dataset for cross-referencing
# ---------------------------------------------------------------------------

def load_hipo() -> list[dict]:
    print("Loading Hipo university dataset...")
    data = json.loads(HIPO_FILE.read_text(encoding="utf-8"))
    print(f"  Loaded {len(data)} universities from Hipo dataset")
    return data


def build_hipo_index(hipo: list[dict]) -> dict:
    """Build normalized-name → hipo-entry lookup."""
    idx = {}
    for entry in hipo:
        key = normalize(entry.get("name", ""))
        if key:
            idx[key] = entry
    return idx


def hipo_lookup(name: str, hipo_list: list[dict], hipo_index: dict, threshold: int = 85) -> dict | None:
    """
    Find best matching Hipo entry for a university name.
    Returns None if no match above threshold.
    """
    norm = normalize(name)

    # Exact match first
    if norm in hipo_index:
        return hipo_index[norm]

    # Fuzzy match against all normalized Hipo names
    choices = list(hipo_index.keys())
    result = process.extractOne(norm, choices, scorer=fuzz.token_sort_ratio)
    if result and result[1] >= threshold:
        return hipo_index[result[0]]

    return None


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(raw_mentions: list[tuple[str, str]]) -> list[dict]:
    """
    Deduplicate university names.
    raw_mentions: list of (name, agency_id) tuples
    Returns list of deduplicated university dicts.
    """
    print(f"  Deduplicating {len(raw_mentions)} raw mentions...")

    # Group by normalized name first (exact dedup)
    groups: dict[str, dict] = {}  # canonical_norm → {canonical_name, agency_ids, variants}

    for raw_name, agency_id in raw_mentions:
        norm = normalize(raw_name)
        if norm in groups:
            if agency_id not in groups[norm]["agency_ids"]:
                groups[norm]["agency_ids"].append(agency_id)
            if raw_name not in groups[norm]["variants"]:
                groups[norm]["variants"].append(raw_name)
        else:
            groups[norm] = {
                "canonical_name": raw_name,
                "agency_ids": [agency_id],
                "variants": [raw_name],
            }

    # Fuzzy merge: merge groups whose canonical_norm is >90% similar
    keys = list(groups.keys())
    merged = set()
    final_groups = {}

    for i, key in enumerate(keys):
        if key in merged:
            continue
        # Find similar keys
        candidates = process.extract(key, keys[i + 1:], scorer=fuzz.token_sort_ratio, limit=5)
        for cand_key, score, _ in candidates:
            if score >= 90 and cand_key not in merged:
                # Merge cand_key into key
                merged.add(cand_key)
                for aid in groups[cand_key]["agency_ids"]:
                    if aid not in groups[key]["agency_ids"]:
                        groups[key]["agency_ids"].append(aid)
                for v in groups[cand_key]["variants"]:
                    if v not in groups[key]["variants"]:
                        groups[key]["variants"].append(v)
                # Keep longer name as canonical
                if len(groups[cand_key]["canonical_name"]) > len(groups[key]["canonical_name"]):
                    groups[key]["canonical_name"] = groups[cand_key]["canonical_name"]

        final_groups[key] = groups[key]

    print(f"  After deduplication: {len(final_groups)} unique universities")
    return list(final_groups.values())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run() -> None:
    print("=== Phase 2: University Extraction & Deduplication ===\n")

    agencies = json.loads(AGENCIES_FILE.read_text(encoding="utf-8"))
    hipo = load_hipo()
    hipo_index = build_hipo_index(hipo)

    # Step 1: Collect raw university mentions
    print(f"\n[1/3] Extracting university mentions from {len(agencies)} agencies...")

    raw_mentions: list[tuple[str, str]] = []  # (name, agency_id)
    agencies_with_unis = 0

    for i, agency in enumerate(agencies):
        agency_id = agency["agency_id"]

        # Start with any universities already recorded in agencies_raw.json
        existing = agency.get("partner_universities_mentioned", [])
        for u in existing:
            raw_mentions.append((u, agency_id))

        # Scrape agency website
        if agency.get("website"):
            print(f"  [{i+1}/{len(agencies)}] Scraping {agency['name']}...")
            scraped = scrape_agency_website(agency)
            if scraped:
                agencies_with_unis += 1
                print(f"    Found {len(scraped)} universities")
                for u in scraped:
                    raw_mentions.append((u, agency_id))
            else:
                print(f"    No universities found or site unreachable")

    # Add well-known universities associated with key destination countries
    # as a seed set when live scraping yields little data
    seed_universities = [
        # UK
        ("University of Oxford", "seed"), ("University of Cambridge", "seed"),
        ("Imperial College London", "seed"), ("University College London", "seed"),
        ("London School of Economics", "seed"), ("University of Manchester", "seed"),
        ("University of Edinburgh", "seed"), ("University of Birmingham", "seed"),
        ("University of Bristol", "seed"), ("King's College London", "seed"),
        ("University of Glasgow", "seed"), ("University of Warwick", "seed"),
        ("University of Southampton", "seed"), ("University of Leeds", "seed"),
        ("University of Sheffield", "seed"), ("University of Nottingham", "seed"),
        ("University of Liverpool", "seed"), ("University of Leicester", "seed"),
        ("Coventry University", "seed"), ("De Montfort University", "seed"),
        ("University of Hertfordshire", "seed"), ("Middlesex University London", "seed"),
        ("London Metropolitan University", "seed"), ("University of East London", "seed"),
        ("University of Bedfordshire", "seed"), ("University of Bolton", "seed"),
        ("University of Huddersfield", "seed"), ("University of Salford", "seed"),
        ("University of West London", "seed"), ("Anglia Ruskin University", "seed"),
        # Canada
        ("University of Toronto", "seed"), ("University of British Columbia", "seed"),
        ("McGill University", "seed"), ("University of Alberta", "seed"),
        ("University of Waterloo", "seed"), ("McMaster University", "seed"),
        ("University of Ottawa", "seed"), ("University of Calgary", "seed"),
        ("York University", "seed"), ("Simon Fraser University", "seed"),
        ("Dalhousie University", "seed"), ("University of Manitoba", "seed"),
        ("Carleton University", "seed"), ("Ryerson University", "seed"),
        ("Concordia University", "seed"), ("University of Regina", "seed"),
        ("University of Windsor", "seed"), ("Brock University", "seed"),
        ("Lakehead University", "seed"), ("Nipissing University", "seed"),
        # Australia
        ("University of Melbourne", "seed"), ("University of Sydney", "seed"),
        ("Australian National University", "seed"), ("University of Queensland", "seed"),
        ("Monash University", "seed"), ("University of New South Wales", "seed"),
        ("University of Adelaide", "seed"), ("University of Western Australia", "seed"),
        ("University of Technology Sydney", "seed"), ("RMIT University", "seed"),
        ("Deakin University", "seed"), ("La Trobe University", "seed"),
        ("Griffith University", "seed"), ("James Cook University", "seed"),
        ("Macquarie University", "seed"), ("Curtin University", "seed"),
        ("Flinders University", "seed"), ("Western Sydney University", "seed"),
        ("Charles Darwin University", "seed"), ("University of Tasmania", "seed"),
        # USA
        ("Massachusetts Institute of Technology", "seed"),
        ("Stanford University", "seed"), ("Harvard University", "seed"),
        ("California Institute of Technology", "seed"),
        ("University of Chicago", "seed"), ("Columbia University", "seed"),
        ("Yale University", "seed"), ("Princeton University", "seed"),
        ("Cornell University", "seed"), ("University of Michigan", "seed"),
        ("New York University", "seed"), ("University of California Los Angeles", "seed"),
        ("University of California Berkeley", "seed"),
        ("Georgia Institute of Technology", "seed"),
        ("University of Texas at Austin", "seed"),
        ("University of Illinois Urbana-Champaign", "seed"),
        ("Purdue University", "seed"), ("Pennsylvania State University", "seed"),
        ("Ohio State University", "seed"), ("University of Washington", "seed"),
        # Germany
        ("Technical University of Munich", "seed"),
        ("Ludwig Maximilian University of Munich", "seed"),
        ("Heidelberg University", "seed"),
        ("Humboldt University of Berlin", "seed"),
        ("Free University of Berlin", "seed"),
        ("RWTH Aachen University", "seed"),
        ("University of Hamburg", "seed"),
        ("University of Frankfurt", "seed"),
        ("University of Cologne", "seed"),
        ("University of Stuttgart", "seed"),
        ("Karlsruhe Institute of Technology", "seed"),
        ("Technical University of Berlin", "seed"),
        # Malaysia
        ("University of Malaya", "seed"),
        ("Universiti Putra Malaysia", "seed"),
        ("Universiti Kebangsaan Malaysia", "seed"),
        ("Universiti Teknologi Malaysia", "seed"),
        ("Universiti Sains Malaysia", "seed"),
        ("Taylor's University", "seed"),
        ("Multimedia University", "seed"),
        ("INTI International University", "seed"),
        ("Asia Pacific University", "seed"),
        ("Sunway University", "seed"),
        # South Korea
        ("Seoul National University", "seed"),
        ("Korea Advanced Institute of Science and Technology", "seed"),
        ("Yonsei University", "seed"),
        ("Korea University", "seed"),
        ("Sungkyunkwan University", "seed"),
        ("Hanyang University", "seed"),
        ("Ewha Womans University", "seed"),
        ("Sogang University", "seed"),
        ("Inha University", "seed"),
        ("Kyung Hee University", "seed"),
        ("Ajou University", "seed"),
        ("Konkuk University", "seed"),
        # Japan
        ("University of Tokyo", "seed"),
        ("Kyoto University", "seed"),
        ("Osaka University", "seed"),
        ("Tohoku University", "seed"),
        ("Tokyo Institute of Technology", "seed"),
        ("Nagoya University", "seed"),
        ("Kyushu University", "seed"),
        ("Waseda University", "seed"),
        ("Keio University", "seed"),
        ("Ritsumeikan University", "seed"),
        # Turkey
        ("Middle East Technical University", "seed"),
        ("Bilkent University", "seed"),
        ("Bogazici University", "seed"),
        ("Istanbul Technical University", "seed"),
        ("Hacettepe University", "seed"),
        ("Istanbul University", "seed"),
        ("Ankara University", "seed"),
        # New Zealand
        ("University of Auckland", "seed"),
        ("Victoria University of Wellington", "seed"),
        ("University of Canterbury", "seed"),
        ("University of Otago", "seed"),
        ("Massey University", "seed"),
        ("Auckland University of Technology", "seed"),
        # China
        ("Peking University", "seed"),
        ("Tsinghua University", "seed"),
        ("Fudan University", "seed"),
        ("Zhejiang University", "seed"),
        ("Shanghai Jiao Tong University", "seed"),
        ("Nanjing University", "seed"),
        ("Tongji University", "seed"),
        ("Wuhan University", "seed"),
        ("Harbin Institute of Technology", "seed"),
        ("Xi'an Jiaotong University", "seed"),
        # Ireland
        ("Trinity College Dublin", "seed"),
        ("University College Dublin", "seed"),
        ("University College Cork", "seed"),
        ("National University of Ireland Galway", "seed"),
        ("Dublin City University", "seed"),
        # Sweden / Nordic
        ("Stockholm University", "seed"),
        ("Uppsala University", "seed"),
        ("Lund University", "seed"),
        ("Chalmers University of Technology", "seed"),
        ("KTH Royal Institute of Technology", "seed"),
        ("University of Oslo", "seed"),
        ("University of Bergen", "seed"),
        ("University of Helsinki", "seed"),
        ("Aalto University", "seed"),
        ("Technical University of Denmark", "seed"),
    ]

    print(f"\n  Adding {len(seed_universities)} seed universities from destination countries")
    for name, src in seed_universities:
        raw_mentions.append((name, src))

    print(f"\n  Total raw mentions: {len(raw_mentions)}")

    # Step 2: Deduplicate
    print("\n[2/3] Deduplicating university names...")
    unique_groups = deduplicate(raw_mentions)

    # Step 3: Cross-reference with Hipo dataset
    print("\n[3/3] Cross-referencing with Hipo university dataset...")
    ts = datetime.now(timezone.utc).isoformat()
    universities = []

    for i, group in enumerate(unique_groups):
        canonical = group["canonical_name"]
        agency_ids = [aid for aid in group["agency_ids"] if aid != "seed"]
        all_ids = group["agency_ids"]

        hipo_match = hipo_lookup(canonical, hipo, hipo_index)

        if hipo_match:
            resolved_name = hipo_match.get("name", canonical)
            country = hipo_match.get("country", "Unknown")
            domains = hipo_match.get("domains", [])
            domain = domains[0] if domains else None
            matched = True
        else:
            resolved_name = canonical
            country = _infer_country(canonical, all_ids, agencies)
            domain = None
            matched = False

        country_code = _country_to_code(country)

        universities.append({
            "university_id": slugify(resolved_name),
            "canonical_name": resolved_name,
            "country": country,
            "country_code": country_code,
            "domain": domain,
            "mentioned_by_agencies": agency_ids,
            "agency_mention_count": len(agency_ids),
            "hipo_matched": matched,
            "source_variants": group["variants"],
            "scraped_at": ts,
        })

    # Sort by agency_mention_count descending
    universities.sort(key=lambda u: u["agency_mention_count"], reverse=True)

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(universities, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(universities)} universities to {OUTPUT_FILE}")

    # Summary
    by_country: dict[str, int] = {}
    for u in universities:
        c = u["country"]
        by_country[c] = by_country.get(c, 0) + 1

    print("\nTop 15 countries by university count:")
    for country, count in sorted(by_country.items(), key=lambda x: -x[1])[:15]:
        print(f"  {country}: {count}")

    hipo_matched = sum(1 for u in universities if u["hipo_matched"])
    print(f"\nHipo matched: {hipo_matched}/{len(universities)}")
    print(f"Agencies that yielded universities: {agencies_with_unis}")


def _infer_country(name: str, agency_ids: list, agencies: list) -> str:
    """Guess country from university name or agency destination countries."""
    norm = normalize(name)
    keyword_map = {
        "uk": "United Kingdom", "london": "United Kingdom", "england": "United Kingdom",
        "edinburgh": "United Kingdom", "scotland": "United Kingdom",
        "canada": "Canada", "toronto": "Canada", "ontario": "Canada",
        "australia": "Australia", "sydney": "Australia", "melbourne": "Australia",
        "usa": "United States", "america": "United States",
        "germany": "Germany", "berlin": "Germany", "munich": "Germany",
        "malaysia": "Malaysia", "kuala lumpur": "Malaysia",
        "korea": "South Korea", "seoul": "South Korea",
        "japan": "Japan", "tokyo": "Japan",
        "turkey": "Turkey", "istanbul": "Turkey", "ankara": "Turkey",
        "china": "China", "beijing": "China", "shanghai": "China",
        "ireland": "Ireland", "dublin": "Ireland",
        "sweden": "Sweden", "stockholm": "Sweden",
        "norway": "Norway", "oslo": "Norway",
        "denmark": "Denmark", "copenhagen": "Denmark",
        "finland": "Finland", "helsinki": "Finland",
        "new zealand": "New Zealand", "auckland": "New Zealand",
    }
    for kw, country in keyword_map.items():
        if kw in norm:
            return country

    # Infer from agency destination countries
    agency_countries: dict[str, int] = {}
    agency_map = {a["agency_id"]: a for a in agencies}
    for aid in agency_ids:
        if aid in agency_map:
            for c in agency_map[aid].get("destination_countries", []):
                agency_countries[c] = agency_countries.get(c, 0) + 1

    if agency_countries:
        return max(agency_countries, key=lambda c: agency_countries[c])

    return "Unknown"


_COUNTRY_CODES = {
    "United Kingdom": "GB", "Canada": "CA", "Australia": "AU",
    "United States": "US", "Germany": "DE", "Malaysia": "MY",
    "South Korea": "KR", "Japan": "JP", "Turkey": "TR",
    "China": "CN", "Ireland": "IE", "Sweden": "SE",
    "Norway": "NO", "Denmark": "DK", "Finland": "FI",
    "New Zealand": "NZ", "France": "FR", "Netherlands": "NL",
    "Belgium": "BE", "Austria": "AT", "Switzerland": "CH",
    "Italy": "IT", "Spain": "ES", "Portugal": "PT",
    "India": "IN", "Singapore": "SG", "Bangladesh": "BD",
    "Unknown": "XX",
}


def _country_to_code(country: str) -> str:
    return _COUNTRY_CODES.get(country, "XX")


if __name__ == "__main__":
    run()
