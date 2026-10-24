# Update v9.5 (24 Oct 2026). Supersedes v9.4.

What changed:
- NEW  pricing.html                 standalone /pricing page: all packages, table, FAQ, Offer + FAQ schema
- NEW  case-studies/ (2 pages)      /case-studies/mighty-warners and /case-studies/konception-designs
- NEW  insights/ 5 articles (21 total): best-aeo-agencies-in-dubai (tested ranking), why-cant-chatgpt-find-my-company-by-name, is-aeo-worth-it-for-a-small-business-in-dubai, how-to-write-a-page-chatgpt-will-quote, what-is-geo-and-is-it-different-from-aeo
- MOD  vercel.json                  removed the /pricing and /case-studies/* redirects (they would hijack the new pages). MUST be uploaded.
- MOD  index.html                   link to /pricing under the pricing section; newest insights cards
- MOD  case-studies.html            links to the two full case studies; clean URLs in nav and footer
- MOD  sitemap.xml, llms.txt        include the new URLs

Upload (GitHub web, "Add file > Upload files"): all files in this folder, keeping the insights/ and case-studies/ folders. Commit to main.

After the push, check:
  https://www.samuraconsulting.com/pricing
  https://www.samuraconsulting.com/case-studies/mighty-warners
  https://www.samuraconsulting.com/insights/best-aeo-agencies-in-dubai
