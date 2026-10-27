"""Silo architecture for llmsmarketing.com.

Builds one hub page per blog silo (/blog/category/<slug>/) and wires every post,
service page and industry page into its silo. Safe to re-run: every change is
idempotent. When you publish a post, add it to the right silo in SILOS and run:

    python3 tools/silo.py

Silo rules applied to each post:
  * visible breadcrumb Home / Blog / Silo and a matching BreadcrumbList schema
  * category label links to the silo hub
  * "Keep reading" rail lists three posts from the same silo
  * a "More on <silo>" block links the hub, every sibling post, the silo's
    service pages and the matching industry page
Service and industry pages get a card linking to their silo hub, and the
blog index sidebar lists the silos.
"""
import glob
import html
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
SITE = "https://llmsmarketing.com"

SILOS = [
    {
        "slug": "ai-search-geo",
        "name": "AI Search & GEO",
        "title": "AI Search and GEO Guides",
        "desc": "Guides to generative engine optimization and AI search visibility: get your brand cited and recommended in ChatGPT, Google AI Mode, Perplexity and Gemini.",
        "intro": [
            "Generative engine optimization (GEO) is the work of making your brand easy for AI assistants to find, understand and recommend. These guides explain how ChatGPT, Google AI Mode, Perplexity and Gemini choose what to cite, how GEO relates to traditional SEO, and the practical steps that move visibility.",
            "Start with the pillar guide on LLM marketing, then go deeper into recommendations, AI search visibility, structured data and how search itself is changing. For done-for-you help, see our <a href=\"/services/ai-search-visibility/\">AI search visibility service</a>, and for the data behind these guides, read our <a href=\"/report/state-of-ai-search-llm-marketing-2026/\">State of AI Search 2026 report</a>.",
        ],
        "posts": [
            "what-is-llm-marketing",
            "ai-search-visibility-how-to-show-up-in-chatgpt-perplexity-and-gemini",
            "how-to-get-your-brand-recommended-by-chatgpt",
            "geo-vs-seo",
            "schema-entity-optimization-llms",
            "seo-is-changing-how-ai-platforms-like-chatgpt-are-redefining-search-visibility",
        ],
        "services": [("/services/ai-search-visibility/", "AI Search Visibility"), ("/services/ai-seo/", "AI SEO & Content")],
    },
    {
        "slug": "ai-marketing",
        "name": "AI Marketing & Automation",
        "title": "AI Marketing and Automation Guides",
        "desc": "Guides to using AI in marketing: choosing an LLM, AI agents for PPC, SEO and email, AI advertising and what to keep in-house versus outsource.",
        "intro": [
            "AI is changing how marketing work gets done, from drafting and analysis to agents that act across your tools. These guides cover how to choose a model, where AI agents genuinely help, how advertising inside AI answers works and how to decide what to automate or outsource.",
            "Each guide is vendor-neutral and built on official documentation, with the guardrails that keep automation safe and compliant. For hands-on help, see our <a href=\"/services/ai-lead-agents/\">AI lead agents</a> and <a href=\"/services/marketing-automation/\">marketing automation</a> services.",
        ],
        "posts": [
            "how-to-use-ai-for-social-media",
            "ai-agents-for-marketing",
            "best-llm-for-business-and-marketing",
            "ai-advertising",
            "companies-that-outsource",
        ],
        "services": [("/services/ai-lead-agents/", "AI Lead Agents"), ("/services/marketing-automation/", "Marketing Automation"), ("/services/email-marketing/", "Email Marketing")],
    },
    {
        "slug": "local-industry-seo",
        "name": "Local & Industry SEO",
        "title": "Local and Industry SEO Guides",
        "desc": "Local and industry SEO guides for gyms, yoga studios, daycares, locksmiths, dentists, law firms and ecommerce: map pack, service pages, reviews and AI answers.",
        "intro": [
            "Local and industry SEO decides who gets the call when someone searches nearby or asks an AI assistant for a recommendation. These guides show how specific industries win the map pack, build pages that match how customers search, collect genuine reviews and stay within the rules of their profession.",
            "Each guide uses real search data and official guidelines. For hands-on help in a specific industry, see the <a href=\"/industries/\">industries we work with</a>.",
        ],
        "posts": [
            "marketing-small-dental-practice",
            "seo-for-dermatologists",
            "seo-for-security-companies",
            "seo-for-locksmiths",
            "seo-for-yoga-studios",
            "daycare-seo",
            "google-ads-vs-seo-for-dentists",
            "generative-engine-optimization-for-dentists",
            "how-to-choose-a-law-firm-seo-company",
            "seo-for-gyms",
            "local-seo-for-ecommerce",
        ],
        "services": [("/services/ai-seo/", "AI SEO & Content"), ("/industries/", "Industries we serve")],
    },
]

