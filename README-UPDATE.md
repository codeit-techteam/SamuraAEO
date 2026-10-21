# Update v9.3 (21 Oct 2026). Supersedes v9.2 and v9.1.

v9.3: desktop header restored to one row with one button (the mobile-menu CTA was leaking onto desktop); all articles labelled 4 min read; publish dates staggered 18 to 21 Oct; clinic and hospitality articles bylined Shoaib Mustaque.


Replace the repo contents with this folder and push. Vercel redeploys automatically.

What changed in v9.2 (on top of v9.1):
- FIX  vercel.json          old /insights redirects removed; they would have hijacked the new article URLs
- NEW  mobile menu          hamburger navigation on phones and tablets, every page
- NEW  privacy.html, terms.html, 404.html
- NEW  assets/og-image.png, favicon.png, apple-touch-icon.png (social preview + proper tab icon)
- FIX  case-studies.html    no sideways scroll on small phones
- FIX  meta descriptions    shortened to about 155 characters on every page
- FIX  heading order, structured-data price range, lazy-loaded photos, cache headers

What changed in v9.1:
- NEW  insights/index.html            -> served at /insights
- NEW  insights/<slug>.html (11 files) -> served at /insights/<slug>
- MOD  index.html                     homepage Insights cards now link to real articles; "See all insights" button
- MOD  sitemap.xml                    includes the 12 new URLs
- MOD  index.html                     Sufia Aram title is now "Managing Partner" everywhere; contact form phone/email boxes aligned
- MOD  llms.txt                       lists the new pages for AI crawlers
- MOD  vercel.json                    adds permanent redirects from the OLD site's URLs
                                      (/services, /about, /insights/<old>, etc.) to the new sections

After the push, check in a browser:
  https://www.samuraconsulting.com/insights
  https://www.samuraconsulting.com/insights/what-does-aeo-cost-in-dubai
  https://www.samuraconsulting.com/services   (should land on the homepage Services section)
