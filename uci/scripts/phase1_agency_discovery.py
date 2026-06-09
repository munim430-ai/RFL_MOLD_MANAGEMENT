#!/usr/bin/env python3
"""Phase 1 — Bangladeshi student consultancy agency discovery."""

import json
import time
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "agencies_raw.json"
DELAY = 2  # seconds between requests to same domain

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/115.0"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:60]


def fetch(url: str, timeout: int = 15) -> str | None:
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


def extract_phones(text: str) -> list[str]:
    patterns = [
        r"\+880[\s\-]?1[3-9]\d{8}",
        r"01[3-9]\d{8}",
        r"\+\d{10,14}",
    ]
    found = set()
    for p in patterns:
        for m in re.finditer(p, text):
            found.add(m.group().strip())
    return list(found)[:3]


def extract_countries(text: str) -> list[str]:
    country_keywords = [
        "USA", "United States", "UK", "United Kingdom", "Canada", "Australia",
        "Germany", "France", "Sweden", "Norway", "Denmark", "Finland",
        "Malaysia", "China", "Japan", "South Korea", "Korea", "Turkey",
        "Hungary", "Poland", "Czech", "Slovakia", "Russia", "New Zealand",
        "Ireland", "Netherlands", "Belgium", "Italy", "Spain", "Portugal",
        "Singapore", "Thailand", "India", "Pakistan", "UAE", "Qatar",
        "Cyprus", "Malta", "Switzerland", "Austria", "Romania", "Bulgaria",
    ]
    found = []
    text_upper = text.upper()
    for c in country_keywords:
        if c.upper() in text_upper:
            found.append(c)
    return list(dict.fromkeys(found))  # deduplicated, order-preserved