# Industry page that best matches a post (shown in the post's silo block).
POST_INDUSTRY = {
    "seo-for-locksmiths": ("/seo-for-electricians/", "SEO for Electricians"),
    "seo-for-security-companies": ("/seo-for-electricians/", "SEO for Electricians"),
    "marketing-small-dental-practice": ("/seo-for-orthodontists/", "SEO for Orthodontists"),
    "seo-for-dermatologists": ("/dental-seo-cypress-tx/", "Dental SEO in Cypress, TX"),
    "daycare-seo": ("/seo-for-educational-institutions/", "SEO for Educational Institutions"),
    "google-ads-vs-seo-for-dentists": ("/dental-seo-cypress-tx/", "Dental SEO in Cypress, TX"),
    "generative-engine-optimization-for-dentists": ("/dental-seo-cypress-tx/", "Dental SEO in Cypress, TX"),
    "how-to-choose-a-law-firm-seo-company": ("/personal-injury-seo/", "Personal Injury Lawyer SEO"),
    "seo-for-gyms": ("/seo-company-cypress-tx/", "Local SEO in Cypress, TX"),
    "seo-for-yoga-studios": ("/seo-company-cypress-tx/", "Local SEO in Cypress, TX"),
}

# Service and industry pages -> silo hub they belong to.
PAGE_SILO = {
    "services/ai-search-visibility": "ai-search-geo",
    "services/ai-seo": "ai-search-geo",
    "services/ai-lead-agents": "ai-marketing",
    "services/marketing-automation": "ai-marketing",
    "services/email-marketing": "ai-marketing",
    "personal-injury-seo": "local-industry-seo",
    "dental-seo-cypress-tx": "local-industry-seo",
    "seo-company-cypress-tx": "local-industry-seo",
    "seo-for-investment-firms": "local-industry-seo",
    "seo-for-electricians": "local-industry-seo",
    "seo-for-orthodontists": "local-industry-seo",
    "seo-for-educational-institutions": "local-industry-seo",
}

esc = lambda s: html.escape(s, quote=True)
hub_url = lambda silo: f"/blog/category/{silo['slug']}/"


def read(p):
    return open(p, encoding="utf-8").read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)


def post_info(slug):
    s = read(f"blog/{slug}/index.html")
    h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", s, re.S).group(1)).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    date = re.search(r'<time datetime="([\d-]+)"', s)
    og = re.search(r'<meta property="og:image" content="([^"]*)"', s)
    return {"slug": slug, "url": f"/blog/{slug}/", "h1": html.unescape(h1), "desc": html.unescape(desc),
            "date": date.group(1) if date else "", "image": og.group(1) if og else f"{SITE}/icon-512.png"}


