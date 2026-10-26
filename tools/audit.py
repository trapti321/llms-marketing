"""Static technical SEO audit for llmsmarketing.com. Run: python3 tools/audit.py"""
import glob
import html
import json
import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
SITE = "https://llmsmarketing.com"
SKIP = ("dist/", "node_modules/", "public/", "tools/")

issues = defaultdict(list)
pages = {}
for f in sorted(glob.glob("**/index.html", recursive=True)):
    if f.startswith(SKIP):
        continue
    path = "/" + f[: -len("index.html")]
    pages[path] = open(f, encoding="utf-8").read()


def exists(href):
    href = href.split("#")[0].split("?")[0]
    if not href:
        return True
    return os.path.exists("." + href + ("index.html" if href.endswith("/") else "")) or os.path.exists("public" + href)


titles, descs, inbound = defaultdict(list), defaultdict(list), defaultdict(set)
redirects = set()
for path, s in pages.items():
    add = lambda msg: issues[path].append(msg)
    if 'http-equiv="refresh"' in s:
        redirects.add(path)
        if "noindex" not in s:
            add("redirect page without noindex")
        continue
    head = s.split("</head>")[0]
    if re.search(r'<meta name="robots" content="[^"]*noindex', head):
        continue
    if not re.search(r'<html lang="[a-z-]+"', s):
        add("missing <html lang>")
    if 'name="viewport"' not in head:
        add("missing viewport")
    if "G-8FEJCYBHWX" not in head:
        add("missing GA4 tag")
    t = re.search(r"<title>(.*?)</title>", head, re.S)
    if not t:
        add("missing <title>")
    else:
        tt = html.unescape(t.group(1).strip())
        titles[tt].append(path)
        if not 25 <= len(tt) <= 65:
            add(f"title length {len(tt)}: {tt}")
    d = re.search(r'<meta name="description" content="([^"]*)"', head)
    if not d:
        add("missing meta description")
    else:
        dd = html.unescape(d.group(1))
        descs[dd].append(path)
        if not 70 <= len(dd) <= 165:
            add(f"description length {len(dd)}")
    c = re.search(r'<link rel="canonical" href="([^"]*)"', head)
    if not c:
        add("missing canonical")
    elif c.group(1) != SITE + path:
        add(f"canonical mismatch: {c.group(1)}")
    robots = re.search(r'<meta name="robots" content="([^"]*)"', head)
    if robots and "noindex" in robots.group(1) and path not in ("/thank-you/",):
        add(f"noindex: {robots.group(1)}")
    for prop in ("og:title", "og:description", "og:image", "og:url"):
        if f'property="{prop}"' not in head:
            add(f"missing {prop}")
    og = re.search(r'property="og:image" content="([^"]*)"', head)
    if og and og.group(1).startswith(SITE) and not exists(og.group(1)[len(SITE):]):
        add(f"og:image file missing: {og.group(1)}")
    if 'name="twitter:card"' not in head:
        add("missing twitter:card")
    for m in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        try:
            json.loads(m)
        except json.JSONDecodeError as e:
            add(f"invalid JSON-LD: {e}")
    body = s.split("<body", 1)[1] if "<body" in s else s
    h1 = len(re.findall(r"<h1[\s>]", body))
    if h1 != 1:
        add(f"{h1} <h1> tags")
    levels = [int(x) for x in re.findall(r"<h([1-6])[\s>]", body.split("<footer")[0])]
    for a, b in zip(levels, levels[1:]):
        if b > a + 1:
            add(f"heading jump h{a} -> h{b}")
            break
    for img in re.findall(r"<img\b[^>]*>", body):
        if "alt=" not in img:
            add(f"img without alt: {img[:80]}")
        if "width=" not in img or "height=" not in img:
            add(f"img without width/height: {img[:80]}")
        src = re.search(r'src="([^"]+)"', img)
        if src and src.group(1).startswith("/") and not exists(src.group(1)):
            add(f"missing image file: {src.group(1)}")
    ids = re.findall(r'\sid="([^"]+)"', body)
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        add(f"duplicate ids: {sorted(dup)[:5]}")
    for href in set(re.findall(r'href="([^"]+)"', body)):
        if href.startswith("/") and not href.startswith("//"):
            if not exists(href):
                add(f"broken internal link: {href}")
            else:
                inbound[href.split("#")[0].split("?")[0]].add(path)
        elif href.startswith("#") and len(href) > 1 and href[1:] not in ids:
            add(f"anchor without target: {href}")
        elif href.startswith("http://"):
            add(f"insecure link: {href}")
    for a in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', body):
        if "noopener" not in a:
            add(f"target=_blank without noopener: {a[:80]}")
    if re.search(r'src="http://', body):
        add("mixed content src")

for t, ps in titles.items():
    if len(ps) > 1:
        issues["(site)"].append(f"duplicate title '{t}': {ps}")
for d, ps in descs.items():
    if len(ps) > 1:
        issues["(site)"].append(f"duplicate description on {ps}")

# sitemap coverage
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
for sm in ("sitemap.xml", "public/sitemap.xml"):
    locs = [e.text.strip() for e in ET.parse(sm).getroot().findall("s:url/s:loc", ns)]
    if len(locs) != len(set(locs)):
        issues["(site)"].append(f"{sm}: duplicate URLs")
    paths = {l[len(SITE):] for l in locs}
    for p in paths - set(pages):
        issues["(site)"].append(f"{sm}: URL with no page {p}")
    for p in set(pages) - paths - redirects - {"/thank-you/"}:
        issues["(site)"].append(f"{sm}: page missing from sitemap {p}")
    for p in paths & (redirects | {"/thank-you/"}):
        issues["(site)"].append(f"{sm}: non-indexable page in sitemap {p}")
if open("sitemap.xml").read() != open("public/sitemap.xml").read():
    issues["(site)"].append("sitemap.xml and public/sitemap.xml differ")
if open("llms.txt").read() != open("public/llms.txt").read():
    issues["(site)"].append("llms.txt and public/llms.txt differ")
for u in re.findall(r"\((https://llmsmarketing\.com[^)]*)\)", open("llms.txt").read()):
    if not exists(u[len(SITE):] or "/"):
        issues["(site)"].append(f"llms.txt broken link {u}")

# vite inputs
v = open("vite.config.js").read()
inputs = set(re.findall(r"resolve\(__dirname, '([^']+)'\)", v))
for path in pages:
    f = (path[1:] + "index.html") if path != "/" else "index.html"
    if f not in inputs:
        issues["(site)"].append(f"page missing from vite.config.js: {f}")

# orphans
for path in pages:
    if path in ("/", "/thank-you/") or path in redirects:
        continue
    if not (inbound[path] - {path}):
        issues["(site)"].append(f"orphan page (no internal links in): {path}")

total = sum(len(v) for v in issues.values())
print(f"pages: {len(pages)} (redirects {len(redirects)}), issues: {total}")
for p, msgs in sorted(issues.items()):
    for m in msgs:
        print(f"{p}: {m}")
