# UCI OSINT Data Collection Report
**Generated:** 2026-06-09 10:32 UTC  

---

## Summary Counts

| Metric | Value |
|--------|-------|
| **Agencies discovered** | 102 |
| **Unique universities** | 187 |
| **Programs scraped** | 77 |
| **Financial refs for review** | 1 |

---

## Programs by Confidence Level

| Confidence | Count |
|-----------|-------|
| High | 40 |
| Medium | 0 |
| Low | 37 |

---

## Universities by Country

| Country | Universities |
|---------|-------------|
| Australia | 27 |
| United Kingdom | 27 |
| United States | 24 |
| Canada | 19 |
| Japan | 14 |
| Korea, Republic of | 13 |
| China | 10 |
| Malaysia | 7 |
| Turkiye | 7 |
| Unknown | 6 |
| New Zealand | 6 |
| Ireland | 5 |
| Sweden | 5 |
| Germany | 3 |
| Italy | 2 |
| Norway | 2 |
| Finland | 2 |
| USA | 1 |
| India | 1 |
| Nigeria | 1 |
| Ghana | 1 |
| Luxembourg | 1 |
| Poland | 1 |
| Malta | 1 |
| Denmark | 1 |

---

## Top 20 Universities by Agency Mention Count

| Rank | University | Country | Agency Mentions | Hipo Matched |
|------|-----------|---------|----------------|-------------|
| 1 | KC University | Korea, Republic of | 3 | ✅ |
| 2 | Future Education Skip to content Future Education Home About Japan Student Visa Japanese Language School University | Japan | 1 | ❌ |
| 3 | Services Japan Tourist Visa Japan Business Visa Our Story Contact University | Japan | 1 | ❌ |
| 4 | Why Study at a Japanese University | Japan | 1 | ❌ |
| 5 | How to Apply Choose a University | USA | 1 | ❌ |
| 6 | Popularity Popularity THE World University Rankings University | Australia | 1 | ❌ |
| 7 | University of Cambridge | United Kingdom | 1 | ✅ |
| 8 | View details California State University | Australia | 1 | ❌ |
| 9 | English Courses available View details James Madison University | Australia | 1 | ❌ |
| 10 | English Courses available View details Bentley University | Australia | 1 | ❌ |
| 11 | English Courses available View details Vanderbilt University | Australia | 1 | ❌ |
| 12 | English Courses available View details University of Essex International College | Australia | 1 | ❌ |
| 13 | English Courses available View details Rhode Island School of | Australia | 1 | ❌ |
| 14 | World University Rankings Complete University | Australia | 1 | ❌ |
| 15 | Discover AECC Partner Institut | Australia | 1 | ❌ |
| 16 | Find out where you can study in Australia Click Here to Explore Universiti | Australia | 1 | ❌ |
| 17 | Green Card Conversion Find out where you can study in Ireland Click Here to Explore Universiti | Ireland | 1 | ❌ |
| 18 | University of Oxford | United Kingdom | 0 | ✅ |
| 19 | Imperial College London | United Kingdom | 0 | ✅ |
| 20 | Linton University College | Malaysia | 0 | ✅ |

---

## Universities Without Scraped Admission Requirements
(143 universities — manual follow-up required)

- KC University
- Future Education Skip to content Future Education Home About Japan Student Visa Japanese Language School University
- Services Japan Tourist Visa Japan Business Visa Our Story Contact University
- Why Study at a Japanese University
- How to Apply Choose a University
- Popularity Popularity THE World University Rankings University
- View details California State University
- English Courses available View details James Madison University
- English Courses available View details Bentley University
- English Courses available View details Vanderbilt University
- English Courses available View details University of Essex International College
- English Courses available View details Rhode Island School of
- World University Rankings Complete University
- Discover AECC Partner Institut
- Find out where you can study in Australia Click Here to Explore Universiti
- Green Card Conversion Find out where you can study in Ireland Click Here to Explore Universiti
- University of Oxford
- Imperial College London
- Linton University College
- London School of Economics
- University of Manchester
- University of Edinburgh
- University of Birmingham
- King's College London
- University of Warwick
- University of Southampton
- The University of Sheffield
- University of Nottingham
- University of Liverpool
- University of Leicester
- Coventry University
- De Montfort University
- University of Hertfordshire
- Middlesex University - London
- University of East London
- University of Huddersfield
- University of Salford
- University of London
- University of Toronto
- University of British Columbia
- McGill University
- University of Alberta
- McMaster University
- University of Ottawa
- York University
- Simon Fraser University
- Dalhousie University
- University of Manitoba
- University of Regina
- University of Windsor
- *(and 93 more — see phase3_meta.json)*

---

## Notes
- Scraping performed on publicly accessible pages only
- robots.txt respected for all university domains
- No personal data stored (testimonials/names skipped)
- Bank balance / proof-of-funds URLs logged separately in `financial_refs_for_human_review.json`
- Rate limit: 2-second delay per domain, exponential backoff on 429/503
