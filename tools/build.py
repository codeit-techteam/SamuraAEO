#!/usr/bin/env python3
"""Builds /insights/ index and article pages into the dist folder, updates sitemap, llms.txt and homepage cards."""
import re, json, html, os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from articles import ARTICLES
BY_DATE = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)  # newest first everywhere

# American spelling guard (CLAUDE.md rule). Skips words inside slugs and URLs. cheque/tyre are UAE buyer terms, allowed.
BRITISH = re.compile(r"(?<![-/\w])(licences?|enquir\w*|jewell\w*|travell\w*|authoris\w*|centres?|catalogues?|favour\w*|summaris\w*|fibres?|paediatric\w*|recognis\w*|optimis(e|ed|es|ing|ation|ations)|neighbour\w*|organis(e|ed|es|ing|ation|ations|er|ers)|prioritis\w*|colours?|coloured|specialis(e|ed|es|ing|ation|ations|m|ms)|labour|judgements?|sceptic\w*|emphasis(e|es|ed|ing)|apologis\w*|metres?|kilometres?|litres?|customis\w*|rumours?|defence|maths|practises?|practised|programmes?|cancelled|cancelling|analys(e|ed|ing)|behaviours?|gynaecolog\w*|orthopaedic\w*|anaesthe\w*|aluminium|honours?|focuss\w*|whilst|amongst|realis(e|ed|es|ing)|utilis(e|ed|es|ing|ation)|minimis(e|ed|es|ing)|maximis(e|ed|es|ing)|standardis(e|ed|es|ing|ation)|localis(e|ed|es|ing|ation)|personalis(e|ed|es|ing|ation)|finalis(e|ed|es|ing)|categoris(e|ed|es|ing)|modelling|labelling|labelled|counsell\w*|fulfils?|tonnes?|ageing|artefacts?)(?![-\w])", re.I)
def check_american(text, name):
    for pn in ("Dubai Exhibition Centre", "Dubai World Trade Centre"):
        text = text.replace(pn, "")  # proper nouns
    m = BRITISH.search(text)
    assert not m, f"British spelling '{m.group(0)}' in {name} (CLAUDE.md: American spelling)"

# Repo root is the deploy root. tools/ sits inside it. Override with SAMURA_DIST if needed.
DIST = os.environ.get('SAMURA_DIST', os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
SITE = 'https://www.samuraconsulting.com'
index_html = open(f'{DIST}/index.html', encoding='utf-8').read()

# Reuse the site's stylesheet, nav and footer so the pages match exactly.
_i = index_html.index('<style>\n/* Layout')
css = index_html[_i:index_html.index('</style>', _i) + 8]
nav = index_html[index_html.index('<nav class="main">'):index_html.index('<header class="hero"')]
footer = index_html[index_html.index('<footer>'):index_html.index('</footer>') + 9]
# Rewrite in-page anchors so they work from /insights/
def rel(s):
    s = s.replace('href="#', 'href="/#').replace('src="assets/', 'src="/assets/').replace('href="case-studies.html"', 'href="/case-studies"')
    s = s.replace('href="/#insights"', 'href="/insights"')
    return s
nav = rel(nav).replace('<a href="/#insights">Insights</a>', '<a href="/insights" class="active">Insights</a>')
nav_plain = nav.replace(' class="active"', '')
footer = rel(footer)
footer = footer.replace('<form id="sub" novalidate>', '<form id="sub" novalidate action="/#contact">')

extra_css = """<style>
.art{max-width:760px;margin:0 auto}
.art-head{padding-block:clamp(1.6rem,3.5vw,2.4rem) 1.2rem;background:linear-gradient(180deg,var(--bg),var(--pale))}
.crumbs{font-family:var(--display);font-weight:700;font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--royal);display:flex;gap:.6rem;flex-wrap:wrap}
.crumbs a{text-decoration:none;color:inherit}
.art-head h1{font-size:clamp(1.45rem,2.3vw,1.95rem);line-height:1.22;margin-top:.7rem;color:var(--navy);max-width:60ch}
.meta-row{display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;margin-top:1rem;color:var(--muted);font-size:.92rem;font-weight:500}
.meta-row img{width:40px;height:40px;border-radius:50%;object-fit:cover;object-position:top}
.meta-row b{font-family:var(--display);color:var(--fg)}
.answer{background:var(--pale);border-left:4px solid var(--royal);border-radius:0 10px 10px 0;padding:1.2rem 1.4rem;font-size:1.08rem;line-height:1.6;margin:1.4rem 0 2rem}
.answer .lbl{display:block;font-family:var(--display);font-weight:800;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--royal);margin-bottom:.5rem}
.body h2{font-size:1.35rem;margin:2.2rem 0 .8rem}
.body pre{white-space:pre-wrap;word-break:break-word;background:#F3F6FB;border:1px solid #DCE4F0;border-radius:10px;padding:1rem 1.1rem;font-size:.9rem;line-height:1.55;margin:1rem 0;color:#0F1A2B}
.body p{margin:0 0 1rem;line-height:1.65}
.body ul{margin:0 0 1rem;padding-left:1.2rem;line-height:1.6}
.body li{margin-bottom:.5rem}
.cta-box{margin:2.5rem 0;padding:1.6rem;border-radius:var(--radius);background:linear-gradient(135deg,var(--navy),var(--royal));color:#fff;display:grid;gap:.8rem}
.cta-box h3{color:#fff;font-size:1.25rem}
.cta-box p{color:rgba(255,255,255,.9)}
.cta-box .btn{justify-self:start;background:#fff;color:var(--royal)}
.faqs{margin:2.5rem 0}
.faqs h2{font-size:1.35rem;margin-bottom:.6rem}
.related{margin:2.5rem 0 0}
.related h2{font-size:1.1rem;letter-spacing:.08em;text-transform:uppercase;color:var(--royal);margin-bottom:1rem}
.related .grid3 .card h3{font-size:1.02rem}
.art-list{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem}
@media (max-width:900px){.art-list{grid-template-columns:1fr}}
.art-list .card{text-decoration:none}
.art-list .ct{font-size:1.2rem;font-weight:700;line-height:1.2;letter-spacing:-.01em}
.art-list .meta{font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;font-family:var(--display);font-weight:700;color:var(--royal)}
.art-list small{color:var(--faint);font-weight:500}
</style>"""

AUTHORS = {
    "madhura": {"name": "Madhura Chowdhury", "title": "Consultant", "img": "/assets/madhura.jpg", "li": ""},
    "sufia": {"name": "Sufia Aram", "title": "Managing Partner", "img": "/assets/sufia.jpg", "li": "https://www.linkedin.com/in/sufia-aram-21a05a219"},
}
def person_ld(key="sufia"):
    p = AUTHORS[key]
    d = {"@type": "Person", "name": p["name"], "jobTitle": p["title"], "url": f"{SITE}/#team",
         "worksFor": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE}}
    if p["li"]: d["sameAs"] = p["li"]
    return d
    return {"@type": "Person", "name": p["name"], "jobTitle": p["title"],
            "url": f"{SITE}/#team", "sameAs": p["li"],
            "worksFor": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE}}

def card(a, lvl="h3"):
    return (f'<a class="card" href="/insights/{a["slug"]}"><div class="meta">{a["category"]}</div>'
            f'<{lvl} class="ct">{html.escape(a["title"])}</{lvl}><p>{html.escape(a["description"][:120]).rsplit(" ",1)[0]}...</p>'
            f'<small>{fmt(a["date"])} · {a["read"]} min read</small></a>')

def fmt(d):
    dt = datetime.date.fromisoformat(d)
    return f"{dt.day} {dt.strftime('%B %Y')}"  # no %-d: it is Linux-only and fails on Windows

def short(desc, n=155):
    if len(desc) <= n: return desc
    cut = desc[:n]
    i = cut.rfind('. ')
    if i > 80: return cut[:i + 1]
    return cut.rsplit(' ', 1)[0].rstrip(',;:') + '.'

