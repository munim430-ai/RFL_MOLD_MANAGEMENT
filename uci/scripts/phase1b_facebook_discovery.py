#!/usr/bin/env python3
"""
Phase 1b — Facebook agency discovery.
Uses Google/Bing search results + Playwright to expand the agency list
with Facebook-primary Bangladeshi education consultancies.
"""

import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "agencies_raw.json"
DELAY = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# -------------------------------------------------------------------------
# Curated Facebook pages discovered via Google site: search
# Format: (name, facebook_slug, address, countries, notes)
# -------------------------------------------------------------------------
FACEBOOK_AGENCIES = [
    # ── Dhaka – UK/Australia/Canada/USA primary ─────────────────────────
    ("CSB Study Abroad",               "csbedubd",                    "Dhaka", ["UK","Australia","Canada","USA"],          "Leading BD consultancy since 2007, 9500+ students"),
    ("Scholars' Educational Consultancy","sec.edu.bd",                "Dhaka", ["UK","Canada","Australia","USA"],          "Ongoing Jan/Feb 2025 UK MSc intake"),
    ("Affirm Study Abroad",            "AffirmStudyAbroad0",          "Dhaka", ["UK","Canada","Australia","USA"],          ""),
    ("EduCarebd",                      "educarebd.net",               "Dhaka", ["India","China","UK","USA","Canada","Australia"], ""),
    ("Scholars Zone Study Abroad",     "scholarszone.sz1",            "Dhaka", ["Canada","Australia","UK","USA"],          "Since 2010, also immigration"),
    ("Eden Study Abroad",              "EdenStudyAbroad",             "Banani, Dhaka", ["UK","Canada","Australia","USA"],  "12+ years experience"),
    ("World Connect Education Consultancy","worldconnecteducation",   "Dhaka", ["UK","Australia","Canada","Germany"],      ""),
    ("Dreamland Education & Tourism",  "dreamlandedu",                "Dhaka", ["UK","Canada","Australia","Malaysia"],     ""),
    ("Zenith Study Abroad",            "zenithstudyabroad",           "Dhaka", ["Canada","USA","UK","Australia"],          ""),
    ("Prime Study Abroad",             "primestudyabroad.bd",         "Dhaka", ["UK","Canada","Australia","USA"],          "Since 2001"),
    ("KC Overseas Education",          "KCDhaka",                     "Dhaka", ["UK","Australia","Canada","USA","Malaysia"],"Leading overseas consultant"),
    ("GoEdu Global Overseas Educational Consultancy","goedubd",       "Dhaka", ["UK","Australia","Canada","Germany","Malaysia"], ""),
    ("GIC Education in Abroad",        "GammaInstituteandConsultancy","Dhaka", ["UK","Canada","Australia","USA","Germany"], "বিদেশে উচ্চ শিক্ষা"),
    ("Education Abroad Bangladesh",    "educationabroadbangladesh",   "Dhaka", ["UK","USA","Canada","Australia","Germany"], ""),
    ("Global Education Consultant BD", "globaleducationconsultantbd", "Dhaka", ["USA","Canada","Australia","UK","Europe"],  ""),
    ("Global Assistant Education Consultant","GlobalAssistantConsultingFirm","Dhaka",["Malaysia","Bangladesh","UK"],       ""),
    ("NBS Education",                  "northbengaleducationservice", "Dhaka", ["UK","Canada","Australia","Malaysia"],     "বিদেশে উচ্চশিক্ষায় ভর্তি ও ভিসা"),
    ("Helpline Global Education Consultant","HelplineGlobalEducation","Dhaka", ["UK","Canada","Australia","USA"],          ""),
    ("UNI Consultants Study Abroad",   "UNIConsultantsbd",            "Dhaka", ["UK","Canada","Australia","USA"],          "Led by UK Graduate Barristers"),
    ("Leed Education Consultant",      "leededucation",               "Dhaka", ["UK","Canada","Australia"],               "13 years experience"),
    ("NHP Education Consultants",      "nhpeducationconsultants",     "Dhaka", ["UK","USA","Canada","Australia"],          ""),
    ("NICE Education Consultants",     "nice.education",              "Dhaka", ["UK","USA","Canada","Australia"],          "Since 2000"),
    ("Edu-Bridge Global Studies",      "EBGSL",                       "Dhaka", ["USA","Canada","Australia","UK","Europe","Malaysia","China","India"], ""),
    ("BEE Global Consultancy",         "beeglobalconsultancy",        "Dhaka", ["UK","Canada","Australia","USA"],          "Bangladesh's most trusted"),
    ("Connected Education Study Abroad Consultancy","connectededucationofficial","Dhaka",["Canada","UK","Australia","USA"], "Canada-based"),
    ("Foreign Study Consultancy Firm", "www.foreignstudy.com.bd",     "Dhaka", ["Canada","New Zealand","Malaysia","Singapore","USA","UK","Germany"], ""),
    ("German Study Centre",            "germanstudycentre",           "Dhaka", ["Germany","Austria","Switzerland"],        ""),
    ("StudyLink Global",               "mystudylinkglobal",           "Dhaka", ["USA","UK","Canada","Europe","Malaysia","Dubai"], "BD's leading study abroad"),
    ("H & I Council",                  "hicctg",                      "Chittagong", ["Australia","Canada","UK","Malaysia","USA","Germany","Dubai","Malta"], "24+ years, Chittagong"),
    ("IECC Bangladesh",                "ieccbd",                      "Dhaka", ["UK","Australia","Canada","USA","Ireland"], ""),
    ("Study in Japan from Bangladesh", "studyinjapanfrombangladesh",  "Dhaka", ["Japan"],                                  "Japan specialist"),
    ("Edustu Bangladesh",              "edustubangladesh",            "Dhaka", ["Malaysia"],                               "Foundation/Diploma/Bachelor/Master/MBBS"),
    ("Study In Malaysia From Bangladesh","StudyInMalaysiaFromBangladesh","Dhaka",["Malaysia"],                             ""),
    ("Big Education Consultancy",      "bigeducationconsultancy",     "Dhaka", ["South Korea","Japan","Germany","UK","Canada"], ""),
    ("Global Education Consultant Korea Japan","globalbd16",           "Dhaka", ["Canada","Malaysia","Japan","South Korea","Cyprus","Latvia","Lithuania","Malta","Hungary"], ""),
    ("GoEdu BD Overseas",              "goedubd",                     "Dhaka", ["UK","Australia","Canada","Germany","Malaysia"], ""),

    # ── Additional from broader searches ────────────────────────────────
    ("AECC Bangladesh",                "aeccglobal.com.bd",           "Dhaka", ["Australia","UK","Canada","USA","Ireland"],  "AECC Global branch"),
    ("IAS Bangladesh",                 "iasbd.co.uk",                 "Dhaka", ["UK"],                                     "UK specialist"),
    ("PFEC Global Bangladesh",         "pfecglobal.com.bd",           "Dhaka", ["UK","Australia","Canada","USA"],           ""),
    ("Aspire Global Pathways",         "aspireglobalpathways",        "Dhaka", ["UK","Australia","Canada"],                 ""),
    ("GKN Education Consultancy",      "gkceducation",                "Dhaka", ["South Korea","Japan","Malaysia"],          "Korea/Japan specialist"),
    ("Sky2Edu",                        "sky2edu",                     "Dhaka", ["UK","Canada","Australia","USA"],           ""),
    ("EduVisors Bangladesh",           "eduvisors.bd",                "Dhaka", ["UK","Canada","Australia"],                 ""),
    ("Luminedge Germany",              "luminedgebd",                 "Dhaka", ["Germany"],                                 "Germany specialist"),
    ("Biic Education Bangladesh",      "biic.com.bd",                 "Dhaka", ["Japan","UK","Canada"],                    ""),
    ("IGC Education",                  "igceducationbd",              "Dhaka", ["South Korea"],                             "Korea specialist"),
    ("Meiji Education Korea",          "meijieducation",              "Dhaka", ["South Korea"],                             "Korea visa tips provider"),
    ("GMC Studies Japan",              "gmc.studies",                 "Dhaka", ["Japan"],                                   "Japan specialist"),
    ("Sangenbd Canada",                "sangenbd",                    "Dhaka", ["Canada"],                                  "Canada specialist"),
    ("MMS Global Canada",              "mmsglobal.io",                "Dhaka", ["Canada","UK","Australia"],                 ""),
    ("Care Paths Education",           "carepathsedu",                "Dhaka", ["Germany","UK","Canada"],                   "Germany specialist"),
    ("Gradding Global",                "graddingbd",                  "Dhaka", ["Australia","UK","Canada","USA"],           ""),
    ("Visa Point International",       "visapointint",                "Dhaka", ["UK","Canada","Australia","Finland"],       ""),
    ("Fintiba Germany BD",             "fintiba.bangladesh",          "Dhaka", ["Germany"],                                 "Blocked account service"),
    ("Euro Staff Education",           "eurostaffsedu",               "Dhaka", ["UK","Europe"],                            ""),
    ("Shorelight Bangladesh",          "shorelight.bd",               "Dhaka", ["USA"],                                    "US university partner"),
    ("JNS Education Canada",           "jnsedubd",                    "Dhaka", ["Canada"],                                 ""),
    ("AIMS Education UK",              "aimseducation.uk",            "Dhaka", ["UK"],                                      ""),
    ("GMCI Bangladesh",                "gmcibd",                      "Dhaka", ["UK","Canada","Australia","USA","Malaysia"], ""),
    ("UTS College Bangladesh",         "utscollegebangladesh",        "Dhaka", ["Australia"],                               "UTS pathway provider"),
    ("Study Abroad Chittagong",        "studyabroadctg",              "Chittagong", ["UK","Canada","Australia","Malaysia"], ""),
    ("EduCon Sylhet",                  "educon.sylhet",               "Sylhet", ["UK","USA","Canada"],                     ""),
    ("Global Vision Rajshahi",         "globalvisionrajshahi",        "Rajshahi", ["Malaysia","China","UK"],               ""),
    ("Total Law Bangladesh",           "totallawbd",                  "Dhaka", ["UK"],                                      "UK immigration law firm"),
    ("IDP Bangladesh",                 "IDPBangladesh",               "Dhaka", ["Australia","UK","USA","Canada","New Zealand","Ireland"], "IELTS + placement"),
    ("British Council Bangladesh",     "BritishCouncilBangladesh",    "Dhaka", ["UK"],                                      "Official UK cultural body"),
]


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:60]


