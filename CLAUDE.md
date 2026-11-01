# Samura Consulting Group website (samuraconsulting.com)

Read OPERATIONS.md before doing anything. It is the full handover: strategy, status, rules, routines and open tasks.

## What this repo is
Static site deployed by Vercel from `main`. The repo root is the deploy root. Clean URLs (`/pricing` serves `pricing.html`). `vercel.json` holds redirects and headers.

## How to change the site
- Articles and all generated pages: edit `tools/articles.py` (append a dict to ARTICLES), then run `python3 tools/build.py` (on Windows: `python tools/build.py`). Never hand-edit files under `insights/`, the service pages, `pricing.html`, `check.html`, `industries.html`, `sitemap.xml` or the generated parts of `llms.txt`; the build overwrites them.
- Homepage copy, case-studies hub, redirects: hand-edit `index.html`, `case-studies.html`, `vercel.json`.
- After any change: run the build, check the pages, commit, push to `main`. Then `python3 tools/notify.py <new or changed URLs>` to ping Bing. Google reads `sitemap.xml` on its own.

## Non-negotiable rules
- No em dashes or en dashes anywhere (use commas, colons, "and", or a new sentence). The build asserts this for articles.
- American spelling: optimization, not optimisation.
- Plain English. Short sentences. UAE readers, many with English as a second language. Specific facts (numbers, places, names) so AI engines can quote the text.
- Authors: Sufia Aram (Managing Partner) or Madhura Chowdhury (Consultant). Nobody else is named on the site. Do not add Shoaib Mustaque anywhere.
- Do not mention Mighty Warners anywhere. Konception Designs is the only client case study.
- Do not frame the company as new. Samura's parent has done search work since 2018. Avoid "we relaunched ten days ago" style claims in public copy.
- Published prices are real: Audit AED 1,999; Launch from AED 2,999; Establish from AED 7,999; Dominate from AED 10,999; Enterprise from AED 10,000 a month. Nothing auto-renews.
- Never invent client results, reviews, awards or figures. Never name competitors as weak; describe them factually.
- Dubai first, then UAE, then GCC. Business Bay, Dubai is the public address; RAKEZ is the licence only.
- Every article: question-style title with sector plus Dubai or UAE, a short answer first, a FAQ block, a keyword paragraph in the buyer's vocabulary.