def head(title, desc, url, ld):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="light only">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title + (" | Samura Consulting Group" if len(title) <= 45 else " | Samura"))}</title>
<meta name="description" content="{html.escape(short(desc))}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(short(desc))}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="en_AE">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Samura Consulting Group">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/og-image.png">
<link rel="icon" type="image/png" sizes="512x512" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{css}
{extra_css}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
"""

tail = """
<script>
document.documentElement.classList.add('js');
document.querySelectorAll('.kicker').forEach(function(k){var t=k.getAttribute('data-text')||'';k.textContent=t;k.classList.add('in')});
var mb=document.getElementById('menu-btn'),ul=document.getElementById('site-links');if(mb){mb.addEventListener('click',function(){var o=ul.classList.toggle('open');mb.setAttribute('aria-expanded',o?'true':'false');});}
var sf=document.getElementById('sub');if(sf){sf.addEventListener('submit',function(e){e.preventDefault();var v=(document.getElementById('sub-email').value||'').trim();if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(v)){document.getElementById('sub-email').focus();return;}document.getElementById('sub-ok').classList.add('show');document.getElementById('sub-email').value='';});}
</script>
</body>
</html>
"""

os.makedirs(f'{DIST}/insights', exist_ok=True)


# --- Clusters and hub pages ---
HUBS = {
 "healthcare": {"title": "AEO for clinics, hospitals and dental practices in the UAE", "h1": "AI search for healthcare providers in the UAE",
   "cats": ["Healthcare"], "desc": "How patients in Dubai and the UAE use ChatGPT, Gemini and Perplexity to choose a clinic or doctor, and what a healthcare provider should publish to be the one recommended. Guides for clinics, dental practices and hospital groups.",
   "answer": "Patients in the UAE now ask AI assistants which clinic or doctor to see, filtering by specialty, area, language and insurer. Clinics get recommended when they publish doctor profiles, specialties, insurers, prices and location consistently on their website, Google Business Profile and health directories. These guides cover what to publish, how to handle reviews, whether to add Arabic pages, and what the engines cite."},
 "agriculture": {"title": "AEO for farms, agritech, veterinary and horticulture businesses in the UAE", "h1": "AI search for agriculture and animal care in the UAE",
   "cats": ["Agriculture"], "desc": "How buyers find UAE farms, hydroponic growers, veterinary and equine services, landscaping companies and agricultural equipment suppliers through AI assistants, and what each should publish to be named.",
   "answer": "Hotel buyers, retailers, pet owners, stable managers, villa owners and farm operators in the UAE increasingly ask AI assistants for suppliers and services. The engines answer from websites, exhibitor lists such as Growtech Middle East, distributor pages, directories and reviews. These guides set out, sector by sector, the questions buyers type and the pages a business needs to be the answer."},
 "food-and-hospitality": {"title": "AEO for food manufacturers, HORECA suppliers, caterers and hotels in the UAE", "h1": "AI search for food and hospitality businesses in the UAE",
   "cats": ["Food and hospitality", "Hospitality"], "desc": "How retail buyers, hotel procurement teams, event clients and diners in the UAE use AI assistants to find food manufacturers, private label partners, HORECA suppliers, caterers, restaurants, hotels and cloud kitchens, and how each gets recommended.",
   "answer": "From Gulfood Manufacturing to Gulf Host, the UAE food and hospitality sector is being searched through AI assistants by buyers who type the whole specification at once: category, certification, capacity, area and price. The engines answer from manufacturer and supplier websites, exhibitor lists, certification registers, venue supplier lists and reviews. These guides cover what each type of business should publish."},
 "real-estate": {"title": "AEO for real estate agencies, developers and property managers in Dubai", "h1": "AI search for real estate in Dubai",
   "cats": ["Real estate"], "desc": "How Dubai property buyers, investors, landlords and travelers use ChatGPT and Perplexity to choose brokers, off-plan projects, property managers and holiday homes, and what each business should publish to be named.",
   "answer": "Real estate is the largest AI-search category in Dubai. Buyers ask by area, budget, language and situation; landlords ask about fees and scope; travelers ask about serviced apartments. The engines answer from agency websites, portal profiles, DLD and RERA data, Google reviews and property news. These guides explain what brokerages, developers, property managers and holiday home operators should publish, including the fee and price data most agencies keep offline."},
 "aeo-basics": {"title": "AEO explained: what it is, what it costs, how long it takes, how to choose an agency", "h1": "Answer engine optimization, explained",
   "cats": ["AEO basics", "Explainers", "How to", "Pricing", "Hiring an agency", "From our calls", "Research"], "desc": "Plain answers to the questions UAE business owners ask about AEO and GEO: what it is, how ChatGPT chooses who to recommend, what it costs in Dubai, how long it takes, how to test your own visibility, and how to read agency rankings.",
   "answer": "Answer engine optimization is the work of getting a business named when customers ask AI assistants for a recommendation. These guides explain how the engines choose, what the work involves, what it costs in Dubai, how long results take, how to run a five-minute visibility test yourself, and how to judge an agency, including a tested ranking of Dubai AEO agencies updated monthly."},
 "apparel-and-textiles": {"title": "AEO for apparel manufacturers, textile exporters and fashion brands", "h1": "AI search for apparel and textiles",
   "cats": ["Apparel and textiles"], "desc": "How global sourcing managers, fabric buyers and Dubai shoppers use AI assistants to find garment manufacturers, textile suppliers, fashion brands and uniform companies, and what each should publish to be named.",
   "answer": "Sourcing managers ask AI assistants for manufacturers by category, country, MOQ and certification; fabric buyers ask by fiber and standard; shoppers ask for brands by occasion and price. The engines answer from websites, B2B platforms, exhibitor lists, certification registers and media. These guides cover manufacturers, textile exporters, fashion brands and uniform suppliers, with a real UAE and India case study."},
 "education": {"title": "AEO for schools, nurseries, tutors and education suppliers in the UAE", "h1": "AI search for education in the UAE",
   "cats": ["Education"], "desc": "How UAE parents use ChatGPT to choose schools, nurseries and tutoring centers, how school procurement teams find edtech and suppliers, and what each provider should publish, consistent with KHDA and ADEK records.",
   "answer": "Parents ask AI assistants for schools by curriculum, regulator rating, fees and area, and for tutors by subject and exam board. Schools ask for suppliers by compliance and reference schools. The engines answer from regulator data, provider websites, parent review platforms and GESS exhibitor lists. These guides cover schools, nurseries, tutoring centers and education suppliers."},
 "automotive": {"title": "AEO for auto parts distributors, accessories dealers, EV charging installers, car dealers, garages and fleet services in the UAE", "h1": "AI search for the automotive aftermarket and mobility in the UAE",
   "cats": ["Automotive"], "desc": "How garages, fleet operators, car owners and parts buyers in the UAE use AI assistants to find auto parts distributors, accessories dealers, tire and battery suppliers, workshop equipment, EV charging installers, dealers and fleet services, and what each should publish to be the one named.",
   "answer": "Automotive questions to AI assistants in the UAE are specific: a genuine parts distributor for a particular make, a tire importer with stock in Sharjah, a workshop equipment supplier, the installed cost of a home EV charger, a trusted dealer, a fleet maintenance contract. The engines answer from business websites, brand distributor and installer lists, exhibitor lists such as Automechanika Dubai, trade license information, reviews and forums. These guides cover the aftermarket from parts distributors and accessories dealers to garages, EV installers, dealers and fleets."},
 "construction-and-facilities": {"title": "AEO for contractors, fit-out, facilities management and HVAC companies in the UAE", "h1": "AI search for construction and facilities in the UAE",
   "cats": ["Construction and facilities"], "desc": "How developers, office tenants, building owners and consultants in Dubai and the UAE use ChatGPT, Gemini and Perplexity to find fit-out contractors, facilities management companies and HVAC contractors, and what each should publish to be named.",
   "answer": "Building owners, tenants, developers and consultants in the UAE now ask AI assistants for contractors and service companies by project type, approval, area and price band. The engines answer from company websites, authority approval information, project pages, certification scopes, exhibitor lists from Big 5 Global and reviews. These guides cover fit-out and MEP contractors, facilities management companies and HVAC contractors and suppliers."},
 "professional-services": {"title": "AEO for consultancies, business setup firms and advisory companies in the UAE", "h1": "AI search for consultancies and advisory firms in the UAE",
   "cats": ["Professional services"], "desc": "How founders, business owners and corporate buyers in Dubai and the UAE use ChatGPT, Gemini and Perplexity to choose business setup consultants, logistics and retail consultancies, strategy advisors, fundraising advisors and event agencies, and what each should publish to be named.",
   "answer": "Founders and business owners in the UAE now ask AI assistants which consultancy or advisor to call, and they ask with the whole brief in one sentence: service, sector, emirate and budget. The engines answer from firm websites with specifics, partner profiles, LinkedIn, government and free zone information, directories and reviews. These guides cover business setup consultants, logistics and supply chain consultancies, retail and procurement advisors, management consultancies, fundraising advisors and event agencies."},
 "retail-and-software": {"title": "AEO for retailers, jewelers, art galleries and software companies in the UAE", "h1": "AI search for retail, jewelry, art and software in the UAE",
   "cats": ["Jewelry", "Software", "Retail"], "desc": "How shoppers, collectors and B2B buyers in the UAE use AI assistants to find gold and jewelry retailers, art galleries and software vendors, and what each should publish to be recommended.",
   "answer": "Shoppers ask AI assistants where to buy gold and jewelry in Dubai, collectors ask which gallery to visit, and business buyers ask which UAE software vendor to shortlist. Both get answered from websites, directories, reviews and comparison pages. These guides cover what retailers and software companies should publish to be named."},
}
def hub_of(a):
    for k, h in HUBS.items():
        if a["category"] in h["cats"]: return k
    return "aeo-basics"
hub_chips = '<div style="display:flex;gap:.6rem;flex-wrap:wrap;margin:1.2rem 0 0">' + ''.join(f'<a href="/insights/{k}" style="display:inline-block;padding:.45rem .9rem;border:1px solid #DCE4F0;border-radius:999px;font-weight:700;font-size:.9rem;text-decoration:none;color:var(--navy);background:#fff">{html.escape(h["h1"])}</a>' for k, h in HUBS.items()) + '</div>'
def related_for(a, n=5):
    same = [x for x in BY_DATE if x is not a and hub_of(x) == hub_of(a)]
    rest = [x for x in BY_DATE if x is not a and hub_of(x) != hub_of(a)]
    return (same + rest)[:n]

# --- Article pages ---
for i, a in enumerate(ARTICLES):
    url = f'{SITE}/insights/{a["slug"]}'
    others = related_for(a, 5)
    ld = [{
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["title"], "description": a["description"], "url": url, "image": [f"{SITE}/assets/og-image.png"],
        "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "en",
        "author": person_ld(a.get("author", "sufia")),
        "publisher": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE,
                      "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo.png"}},
        "mainEntityOfPage": url, "about": ["Answer engine optimization", "Generative engine optimization", "SEO", "Dubai"]
    }, {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{SITE}/insights"},
            {"@type": "ListItem", "position": 3, "name": HUBS[hub_of(a)]["h1"], "item": f"{SITE}/insights/{hub_of(a)}"},
            {"@type": "ListItem", "position": 4, "name": a["title"], "item": url}]
    }]
    faq_html = ''.join(f'<details{" open" if j == 0 else ""}><summary>{html.escape(q)}</summary><p>{html.escape(ans)}</p></details>' for j, (q, ans) in enumerate(a["faq"]))
    page = head(a["title"], a["description"], url, ld) + nav + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><a href="/insights">Insights</a><span>/</span><a href="/insights/{hub_of(a)}">{a["category"]}</a></div>
  <h1>{html.escape(a["title"])}</h1>
  <div class="meta-row"><img src="{AUTHORS[a.get("author","sufia")]["img"]}" alt="{AUTHORS[a.get("author","sufia")]["name"]}"><span>By <b>{AUTHORS[a.get("author","sufia")]["name"]}</b>, {AUTHORS[a.get("author","sufia")]["title"]}{", Samura Consulting Group" if a.get("author","sufia")!="sufia" else ""}</span><span>Published {fmt(a["date"])}</span><span>{a["read"]} min read</span></div>
</div></header>
<main><div class="wrap art">
  <div class="answer"><span class="lbl">The short answer</span>{html.escape(a["answer"])}</div>
  <div class="body">{a["body"]}</div>
  <div class="cta-box"><h3>Want to see where your business stands?</h3><p>The AI Visibility Audit tests 50 real buyer questions across ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews and shows who is being recommended instead of you. AED 1,999, credited against any program within 30 days.</p><div style="display:flex;gap:.6rem;flex-wrap:wrap"><a class="btn" href="/#contact">Order the audit</a><a class="btn" href="https://wa.me/971555848267?text=Hi%20Samura%2C%20I%20read%20your%20guide%20and%20want%20to%20know%20if%20AI%20tools%20recommend%20my%20business." target="_blank" rel="noopener" style="background:rgba(255,255,255,.14);color:#fff;border-color:rgba(255,255,255,.5)">WhatsApp us</a></div></div>
  <section class="faqs"><h2>Frequently asked</h2>{faq_html}</section>
  <section class="related"><h2>Related insights</h2><div class="grid3">{''.join(card(o) for o in others)}</div><p style="margin-top:1rem"><a href="/insights/{hub_of(a)}" style="font-weight:700">All guides in this series</a> · <a href="/insights" style="font-weight:700">All insights</a></p></section>
</div></main>
""" + footer + tail
    assert '—' not in page and '–' not in page, a["slug"]
    check_american(page, a["slug"])
    open(f'{DIST}/insights/{a["slug"]}.html', 'w', encoding='utf-8', newline='\n').write(page)