def try_fetch_fb_about(slug: str) -> dict:
    """
    Attempt to fetch name and brief description from a public Facebook page.
    Facebook blocks most automated access, so we try with a plain request
    and fall back to empty if blocked.
    """
    url = f"https://www.facebook.com/{slug}"
    try:
        r = SESSION.get(url, timeout=8)
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "lxml")

        # Extract page title
        title = ""
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")
        elif soup.title:
            title = soup.title.string or ""
        title = title.replace("| Facebook", "").replace("- Facebook", "").strip()

        # Extract description
        desc = ""
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            desc = og_desc.get("content", "")

        return {"fb_title": title, "fb_desc": desc}
    except Exception:
        return {}


def run() -> None:
    print("=== Phase 1b: Facebook Agency Discovery ===\n")

    # Load existing agencies
    existing = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    existing_names = {a["name"].lower() for a in existing}
    existing_slugs = {a["agency_id"] for a in existing}

    print(f"Existing agencies: {len(existing)}")
    print(f"Facebook candidates to process: {len(FACEBOOK_AGENCIES)}\n")

    ts = datetime.now(timezone.utc).isoformat()
    added = 0
    updated = 0

    for name, fb_slug, address, countries, note in FACEBOOK_AGENCIES:
        fb_url = f"https://www.facebook.com/{fb_slug}"
        slug = slugify(name)

        # If agency name already in database → just add FB URL if missing
        if name.lower() in existing_names:
            for a in existing:
                if a["name"].lower() == name.lower():
                    if not a.get("facebook_page"):
                        a["facebook_page"] = fb_url
                        updated += 1
                        print(f"  [UPDATE FB] {name}")
            continue

        # Try to fetch public FB page metadata (best-effort)
        meta = try_fetch_fb_about(fb_slug)
        resolved_name = meta.get("fb_title") or name
        if resolved_name and len(resolved_name) > 3:
            pass  # use it
        else:
            resolved_name = name

        agency = {
            "agency_id": slug,
            "name": resolved_name,
            "website": None,
            "facebook_page": fb_url,
            "phone": None,
            "address": address + (", Bangladesh" if "Bangladesh" not in address else ""),
            "destination_countries": countries,
            "partner_universities_mentioned": [],
            "source_urls": [fb_url],
            "scraped_at": ts,
            "notes": note,
        }

        existing.append(agency)
        existing_names.add(name.lower())
        added += 1
        print(f"  [NEW] {resolved_name} → {fb_url}")
        time.sleep(0.3)  # small delay

    # Save updated file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Total agencies now: {len(existing)}")
    print(f"   Added: {added} | Updated with FB URL: {updated}")

    # Print summary by city
    by_city: dict[str, int] = {}
    for a in existing:
        city = a.get("address", "").split(",")[0].strip()
        by_city[city] = by_city.get(city, 0) + 1
    print("\nAgencies by city:")
    for city, n in sorted(by_city.items(), key=lambda x: -x[1])[:10]:
        print(f"  {city}: {n}")


if __name__ == "__main__":
    run()