# ---------------------------------------------------------------- posts
def wire_post(silo, info, siblings):
    p = f"blog/{info['slug']}/index.html"
    s = read(p)
    hub = hub_url(silo)

    # 1. visible breadcrumb + category label linking to the hub
    s = re.sub(r'\s*<nav class="crumbs post-crumbs".*?</nav>', "", s, count=1, flags=re.S)
    crumbs = (f'<nav class="crumbs post-crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> '
              f'<a href="/blog/">Blog</a> <span aria-hidden="true">/</span> <a href="{hub}">{esc(silo["name"])}</a></nav>')
    s, n = re.subn(r'(<header class="post-header[^"]*">\s*)<div class="post-meta">.*?</div>',
                   lambda m: f'{m.group(1)}{crumbs}\n      <div class="post-meta"><a href="{hub}">{esc(silo["name"])}</a></div>',
                   s, count=1, flags=re.S)
    assert n == 1, f"post-meta not found in {p}"

    # 2. BreadcrumbList schema: Home > Blog > Silo > Post
    def strip_breadcrumbs(m):
        if "data-silo" in m.group(1):
            return m.group(0)
        raw = m.group(2)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return m.group(0)
        if isinstance(data, dict) and data.get("@type") == "BreadcrumbList":
            return ""
        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            kept = [g for g in data["@graph"] if g.get("@type") != "BreadcrumbList"]
            if len(kept) != len(data["@graph"]):
                data["@graph"] = kept
                body = "\n".join("  " + l for l in json.dumps(data, indent=2, ensure_ascii=False).splitlines())
                return f'{m.group(1)}\n{body}\n  </script>'
        return m.group(0)
    s = re.sub(r'(<script type="application/ld\+json"(?: data-silo="breadcrumb")?>)(.*?)</script>', strip_breadcrumbs, s, flags=re.S)
    s = re.sub(r'\n[ \t]*<script type="application/ld\+json" data-silo="breadcrumb">.*?</script>', "", s, flags=re.S)
    s = re.sub(r'(\n[ \t]*)+\n</head>', "\n</head>", s, count=1)
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
        {"@type": "ListItem", "position": 3, "name": silo["name"], "item": f"{SITE}{hub}"},
        {"@type": "ListItem", "position": 4, "name": info["h1"], "item": f"{SITE}{info['url']}"}]}
    bc_json = "\n".join("  " + l for l in json.dumps(bc, indent=2, ensure_ascii=False).splitlines())
    s = s.replace("\n</head>", f'\n  <script type="application/ld+json" data-silo="breadcrumb">\n{bc_json}\n  </script>\n</head>', 1)

    # 3. Keep-reading rail: three posts from the same silo
    rail = "\n".join(f'            <li><a href="{x["url"]}">{esc(x["h1"])}</a></li>' for x in siblings[:3])
    s, n = re.subn(r'(<p class="rail-heading">Keep reading</p>\s*<ul class="rail-list">\n).*?(\n\s*</ul>)',
                   lambda m: m.group(1) + rail + m.group(2), s, count=1, flags=re.S)
    assert n == 1, f"rail not found in {p}"

    # 4. "More on <silo>" block before the lead form
    s = re.sub(r"\n+[ \t]*<!-- silo:start -->.*?<!-- silo:end -->", "", s, flags=re.S)
    links = [f'<a href="{u}">{esc(t)}</a>' for u, t in silo["services"]]
    if info["slug"] in POST_INDUSTRY:
        u, t = POST_INDUSTRY[info["slug"]]
        links.append(f'<a href="{u}">{esc(t)}</a>')
    items = "\n".join(f'          <li><a href="{x["url"]}">{esc(x["h1"])}</a></li>' for x in siblings)
    block = f'''<!-- silo:start -->
      <aside class="silo-nav" aria-labelledby="silo-nav-title">
        <p class="silo-eyebrow">Part of our {esc(silo["name"])} guides</p>
        <h2 id="silo-nav-title">More on <a href="{hub}">{esc(silo["name"])}</a></h2>
        <ul class="silo-list">
{items}
        </ul>
        <p class="silo-links"><span>Related:</span> {" · ".join(links)} · <a href="{hub}" class="silo-all">All {esc(silo["name"])} guides →</a></p>
      </aside>
      <!-- silo:end -->'''
    s, n = re.subn(r'\n+([ \t]*)<section class="lead-box"',
                   lambda m: f'\n\n{m.group(1)}{block}\n\n{m.group(1)}<section class="lead-box"', s, count=1)
    assert n == 1, f"lead box not found in {p}"
    write(p, s)