# --- Index page ---
url = f'{SITE}/insights'
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Insights | Samura Consulting Group",
      "url": url, "description": "Plain answers to the questions UAE business owners ask about AEO, GEO, SEO and AI search visibility.",
      "publisher": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE},
      "hasPart": [{"@type": "Article", "headline": a["title"], "url": f'{SITE}/insights/{a["slug"]}', "datePublished": a["date"]} for a in ARTICLES]}
idx = head("Insights", "Plain answers to the questions UAE business owners ask about AEO, GEO, SEO and AI search visibility, from the team that tests its own AI visibility every month and publishes the results.", url, ld).replace('content="article"', 'content="website"') + nav + f"""
<header class="art-head"><div class="wrap">
  <div class="kicker" data-text="Insights"></div><div class="kicker-bar"></div>
  <h1 style="max-width:18ch">Questions UAE business owners ask AI tools, answered.</h1>
  <p class="lead" style="margin-top:1rem">Each piece answers one question in plain language, the way a buyer would ask it. Written by the people who run Samura's own ranking program.</p>
  {hub_chips}
</div></header>
<main><section><div class="wrap">
  <div class="art-list">{''.join(card(a, "h2") for a in BY_DATE)}</div>
</div></section></main>
""" + footer + tail
open(f'{DIST}/insights/index.html', 'w', encoding='utf-8', newline='\n').write(idx)

# --- Hub pages ---
for k, h in HUBS.items():
    arts = [a for a in BY_DATE if hub_of(a) == k]
    url = f'{SITE}/insights/{k}'
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": h["title"], "url": url, "description": h["desc"],
           "publisher": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE},
           "hasPart": [{"@type": "Article", "headline": a["title"], "url": f'{SITE}/insights/{a["slug"]}', "datePublished": a["date"]} for a in arts]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
           {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}, {"@type": "ListItem", "position": 2, "name": "Insights", "item": f"{SITE}/insights"}, {"@type": "ListItem", "position": 3, "name": h["h1"], "item": url}]}]
    page = head(h["title"], h["desc"], url, ld).replace('content="article"', 'content="website"') + nav + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><a href="/insights">Insights</a><span>/</span><span>{html.escape(h["h1"])}</span></div>
  <h1>{html.escape(h["title"])}</h1>
</div></header>
<main><div class="wrap art">
  <div class="answer"><span class="lbl">In short</span>{html.escape(h["answer"])}</div>
  <section style="margin-top:2rem"><h2>Guides in this series ({len(arts)})</h2><div class="art-list">{''.join(card(a, "h3") for a in arts)}</div></section>
  <div class="cta-box"><h3>Want to know where your business stands in AI answers?</h3><p>The AI Visibility Audit runs up to 50 real buyer questions for your sector across ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews and shows who is being recommended instead of you. AED 1,999, credited against any program within 30 days.</p><a class="btn" href="/#contact">Order the audit</a></div>
  <p style="margin-top:1.5rem"><a href="/insights" style="font-weight:700">All insights</a></p>
</div></main>
""" + footer + tail
    open(f'{DIST}/insights/{k}.html', 'w', encoding='utf-8', newline='\n').write(page)

# --- Legal and 404 pages ---
LEGAL = {
"privacy": ("Privacy Policy", "How Samura Consulting Group collects, uses and protects the information you share through samuraconsulting.com.", """
<h2>Who we are</h2>
<p>Samura Consulting Group ("Samura", "we") is a UAE-licensed company registered at RAKEZ Business Zone, Ras Al Khaimah, with an office in Business Bay, Dubai. This policy explains what we collect on samuraconsulting.com and how we use it. Questions go to mail@samuraconsulting.com.</p>
<h2>What we collect</h2>
<p><strong>Contact form.</strong> Name, company, phone or WhatsApp number, email, website, the package you are interested in and your message. We use it to reply to your inquiry and, if you become a client, to deliver the work.</p>
<p><strong>Newsletter sign-up.</strong> Your email address, used to send occasional insights and offers. Every email includes an unsubscribe link.</p>
<p><strong>Booking.</strong> Calls booked through Calendly are handled under Calendly's own privacy policy.</p>
<p><strong>Website usage.</strong> Standard server logs and privacy-respecting analytics (page views, approximate location, device type). We do not sell this data and do not use it to build advertising profiles.</p>
<h2>How we use it</h2>
<p>To answer your inquiry, to deliver services you have asked for, to send the insights you signed up for, and to keep the website working. We do not share your details with third parties except the service providers we use to run email, bookings and hosting, each bound by their own data protection terms.</p>
<h2>Your rights</h2>
<p>You can ask us at any time to see, correct or delete the information we hold about you, or to stop sending you email. Write to mail@samuraconsulting.com and we will act within 14 days.</p>
<h2>Retention and security</h2>
<p>Inquiry records are kept for as long as needed to serve you and for up to three years afterwards for business records, then deleted. Data is stored with reputable providers that use encryption in transit and at rest.</p>
<h2>Changes</h2>
<p>We may update this policy. The date below shows the latest version.</p>
<p><em>Last updated 21 October 2026.</em></p>
"""),
"terms": ("Terms of Service", "The terms on which Samura Consulting Group provides AEO, GEO and SEO services and operates samuraconsulting.com.", """
<h2>Using this website</h2>
<p>samuraconsulting.com is published by Samura Consulting Group, a UAE-licensed company registered at RAKEZ Business Zone with an office in Business Bay, Dubai. Content on the site is for general information. It is accurate to the best of our knowledge on the date published, but search and AI engines change constantly, and we do not guarantee that any statement about them remains true.</p>
<h2>Our services</h2>
<p>Programs (AI Visibility Audit, Launch, Establish, Dominate, Enterprise) are described on the Pricing section. The scope, price and term of any engagement are confirmed in a written proposal or order before work starts. Prices on the website are starting points in UAE dirhams, exclusive of VAT where applicable.</p>
<h2>What we do not promise</h2>
<p>AI assistants and search engines decide their own answers. We do not guarantee a specific position, mention or volume of inquiries. We commit to the work described in your order, to weekly tracking across the engines named in it, and to reporting results plainly.</p>
<h2>Payment and term</h2>
<p>Programs are paid in advance for the term chosen. Nothing renews automatically. If a program is canceled after work has started, fees for work completed are not refundable.</p>
<h2>Your content and ours</h2>
<p>You keep ownership of your brand, website and materials. Pages, articles and structured data we create for you become yours on payment. Our methods, templates and tools remain ours. We may describe anonymised results in our own case studies unless you ask us not to.</p>
<h2>Liability</h2>
<p>Our liability under any engagement is limited to the fees paid for that engagement. We are not liable for indirect or consequential loss, including loss of revenue arising from changes made by third-party platforms.</p>
<h2>Governing law</h2>
<p>These terms are governed by the laws of the United Arab Emirates. Disputes are subject to the courts of the Emirate of Ras Al Khaimah unless both parties agree otherwise in writing.</p>
<p><em>Last updated 21 October 2026.</em></p>
"""),
}
for slug, (ttl, desc, body) in LEGAL.items():
    url = f'{SITE}/{slug}'
    ld = {"@context": "https://schema.org", "@type": "WebPage", "name": ttl, "url": url, "description": desc,
          "publisher": {"@type": "Organization", "name": "Samura Consulting Group", "url": SITE}}
    page = head(ttl, desc, url, ld).replace('content="article"', 'content="website"') + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>{ttl}</span></div>
  <h1>{ttl}</h1>
</div></header>
<main><div class="wrap art"><div class="body">{body}</div></div></main>
""" + footer + tail
    open(f'{DIST}/{slug}.html', 'w', encoding='utf-8', newline='\n').write(page)

nf_url = f'{SITE}/404'
nf = head("Page not found", "The page you asked for is not here. Try the homepage, Insights or Case studies.", nf_url,
          {"@context": "https://schema.org", "@type": "WebPage", "name": "Page not found", "url": nf_url}) \
     .replace('content="article"', 'content="website"').replace('<link rel="canonical" href="' + nf_url + '">', '<meta name="robots" content="noindex">') + nav_plain + """
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>404</span></div>
  <h1>That page is not here.</h1>
  <p class="lead" style="margin-top:1rem">The address may have changed when we rebuilt the site. Try one of these instead.</p>
  <div style="display:flex;gap:.8rem;flex-wrap:wrap;margin-top:1.6rem">
    <a class="btn btn-primary" href="/">Homepage</a>
    <a class="btn btn-outline" href="/insights">Insights</a>
    <a class="btn btn-outline" href="/case-studies">Case studies</a>
    <a class="btn btn-outline" href="/#contact">Contact</a>
  </div>
</div></header>
""" + footer + tail
open(f'{DIST}/404.html', 'w', encoding='utf-8', newline='\n').write(nf)



# --- Industries page ---
INDUSTRY_ORDER = ["healthcare","real-estate","food-and-hospitality","agriculture","apparel-and-textiles","education","automotive","construction-and-facilities","professional-services","retail-and-software","aeo-basics"]
ind_url = f'{SITE}/industries'
ind_title = "Industries we write for and rank in the UAE: AEO by sector"
ind_desc = "Samura Consulting Group publishes sector guides on how UAE businesses get recommended by ChatGPT, Gemini, Perplexity and Google AI: healthcare, real estate, food and hospitality, agriculture, apparel, education, automotive, construction and facilities, consultancies and advisory firms, retail and software."
ind_ld = [{"@context":"https://schema.org","@type":"CollectionPage","name":ind_title,"url":ind_url,"description":ind_desc,"publisher":{"@type":"Organization","name":"Samura Consulting Group","url":SITE},
           "hasPart":[{"@type":"WebPage","name":HUBS[k]["h1"],"url":f"{SITE}/insights/{k}"} for k in INDUSTRY_ORDER]}]
