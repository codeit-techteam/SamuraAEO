#!/usr/bin/env python3
"""Tell Bing (IndexNow, and the Bing Webmaster API if BING_API_KEY is set) about new or changed URLs.
Usage:  python3 tools/notify.py URL [URL ...]
        python3 tools/notify.py --file urls.txt
Google has no equivalent API for ordinary pages; it reads sitemap.xml on its own.
"""
import sys, os, json, urllib.request, urllib.parse
KEY = '32652ca172d2a57a4b51ba12e38ed96e'          # must match /<KEY>.txt at the site root
HOST = 'www.samuraconsulting.com'
urls = sys.argv[1:]
if urls[:1] == ['--file']:
    urls = [l.strip() for l in open(urls[1]) if l.strip().startswith('http')]
if not urls:
    sys.exit(__doc__)
# IndexNow: one request, many URLs
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow:', r.status, 'ok' if r.status in (200, 202) else r.read()[:200])
except Exception as e:
    print('IndexNow failed:', e)
# Bing Webmaster URL submission API (optional)
api = os.environ.get('BING_API_KEY')
if api:
    ep = f'https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch?apikey={api}'
    body = json.dumps({"siteUrl": f"https://{HOST}/", "urlList": urls}).encode()
    req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print('Bing API:', r.status, r.read()[:200])
    except Exception as e:
        print('Bing API failed:', e)
else:
    print('Bing API skipped (set BING_API_KEY to enable). Paste the URLs in Bing Webmaster > URL Submission instead.')
print('\n'.join(urls))