# ---------------------------------------------------------------- hubs
def build_hub(silo, infos, template):
    url = hub_url(silo)
    head_top = template.split("  <title>")[0]
    header = re.search(r"  <header class=\"header\">.*?</header>\n", template, re.S).group(0)
    footer = re.search(r"  <footer class=\"footer\">.*?</html>\n", template, re.S).group(0)
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": f"{SITE}{url}#webpage", "url": f"{SITE}{url}", "name": silo["title"],
         "description": silo["desc"], "inLanguage": "en", "isPartOf": {"@id": f"{SITE}/#website"},
         "about": {"@type": "Thing", "name": silo["name"]},
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": f"{SITE}{x['url']}", "name": x["h1"]} for i, x in enumerate(infos)]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": silo["name"], "item": f"{SITE}{url}"}]}]}
    schema = "\n".join("  " + l for l in json.dumps(graph, indent=2, ensure_ascii=False).splitlines())
    title = f"{silo['title']} | LLM's Marketing"
    head = f'''  <title>{esc(title)}</title>
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" href="/favicon-96x96.png" type="image/png" sizes="96x96">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#171717">
  <link rel="canonical" href="{SITE}{url}">
  <meta name="description" content="{esc(silo['desc'])}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="LLM's Marketing">
  <meta property="og:url" content="{SITE}{url}">
  <meta property="og:title" content="{esc(silo['title'])}">
  <meta property="og:description" content="{esc(silo['desc'])}">
  <meta property="og:image" content="{infos[0]['image']}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="/assets/css/style.css">
  <script type="application/ld+json">
{schema}
  </script>
</head>
<body>

'''
    pillar, rest = infos[0], infos[1:]
    cards = "\n".join(f'''          <a href="{x['url']}" class="svc-card reveal-fade-up">
            <span class="num-card-num">{i + 2:02d}</span>
            <h3>{esc(x['h1'])}</h3>
            <p>{esc(x['desc'])}</p>
            <span class="link-arrow">Read the guide <span>→</span></span>
          </a>''' for i, x in enumerate(rest))
    other = [o for o in SILOS if o is not silo]
    related = "\n".join(f'        <a href="{u}"><small>Related service</small><strong>{esc(t)}</strong></a>' for u, t in silo["services"])
    related += "\n" + "\n".join(f'        <a href="{hub_url(o)}"><small>More guides</small><strong>{esc(o["name"])}</strong></a>' for o in other)
    body = f'''  <section class="page-header">
    <div class="container reveal-fade-up">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/blog/">Blog</a> <span aria-hidden="true">/</span> <span aria-current="page">{esc(silo['name'])}</span></nav>
      <span class="section-label">Guides</span>
      <h1>{esc(silo['title'])}</h1>
      <p>{esc(silo['intro'][0])}</p>
    </div>
  </section>

  <section class="section-white">
    <div class="container">
      <div class="section-header reveal-fade-up" style="text-align: left; margin-bottom: 16px;">
        <span class="section-label">All guides</span>
        <h2 class="section-title">{esc(silo['name'])} <em class="accent">guides.</em></h2>
      </div>
      <p class="reveal-fade-up" style="max-width: 760px; margin: 0 0 32px;">{silo['intro'][1]}</p>
      <div class="svc-cards">
          <a href="{pillar['url']}" class="svc-card reveal-fade-up">
            <span class="num-card-num">01 · Start here</span>
            <h3>{esc(pillar['h1'])}</h3>
            <p>{esc(pillar['desc'])}</p>
            <span class="link-arrow">Read the guide <span>→</span></span>
          </a>
{cards}
      </div>
    </div>
  </section>

  <section class="section-white" style="padding-top: 0;">
    <div class="container">
      <div class="section-header reveal-fade-up">
        <span class="section-label">Keep exploring</span>
        <h2 class="section-title">Related services <em class="accent">and guides.</em></h2>
      </div>
      <div class="related-links">
{related}
      </div>
    </div>
  </section>

  <section class="section-contrast final-cta">
    <div class="container">
      <div class="final-cta-content reveal-fade-up">
        <h2>Want this done <em class="accent">for your brand?</em></h2>
        <p>Get a free review of your search and AI visibility, with the first fixes to make.</p>
        <div class="final-cta-actions">
          <a href="/book-a-call/" class="btn btn-primary">Book a free call</a>
          <a href="/contact/" class="btn btn-secondary">Send us a message</a>
        </div>
      </div>
    </div>
  </section>

'''
    out = head_top + head + header + "\n" + body + footer
    out = out.replace(' class="nav-link active"', ' class="nav-link"')
    write(f"blog/category/{silo['slug']}/index.html", out)