cards_html = ''.join(f'<a class="card" href="/insights/{k}" style="text-decoration:none"><div class="meta">{len([a for a in ARTICLES if hub_of(a)==k])} guides</div><h3>{html.escape(HUBS[k]["h1"])}</h3><p>{html.escape(HUBS[k]["desc"][:150]).rsplit(" ",1)[0]}...</p></a>' for k in INDUSTRY_ORDER)
page = head(ind_title, ind_desc, ind_url, ind_ld).replace('content="article"', 'content="website"') + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>Industries</span></div>
  <h1>AEO by industry: who we write for and rank in the UAE</h1>
  <p class="lead" style="margin-top:.8rem">Every sector below has its own series of guides on how buyers in that sector ask AI assistants, which sources the engines cite, and what a business should publish. The method is the same; the questions, sources and keywords are not.</p>
</div></header>
<main><div class="wrap art">
  <div class="art-list">{cards_html}</div>
  <div class="cta-box"><h3>Not on the list yet?</h3><p>We research a new sector in a week: the buyer questions, the cited sources and the gaps. The AI Visibility Audit does it for your business specifically, AED 1,999, credited against any program within 30 days.</p><a class="btn" href="/#contact">Order the audit</a></div>
</div></main>
""" + footer + tail
open(f'{DIST}/industries.html', 'w', encoding='utf-8', newline='\n').write(page)


# --- Service landing pages (keyword-targeted) ---
COMMON_FAQ = [
 ("How is AEO different from traditional SEO?", "Traditional SEO gets your website into a list of ten links on Google. AEO gets your business named inside the single answer that ChatGPT, Gemini or Perplexity writes. The two overlap, because AI engines read the same web, but AEO adds entity work, structured data and citations on third-party sources that classic SEO ignores. Samura does both, with AI answers as the target."),
 ("How long does it take to show results in Dubai?", "First mentions for specific questions typically appear in three to six weeks, usually in Perplexity or ChatGPT search first. Broad questions like 'best clinic in Dubai' take two to three months of consistent work, because they depend on other websites naming you."),
 ("How much does it cost?", "Samura's prices are published: a one-time AI visibility audit at AED 1,999, a one-month Launch program from AED 2,999, two months from AED 7,999, three months from AED 10,999, enterprise from AED 10,000 a month. Nothing renews automatically."),
 ("Which AI engines do you cover?", "ChatGPT (including ChatGPT search), Claude, Gemini, Perplexity and Google AI Overviews. Each trusts a slightly different set of sources, so we track all five separately every week."),
 ("Do you work in Arabic and English?", "Yes. The Establish and Dominate programs include an Arabic FAQ layer and bilingual business descriptions, because many UAE buyers ask AI assistants in Arabic and the engines answer Arabic questions from Arabic sources."),
 ("Can you guarantee my brand will appear in ChatGPT answers?", "No, and no honest agency can. AI answers change with wording, location and the day. We guarantee the work, a weekly log of real AI answers you can reproduce, and a plain account of what moved and what did not."),
 ("How do you measure success?", "By AI citations and brand mentions: how many of your tracked buyer questions name you, in which engines, which sources the engines cite, plus AI referral visits in your analytics and inquiries that mention finding you through an AI assistant."),
 ("Should I hire a Dubai-based agency or a remote one?", "A Dubai-based agency knows the local sources AI engines cite, such as UAE directories, regulators and Arabic media. Samura is in Business Bay, Dubai, with an engineering bench of 50+ in India, so you get local presence and delivery capacity."),
 ("Which industries in Dubai benefit most?", "Any category where customers ask AI assistants for a recommendation: healthcare and dental, real estate, hotels and restaurants, food suppliers, schools and tutors, automotive and EV, software, retail. We publish a guide series for each on the Industries page."),
 ("What is answer engine optimization (AEO)?", "Answer engine optimization is the work of getting a business named inside the answer that ChatGPT, Gemini, Perplexity or Google AI Overviews gives when a customer asks for a recommendation. It covers your website, your business identity across the web, structured data, and presence on the sources AI engines cite. Generative engine optimization (GEO) and AI SEO are other names for the same work."),
 ("Who is the best AEO agency in Dubai?", "There is no independent ranking yet; most 'best AEO agency in Dubai' lists are written by an agency that puts itself first. Samura publishes a tested ranking based on what the AI engines actually say, re-run monthly, at samuraconsulting.com/insights/best-aeo-agencies-in-dubai. Judge any agency by a client's before and after, the exact prompts, published pricing and whether it covers Arabic and English."),
 ("How do I choose an AEO agency in Dubai?", "Ask for a client's dated before-and-after prompt log, the exact prompts and engines the agency tracks, its published pricing, whether it covers Arabic and English, and who does the work. Samura's guide to the five questions to ask is at samuraconsulting.com/insights/five-questions-to-ask-an-aeo-agency-before-you-hire."),
]
SERVICES = {
 "answer-engine-optimization-dubai": {
   "title": "Answer Engine Optimization (AEO) Services in Dubai | Samura Consulting Group",
   "h1": "Answer engine optimization services in Dubai",
   "kicker": "AEO agency in Dubai",
   "meta": "Answer engine optimization services in Dubai. Samura gets UAE businesses cited and recommended by ChatGPT, Gemini and Perplexity. Pricing from AED 2,999.",
   "desc": "Answer engine optimization (AEO) services in Dubai from Samura Consulting Group: get your business cited and recommended by ChatGPT, Gemini, Perplexity and Google AI Overviews. Published pricing from AED 2,999, Arabic and English, weekly AI visibility tracking.",
   "answer": "Answer engine optimization (AEO) is the work of getting your business named in the answer an AI assistant gives when a customer in Dubai asks for a recommendation. Samura is an AEO agency in Dubai. We fix how AI engines identify your business, rebuild your pages so they can be quoted, build citations on the sources ChatGPT, Gemini and Perplexity trust, and track real AI answers every week. Programs from AED 2,999 a month, published in full.",
   "sections": [
    ("What is answer engine optimization?", "<p>When someone in Dubai asks ChatGPT 'best dentist in Jumeirah' or asks Perplexity 'which company builds HR software for UAE firms', the AI does not show ten links. It writes one answer and names three to five businesses. Answer engine optimization is everything that decides whether your business is one of them.</p><p>The AI engines choose from what they can read and verify: your website, your Google Business Profile, directories, reviews, news and comparison articles. AEO makes all of those say the same clear things about you, in words a buyer would use, so the engine has something to quote.</p>"),
    ("Why Dubai businesses need AEO now", "<p>Dubai buyers moved to AI search faster than most markets: a mobile, multilingual population that asks assistants in English and Arabic for clinics, brokers, suppliers and schools. The businesses named in those answers today will hold the position for years, the way the first page of Google was held a decade ago. Most Dubai companies have not published the facts the engines need, which is why the same few names keep appearing.</p>"),
    ("What our AEO service includes", "<ul><li><strong>AI visibility audit</strong>: 50 real buyer prompts across ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews; who is named, which sources are cited, your AI share of voice.</li><li><strong>Entity optimization</strong>: one identical name, address, description and leadership across your site, Google, LinkedIn, Crunchbase and directories, with organization and person structured data.</li><li><strong>Answer-first pages</strong>: service and FAQ pages rebuilt so the answer is in the first paragraph, with JSON-LD schema and llms.txt.</li><li><strong>AI citations and brand mentions</strong>: listings, reviews, press and comparison pages on the sources each engine cites for your category.</li><li><strong>Arabic and English</strong> coverage for UAE buyers.</li><li><strong>Weekly prompt tracking</strong>: a log of real AI answers you can reproduce yourself.</li></ul>"),
    ("AEO vs traditional SEO", '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.95rem"><thead><tr style="text-align:left;border-bottom:2px solid #DCE4F0"><th style="padding:.5rem .4rem"></th><th style="padding:.5rem .4rem">Traditional SEO</th><th style="padding:.5rem .4rem">Answer engine optimization</th></tr></thead><tbody><tr style="border-bottom:1px solid #E7ECF4"><td style="padding:.5rem .4rem">Goal</td><td style="padding:.5rem .4rem">Rank a page in a list of links</td><td style="padding:.5rem .4rem">Be named inside the AI answer</td></tr><tr style="border-bottom:1px solid #E7ECF4"><td style="padding:.5rem .4rem">Measured by</td><td style="padding:.5rem .4rem">Rankings and clicks</td><td style="padding:.5rem .4rem">AI citations, brand mentions, share of voice</td></tr><tr style="border-bottom:1px solid #E7ECF4"><td style="padding:.5rem .4rem">Main work</td><td style="padding:.5rem .4rem">Keywords, links, technical fixes</td><td style="padding:.5rem .4rem">Entity consistency, answer-first pages, structured data, third-party citations</td></tr><tr><td style="padding:.5rem .4rem">Where it shows</td><td style="padding:.5rem .4rem">Google and Bing results</td><td style="padding:.5rem .4rem">ChatGPT, Gemini, Perplexity, Claude, Google AI Overviews, zero-click answers</td></tr></tbody></table></div><p>You need both. AI engines read Google and Bing, so a site that cannot rank is rarely cited. Every Samura program includes the SEO foundation.</p>'),
    ("How we measure it", "<p>Four numbers every week: how many of your tracked prompts name you, how many cite your site as a source, AI referral visits in your analytics, and inquiries that mention finding you through an AI assistant. We publish the same log for Samura itself.</p>"),
   ],
 },
 "generative-engine-optimization-dubai": {
   "title": "Generative Engine Optimization (GEO) Agency in Dubai | Samura Consulting Group",
   "h1": "Generative engine optimization agency in Dubai",
   "kicker": "GEO agency in Dubai",
   "meta": "Generative engine optimization agency in Dubai. Samura gets UAE brands cited in AI answers from ChatGPT, Gemini, Perplexity and Claude. Published pricing.",
   "desc": "Generative engine optimization (GEO) in Dubai: Samura gets UAE brands cited in AI-generated answers from ChatGPT, Gemini, Perplexity and Claude. Entity work, structured data, AI citations, Arabic and English. Published pricing.",
   "answer": "Generative engine optimization (GEO) is the practice of getting your brand cited by the AI engines that generate text answers: ChatGPT, Gemini, Perplexity and Claude. Samura is a GEO agency in Dubai. We make your business one of the sources those engines draw on, through consistent entity data, answer-first content, structured data and brand mentions on the sites the engines read. The work overlaps almost entirely with AEO; we do both and track results weekly.",
   "faq": [
    ("What is generative engine optimization (GEO)?", "Generative engine optimization is the work of getting a business cited and recommended by the AI engines that write answers: ChatGPT, Gemini, Perplexity and Claude. It covers how the engines identify your business, whether your pages can be quoted, structured data, and your presence on the third-party sources each engine reads. Answer engine optimization (AEO) and AI SEO are other names for the same work."),
    ("Is GEO different from AEO?", "In practice no. GEO puts the emphasis on the engines that generate text; AEO on being the answer wherever answers appear, including Google AI Overviews and voice assistants. The work is the same: entity consistency, answer-first pages, structured data, citations and weekly tracking. Samura does both under one program."),
    ("How much does a GEO agency in Dubai cost?", "Samura publishes its prices: a one-time AI visibility audit at AED 1,999, a one-month Launch program from AED 2,999, Establish for two months from AED 7,999, Dominate for three months from AED 10,999, and Enterprise from AED 10,000 a month. Nothing renews automatically. Many Dubai agencies do not publish GEO prices; ask for a written quote and what it includes."),
    ("Who is the best GEO agency in Dubai?", "There is no independent ranking. Most 'best GEO agency in Dubai' lists are written by an agency that puts itself first. Samura publishes a tested comparison, re-run monthly with the same prompts, at samuraconsulting.com/insights/best-aeo-agencies-in-dubai, and is scored in it by the same method as every other agency. Judge any agency by a client's dated before-and-after prompt log, its published pricing and whether it covers Arabic and English."),
    ("Which engines does a GEO program cover?", "ChatGPT including ChatGPT search, Claude, Gemini, Perplexity and Google AI Overviews. Each trusts a different mix of sources, so Samura tracks all five separately every week and tunes the work to whichever is behind."),
    ("How long does GEO take to show results in Dubai?", "First citations for specific questions typically appear in three to six weeks, usually in Perplexity or ChatGPT search first. Broad questions such as 'best clinic in Dubai' take two to three months of consistent work, because they depend on other websites naming you."),
    ("Do you work in Arabic and English?", "Yes. The Establish and Dominate programs include an Arabic FAQ layer and bilingual business descriptions, because many UAE buyers ask AI assistants in Arabic and the engines answer Arabic questions from Arabic sources."),
    ("How do you measure GEO results?", "By AI citations and brand mentions: how many tracked buyer questions name you, in which engines, which sources the engines cite, plus AI referral visits in your analytics and inquiries that mention finding you through an AI assistant. You get the weekly log and can reproduce every prompt yourself."),
   ],
   "sections": [
    ("What is generative engine optimization?", "<p>Generative engines write their answers by reading a set of web pages and summarizing them. GEO is the work of being one of those pages, and of being described accurately when the engine summarizes you. It started as a 2023 research idea and is now the main way a Dubai business gets recommended in AI search.</p><p>The levers are the same as AEO: a clear entity, pages that answer questions with facts, structured data, and presence on the third-party sources each engine trusts. GEO puts extra weight on earned coverage, because generative engines lean heavily on articles, lists and directories when they choose who to name.</p>"),
    ("GEO for the Dubai and GCC market", "<p>Dubai buyers ask AI assistants in English and Arabic, and the engines answer each language from different sources. A GEO program for the UAE covers both, and covers the local sources the engines cite: UAE directories, regulator registers, Gulf business media, exhibitor lists from Dubai trade shows. Most global GEO agencies do not know these sources exist.</p>"),
    ("What our GEO service includes", "<ul><li>AI visibility audit across five generative engines, with AI share of voice</li><li>Entity optimization with organization, person and service structured data</li><li>Answer-first content: pages and guides written to be quoted, with FAQ schema</li><li>Brand mentions and citations: directories, reviews, press, comparison pages, llms.txt</li><li>Arabic and English coverage</li><li>Weekly prompt tracking with AI citation counts</li></ul>"),
    ("GEO vs AEO vs SEO", "<p>GEO and AEO describe the same work with a different emphasis: GEO on the engines that generate text, AEO on being the answer wherever answers appear, including Google AI Overviews and voice. SEO is the foundation both sit on. When an agency uses one term or another, ask which engines it tracks and how. <a href=\"/insights/what-is-geo-and-is-it-different-from-aeo\">Our plain-language explainer is here.</a></p>"),
   ],
 },
 "ai-seo-agency-dubai": {
   "title": "AI SEO Agency in Dubai: ChatGPT SEO, AI Search Optimization | Samura Consulting Group",
   "h1": "AI SEO agency in Dubai",
   "kicker": "ChatGPT SEO · AI search optimization",
   "meta": "AI SEO agency in Dubai: traditional SEO plus AI search optimization, so UAE businesses rank on Google and get recommended by ChatGPT. From AED 2,999.",
   "desc": "AI SEO agency in Dubai. Samura combines traditional SEO with AI search optimization so UAE businesses rank on Google and get recommended by ChatGPT, Gemini and Perplexity. Published pricing from AED 2,999.",
   "answer": "AI SEO, sometimes called ChatGPT SEO or AI search optimization, means doing search work with AI answers as the target instead of a list of links. Samura is an AI SEO agency in Dubai: we run the technical SEO, content and link building that Google and Bing still require, and on top of it the entity, structured data and citation work that gets a business named in ChatGPT, Gemini, Perplexity and Google AI Overviews. One program, both results, measured weekly.",
   "sections": [
    ("What an AI SEO agency does differently", "<p>A traditional SEO agency optimizes pages for keywords and builds links to rank them. An AI SEO agency does that and then asks a second question: when an AI engine reads this page, can it identify the business, quote the answer, and verify it elsewhere? That second question changes how pages are written, what structured data is added, and where the business needs to be listed.</p>"),
    ("How to rank on ChatGPT and AI search", "<ol><li>Make the business easy to identify: the same name, address, description and leadership on the website, Google Business Profile, LinkedIn and directories.</li><li>Publish pages that answer buyer questions in the first paragraph, with facts, prices and places.</li><li>Add structured data (JSON-LD) and an llms.txt file.</li><li>Get listed and reviewed on the sources each engine cites for your category.</li><li>Track real AI answers weekly and fix what the sources say is missing.</li></ol><p><a href=\"/insights/how-to-check-if-chatgpt-recommends-your-business\">Run the five-minute test yourself first.</a></p>"),
    ("What our AI SEO service includes", "<ul><li>Technical SEO and site speed fixes delivered by our engineering bench</li><li>Keyword and question research in the vocabulary your buyers use</li><li>Answer-first content and FAQ pages with schema</li><li>Link building and citations on UAE and sector sources</li><li>AI visibility audit and weekly prompt tracking across five engines</li><li>Arabic and English coverage</li></ul>"),
    ("Pricing", "<p>Published on the <a href=\"/pricing\">pricing page</a>: a one-time AI visibility audit at AED 1,999, programs from AED 2,999 for one month. Nothing renews automatically.</p>"),
   ],
 },
 "chatgpt-seo-services-dubai": {
   "title": "ChatGPT SEO Services in Dubai and the UAE | Samura Consulting Group",
   "h1": "ChatGPT SEO services in Dubai",
   "kicker": "ChatGPT SEO · get recommended by ChatGPT",
   "meta": "ChatGPT SEO services in Dubai and the UAE: Samura gets your business named when customers ask ChatGPT for a recommendation. Published pricing from AED 2,999.",
   "desc": "ChatGPT SEO services in Dubai and the UAE from Samura Consulting Group: entity setup, answer-first pages, structured data, citations and weekly tracking so your business is named when customers ask ChatGPT, ChatGPT search, Gemini and Perplexity. Published pricing from AED 2,999.",
   "answer": "ChatGPT SEO is the work of getting your business named when a customer asks ChatGPT, including ChatGPT search, for a recommendation. ChatGPT reads the Bing index and a short list of sources it trusts, so the work is specific: make your business easy to identify everywhere, publish pages that answer buyer questions with facts in the first paragraph, add structured data and an llms.txt file, and get listed on the directories and review sites ChatGPT cites for your category. Samura does this for Dubai and UAE businesses and shows you a weekly log of real ChatGPT answers. Programs from AED 2,999 a month, published in full.",
   "sections": [
    ("How ChatGPT decides which Dubai businesses to recommend", "<p>When a customer in Dubai asks ChatGPT for a dentist, a broker, a supplier or an agency, ChatGPT search runs web searches through Bing, reads the top results and a set of sources it already trusts, and writes one answer naming three to five businesses. It names the businesses it can identify clearly and quote confidently. A business that is described the same way on its website, Google Business Profile, LinkedIn and two or three directories, with prices, places and specialties in plain text, is easy to name. A business with a brochure site and no listings is not.</p><p><a href=\"/insights/how-chatgpt-decides-which-dubai-businesses-to-recommend\">How ChatGPT chooses, in detail.</a></p>"),
    ("What ChatGPT SEO services include", "<ul><li><strong>Bing and Google indexing</strong>: ChatGPT search reads the Bing index, so every page is submitted to Bing Webmaster Tools and IndexNow as well as Google, and checked weekly.</li><li><strong>Entity setup</strong>: one identical name, address, description and leadership across your website, Google Business Profile, LinkedIn, Crunchbase and the directories ChatGPT cites, with Organization and Person structured data.</li><li><strong>Answer-first pages</strong>: service and FAQ pages rewritten so the answer is in the first paragraph with facts, prices and places, plus FAQ schema and llms.txt.</li><li><strong>Citations</strong>: listings, reviews and mentions on the sources ChatGPT uses for your category in the UAE.</li><li><strong>Arabic and English</strong> coverage, because many UAE customers ask ChatGPT in Arabic.</li><li><strong>Weekly ChatGPT tracking</strong>: your buyer questions run every week, logged out, with screenshots, so you see exactly when your name appears.</li></ul>"),
    ("ChatGPT SEO versus traditional SEO", "<p>Traditional SEO gets a page into a list of ten links. ChatGPT SEO gets a business into the one answer ChatGPT writes. The two overlap, because ChatGPT reads the same web, but ChatGPT puts more weight on whether it can identify the business and verify it on other sites, and less on backlinks alone. Every Samura program includes the SEO foundation, because a page that cannot rank on Bing is rarely read by ChatGPT.</p>"),
    ("How long it takes and what it costs", "<p>First ChatGPT mentions for specific questions typically take three to six weeks; broad questions such as 'best clinic in Dubai' take two to three months of consistent work. Prices are published on the <a href=\"/pricing\">pricing page</a>: a one-time AI visibility audit at AED 1,999, Launch from AED 2,999 for one month, Establish from AED 7,999, Dominate from AED 10,999, Enterprise from AED 10,000 a month. Nothing renews automatically.</p><p><a href=\"/insights/how-to-check-if-chatgpt-recommends-your-business\">Check in five minutes whether ChatGPT recommends you today.</a></p>"),
   ],
   "faq": [
    ("What is ChatGPT SEO?", "ChatGPT SEO is the work of getting a business named when a customer asks ChatGPT for a recommendation. It covers how ChatGPT identifies the business, whether its pages can be quoted, structured data, and presence on the sources ChatGPT cites. It is the same work as answer engine optimization (AEO) and generative engine optimization (GEO), aimed at one engine."),
    ("How does ChatGPT find businesses in Dubai?", "ChatGPT search runs web searches through Bing and reads the top results plus sources it trusts: business websites, Google Business Profile, LinkedIn, directories, review sites and comparison articles. It names the businesses it can identify clearly and verify on more than one source. Being indexed by Bing is the first requirement."),
    ("How much do ChatGPT SEO services cost in Dubai?", "Samura publishes its prices: an AI visibility audit at AED 1,999, a one-month Launch program from AED 2,999, Establish for two months from AED 7,999, Dominate for three months from AED 10,999, and Enterprise from AED 10,000 a month. Nothing renews automatically. Many Dubai agencies do not publish ChatGPT SEO prices; ask for a written scope."),
    ("How long until ChatGPT recommends my business?", "For specific questions, such as a service plus an area, three to six weeks. For broad questions in a competitive UAE category, two to three months of consistent work, because those answers depend on other websites naming you. Samura shows a weekly log of real ChatGPT answers so you can see the change as it happens."),
    ("Can you guarantee my business will appear in ChatGPT?", "No, and no honest agency can. ChatGPT answers change with wording, location and the day. Samura commits to the work, a weekly log of real answers you can reproduce yourself, and a plain account of what moved and what did not."),
    ("Do you also cover Gemini, Perplexity and Google AI Overviews?", "Yes. The same program tracks ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews separately every week, because each engine trusts a slightly different set of sources. ChatGPT is usually the first to change for specific questions."),
    ("Do you work in Arabic and English?", "Yes. The Establish and Dominate programs include an Arabic FAQ layer and bilingual business descriptions, because many UAE customers ask ChatGPT in Arabic and it answers Arabic questions from Arabic sources."),
    ("Which industries in Dubai benefit most from ChatGPT SEO?", "Any category where customers ask ChatGPT for a recommendation: clinics and dental, real estate, hotels and restaurants, food suppliers, schools and tutors, car dealers, software, retail, consultancies and business setup firms. Samura publishes a guide series for each on the Industries page."),
   ],
 },
 "ai-visibility-audit": {
   "title": "AI Visibility Audit: See If ChatGPT Recommends Your Business | Samura Consulting Group",
   "h1": "AI visibility audit",
   "kicker": "AED 1,999 · credited against any program",
   "meta": "AI visibility audit, AED 1,999: 50 real buyer questions tested across five AI engines, who is named instead of you, and what to fix first. Dubai.",
   "desc": "An AI visibility audit tests 50 real buyer questions across ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews and shows whether your business is named, who is named instead, which sources the engines cite, and what to fix first. AED 1,999, Dubai.",
   "answer": "An AI visibility audit answers one question: when your customers ask AI assistants for a business like yours, are you named? Samura runs 50 real buyer prompts for your category across ChatGPT, Claude, Gemini, Perplexity and Google AI Overviews, logged out, and records who is named, which sources each engine cites, and your AI share of voice. You get a prioritized fix list and a 30-minute walkthrough. AED 1,999, credited in full against any program within 30 days.",
   "sections": [
    ("What the audit checks", "<ol><li><strong>Current visibility</strong>: 50 prompts, five engines, dated screenshots; named or not, who instead, which sources.</li><li><strong>Entity</strong>: can the engines identify your business, and do all sources agree on name, address, description and people.</li><li><strong>Pages</strong>: can your service pages be quoted; titles, first paragraphs, structured data, llms.txt.</li><li><strong>Sources</strong>: are you on the directories, review sites, lists and media the engines cite for your category.</li><li><strong>Competitors</strong>: which businesses are named instead of you, and why.</li></ol>"),
    ("What you receive", "<ul><li>A report with the prompt log, competitor citation map and AI share of voice</li><li>A fix list in order of effect, each item small enough to do in a week</li><li>A 30-minute walkthrough with the Managing Partner</li><li>The audit fee credited against Launch, Establish or Dominate within 30 days</li></ul>"),
    ("How to run a basic version yourself", "<p>Open ChatGPT, Gemini, Perplexity and Claude in a private window, type five questions a customer would ask, and note whether you are named, who is named instead, and which sources appear. <a href=\"/insights/how-to-check-if-chatgpt-recommends-your-business\">The five-minute test is here.</a> The paid audit does the same with 50 prompts, five engines, a source map and a plan.</p>"),
    ("Who it is for", "<p>Any Dubai or UAE business that wants to know where it stands before spending on AEO: clinics, real estate agencies, food suppliers, schools, car dealers, software companies, retailers. Businesses we meet at Dubai events this season can request a <a href=\"/check\">complimentary short version</a>.</p>"),
   ],
 },
}
for slug, sv in SERVICES.items():
    url = f'{SITE}/{slug}'
    faqs = sv.get("faq", COMMON_FAQ)
    ld = [{"@context":"https://schema.org","@type":"Service","name":sv["h1"],"serviceType":sv["h1"],"areaServed":[{"@type":"City","name":"Dubai"},{"@type":"Country","name":"United Arab Emirates"}],
           "provider":{"@type":"Organization","name":"Samura Consulting Group","url":SITE},"url":url,"description":sv["desc"],
           "offers":{"@type":"Offer","priceCurrency":"AED","price":("1999" if slug == "ai-visibility-audit" else "2999"),"url":f"{SITE}/pricing"}},
          {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},
          {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},{"@type":"ListItem","position":2,"name":sv["h1"],"item":url}]}]
    body = ''.join(f'<h2>{html.escape(h)}</h2>{b}' for h,b in sv["sections"])
    body += '<h2>Frequently asked</h2>' + ''.join(f'<details{" open" if j==0 else ""}><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for j,(q,a) in enumerate(faqs))
    body += '<p style="margin-top:2rem"><a class="btn btn-primary" href="/#contact">Get a written quote</a> &nbsp; <a class="btn btn-outline" href="/pricing">See all prices</a></p>'
    page = head(sv["title"].split(" | ")[0], sv.get("meta", sv["desc"]), url, ld).replace('content="article"', 'content="website"') + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>{html.escape(sv["kicker"])}</span></div>
  <h1>{html.escape(sv["h1"])}</h1>
  <p class="lead" style="margin-top:.8rem">{html.escape(sv["kicker"])} · Samura Consulting Group, Business Bay, Dubai</p>
</div></header>
<main><div class="wrap art">
  <div class="answer"><span class="lbl">The short answer</span>{html.escape(sv["answer"])}</div>
  <div class="body">{body}</div>
</div></main>
""" + footer + tail
    page = page.replace(f'<title>{html.escape(sv["title"].split(" | ")[0])} | Samura</title>', f'<title>{html.escape(sv["title"])}</title>')
    open(f'{DIST}/{slug}.html', 'w', encoding='utf-8', newline='\n').write(page)

