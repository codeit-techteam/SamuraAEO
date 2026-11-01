# tools/

- `articles.py`  The content database: one Python dict per article (slug, title, category, date, read, optional author, description, answer, body HTML, faq list). Add new articles at the end of ARTICLES.
- `build.py`     Rebuilds every generated page from articles.py and the live index.html: /insights/*, hub pages, /pricing, /check, /industries, the four service pages, /case-studies/*, /privacy, /terms, /404, sitemap.xml, llms.txt, and the homepage Insights cards. Run from anywhere: `python3 tools/build.py`. It rewrites files in the repo root (the deploy root).
- `notify.py`    Pings Bing (IndexNow, plus the Bing API if BING_API_KEY is set) with new or changed URLs.

index.html, case-studies.html and vercel.json are hand-edited sources; everything else under the root that build.py lists is generated and should not be edited by hand.

Hard rules for generated content: no em dashes or en dashes anywhere (build.py asserts this), American spelling ("optimization"), plain-English short answers, every article has a FAQ, bylines only for Sufia Aram or Madhura Chowdhury.