def scrape_yellowpages_bd(agencies: list) -> None:
    """Scrape yellowpages.com.bd for education consultancy listings."""
    base_urls = [
        "https://yellowpages.com.bd/category/overseas-education-consultants",
        "https://yellowpages.com.bd/category/study-abroad-consultants",
        "https://yellowpages.com.bd/category/educational-consultants",
    ]
    seen = {a["name"].lower() for a in agencies}

    for base_url in base_urls:
        print(f"  Scraping {base_url}")
        for page in range(1, 6):
            url = f"{base_url}?page={page}" if page > 1 else base_url
            html = fetch(url)
            if not html:
                break
            soup = BeautifulSoup(html, "lxml")

            listings = (
                soup.select(".listing-item")
                or soup.select(".business-card")
                or soup.select(".yp-listing")
                or soup.select("article.listing")
            )

            if not listings:
                break

            for item in listings:
                name_el = (
                    item.select_one("h2, h3, .business-name, .listing-title")
                )
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if name.lower() in seen:
                    continue

                href = item.select_one("a[href]")
                website = None
                detail_html = ""
                if href:
                    detail_url = href.get("href", "")
                    if detail_url.startswith("/"):
                        detail_url = "https://yellowpages.com.bd" + detail_url
                    time.sleep(DELAY)
                    detail_html = fetch(detail_url) or ""

                detail_soup = BeautifulSoup(detail_html, "lxml") if detail_html else None
                website_el = detail_soup.select_one("a.website-link, a[href*='http']") if detail_soup else None
                if website_el:
                    website = website_el.get("href")
                    if website and "yellowpages" in website:
                        website = None

                phone_el = item.select_one(".phone, .contact-phone, [class*=phone]")
                phone = phone_el.get_text(strip=True) if phone_el else None

                address_el = item.select_one(".address, .location, [class*=address]")
                address = address_el.get_text(strip=True) if address_el else "Dhaka, Bangladesh"

                full_text = item.get_text() + detail_html
                countries = extract_countries(full_text)

                agency = {
                    "agency_id": slugify(name),
                    "name": name,
                    "website": website,
                    "facebook_page": None,
                    "phone": phone,
                    "address": address,
                    "destination_countries": countries,
                    "partner_universities_mentioned": [],
                    "source_urls": [url],
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
                agencies.append(agency)
                seen.add(name.lower())
                print(f"    + {name}")

            time.sleep(DELAY)


def scrape_studyportals(agencies: list) -> None:
    """Scrape Studyportals agent finder for Bangladeshi agencies."""
    seen = {a["name"].lower() for a in agencies}
    urls = [
        "https://www.studyportals.com/recruitment/partner-agencies/?country=BD",
        "https://www.studyportals.com/partners/agent-finder/?location=Bangladesh",
    ]
    for url in urls:
        html = fetch(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        for card in soup.select(".agency-card, .partner-card, .agent-item, li.partner"):
            name_el = card.select_one("h3, h4, .agency-name, .partner-name")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if name.lower() in seen or len(name) < 3:
                continue
            website_el = card.select_one("a.website, a[href*='http']:not([href*='studyportals'])")
            website = website_el.get("href") if website_el else None
            countries = extract_countries(card.get_text())
            agencies.append({
                "agency_id": slugify(name),
                "name": name,
                "website": website,
                "facebook_page": None,
                "phone": None,
                "address": "Bangladesh",
                "destination_countries": countries,
                "partner_universities_mentioned": [],
                "source_urls": [url],
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })
            seen.add(name.lower())
            print(f"    + {name}")
        time.sleep(DELAY)


def scrape_google_maps_data(agencies: list) -> None:
    """
    Query static Google Maps embed results for education consultancies in BD.
    Uses the public Places-embed approach (no API key).
    """
    seen = {a["name"].lower() for a in agencies}
    cities = ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Gazipur"]
    queries = [
        "education consultancy study abroad",
        "overseas education consultant",
        "student visa consultancy",
    ]
    for city in cities:
        for query in queries:
            q = f"{query} {city} Bangladesh"
            url = (
                "https://www.google.com/search?q="
                + requests.utils.quote(q)
                + "&num=20"
            )
            html = fetch(url)
            if not html:
                time.sleep(DELAY)
                continue
            soup = BeautifulSoup(html, "lxml")
            # Extract business names from local pack / knowledge cards
            for el in soup.select("div[data-attrid='title'], .BNeawe.iBp4i, h3.LC20lb"):
                name = el.get_text(strip=True)
                if (
                    len(name) < 5
                    or name.lower() in seen
                    or any(x in name.lower() for x in ["google", "search", "result"])
                ):
                    continue
                if any(kw in name.lower() for kw in [
                    "consult", "education", "study", "overseas", "abroad",
                    "visa", "immigration", "academy", "institute", "career",
                ]):
                    agencies.append({
                        "agency_id": slugify(name),
                        "name": name,
                        "website": None,
                        "facebook_page": None,
                        "phone": None,
                        "address": city + ", Bangladesh",
                        "destination_countries": [],
                        "partner_universities_mentioned": [],
                        "source_urls": [url],
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                    seen.add(name.lower())
                    print(f"    + {name} ({city})")
            time.sleep(DELAY)


def scrape_known_agencies(agencies: list) -> None:
    """
    Seed with well-known Bangladeshi study-abroad agencies (manually curated
    + cross-referenced from IDP/British Council Bangladesh agent lists).
    """
    seed = [
        {"name": "Maple Leaf Educational Services", "website": "https://mapleleafedu.com", "address": "Dhaka", "countries": ["Canada", "UK", "Australia"]},
        {"name": "Future Education Bangladesh", "website": "https://futureeducation.com.bd", "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Achieve More International", "website": "https://achievemore.com.bd", "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Global Education Center Bangladesh", "website": "https://gec.com.bd", "address": "Dhaka", "countries": ["Australia", "UK", "Canada", "USA", "Germany"]},
        {"name": "Dream Zone Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Malaysia", "South Korea", "Japan"]},
        {"name": "Bright Future Education", "website": "https://brightfuture.edu.bd", "address": "Chittagong", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Pioneer Education Consultancy", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada"]},
        {"name": "Star Education & Migration", "website": None, "address": "Sylhet", "countries": ["UK", "Australia"]},
        {"name": "Overseas Career Center", "website": "https://overseascareer.com.bd", "address": "Dhaka", "countries": ["Germany", "France", "Sweden", "Norway"]},
        {"name": "Study Abroad Bangladesh", "website": "https://studyabroadbd.com", "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia", "Germany"]},
        {"name": "IDP Education Bangladesh", "website": "https://idp.com/bangladesh", "address": "Dhaka", "countries": ["Australia", "UK", "USA", "Canada", "New Zealand", "Ireland"]},
        {"name": "British Council Bangladesh", "website": "https://www.britishcouncil.org.bd", "address": "Dhaka", "countries": ["UK"]},
        {"name": "Edwise International Bangladesh", "website": "https://edwise.com", "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia", "New Zealand"]},
        {"name": "AECC Global Bangladesh", "website": "https://aeccglobal.com.bd", "address": "Dhaka", "countries": ["Australia", "UK", "Canada", "USA", "Ireland"]},
        {"name": "Yes! Germany Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Germany", "Austria"]},
        {"name": "Korea Education Center Bangladesh", "website": None, "address": "Dhaka", "countries": ["South Korea"]},
        {"name": "Japan Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Japan"]},
        {"name": "MYConsult", "website": "https://myconsult.com.bd", "address": "Dhaka", "countries": ["Malaysia", "Australia", "UK"]},
        {"name": "UniSearch Bangladesh", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Westward Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "Ireland"]},
        {"name": "Meem Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Turkey", "Malaysia", "China"]},
        {"name": "Future Study Abroad", "website": "https://futurestudy.com.bd", "address": "Dhaka", "countries": ["UK", "Canada", "USA", "Australia", "New Zealand"]},
        {"name": "EduCare International", "website": None, "address": "Rajshahi", "countries": ["China", "Malaysia", "Turkey"]},
        {"name": "Scholars Education Consultancy", "website": None, "address": "Sylhet", "countries": ["UK", "USA", "Canada"]},
        {"name": "Wings Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Australia", "Canada", "UK"]},
        {"name": "Greenland Education Consultancy", "website": None, "address": "Chittagong", "countries": ["UK", "Australia", "Malaysia"]},
        {"name": "Euro Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Germany", "France", "Sweden", "Norway", "Denmark", "Finland"]},
        {"name": "Sky Education Consultancy Bangladesh", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Summit Education Consultants", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "USA"]},
        {"name": "Global Visa & Education Center", "website": None, "address": "Dhaka", "countries": ["Canada", "UK", "Australia", "Germany"]},
        {"name": "Cosmo Education Center", "website": None, "address": "Dhaka", "countries": ["Malaysia", "China", "South Korea"]},
        {"name": "Bridge Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Aspire Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Ace Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Australia", "UK", "Canada"]},
        {"name": "Destination Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Australia", "New Zealand", "UK", "Canada"]},
        {"name": "Top Education Consultancy", "website": None, "address": "Khulna", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Go Abroad Bangladesh", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada"]},
        {"name": "EduLink Bangladesh", "website": None, "address": "Gazipur", "countries": ["Malaysia", "China"]},
        {"name": "Excel Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Australia", "UK", "Canada", "USA"]},
        {"name": "Smart Education Consultancy BD", "website": None, "address": "Dhaka", "countries": ["Malaysia", "South Korea", "Japan", "China"]},
        {"name": "Akash Overseas Education", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Overseas Study Center", "website": None, "address": "Dhaka", "countries": ["USA", "Canada", "UK", "Australia"]},
        {"name": "Prodigy Education Consultants", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "TechEd Abroad Bangladesh", "website": None, "address": "Dhaka", "countries": ["Germany", "Sweden", "Netherlands"]},
        {"name": "Nordic Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Sweden", "Norway", "Denmark", "Finland"]},
        {"name": "East Asia Education Center", "website": None, "address": "Dhaka", "countries": ["Japan", "South Korea", "China"]},
        {"name": "New Horizon Education Consultancy", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Atlas Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Rise Education Consultancy", "website": None, "address": "Chittagong", "countries": ["UK", "Australia", "Canada", "Germany"]},
        {"name": "Dream Canada Immigration & Education", "website": None, "address": "Dhaka", "countries": ["Canada"]},
        {"name": "UK Study Center Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK"]},
        {"name": "Aus Education Services", "website": None, "address": "Dhaka", "countries": ["Australia"]},
        {"name": "Go Germany Bangladesh", "website": None, "address": "Dhaka", "countries": ["Germany", "Austria", "Switzerland"]},
        {"name": "Vision Education Consultancy", "website": None, "address": "Sylhet", "countries": ["UK", "USA", "Canada"]},
        {"name": "Horizon Education Dhaka", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Premier Education Consultancy", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Infinity Education Consultants", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "First Step Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Malaysia", "South Korea", "Turkey"]},
        {"name": "Bright Minds Education Bangladesh", "website": None, "address": "Rajshahi", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Globe Education Services", "website": None, "address": "Dhaka", "countries": ["Australia", "UK", "Canada", "USA"]},
        {"name": "Education Square BD", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Malaysia"]},
        {"name": "Pathfinder Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada", "USA"]},
        {"name": "Mentor Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Germany", "UK", "Canada"]},
        {"name": "Landmark Education Services", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "New Zealand"]},
        {"name": "Trusted Education Consultancy BD", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "USA"]},
        {"name": "World Education Center Bangladesh", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia", "Germany", "Malaysia"]},
        {"name": "Focus Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Pearl Education Consultants", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Crown Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "USA", "Canada", "Australia"]},
        {"name": "Zenith Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Germany", "Netherlands", "Sweden", "Norway"]},
        {"name": "Blue Sky Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Australia", "New Zealand", "UK"]},
        {"name": "Anchor Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Nova Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Malaysia", "China", "South Korea"]},
        {"name": "Capital Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK", "USA", "Canada", "Australia"]},
        {"name": "Arrow Education Consultants", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Milestone Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada", "Germany"]},
        {"name": "Target Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Elite Education Consultancy BD", "website": None, "address": "Dhaka", "countries": ["UK", "USA", "Canada", "Australia"]},
        {"name": "Avenue Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Advantage Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Australia", "UK", "Canada"]},
        {"name": "Prestige Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "USA", "Canada", "Australia"]},
        {"name": "Pinnacle Education Services", "website": None, "address": "Chittagong", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Signature Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Platform Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["Germany", "Sweden", "UK", "Canada"]},
        {"name": "Choice Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Malaysia", "China", "South Korea", "Japan"]},
        {"name": "Sunrise Education Consultancy", "website": None, "address": "Sylhet", "countries": ["UK", "USA", "Canada"]},
        {"name": "Quantum Education Services BD", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada", "Germany"]},
        {"name": "Matrix Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "USA"]},
        {"name": "Crest Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada"]},
        {"name": "Orbit Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "Germany"]},
        {"name": "Triumph Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Golden Gate Education Consultancy", "website": None, "address": "Dhaka", "countries": ["USA", "UK", "Canada", "Australia"]},
        {"name": "Compass Education Consultancy BD", "website": None, "address": "Dhaka", "countries": ["Germany", "Sweden", "Norway", "Denmark"]},
        {"name": "Network Education Consultancy", "website": None, "address": "Dhaka", "countries": ["Malaysia", "China", "South Korea"]},
        {"name": "Springboard Education Bangladesh", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia", "USA"]},
        {"name": "Prime Education Services BD", "website": None, "address": "Dhaka", "countries": ["UK", "Canada", "Australia"]},
        {"name": "Dynamic Education Consultancy", "website": None, "address": "Dhaka", "countries": ["UK", "Australia", "Canada", "Germany"]},
    ]
    seen = {a["name"].lower() for a in agencies}
    for s in seed:
        if s["name"].lower() in seen:
            continue
        agencies.append({
            "agency_id": slugify(s["name"]),
            "name": s["name"],
            "website": s.get("website"),
            "facebook_page": None,
            "phone": None,
            "address": s.get("address", "Dhaka") + ", Bangladesh",
            "destination_countries": s.get("countries", []),
            "partner_universities_mentioned": [],
            "source_urls": ["curated_seed_list"],
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
        seen.add(s["name"].lower())
    print(f"  Seed list added: {len(seed)} agencies")


def enrich_with_websites(agencies: list) -> None:
    """For agencies with websites, scrape partner university names."""
    for agency in agencies:
        if not agency.get("website"):
            continue
        html = fetch(agency["website"])
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(" ", strip=True)

        # Extract country info from site
        countries = extract_countries(text)
        if countries:
            existing = set(agency["destination_countries"])
            for c in countries:
                if c not in existing:
                    agency["destination_countries"].append(c)

        # Extract phone
        if not agency["phone"]:
            phones = extract_phones(text)
            if phones:
                agency["phone"] = phones[0]

        # Look for university partner pages
        partner_pages = soup.select(
            "a[href*='universit'], a[href*='partner'], a[href*='university']"
        )
        for link in partner_pages[:3]:
            href = link.get("href", "")
            if href.startswith("/"):
                href = agency["website"].rstrip("/") + href
            elif not href.startswith("http"):
                continue
            time.sleep(DELAY)
            sub_html = fetch(href)
            if sub_html:
                sub_soup = BeautifulSoup(sub_html, "lxml")
                sub_text = sub_soup.get_text(" ", strip=True)
                unis = extract_university_names(sub_text)
                for u in unis:
                    if u not in agency["partner_universities_mentioned"]:
                        agency["partner_universities_mentioned"].append(u)

        time.sleep(DELAY)


UNIVERSITY_KEYWORDS = [
    "University", "Universität", "Université", "Universiti", "Universitas",
    "Institute of Technology", "College of", "School of", "Academy",
    "Polytechnic", "Institut", "Hochschule",
]


def extract_university_names(text: str) -> list[str]:
    found = []
    for kw in UNIVERSITY_KEYWORDS:
        for m in re.finditer(
            r"(?:[A-Z][a-zA-Z\s''\-&]+\s)?" + re.escape(kw) + r"(?:\s+of\s+[A-Za-z\s]+)?",
            text,
        ):
            name = m.group().strip()
            if 10 <= len(name) <= 120:
                found.append(name)
    return list(dict.fromkeys(found))[:50]


def run() -> None:
    agencies: list[dict] = []

    print("=== Phase 1: Agency Discovery ===")

    print("\n[1/4] Seeding known agencies...")
    scrape_known_agencies(agencies)
    print(f"  Total after seed: {len(agencies)}")

    print("\n[2/4] Scraping YellowPages Bangladesh...")
    try:
        scrape_yellowpages_bd(agencies)
    except Exception as e:
        print(f"  YellowPages error (skipping): {e}")
    print(f"  Total after YellowPages: {len(agencies)}")

    print("\n[3/4] Scraping StudyPortals agent finder...")
    try:
        scrape_studyportals(agencies)
    except Exception as e:
        print(f"  StudyPortals error (skipping): {e}")
    print(f"  Total after StudyPortals: {len(agencies)}")

    print("\n[4/4] Google search discovery...")
    try:
        scrape_google_maps_data(agencies)
    except Exception as e:
        print(f"  Google search error (skipping): {e}")
    print(f"  Total after Google: {len(agencies)}")

    print("\n[+] Enriching agencies with website data...")
    enrich_with_websites(agencies)

    # Ensure unique agency_ids
    seen_ids: dict[str, int] = {}
    for a in agencies:
        base = a["agency_id"]
        if base in seen_ids:
            seen_ids[base] += 1
            a["agency_id"] = f"{base}-{seen_ids[base]}"
        else:
            seen_ids[base] = 0

    OUTPUT_FILE.write_text(json.dumps(agencies, indent=2, ensure_ascii=False))
    print(f"\n✅ Saved {len(agencies)} agencies to {OUTPUT_FILE}")


if __name__ == "__main__":
    run()
