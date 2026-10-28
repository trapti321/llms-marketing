"""Rewrite the main navigation on every page with the dropdown header.

To add a future page, append it to SERVICES / INDUSTRIES / LOCATIONS / ABOUT and re-run.
"""
import glob, re, sys, os

os.chdir(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SERVICES = [
    ("/services/ai-search-visibility/", "AI Search Visibility", "Get mentioned and cited in AI answers"),
    ("/services/ai-seo/", "AI SEO & Content", "Rank on Google and get quoted by AI"),
    ("/services/ai-lead-agents/", "AI Lead Agents", "Answer and qualify inquiries 24/7"),
    ("/services/marketing-automation/", "Marketing Automation", "Forms, CRM and follow-up connected"),
    ("/services/email-marketing/", "Email Marketing", "Sequences that turn leads into calls"),
]
INDUSTRIES = [
    ("/personal-injury-seo/", "Personal Injury Law Firms", "SEO and AI visibility for injury lawyers"),
    ("/dental-seo-cypress-tx/", "Dental Practices", "Dental SEO for Cypress, TX practices"),
    ("/seo-for-investment-firms/", "Investment Firms", "SEO for RIAs, funds and real estate firms"),
    ("/seo-for-electricians/", "Electricians", "SEO for electrical contractors"),
    ("/seo-for-orthodontists/", "Orthodontists", "SEO for orthodontic practices"),
    ("/seo-for-hvac/", "HVAC Companies", "SEO for heating and cooling contractors"),
    ("/seo-for-educational-institutions/", "Education", "SEO for schools, colleges and universities"),
]
LOCATIONS = [
    ("/seo-company-cypress-tx/", "Cypress, TX", "Local SEO for Cypress businesses"),
]
BLOG = [
    ("/blog/category/ai-search-geo/", "AI Search & GEO", "Get cited and recommended by AI"),
    ("/blog/category/ai-marketing/", "AI Marketing & Automation", "LLMs, AI agents and AI ads"),
    ("/blog/category/local-industry-seo/", "Local & Industry SEO", "Guides for local businesses by industry"),
    ("/report/", "Reports & Insights", "Original research and trend reports"),
]
ABOUT = [
    ("/about-us/", "About Us", "Who we are and how we work"),
    ("/our-approach/", "Our Approach", "Our testing-led SEO process"),
    ("/author/mohd-adil-kazmi/", "Our Founder", "Mohd Adil Kazmi, 8+ years in SEO"),
]

CHEVRON = '<svg viewBox="0 0 12 12" aria-hidden="true" focusable="false"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
esc = lambda s: s.replace("&", "&amp;")

def section_for(path):
    if path.startswith(("/our-services/", "/services/")): return "services"
    if path.startswith(("/industries/",)) or path in [u for u, *_ in INDUSTRIES + LOCATIONS]: return "industries"
    if path.startswith("/case-studies/"): return "case"
    if path.startswith(("/blog/", "/report/")): return "blog"
    if path.startswith(("/about-us/", "/our-approach/", "/author/")): return "about"
    if path.startswith("/contact/"): return "contact"
    return None

def links(items, path):
    out = []
    for u, t, d in items:
        cur = ' aria-current="page"' if path == u else ""
        out.append(f'<a href="{u}" class="nav-dd-link"{cur}><strong>{esc(t)}</strong><span>{esc(d)}</span></a>')
    return "".join(out)

def dropdown(key, label, href, inner, active, wide=False):
    cls = "nav-link active" if active else "nav-link"
    return (f'<li class="nav-item has-dropdown"><a href="{href}" class="{cls}">{label}</a>'
            f'<button type="button" class="nav-dd-toggle" aria-expanded="false" aria-controls="dd-{key}" aria-label="Show {label} menu">{CHEVRON}</button>'
            f'<div class="nav-dropdown{" nav-dropdown--wide" if wide else ""}" id="dd-{key}"><div class="nav-dropdown-inner">{inner}</div></div></li>')

def nav(path):
    sec = section_for(path)
    simple = lambda href, label, key: f'<li><a href="{href}" class="nav-link{" active" if sec == key else ""}">{label}</a></li>'
    services = links(SERVICES, path) + '<a href="/our-services/" class="nav-dd-all">All services →</a>'
    industries = ('<p class="nav-dd-group-label">Industries</p>' + links(INDUSTRIES, path)
                  + '<p class="nav-dd-group-label">Locations</p>' + links(LOCATIONS, path)
                  + '<a href="/industries/" class="nav-dd-all">All industries and locations →</a>')
    about = links(ABOUT, path)
    items = [
        dropdown("services", "Services", "/our-services/", services, sec == "services"),
        dropdown("industries", "Industries", "/industries/", industries, sec == "industries", wide=True),
        simple("/case-studies/", "Case Studies", "case"),
        dropdown("blog", "Blog", "/blog/", links(BLOG, path) + '<a href="/blog/" class="nav-dd-all">All articles →</a>', sec == "blog"),
        dropdown("about", "About", "/about-us/", about, sec == "about"),
        simple("/contact/", "Contact", "contact"),
        '<li><a href="/book-a-call/" class="btn btn-nav-cta">Book a free call <span class="btn-nav-arrow" aria-hidden="true">→</span></a></li>',
    ]
    body = "\n".join("          " + i for i in items)
    return f'<nav class="nav-container" aria-label="Main">\n        <ul class="nav-menu">\n{body}\n        </ul>\n      </nav>'

files = [f for f in glob.glob("**/index.html", recursive=True) if not f.startswith(("dist/", "node_modules/", "public/", "tools/"))]
n = 0
for f in files:
    s = open(f, encoding="utf-8").read()
    m = re.search(r'<nav class="nav-container" aria-label="Main">.*?</nav>', s, re.S)
    if not m: continue
    path = "/" + f[:-len("index.html")] if f != "index.html" else "/"
    new = s[:m.start()] + nav(path) + s[m.end():]
    if new != s:
        open(f, "w", encoding="utf-8").write(new); n += 1
print("headers rewritten:", n, "of", len(files))
