"""SEO by City: registry, page builder and site wiring for /seo-by-city/.

Launching a new city page:
  1. Write the page content (everything between </header> and <footer>) to a main.html file
     and the head data to a meta.json file (title, desc, og_title, og_desc, image, image_alt, ld).
  2. Add the city to CITIES below.
  3. python3 tools/cities.py build <slug> main.html meta.json
  4. python3 tools/cities.py sync   (hub directory, ItemList, "More cities" blocks,
     sitemaps, llms.txt and vite inputs), then run nav.py, silo.py and audit.py.

Every city page must be genuinely local (own data, neighborhoods, rules and search demand).
Never publish a page that only swaps the city name: Google treats that as doorway abuse.
"""
import html, json, os, re, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://llmsmarketing.com"
HUB = "/seo-by-city/"
TEMPLATE = "seo-for-hvac/index.html"

REGIONS = ["Pacific & Northwest", "Mountain & Southwest", "Texas & South Central", "Midwest", "Southeast", "Northeast & Mid-Atlantic"]

# slug -> page lives at /seo-by-city/<slug>/ unless "url" is given.
CITIES = [
    {"slug": "seattle-seo-agency", "city": "Seattle", "state": "WA", "region": "Pacific & Northwest",
     "blurb": "Seattle and the Eastside: neighborhood pages, the Lake Washington split and Washington's health data law."},
    {"slug": "chicago-seo-agency", "city": "Chicago", "state": "IL", "region": "Midwest",
     "blurb": "Chicago neighborhoods and suburbs: community-area pages, lakefront geography and Illinois' biometric privacy law."},
    {"slug": "seo-company-cypress-tx", "city": "Cypress", "state": "TX", "region": "Texas & South Central",
     "url": "/seo-company-cypress-tx/",
     "blurb": "Local SEO and Google Business Profile work for service businesses across Cypress and Cy-Fair."},
]

esc = lambda s: html.escape(s, quote=True)
url_of = lambda c: c.get("url") or f"{HUB}{c['slug']}/"
read = lambda p: open(p, encoding="utf-8").read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


def build(path, main_file, meta_file):
    """Build a landing page at <path>/index.html from the shared template, main.html and meta.json."""
    m = json.load(open(meta_file, encoding="utf-8"))
    main = read(main_file).strip("\n")
    url = f"{SITE}/{path.strip('/')}/"
    s = read(TEMPLATE)
    old = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
    s = re.sub(r"<title>.*?</title>", f"<title>{esc(m['title'])}</title>", s, count=1)
    for k, v in {'name="description"': m["desc"], 'property="og:title"': m["og_title"], 'property="og:description"': m["og_desc"],
                 'name="twitter:title"': m["og_title"], 'name="twitter:description"': m["og_desc"], 'property="og:image:alt"': m["image_alt"],
                 'property="og:image"': m["image"], 'name="twitter:image"': m["image"]}.items():
        s = re.sub(rf'<meta {k} content="[^"]*"', f'<meta {k} content="{esc(v)}"', s, count=1)
    s = s.replace(f'<link rel="canonical" href="{old}">', f'<link rel="canonical" href="{url}">')
    s = s.replace(f'<meta property="og:url" content="{old}">', f'<meta property="og:url" content="{url}">')
    ld = "\n".join("  " + l for l in json.dumps({"@context": "https://schema.org", "@graph": m["ld"]}, indent=2, ensure_ascii=False).splitlines())
    s = re.sub(r'(<script type="application/ld\+json">).*?</script>', lambda x: f"{x.group(1)}\n{ld}\n  </script>", s, count=1, flags=re.S)
    s = re.sub(r'\n[ \t]*<script type="application/ld\+json" data-[a-z]+="[^"]*">.*?</script>', "", s, flags=re.S)
    i, j = s.index("</header>") + len("</header>"), s.index("<footer")
    s = s[:i] + "\n\n" + main + "\n\n  " + s[j:]
    write(f"{path.strip('/')}/index.html", s)
    print("built", f"/{path.strip('/')}/")


def directory():
    blocks = []
    for r in REGIONS:
        cs = sorted((c for c in CITIES if c["region"] == r), key=lambda c: (c["state"], c["city"]))
        if not cs:
            continue
        items = "\n".join(f'            <li><a href="{url_of(c)}"><strong>{esc(c["city"])}, {c["state"]}</strong><span>{esc(c["blurb"])}</span></a></li>' for c in cs)
        blocks.append(f'''        <div class="city-region reveal-fade-up">
          <h3>{esc(r)} <small>{len(cs)} {"city" if len(cs) == 1 else "cities"}</small></h3>
          <ul class="city-list">
{items}
          </ul>
        </div>''')
    return "<!-- city-directory:start -->\n      <div class=\"city-directory\">\n" + "\n".join(blocks) + "\n      </div>\n      <!-- city-directory:end -->"