# --- Standalone pricing page and individual case studies ---
PLANS = [
 ("AI Visibility Audit", "AED 1,999", "one-time", "Businesses that want to see the gap before spending on it",
  ["50 prompts tested on ChatGPT, Gemini, Perplexity, Claude and Google AI Overviews", "Competitor citation map: who is named instead of you, and which sources each engine cites", "Priority action plan in order of effect", "30-minute walkthrough", "Credited in full against any program within 30 days"]),
 ("Launch", "from AED 2,999", "1 month", "A focused push on one service in Dubai",
  ["Audit included", "Entity setup: identical name, address, description and founders across Google, LinkedIn, directories and the site", "6 pages rebuilt with answer-first copy and schema", "6 answer-first articles with FAQ blocks", "Weekly prompt tracking, shared as a live log"]),
 ("Establish", "from AED 7,999", "2 months (AED 3,999 a month)", "Businesses in a competitive category",
  ["Everything in Launch", "Citation and directory building on the sources the engines cite for your category", "20 articles plus an Arabic FAQ layer", "Competitor displacement plan: the questions where you can replace a named competitor first"]),
 ("Dominate", "from AED 10,999", "3 months (AED 3,666 a month)", "Owning your category across the UAE",
  ["Everything in Establish", "Press and PR placements", "30 or more articles across the full question cluster", "Monthly review with a director"]),
 ("Enterprise", "from AED 10,000 a month", "quoted per program", "Multi-location, multi-language or multi-brand groups",
  ["Scope, team and reporting agreed per brand or location", "Arabic and English programs run in parallel", "Dedicated director and weekly reporting"]),
]
PRICING_FAQ = [
 ("How much does AEO cost in Dubai?", "Published AEO packages in Dubai run from roughly AED 3,000 to AED 10,000 a month for small and mid-sized businesses. Samura's programs start at AED 2,999 for one month, AED 7,999 for two months and AED 10,999 for three months, with a one-time AED 1,999 audit. Enterprise programs are quoted from AED 10,000 a month."),
 ("Are these the final prices?", "They are starting points, exclusive of VAT. The final price is confirmed in a written proposal after a short call, and it moves only if the scope does, for example more locations, Arabic content or a second brand."),
 ("Is there a minimum contract?", "No. Programs are one, two or three months, paid in advance, and nothing renews automatically. Longer programs have a lower monthly rate because the work compounds."),
 ("Why is the audit credited against a program?", "Because the audit is the first step of every program anyway. If you buy the audit first and start Launch, Establish or Dominate within 30 days, you pay the difference, not both."),
 ("What do I get every week?", "A log of real AI answers for your tracked prompts across the engines in your program, showing whether you were named, who was named instead, and which sources each engine cited. You can run any prompt yourself to check it."),
 ("Do you guarantee a position on ChatGPT?", "No, and no agency honestly can. AI answers change with the wording of the question, the user's location and the day. We commit to the work, the weekly log and a plain account of what moved and what did not."),
]
def plan_card(name, price, term, for_, items):
    lis = ''.join(f'<li>{html.escape(i)}</li>' for i in items)
    return ('<div style="border:1px solid #DCE4F0;border-radius:14px;padding:1.3rem 1.4rem;background:#fff">'
            f'<div style="font-family:var(--display);font-weight:800;font-size:1.1rem;color:var(--ink)">{html.escape(name)}</div>'
            f'<div style="font-family:var(--display);font-weight:800;font-size:1.6rem;color:var(--royal);margin:.3rem 0 .1rem">{html.escape(price)}</div>'
            f'<div style="color:var(--muted);font-size:.9rem;font-weight:600">{html.escape(term)}</div>'
            f'<p style="margin:.7rem 0 .4rem;font-weight:600">For: {html.escape(for_)}</p>'
            f'<ul style="margin:0;padding-left:1.1rem">{lis}</ul></div>')