# ---------------------------------------------------------------- blog index
def wire_blog_index(all_infos):
    p = "blog/index.html"
    s = read(p)
    cats = "\n".join(f'              <li><a href="{hub_url(o)}">{esc(o["name"])} ({len(o["posts"])})</a></li>' for o in SILOS)
    s, n = re.subn(r'(<h3 class="widget-title">Categories</h3>\s*<ul class="widget-list">\n).*?(\n\s*</ul>)',
                   lambda m: m.group(1) + cats + m.group(2), s, count=1, flags=re.S)
    assert n == 1
    silo_of = {slug: o for o in SILOS for slug in o["posts"]}

    def fix_card(m):
        date, href = m.group(2), m.group(4)
        slug = href.strip("/").split("/")[-1]
        if slug not in silo_of:
            return m.group(0)
        return f'{m.group(1)}{date} • {esc(silo_of[slug]["name"])}{m.group(3)}{href}{m.group(5)}'
    s = re.sub(r'(<div class="post-meta">)([^<•]+?) • [^<]*(</div>\s*<h2 class="post-title">\s*<a href=")([^"]+)(")', fix_card, s)
    write(p, s)


# ---------------------------------------------------------------- service and industry pages
def wire_pages():
    for page, slug in PAGE_SILO.items():
        p = f"{page}/index.html"
        if not os.path.exists(p):
            continue
        s = read(p)
        silo = next(o for o in SILOS if o["slug"] == slug)
        s = re.sub(r'\n\s*<a href="/blog/category/[^"]+/" data-silo-card>.*?</a>', "", s, flags=re.S)
        card = f'\n        <a href="{hub_url(silo)}" data-silo-card><small>Guides</small><strong>{esc(silo["name"])} guides</strong></a>'
        s, n = re.subn(r'(<div class="related-links">)', lambda m: m.group(1) + card, s, count=1)
        if n:
            write(p, s)


def wire_topic_sections():
    """Add a 'Guides by topic' section linking every silo hub to /our-services/ and /industries/."""
    for p, first in (("our-services/index.html", None), ("industries/index.html", "local-industry-seo")):
        if not os.path.exists(p):
            continue
        s = read(p)
        s = re.sub(r"\n+[ \t]*<!-- silo-topics:start -->.*?<!-- silo-topics:end -->", "", s, flags=re.S)
        order = sorted(SILOS, key=lambda o: o["slug"] != first)
        cards = "\n".join(f'''        <a href="{hub_url(o)}"><small>{len(o["posts"])} guides</small><strong>{esc(o["name"])}</strong></a>''' for o in order)
        block = f'''<!-- silo-topics:start -->
  <section class="section-white" style="padding-top: 0;">
    <div class="container">
      <div class="section-header reveal-fade-up">
        <span class="section-label">Guides by topic</span>
        <h2 class="section-title">Learn how it works <em class="accent">before you hire.</em></h2>
      </div>
      <div class="related-links">
{cards}
      </div>
    </div>
  </section>
  <!-- silo-topics:end -->'''
        s, n = re.subn(r'\n+([ \t]*)<section class="section-contrast final-cta">',
                       lambda m: f'\n\n{m.group(1)}{block}\n\n{m.group(1)}<section class="section-contrast final-cta">', s, count=1)
        assert n == 1, p
        write(p, s)


def main():
    template = read("blog/index.html")
    all_infos = {}
    for silo in SILOS:
        infos = [post_info(x) for x in silo["posts"]]
        for info in infos:
            all_infos[info["slug"]] = info
            siblings = [x for x in infos if x["slug"] != info["slug"]]
            wire_post(silo, info, siblings)
        build_hub(silo, infos, template)
    wire_blog_index(all_infos)
    wire_pages()
    wire_topic_sections()
    covered = {x for o in SILOS for x in o["posts"]}
    posts = {p.split("/")[1] for p in glob.glob("blog/*/index.html")} - {"category"}
    redirects = {p.split("/")[1] for p in glob.glob("blog/*/index.html") if "http-equiv=\"refresh\"" in read(p)}
    missing = posts - covered - redirects
    print("silos:", {o["slug"]: len(o["posts"]) for o in SILOS})
    if missing:
        print("POSTS NOT IN ANY SILO:", sorted(missing))
        sys.exit(1)


if __name__ == "__main__":
    main()