def sync():
    # hub directory + ItemList
    p = "seo-by-city/index.html"
    s = read(p)
    s, n = re.subn(r"<!-- city-directory:start -->.*?<!-- city-directory:end -->", directory(), s, flags=re.S)
    assert n == 1, "hub directory markers missing"
    ld_m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, re.S)
    data = json.loads(ld_m.group(2))
    for node in data["@graph"]:
        if node.get("@type") == "ItemList":
            node["numberOfItems"] = len(CITIES)
            node["itemListElement"] = [{"@type": "ListItem", "position": k + 1, "name": f'SEO in {c["city"]}, {c["state"]}', "url": SITE + url_of(c)}
                                       for k, c in enumerate(sorted(CITIES, key=lambda c: (REGIONS.index(c["region"]), c["state"], c["city"])))]
    ld = "\n".join("  " + l for l in json.dumps(data, indent=2, ensure_ascii=False).splitlines())
    s = s[:ld_m.start(2)] + "\n" + ld + "\n  " + s[ld_m.end(2):]
    write(p, s)

    # "More cities" block on every city page under /seo-by-city/
    for c in CITIES:
        if c.get("url"):
            continue
        p = f"seo-by-city/{c['slug']}/index.html"
        if not os.path.exists(p):
            continue
        others = [o for o in CITIES if o is not c]
        others.sort(key=lambda o: (o["region"] != c["region"], o["city"]))
        cards = "\n".join(f'        <a href="{url_of(o)}"><small>{esc(o["region"])}</small><strong>SEO in {esc(o["city"])}, {o["state"]}</strong></a>' for o in others[:5])
        cards += f'\n        <a href="{HUB}"><small>All locations</small><strong>SEO by City directory</strong></a>'
        block = f'''<!-- more-cities:start -->
  <section class="section-white" style="padding-top: 0;">
    <div class="container">
      <div class="section-header reveal-fade-up">
        <span class="section-label">SEO by City</span>
        <h2 class="section-title">Local SEO in <em class="accent">other cities.</em></h2>
      </div>
      <div class="related-links">
{cards}
      </div>
    </div>
  </section>
  <!-- more-cities:end -->'''
        s = read(p)
        if "<!-- more-cities:start -->" in s:
            s = re.sub(r"<!-- more-cities:start -->.*?<!-- more-cities:end -->", block, s, flags=re.S)
        else:
            s = s.replace('  <section class="section-contrast final-cta">', block + '\n\n  <section class="section-contrast final-cta">', 1)
        write(p, s)

    # sitemaps, llms.txt, vite inputs
    pages = [HUB] + [url_of(c) for c in CITIES if not c.get("url")]
    for sm in ("sitemap.xml", "public/sitemap.xml"):
        s = read(sm)
        for u in pages:
            if f"<loc>{SITE}{u}</loc>" not in s:
                s = s.replace("</urlset>", f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>0.8</priority>\n  </url>\n</urlset>")
        write(sm, s)
    for lt in ("llms.txt", "public/llms.txt"):
        s = read(lt)
        lines = [f"- [SEO by City: local SEO programs for US businesses]({SITE}{HUB})"] + \
                [f"- [SEO agency in {c['city']}, {c['state']}]({SITE}{url_of(c)})" for c in CITIES if not c.get("url")]
        sec = "## SEO by City\n\n" + "\n".join(lines) + "\n"
        if "## SEO by City" in s:
            s = re.sub(r"## SEO by City\n\n.*?(?=\n## |\Z)", sec.rstrip("\n") + "\n", s, flags=re.S)
        elif "\n## Company" in s:
            s = s.replace("\n## Company", "\n" + sec + "\n## Company", 1)
        else:
            s = s.rstrip("\n") + "\n\n" + sec
        write(lt, s)
    s = read("vite.config.js")
    for u in pages:
        f = u.strip("/") + "/index.html"
        if f"'{f}'" not in s:
            key = "city_" + re.sub(r"[^a-z0-9]+", "_", u.strip("/").split("/")[-1])
            s = re.sub(r"(input:\s*\{\n)", lambda m: m.group(1) + f"        {key}: resolve(__dirname, '{f}'),\n", s, count=1)
        assert f"'{f}'" in s, f"vite input not added for {f}"
    write("vite.config.js", s)
    print("synced", len(CITIES), "cities")


TODAY = os.environ.get("TODAY") or __import__("datetime").date.today().isoformat()

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        slug = sys.argv[2]
        build("seo-by-city" if slug == "hub" else f"seo-by-city/{slug}", sys.argv[3], sys.argv[4])
    elif len(sys.argv) >= 2 and sys.argv[1] == "sync":
        sync()
    else:
        print(__doc__)
