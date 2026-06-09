# INTELLIGENCE BRIEF: Illegal Online Gambling Network Targeting Bangladesh
**Classification:** Law Enforcement / Investigative Journalism Use  
**Prepared for:** Bangladesh CID Cyber Police Centre  
**Date:** 2026-06-09  
**Primary Target:** bdbetsolution.com  
**Investigation Method:** Passive OSINT (no active exploitation performed)

---

## EXECUTIVE SUMMARY

A coordinated network of at least **5 domains** operating from a single server in Mumbai, India provides B2B infrastructure for illegal online gambling targeting Bangladesh. The network sells white-label clones of 15+ known gambling brands to Bangladeshi operators. The primary operator communicates via a UAE phone number and maintains active presence on Telegram, Facebook, YouTube, and Instagram under consistent brand handles.

---

## 1. PRIMARY TARGET: bdbetsolution.com

### Site Identity
| Field | Value |
|-------|-------|
| Title | "White Label Betting Platform/Panel Provider in Bangladesh" |
| Services | B2B white-label betting platforms, B2C betting, Payment Solutions, Casino Aggregator |
| Language | English + Bengali (বাংলা) — explicitly targeting Bangladeshi market |

### Operator Contact Intelligence
| Channel | Identifier | Notes |
|---------|-----------|-------|
| Email | bdbetsolution@gmail.com | Primary contact |
| Phone/WhatsApp | **+971557785416** | UAE mobile — operator likely UAE-based |
| Telegram | @bdbetsolution | Confirmed active channel |
| Facebook | facebook.com/bdbetsolution | |
| YouTube | @Bdbetssolution | |
| Instagram | bdbetsolutionofficial | |

---

## 2. NETWORK INFRASTRUCTURE

### Shared Server — 172.105.56.131
**All five domains resolve to the same IP, running identical Apache 2.4.41/Ubuntu stack.**

| Domain | Purpose | Tracking IDs |
|--------|---------|-------------|
| bdbetsolution.com | B2B white-label platform provider (Bangladesh) | G-PTC22BRC8J, GTM-MVF3XG4M, **AW-16724438971** |
| play.sky247.bet | White-label Sky247 clone — operated by same entity | **AW-16724438971** (SHARED with bdbetsolution.com) |
| bettingsolutions.in | Gambling API supplier (Casino, Odds, Score, Betfair APIs) | G-1LD07KC3FB, GTM-MGD7X67X |
| ctfc.in | "CTFC B2B Sports Betting Website Provider in Bangladesh India" | G-MV496SX2BD, GTM-55327N4S |
| delhibook.live | Cricket bookmaker (Delhi Bookmaker) | — |

### Infrastructure Details
| Field | Value |
|-------|-------|
| Host IP | 172.105.56.131 |
| Hosting Provider | Akamai Connected Cloud (Linode), Mumbai, India (AS63949) |
| Reverse DNS | 172-105-56-131.ip.linodeusercontent.com |
| Web Server | Apache/2.4.41 (Ubuntu) |
| Backend Language | PHP (PHPSESSID cookies) |
| Admin Backend | Node.js/Express (admin.delhibook.live) |
| Frontend Framework | Bootstrap 5.0.2 |
| Domain Registrar DNS | GoDaddy (ns35.domaincontrol.com / ns36.domaincontrol.com) |
| SSL Issuer | Let's Encrypt (renewed 2026-05-18) |

### Proven Link Between bdbetsolution.com and play.sky247.bet
**Both domains share Google Ads conversion ID `AW-16724438971`** — uniquely identifying the same Google Ads account and therefore the same operator. The `play.sky247.bet` site explicitly brands itself "BDBETS" and lists contact email `bdbetsolution@gmail.com`.

---

## 3. WHITE-LABEL PRODUCTS SOLD (Illegal Gambling Brands Cloned for Bangladesh)

The operator's contact form explicitly lists these products as available for purchase:

1. Playsta (White Label Betting Website)
2. **Stake** (White Label Betting Website)
3. Babu88 (Betting Website)
4. **Sky247** (Betting Website — operator runs `play.sky247.bet`)
5. 7Wicket (White Label Betting Website)
6. SkyExch (White Label Betting Website)
7. Jeetwin (Betting Website)
8. Takabet11 (White Label Betting Website)
9. Jita (White Label Betting Website)
10. Betjili (White Label Betting Website)
11. Betvisa (White Label Betting Website)
12. Elon-Bet (White Label Betting Website)
13. Sportsbet (White Label Betting Website)
14. Krikya22 (White Label Betting Website)
15. Velki (White Label Betting Website)

---

## 4. RELATED ENTITY: bettingsolutions.in

| Field | Value |
|-------|-------|
| Title | "Casino API | Score API | Odds API | Fancy API | Virtual Games" |
| Contact Email | info@bettingsolutions.in |
| Contact Phone | **+971557785416** (SAME UAE number as bdbetsolution.com) |
| Services | Live Casino API, Score API, Odds API, Fancy API, Bookmaker API, Sports Result API, TV API, Betfair API |

**The shared UAE phone number +971557785416 directly links bettingsolutions.in and bdbetsolution.com to the same operator.**

---

## 5. RELATED ENTITY: ctfc.in

