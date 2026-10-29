# Update v10.2 (29 Oct 2026). Supersedes v10.1.

What changed:
- DEL  case-studies/mighty-warners.html   DELETE this file from the repo (GitHub: open the file, click the trash icon, commit). vercel.json now redirects that URL to /case-studies.
- MOD  case-studies.html, index.html      Mighty Warners removed; homepage proof card replaced with Samura's own live program
- MOD  vercel.json                        redirect added (must be uploaded)
- NEW  industries.html                    /industries page listing every sector series
- NEW  insights/ hubs: apparel-and-textiles, education, automotive
- NEW  insights/ 10 articles (51 total): apparel x3, food and hotel x3, education x2, EV and automotive x2; four bylined Madhura Chowdhury
- MOD  index.html                         industry tiles link to series hubs; "See the guides by industry" link
- MOD  insights/ (all)                    related links rebuilt; ranking article carries "Last tested / next re-test" line
- FIX  index.html                         homepage no longer lands on the contact form on open (phone field was being focused on load)
- MOD  insights/ (all)                    smaller article headings so the short answer is visible on open; every short answer rewritten in plain English
- MOD  sitemap.xml, llms.txt

Upload: everything in this folder, keeping the insights/ folder. Commit to main. Then delete case-studies/mighty-warners.html in a second commit.
Check after push: https://www.samuraconsulting.com/industries and https://www.samuraconsulting.com/case-studies/mighty-warners (should land on /case-studies)
