# OPERATIONS.md: Samura Consulting Group AEO program handover

Last updated: 31 October 2026, evening session (v10.3 live and verified byte-identical; v10.4 committed locally on Sufia's PC, push pending GitHub login). Maintained by whoever runs the program. Update the Status section after every working session.

## 1. Goal
Make Samura Consulting Group the agency named when someone asks ChatGPT, Claude, Gemini, Perplexity or Google AI Overviews for an AEO / GEO / AI search agency in Dubai (then UAE), and get organic leads through the contact form and the /check page. Secondary: rank the sector guides so businesses in those sectors find Samura.

## 2. Who
- Sufia Aram, Managing Partner. Runs everything, posts on LinkedIn, attends events, approves content. Wants exact click-by-click instructions for any tool step, and a check before each step. Wants the company portrayed as established and leading, not new.
- Madhura Chowdhury, Consultant, Samura Consulting Group. Byline on roughly a third of articles (photo at /assets/madhura.jpg).
- Shoaib Mustaque, co-founder and director: NOT shown anywhere on the site by his choice. Advises in the background; vetoed the "ten days ago we relaunched" LinkedIn post.
- Engineering bench: Altix Codeit, India (50+ engineers), can be mentioned as the group's technical team.

## 3. Accounts and assets (no passwords here; Sufia holds them)
- Domain: samuraconsulting.com, DNS at GoDaddy. Hosting: Vercel, auto-deploys from GitHub `codeit-techteam/SamuraAEO` (public repo), branch `main`. Deploys up to v10.3 were done by GitHub web upload of zip contents. Since 31 Oct, Sufia's Windows PC has Git 2.56, Python 3.12 and GitHub CLI 2.103 (installed with winget) and a clone of the repo, so the routine is: edit, `python tools/build.py` (on Windows the command is `python`, not `python3`), commit, `git push`. First push needs `gh auth login` once in a terminal.
- Google: samuraconsulting@gmail.com. Search Console (domain property, verified), Google Business Profile (created, verification status to confirm), Google Ads credit available (brand campaign not yet started).
- Bing Webmaster Tools: property `https://samuraconsulting.com/` (covers www too). Sitemap submitted and Success. Homepage "Request indexing" done 30 Oct. Old record showed last crawl 15 Oct as a redirect; Live URL test on 30 Oct: "URL can be indexed, no SEO/GEO issues".
- IndexNow key: `32652ca172d2a57a4b51ba12e38ed96e`, file live at /32652ca172d2a57a4b51ba12e38ed96e.txt. Ping with `python3 tools/notify.py URL...` or by opening `https://api.indexnow.org/indexnow?url=PAGE&key=32652ca172d2a57a4b51ba12e38ed96e` in a browser (blank page = success).
- Web3Forms (contact form, footer subscribe, /check form): access key `ff2a2e87-c12d-4ced-acd8-467f85574bb2`, account samuraconsulting@gmail.com, linked recipient mail@samuraconsulting.com. Submissions also listed in the Web3Forms dashboard. Live test still to be confirmed with a screenshot.
- Calendly: https://calendly.com/sufiaaram2/30min (hero button).
- LinkedIn company page: https://www.linkedin.com/company/samuraconsulting (Day 1 and Day 2 posts published; Day 3 event-offer post drafted, awaiting posting).
- Crunchbase: person profiles for Sufia and Shoaib live; company profile submitted, under review (no public URL yet).
- GoodFirms: https://www.goodfirms.co/company/samura-consulting-group (submitted; in site schema sameAs).
- DesignRush: profile submitted 26 Oct; awaiting approval; URL unknown. Ask Sufia for it; add to sameAs in index.html schema when available.
- Clutch, Semrush Agency Partners, TechBehemoths: not yet created.
- Emails: mail@samuraconsulting.com (public, directories), sufia.aram@samuraconsulting.com, samuraconsulting@gmail.com (Google services).
- Phone/WhatsApp: +971 55 584 8267. Office: Business Bay, Dubai.

## 4. Site map (what exists)
- `/` homepage: hero (AEO agency in Dubai), proof strip, services, six-step method, "how we are different", industries tiles (link to hubs), comparison table, leadership (Sufia only), pricing section, case studies (Samura's own program card + Konception), insights cards (newest 3), FAQ (18 questions, FAQPage schema), contact form with country picker, footer with subscribe.
- `/pricing`, `/check` (event lead capture with QR), `/industries`, `/case-studies`, `/case-studies/konception-designs`.
- Service pages: `/answer-engine-optimization-dubai`, `/generative-engine-optimization-dubai`, `/ai-seo-agency-dubai`, `/ai-visibility-audit`.
- `/insights` plus 9 series hubs: healthcare, real-estate, food-and-hospitality, agriculture, apparel-and-textiles, education, automotive, retail-and-software, aeo-basics.
- 56 articles under `/insights/<slug>` (as of v10.3). Each has Article + FAQPage + Breadcrumb schema, byline, related links within its series.
- `/privacy`, `/terms`, `/404`, `sitemap.xml` (78 URLs), `llms.txt`, `robots.txt`.
- Redirects in vercel.json: old site URLs (/about, /services/*, /industries/*, /contact, three old article slugs, /privacy-policy) and `/case-studies/mighty-warners` -> `/case-studies`.

## 5. Build and deploy routine
1. Edit `tools/articles.py` (append dicts) or hand-edit `index.html` / `case-studies.html` / `vercel.json`.
2. `python3 tools/build.py` from the repo root. It prints "built N articles".
3. Check: open a few generated pages; no horizontal overflow at 390px width; one H1 per page; no em dashes.
4. Commit and push to `main`. Vercel deploys in about a minute. Verify the live URLs.
5. `python3 tools/notify.py` with every new or changed URL (IndexNow; Bing API too if BING_API_KEY is set).
6. Give Sufia the day's four URLs for Google Search Console "Request indexing" (manual; no API). Priority: new service/landing pages, then event-relevant articles.
7. Log the version and the URL list in Section 10.
If pushing is not possible, produce a zip of changed files (keep folder paths) for GitHub web upload, with a README-UPDATE.md describing the change. Deleting a file needs a separate GitHub action.

## 6. Content rules and format
Article dict fields: slug, title, category, date (YYYY-MM-DD), read (4), optional author ("madhura"; default Sufia), description (<=155 chars ideal), answer (plain-English short answer, 60 to 110 words, facts included), body (HTML: h2 sections, ul/ol, short paragraphs, ends with a "Keywords to build pages around" paragraph for sector pieces), faq (4 question/answer pairs).
Categories map to hubs in build.py HUBS: Healthcare; Real estate; Food and hospitality / Hospitality; Agriculture; Apparel and textiles; Education; Automotive; Jewellery / Software (retail-and-software); AEO basics / Explainers / How to / Pricing / Hiring an agency / From our calls / Research (aeo-basics). A new sector needs a new HUBS entry and INDUSTRY_ORDER entry.
Cadence agreed with Sufia: 5 articles per day minimum, clustered by the next event or sector she will pitch. Ten on event days.
Keyword vocabulary (from research on the pages AI engines cite, 30 Oct): answer engine optimization, generative engine optimization, AEO agency in Dubai, GEO agency, AI SEO, ChatGPT SEO, AI search, AI visibility, AI visibility audit, AI Overviews, ChatGPT, Perplexity, Gemini, Claude, structured data, entity, citations, brand mentions, traditional SEO, rank on ChatGPT, get recommended by ChatGPT, AEO vs SEO, Dubai businesses, Arabic and English, GCC, MENA, zero-click, share of voice, prompt tracking, llms.txt. Use American spelling. "Dubai" outranks "UAE" in searches; use both.
Common FAQ questions competitors all answer (use on service pages and hubs): what is AEO; AEO vs SEO; how long does it take; what does it cost in Dubai; who is the best AEO agency in Dubai; how to choose; Dubai-based or remote; Arabic and English; which engines; can you guarantee ChatGPT; how do you measure; which industries benefit most.
Tone: confident, factual, no superlatives about ourselves, no attacks on competitors. Position: founder-led, published pricing, measured by AI citations, Arabic and English, IIT and IIM professionals in the team, search work since 2018.

## 7. Events calendar (Sufia attends all; content is written before each)
- Done: Growtech Middle East, Dubai AI Festival (26 to 28 Oct).
- 3 to 5 Nov: Gulfood Manufacturing, Gulf Host, ISM Middle East, Private Label Middle East (food and hospitality cluster written).
- 10 to 12 Nov: GESS (education cluster written), EV World Show (automotive cluster written), World Vape Show (skip).
- 16 to 18 Nov: International Apparel and Textile Fair (apparel cluster written), Dubai International Food Safety Conference (food safety article written), Middle East Organic and Natural Products Expo (not yet written), The Mining Show and World Police Summit (Sufia said no content for these).
- 19 to 22 Nov: World Art Dubai (not written).
- 23 to 26 Nov: Big 5 Global (construction), GeoWorld / Future FM (facilities management), HVACR World (not written; next clusters to write).

## 8. Measurement
- Weekly prompt log (Sufia runs, logged out, screenshots): "best AEO agency in Dubai"; "which agency can get my business recommended by ChatGPT in the UAE"; "answer engine optimization agency Dubai pricing"; "who are the top AI search optimization agencies in Dubai 2026"; "Samura Consulting Group Dubai". Engines: ChatGPT (search on), Claude, Gemini, Perplexity. Baseline 21 and 24 Oct: Samura named 0 times; name not recognised by ChatGPT or Claude.
- Google Search Console (18 to 29 Oct): 608 impressions, 6 clicks, average position 51 overall and 37.6 in the week of 25 to 29 Oct (was 58). Generative AI features: 18 impressions by 30 Oct, 16 of them 25 to 30 Oct; pages shown include the homepage and several articles. 45 pages indexed, 13 not (mostly old URLs).
- Bing (30 Oct): sitemap Success (34 URLs seen on 28 Oct); zero impressions, zero backlinks; homepage re-index requested; IndexNow pinged for 6 URLs.
- Bing (31 Oct): IndexNow pinged for all 78 sitemap URLs (HTTP 200). DuckDuckGo, which uses the Bing index, returned about 6 Samura pages for `site:samuraconsulting.com` and the homepage was not among them. On the brand query Bing autocorrects "Samura Consulting Group" to "Samurai Consulting Group" and shows /insights above the homepage. ChatGPT search reads the Bing index, so Bing coverage is the first thing to grow.
- Agency ranking article (`/insights/best-aeo-agencies-in-dubai`) must be re-tested in the last week of November and updated with Gemini and Perplexity added.

## 9. Open tasks (priority order)
1. v10.3 is live (every page verified identical to the build on 31 Oct). IndexNow done for all 78 URLs on 31 Oct. Remaining: push the v10.4 commits (handover docs, tools/, Windows fix in build.py, deletion of `case-studies/mighty-warners.html` and `assets/shoaib.jpg`), then Google Search Console "Request indexing" for the homepage, /industries and the four service pages, then Bing Webmaster URL submission for the same six.
2. Next content build from the 31 Oct site audit (62 findings; report kept on Sufia's PC as site-audit-2026-10-31.md, not in the repo): American spelling sweep across articles.py, build.py, index.html and case-studies.html (about 157 British forms on 50 pages); remove the relaunch framing (needs the task 9 decision); one Business Bay address in the schema with RAKEZ as a licence line only; GEO wording on the ranking article, a GEO-specific FAQ on the GEO service page and in llms.txt (the site never says 'GEO company' or 'best GEO agency'); question-style titles with Dubai or UAE for 11 articles; keywords paragraph for 11 sector articles; Madhura on the homepage team section; About and Contact pages and author profile pages; one audit-credit wording; drop the 'Most chosen' badge and the guarantee wording; fix case-studies.html footer and schema; meta descriptions and titles trimmed.
3. Confirm the contact form and /check form deliver email (live test, screenshot).
4. DesignRush URL from Sufia -> add to index.html schema sameAs. Crunchbase company URL when approved -> same.
5. Clutch profile; Konception review on Clutch and Google; Konception footer credit link; website link in Sufia's personal LinkedIn.
6. Google Ads brand campaign on "samura consulting" variants, AED 5 to 10 a day.
7. Google Search Console: Removals request for `/case-studies/mighty-warners`; Bing: Block URL for the same.
8. LinkedIn Day 3 post (event offer; draft in chat history, final wording: opens with "Next week, Dubai hosts Gulfood Manufacturing, Gulf Host and Private Label Middle East (3 to 5 November 2026)..."; first comment links to /check). Then one post per day: article shares and event posts.
9. Decide with Sufia and Shoaib whether to remove the "new site / relaunched" framing from: homepage Samura case card ("50+ guides in two weeks"), the ranking article ("site relaunched 18 October"), and the article "Why can't ChatGPT find my company by name? Our own case, five days after launch".
10. Next article clusters: organic and natural products, construction and fit-out (Big 5), facilities management, HVAC, art galleries; then second passes on healthcare and real estate with Arabic-angle pieces.
11. Tahani Flowers (Kuwait AEO/SEO client, listed in DesignRush portfolio): get numbers and permission from Sufia, then add a case study page.
12. Weekly Monday report to Sufia: GSC position/clicks/AI impressions, Bing indexed count, prompt log, what changed, what is next.
13. Monthly: competitor scan (WAIM, SEO Sherpa, Digital Gravity, SEO Tech Experts, Digital Nexa, NorthQuery, Web Tonic, Red Berries, Tenet, Royex), keyword map refresh, ranking article re-test.
14. Outreach emails drafted earlier (send from mail@samuraconsulting.com with Sufia's approval): ivanooo.com (hello@ivanooo.com) to be included in their tested ranking; AllBlogThings and TechBullion paid profile (Sufia to decide on spend).

## 10. Version log
- v8 / v8.1 (18 to 19 Oct): relaunch, dark mode removed, flags fixed.
- v9.x (20 to 24 Oct): insights section, legal pages, mobile menu, pricing page, case study pages, first 21 articles, tested agency ranking.
- v10 (28 Oct): Shoaib removed; 10 agriculture and food articles; hubs; industries tiles.
- v10.1 (28 Oct): Web3Forms lead capture; 6 hubs; 5 real estate articles; /check page + QR; IndexNow key file; GoodFirms sameAs.
- v10.2 (29 Oct, live): Mighty Warners removed; /industries; 10 articles (apparel, food, education, automotive); plain-English short answers; smaller article headings; homepage no longer scrolls to the form on load.
- v10.3 (30 Oct, built, not yet deployed): keyword build; homepage rewrite; four service pages; 5 search-targeted articles; American spelling; footer links. 78 URLs in sitemap.
- v10.4 (31 Oct): this handover: tools/ in repo, CLAUDE.md, OPERATIONS.md, .vercelignore. build.py fixed to run on Windows (date format, UTF-8 file handling); output verified identical to v10.3. `case-studies/mighty-warners.html` and `assets/shoaib.jpg` deleted in a second commit. Third commit: the `/industries` redirect removed from vercel.json (it had made the industries hub unreachable) and the audit Offer price in the /ai-visibility-audit schema corrected from 2999 to 1999. Site audit run the same day (see task 2).

## 11. URL submission lists still owed to Bing and Google
v10.3 new URLs (submit after deploy):
https://www.samuraconsulting.com/
https://www.samuraconsulting.com/answer-engine-optimization-dubai
https://www.samuraconsulting.com/generative-engine-optimization-dubai
https://www.samuraconsulting.com/ai-seo-agency-dubai
https://www.samuraconsulting.com/ai-visibility-audit
https://www.samuraconsulting.com/insights/how-to-get-your-business-recommended-by-chatgpt-in-the-uae
https://www.samuraconsulting.com/insights/how-to-rank-on-chatgpt-and-ai-search-engines-in-2026
https://www.samuraconsulting.com/insights/how-to-run-an-ai-visibility-audit-yourself
https://www.samuraconsulting.com/insights/dubai-based-aeo-agency-or-remote-which-should-you-hire
https://www.samuraconsulting.com/insights/which-industries-in-dubai-benefit-most-from-aeo
https://www.samuraconsulting.com/insights/what-is-aeo-and-how-is-it-different-from-seo