| Field | Value |
|-------|-------|
| Title | "CTFC B2B Sports Betting Website Provider in Bangladesh India" |
| Contact Email | info@ctfc.in |
| Contact Phone | +17163749919 (US VOIP number) |
| Telegram | t.me/ctfcplay, t.me/justforctfc |
| Active Subdomains | demouser.ctfc.in (live user frontend demo), websitedata.ctfc.in |

---

## 6. RELATED ENTITY: delhibook.live

| Field | Value |
|-------|-------|
| Type | Cricket bookmaker (Delhi Book — "book" = bookmaker in South Asian betting) |
| Active Subdomains | admin.delhibook.live (**LIVE admin panel, 200 OK**), book.delhibook.live |
| Admin Panel Tech | Node.js/Express |

---

## 7. EXPOSED ADMIN PANELS

| URL | HTTP Status | Notes |
|-----|-------------|-------|
| https://bdbetsolution.com/admin/login | **200 OK** | Title: "Admin - bdbetsolutions" — login form live |
| https://admin.delhibook.live | **200 OK** | Express.js backend — live panel |
| https://demouser.ctfc.in | **200 OK** | "Userfrontend" — demo user panel |

---

## 8. KNOWN VULNERABILITIES (Shodan InternetDB)

The server at 172.105.56.131 has **90+ CVEs** mapped against Apache 2.4.41. Notably:
- CVE-2021-40438 (SSRF via mod_proxy — Critical)
- CVE-2021-41773 / CVE-2021-42013 (Path traversal — Critical)
- CVE-2022-22719, CVE-2022-22720, CVE-2022-22721 (Apache request smuggling)
- CVE-2024-38473, CVE-2024-38474, CVE-2024-38476 (Apache path confusion)

*(Provided for law enforcement context only — no exploitation performed.)*

---

## 9. CERTIFICATE TRANSPARENCY RECORD

| Date | Domain | Issuer |
|------|--------|--------|
| 2026-05-18 | bdbetsolution.com | Let's Encrypt R12 |
| 2026-05-18 | www.bdbetsolution.com | Let's Encrypt R12 |
| — | delhibook.live | — |
| — | www.delhibook.live | — |
| — | admin.delhibook.live | — |
| — | *.delhibook.live | — |
| — | book.delhibook.live | — |

---

## 10. NETWORK MAP SUMMARY

```
OPERATOR (UAE: +971557785416)
├── bdbetsolution.com         [B2B platform provider, Bangladesh]
│   ├── Gmail: bdbetsolution@gmail.com
│   ├── Telegram: @bdbetsolution
│   ├── Social: FB/IG/YT @bdbetsolution
│   └── Google Ads: AW-16724438971 ──────────────────┐
│                                                     │ (SHARED — same operator)
├── play.sky247.bet            [Sky247 clone]         │
│   └── Google Ads: AW-16724438971 ──────────────────┘
│
├── bettingsolutions.in        [API supplier]
│   ├── Email: info@bettingsolutions.in
│   └── Phone: +971557785416 (SAME UAE number)
│
├── ctfc.in                    [B2B provider, BD/India]
│   ├── Email: info@ctfc.in
│   ├── Phone: +17163749919 (US VOIP)
│   └── Telegram: t.me/ctfcplay, t.me/justforctfc
│
└── delhibook.live             [Cricket bookmaker]
    └── admin.delhibook.live   [Live admin panel]

ALL HOSTED ON: 172.105.56.131 (Akamai/Linode Mumbai, AS63949)
```

---

## 11. RECOMMENDED ACTIONS FOR LAW ENFORCEMENT

1. **Legal Process to Linode/Akamai** (AS63949): Subscriber records for IP 172.105.56.131, billing address, payment method.
2. **Legal Process to GoDaddy**: Domain registrant records for bdbetsolution.com (ns35/ns36.domaincontrol.com).
3. **Legal Process to Google**: Account holder for `bdbetsolution@gmail.com`, Google Ads account `AW-16724438971`, Analytics accounts G-PTC22BRC8J / G-1LD07KC3FB / G-MV496SX2BD.
4. **Coordination with UAE authorities**: Phone number +971557785416 — subscriber identity via Emirati telecom regulator (TRA).
5. **Telegram**: Content preservation request for @bdbetsolution, t.me/ctfcplay, t.me/justforctfc.
6. **Social Media**: Facebook (bdbetsolution), Instagram (bdbetsolutionofficial), YouTube (@Bdbetssolution) — account holder identity and linked phone/email.

---

## 12. OSINT METHODOLOGY

All findings derived from **passive, publicly available sources only**:
- DNS/WHOIS queries (Google DNS-over-HTTPS, public WHOIS)
- SSL certificate transparency logs (crt.sh)
- Reverse IP lookup (HackerTarget API)
- Shodan InternetDB (public endpoint, no authentication)
- HTTP header inspection
- Public web page content analysis
- Google/Telegram/social media public APIs

No credentials were tested, no systems were accessed without authorization, and no traffic was generated beyond standard HTTP GET requests to public-facing pages.

---

*Report generated using Reconator OSINT framework + manual analysis*  
*Investigation branch: claude/gambling-network-investigation-tool-m7xqhp*