def td(x): return f'<td style="padding:.6rem .4rem">{x}</td>'
ROWS = [("AI Visibility Audit","AED 1,999","One-time","Credited against any program"),("Launch","from AED 2,999","1 month","AED 2,999"),("Establish","from AED 7,999","2 months","AED 3,999"),("Dominate","from AED 10,999","3 months","AED 3,666"),("Enterprise","from AED 10,000 a month","Quoted","From AED 10,000")]
table = ('<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:.95rem"><thead><tr style="text-align:left;border-bottom:2px solid #DCE4F0">'
         + ''.join(f'<th style="padding:.6rem .4rem">{h}</th>' for h in ("Program","Price","Term","Monthly equivalent")) + '</tr></thead><tbody>'
         + ''.join('<tr style="border-bottom:1px solid #E7ECF4">' + ''.join(td(c) for c in r) + '</tr>' for r in ROWS) + '</tbody></table></div>')
pr_url = f'{SITE}/pricing'
pr_title = "AEO agency pricing in Dubai: Samura's packages and what each includes"
pr_desc = "Published prices for answer engine optimization in Dubai: a one-time AED 1,999 audit, programs from AED 2,999 a month, and what every package includes. No lock-in, nothing renews on its own."
def _price_num(p): return p.replace('from ','').replace('AED ','').replace(',','').split(' ')[0]
pr_ld = [
 {"@context":"https://schema.org","@type":"WebPage","name":pr_title,"url":pr_url,"description":pr_desc,
  "publisher":{"@type":"Organization","name":"Samura Consulting Group","url":SITE}},
 {"@context":"https://schema.org","@type":"OfferCatalog","name":"Samura AEO programs","url":pr_url,
  "itemListElement":[{"@type":"Offer","name":n,"price":_price_num(p),"priceCurrency":"AED","description":f"{t}. For {f_}.","url":pr_url,"seller":{"@type":"Organization","name":"Samura Consulting Group"}} for n,p,t,f_,_ in PLANS]},
 {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in PRICING_FAQ]},
]
pr_body = (
 '<p class="lead" style="font-size:1.1rem;font-weight:500">Every price we charge is on this page. Most AEO agencies in Dubai do not publish prices; we do, because a buyer comparing five proposals should be able to see the numbers before the first call. All prices are in UAE dirhams, exclusive of VAT, and nothing renews automatically.</p>'
 '<h2>The packages</h2><div style="display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));margin:1rem 0 1.6rem">' + ''.join(plan_card(*p) for p in PLANS) + '</div>'
 '<h2>Prices at a glance</h2>' + table +
 '<h2>How to choose</h2>'
 '<p><strong>Not sure the problem is real?</strong> Buy the audit. It shows you up to fifty real AI answers for your category with your competitors\' names in them, which is usually enough to decide.</p>'
 '<p><strong>One service, one city, a few competitors?</strong> Launch. A month is enough to fix identity, rebuild the core pages and see first appearances for specific questions.</p>'
 '<p><strong>Crowded category (clinics, real estate, agencies, software)?</strong> Establish. The second month is where directory and citation work starts paying, and where Arabic questions get covered.</p>'
 '<p><strong>Want the category across the UAE, not just Dubai?</strong> Dominate, which adds press placements and a full question cluster.</p>'
 '<h2>What is never included</h2>'
 '<p>Fake reviews, paid links from unrelated sites, content stuffed with your name, or guarantees of a position. All four produce a screenshot and all four get a business discounted by the engines within months.</p>'
 '<h2>Frequently asked</h2>' + ''.join(f'<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>' for q,a in PRICING_FAQ) +
 '<p style="margin-top:2rem"><a class="btn btn-primary" href="/#contact">Get a written quote</a> &nbsp; <a class="btn btn-outline" href="/#contact">Order the audit</a></p>'
)
page = head(pr_title, pr_desc, pr_url, pr_ld).replace('content="article"', 'content="website"') + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>Pricing</span></div>
  <h1>AEO agency pricing in Dubai</h1>
  <p class="lead" style="margin-top:.8rem">Samura's packages, published in full. From AED 2,999 a month. Updated 24 October 2026.</p>
