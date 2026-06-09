# Tool Inventory — UCI OSINT Data Collection Pipeline
**Written:** 2026-06-09  
**Phase:** 0 — Pre-flight survey

---

## Available Tools

### Web Enumeration & Link Extraction
| Tool | Location | Status | Use in Pipeline |
|------|----------|--------|----------------|
| **requests + BeautifulSoup4** | pip (system) | ✅ Ready | Primary scraper for static HTML pages |
| **lxml** | pip (system) | ✅ Ready | Fast HTML/XML parser (fallback to bs4) |
| **Playwright** | `/opt/node22/bin/playwright` | ✅ Installed | Headless JS rendering for React/Vue agency sites |
| **Scrapy** | pip | ✅ Installed | Spider framework for multi-page crawls |
| **theHarvester** | stub pip package | ⚠️ Stub only | Not used |
| **Recon-ng** | Not available | ❌ | Not used |
| **SpiderFoot** | `/opt/spiderfoot` (partial) | ⚠️ Deps failed | Not used |

### Data Processing
| Tool | Status | Use |
|------|--------|-----|
| **fuzzywuzzy + python-Levenshtein** | ✅ Ready | University name deduplication (Phase 2) |
| **rapidfuzz** | ✅ Ready (installed as fuzzywuzzy backend) | Faster fuzzy matching |
| **json / csv** | ✅ stdlib | Output serialization |
| **uuid** | ✅ stdlib | ID generation |

### Reference Data
| Dataset | Location | Records | Use |
|---------|----------|---------|-----|
| **Hipo university-domains-list** | `docs/references/hipo_universities.json` | 10,249 universities, 201 countries | Phase 2 canonical name + domain resolution |
| **vigneshk Admission-Dataset** | `docs/references/Admission.csv` | GRE/TOEFL/GPA structured data | Phase 3 validation cross-reference |

---

## Tool Selection Per Phase

| Phase | Primary Tool | Fallback | Reason |
|-------|-------------|---------|--------|
| **Phase 1** — Agency discovery | `requests + bs4` | Playwright | Most BD agency sites are simple HTML; Playwright for JS-rendered sites |
| **Phase 2** — University extraction | `requests + bs4 + fuzzywuzzy` | Playwright | Static pages sufficient; fuzzywuzzy for name dedup |
| **Phase 3** — Admission requirements | `requests + bs4` + Playwright | Scrapy spider | University sites vary; JS rendering needed for ~30% |
| **Phase 4** — Schema export | Python `json` + `uuid` | — | Pure data transformation |

---

## Rate Limiting Strategy
- Minimum **2-second delay** between requests to the same domain
- `requests.Session` with `User-Agent: Mozilla/5.0` to avoid basic blocks
- On 429/503: exponential backoff up to 30s, then skip and log

## robots.txt Compliance
All scrapers check `robots.txt` before crawling university domains.  
Agencies blocked from scraping → logged in `COLLECTION_REPORT.md`.