</div></header>
<main><div class="wrap art"><div class="body">{pr_body}</div></div></main>
""" + footer + tail
open(f'{DIST}/pricing.html', 'w', encoding='utf-8', newline='\n').write(page)

CASES = [
 ("konception-designs", "Konception Designs: 120% more inbound sourcing inquiries from three countries", "2025-09-01",
  "How an apparel sourcing company with offices in India, Dubai, London and Los Angeles became visible to international buyers searching for manufacturing partners, and grew inbound inquiries 120%.",
  "Apparel sourcing and product development · India, Dubai, London, Los Angeles",
  [("+120%","Inbound sourcing inquiries"),("3 countries","Where the site now ranks"),("5 offices","Across 4 countries"),("B2B export","Program type")],
  """
<h2>The client</h2>
<p>Konception Designs is an apparel sourcing and product development company with three factories, 980 machines and offices in Gurugram, Mumbai, Dubai, London and Los Angeles. It supplies finished garments and home goods to global retailers and high-end designers.</p>
<h2>The problem</h2>
<p>Buyers at international brands search for manufacturing partners by capability and country. Konception was invisible for those searches outside India, so sourcing inquiries came almost entirely through trade shows and personal networks.</p>
<h2>What we did</h2>
<ul>
<li>Rebuilt the site structure around capabilities: product development, vendor selection, quality assurance, shipping</li>
<li>Country-specific landing pages for the UAE, UK and US markets with local contact details and schema</li>
<li>Content answering the questions sourcing managers actually ask: minimums, lead times, compliance, categories</li>
<li>Listings on international sourcing directories and trade platforms, with a consistent entity description</li>
<li>Tracking of inquiry source so the client could see which market each lead came from</li>
</ul>
<h2>Outcome</h2>
<p>Inbound sourcing inquiries rose 120% and the site now ranks for manufacturing-partner searches in three countries, giving the sales team a pipeline that no longer depends on the trade-show calendar.</p>
<h2>What it means for AI search</h2>
<p>Sourcing managers now ask ChatGPT and Perplexity for manufacturers by country and capability. The capability pages, the plain answers on minimums and lead times, and the directory listings built for this program are exactly what those engines quote. A B2B exporter in the UAE that wants to be named in AI answers starts from the same list.</p>
"""),
]
os.makedirs(f'{DIST}/case-studies', exist_ok=True)
for slug, ttl, date, desc, meta, kpis, body in CASES:
    url = f'{SITE}/case-studies/{slug}'
    ld = [{"@context":"https://schema.org","@type":"Article","headline":ttl,"description":desc,"url":url,"datePublished":date,"dateModified":"2026-10-24",
           "author":{"@type":"Organization","name":"Samura Consulting Group","url":SITE},
           "publisher":{"@type":"Organization","name":"Samura Consulting Group","url":SITE,"logo":{"@type":"ImageObject","url":f"{SITE}/assets/logo.png"}},
           "mainEntityOfPage":url,"image":f"{SITE}/assets/og-image.png"},
          {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
           {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},{"@type":"ListItem","position":2,"name":"Case studies","item":SITE+"/case-studies"},{"@type":"ListItem","position":3,"name":ttl,"item":url}]}]
    kp = ''.join(f'<div style="border:1px solid #DCE4F0;border-radius:12px;padding:.9rem 1rem;background:#fff"><b style="display:block;font-family:var(--display);font-size:1.5rem;color:var(--royal)">{html.escape(b)}</b><small style="color:var(--muted);font-weight:600">{html.escape(sm)}</small></div>' for b,sm in kpis)
    page = head(ttl, desc, url, ld) + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><a href="/case-studies">Case studies</a><span>/</span><span>{html.escape(slug.replace('-',' ').title())}</span></div>
  <h1>{html.escape(ttl)}</h1>
  <p class="lead" style="margin-top:.8rem;color:var(--muted)">{html.escape(meta)}</p>
</div></header>
<main><div class="wrap art">
  <div style="display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:0 0 1.6rem">{kp}</div>
  <div class="body">{body}
  <p style="margin-top:2rem"><a class="btn btn-primary" href="/#contact">Want results like these? Start with a call</a> &nbsp; <a class="btn btn-outline" href="/case-studies">All case studies</a></p></div>
</div></main>
""" + footer + tail
    open(f'{DIST}/case-studies/{slug}.html', 'w', encoding='utf-8', newline='\n').write(page)



# --- /check event landing page ---
ck_url = f'{SITE}/check'
ck_title = "Free AI visibility check for businesses we meet at Dubai events"
ck_desc = "Met Samura at an event? Tell us your company and the question your customer would ask an AI assistant. Within three working days you get a report on whether ChatGPT, Gemini and Perplexity name you, who they name instead, and what to fix."
ck_ld = [{"@context":"https://schema.org","@type":"WebPage","name":ck_title,"url":ck_url,"description":ck_desc,"publisher":{"@type":"Organization","name":"Samura Consulting Group","url":SITE}},
         {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
          {"@type":"Question","name":"What do I get from the free AI visibility check?","acceptedAnswer":{"@type":"Answer","text":"A short report within three working days: whether ChatGPT, Gemini, Perplexity and Claude name your business for five questions your customers ask, who they name instead, which sources each engine cites, and the first three things to fix."}},
          {"@type":"Question","name":"Is there any cost or obligation?","acceptedAnswer":{"@type":"Answer","text":"None. The check is complimentary for businesses we meet during Dubai's events season, limited to twenty companies. The report is yours whether or not you work with us."}},
          {"@type":"Question","name":"What happens after the report?","acceptedAnswer":{"@type":"Answer","text":"We offer a 30-minute call to walk through it. If you want the gaps fixed, the full AI Visibility Audit (AED 1,999) or a Launch program (from AED 2,999) picks up from the report."}}]}]
ck_body = f"""
<p class="lead" style="font-size:1.1rem;font-weight:500">Good to meet you. Fill this in and within three working days you will have a report showing what ChatGPT, Gemini, Perplexity and Claude say when your customers ask for a business like yours in the UAE, who they name instead of you, and what to do about it. No cost, no obligation, limited to twenty companies this season.</p>
<form id="check" novalidate style="display:grid;gap:1rem;margin:1.6rem 0;max-width:640px">
  <label style="display:grid;gap:.3rem;font-weight:600">Your name<input id="c-name" name="name" type="text" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <label style="display:grid;gap:.3rem;font-weight:600">Company<input id="c-co" name="company" type="text" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <label style="display:grid;gap:.3rem;font-weight:600">Website<input id="c-web" name="website" type="text" placeholder="www.yourcompany.com" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <label style="display:grid;gap:.3rem;font-weight:600">WhatsApp number<input id="c-ph" name="phone" type="tel" placeholder="+971 5x xxx xxxx" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <label style="display:grid;gap:.3rem;font-weight:600">Email<input id="c-em" name="email" type="email" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <label style="display:grid;gap:.3rem;font-weight:600">The question your best customer would ask an AI assistant<textarea id="c-q" name="customer_question" rows="3" placeholder="For example: best dental clinic in Jumeirah that accepts Daman" required style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></textarea></label>
  <label style="display:grid;gap:.3rem;font-weight:600">Where did we meet?<input id="c-ev" name="event" type="text" placeholder="Gulfood Manufacturing, Growtech, Dubai AI Festival..." style="padding:.8rem;border:1px solid #CBD5E1;border-radius:10px;font:inherit"></label>
  <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
  <button class="btn btn-primary" type="submit" style="justify-self:start">Send my details</button>
  <div class="ok" id="c-ok" style="display:none;padding:1rem;border-radius:10px;background:#EAF3FF;color:var(--navy);font-weight:600">Thank you. Your report will reach you within three working days. If you would rather talk now, WhatsApp us on +971 55 584 8267.</div>
  <div id="c-err" style="display:none;padding:1rem;border-radius:10px;background:#FFF1F0;color:#8A1C1C;font-weight:600">That did not send. Please WhatsApp your details to +971 55 584 8267 and we will take it from there.</div>
</form>
<h2>What the check covers</h2>
<ul>
<li>Five questions your customers ask, run in ChatGPT, Gemini, Perplexity and Claude, logged out</li>
<li>Whether you are named, who is named instead, and the sources each engine cites</li>
<li>The first three things to fix, in order of effect</li>
<li>A 30-minute walkthrough call if you want one</li>
</ul>
<h2>Frequently asked</h2>
<h3>What do I get from the free AI visibility check?</h3><p>A short report within three working days: whether the four engines name your business for five customer questions, who they name instead, which sources each engine cites, and the first three things to fix.</p>
<h3>Is there any cost or obligation?</h3><p>None. The check is complimentary for businesses we meet during Dubai's events season, limited to twenty companies. The report is yours whether or not you work with us.</p>
<h3>What happens after the report?</h3><p>We offer a 30-minute call to walk through it. If you want the gaps fixed, the full <a href="/pricing">AI Visibility Audit or a Launch program</a> picks up from the report.</p>
<script>
(function(){{var f=document.getElementById('check');if(!f)return;f.addEventListener('submit',function(e){{e.preventDefault();
var g=function(id){{return (document.getElementById(id).value||'').trim();}};
var ok=true;['c-name','c-co','c-web','c-ph','c-em','c-q'].forEach(function(id){{var el=document.getElementById(id);if(!g(id)){{el.style.borderColor='#D14343';ok=false;}}else{{el.style.borderColor='#CBD5E1';}}}});
if(!ok)return;var btn=f.querySelector('button');btn.disabled=true;btn.textContent='Sending...';
var w=g('c-web');if(w&&!/^https?:\\/\\//i.test(w))w='https://'+w;
fetch('https://api.web3forms.com/submit',{{method:'POST',headers:{{'Content-Type':'application/json',Accept:'application/json'}},body:JSON.stringify({{access_key:'ff2a2e87-c12d-4ced-acd8-467f85574bb2',subject:'AI check request: '+g('c-co')+' ('+(g('c-ev')||'event')+')',from_name:'Samura /check page',name:g('c-name'),company:g('c-co'),website:w,phone:g('c-ph'),email:g('c-em'),customer_question:g('c-q'),event:g('c-ev'),type:'ai-check',page:location.href,botcheck:''}})}}).then(function(r){{return r.json();}}).then(function(j){{btn.disabled=false;btn.textContent='Send my details';if(j&&j.success){{document.getElementById('c-ok').style.display='block';f.reset();}}else{{document.getElementById('c-err').style.display='block';}}}}).catch(function(){{btn.disabled=false;btn.textContent='Send my details';document.getElementById('c-err').style.display='block';}});
}});}})();
</script>
"""
page = head(ck_title, ck_desc, ck_url, ck_ld).replace('content="article"', 'content="website"') + nav_plain + f"""
<header class="art-head"><div class="wrap art">
  <div class="crumbs"><a href="/">Home</a><span>/</span><span>AI visibility check</span></div>
  <h1>Met us at an event? Get your free AI visibility check.</h1>
  <p class="lead" style="margin-top:.8rem">Twenty complimentary checks this season for businesses we meet in Dubai. Three working days, no cost, no obligation.</p>
</div></header>
<main><div class="wrap art"><div class="body">{ck_body}</div></div></main>
""" + footer + tail
open(f'{DIST}/check.html', 'w', encoding='utf-8', newline='\n').write(page)

# --- Sitemap ---
today = datetime.date.today().isoformat()
urls = [(SITE + '/', 'weekly', '1.0'), (SITE + '/case-studies', 'monthly', '0.8'), (SITE + '/case-studies/konception-designs', 'monthly', '0.7'), (SITE + '/pricing', 'monthly', '0.9'), (SITE + '/check', 'monthly', '0.6'), (SITE + '/industries', 'weekly', '0.8')] + [(f'{SITE}/{k}', 'monthly', '0.9') for k in SERVICES] + [(f'{SITE}/insights/{k}', 'weekly', '0.8') for k in HUBS] + [ (SITE + '/insights', 'weekly', '0.8'), (SITE + '/privacy', 'yearly', '0.2'), (SITE + '/terms', 'yearly', '0.2')] + \
       [(f'{SITE}/insights/{a["slug"]}', 'monthly', '0.7') for a in ARTICLES]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     ''.join(f'<url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n' for u, c, p in urls) + '</urlset>\n'
open(f'{DIST}/sitemap.xml', 'w', encoding='utf-8', newline='\n').write(sm)

# --- llms.txt ---
l = open(f'{DIST}/llms.txt', encoding='utf-8').read()
l = re.sub(r'## Pages\n.*?\n\n', '', l, flags=re.S)
pages = '## Pages\n- Home: ' + SITE + '/\n- Pricing (all packages): ' + SITE + '/pricing\n' + ''.join(f'- {v["h1"]}: {SITE}/{k}\n' for k, v in SERVICES.items()) + '- Industries we cover: ' + SITE + '/industries\n- Free AI visibility check for event contacts: ' + SITE + '/check\n- Case studies: ' + SITE + '/case-studies\n- Case study, Konception Designs (+120% inquiries): ' + SITE + '/case-studies/konception-designs\n- Insights: ' + SITE + '/insights\n' + ''.join(f'- Guide series, {h["h1"]}: {SITE}/insights/{k}\n' for k, h in HUBS.items()) + \
        ''.join(f'- {a["title"]}: {SITE}/insights/{a["slug"]}\n' for a in ARTICLES) + '\n'
l = l.replace('## Contact', pages + '## Contact')
open(f'{DIST}/llms.txt', 'w', encoding='utf-8', newline='\n').write(l)

# --- Homepage insights cards link to real articles ---
h = index_html
start = h.index('<div class="grid3">', h.index('id="insights"'))
end = h.index('</div>\n</div></section>', start)
cards = '<div class="grid3">\n' + '\n'.join(
    f'    <a class="card" href="/insights/{a["slug"]}" style="text-decoration:none"><div class="meta" style="font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;font-family:var(--display);font-weight:700;color:var(--royal)">{a["category"]}</div><h3>{html.escape(a["title"])}</h3><p>{html.escape(a["description"][:110]).rsplit(" ",1)[0]}...</p></a>'
    for a in BY_DATE[:3]) + '\n  '
h = h[:start] + cards + h[end:]
if 'href="/insights">See all insights' not in h:
    h = h.replace('</div>\n</div></section>\n\n<section><div class="wrap">\n  <div class="sec-head">\n    <div class="kicker" data-text="FAQ">',
                  '</div>\n  <div class="center"><a class="btn btn-outline" href="/insights">See all insights</a></div>\n</div></section>\n\n<section><div class="wrap">\n  <div class="sec-head">\n    <div class="kicker" data-text="FAQ">', 1)
h = h.replace('<li><a href="#insights">Insights</a></li>', '<li><a href="/insights">Insights</a></li>')
open(f'{DIST}/index.html', 'w', encoding='utf-8', newline='\n').write(h)
print('built', len(ARTICLES), 'articles')

# Final guard over every generated page and the hand-edited sources
import glob as _glob
for _f in sorted(set([f'{DIST}/index.html', f'{DIST}/case-studies.html', f'{DIST}/llms.txt'] + _glob.glob(f'{DIST}/*.html') + _glob.glob(f'{DIST}/insights/*.html') + _glob.glob(f'{DIST}/case-studies/*.html'))):
    _t = open(_f, encoding='utf-8').read()
    assert '—' not in _t and '–' not in _t, f"dash in {_f}"
    check_american(_t, os.path.relpath(_f, DIST))
print('spelling and dash checks passed')
