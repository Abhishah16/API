#!/usr/bin/env python3
"""
All Things 3D — static site generator.

Every page on the site is written from this one file so the header, footer,
meta tags and styling stay identical across all of them. Edit the content
below, then run:

    python3 _build/build.py

from the allthings3d-website folder. It rewrites the .html files in place.
Nothing is installed, nothing is fetched — it is plain Python 3.
"""

import os
import re
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DOMAIN = "https://allthings3d.com"
EMAIL = "info.allthings3d@gmail.com"
PHONE_DISPLAY = "+91 76660 04531"
INSTAGRAM = "https://www.instagram.com/allthings3d.in"
TAGLINE = "Because your ideas deserve to exist"

# --------------------------------------------------------------------------
# Icons (inline SVG, stroke-based, 24x24)
# --------------------------------------------------------------------------
I = {
    "upload": '<path d="M12 16V4m0 0L7 9m5-5 5 5M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2"/>',
    "cube": '<path d="m12 2 8.5 4.9v10.2L12 22l-8.5-4.9V6.9zM12 22V12m0 0L3.5 7M12 12l8.5-5"/>',
    "gift": '<path d="M20 12v8a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-8M2 7h20v5H2zM12 21V7M12 7H7.5a2.5 2.5 0 1 1 0-5C11 2 12 7 12 7zm0 0h4.5a2.5 2.5 0 1 0 0-5C13 2 12 7 12 7z"/>',
    "factory": '<path d="M3 21h18M4 21V10l6 4V10l6 4V6l4-3v18M8 21v-4h3v4"/>',
    "layers": '<path d="m12 2 9 5-9 5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5"/>',
    "tag": '<path d="M20.6 13.4 12 22l-9-9V4a1 1 0 0 1 1-1h9zM7.5 7.5h.01"/>',
    "spark": '<path d="M12 2v4m0 12v4M2 12h4m12 0h4M5 5l2.8 2.8M16.2 16.2 19 19M19 5l-2.8 2.8M7.8 16.2 5 19"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "mail": '<path d="M3 5h18v14H3z"/><path d="m3 6 9 7 9-7"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7A2 2 0 0 1 22 16.9z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>',
    "whatsapp": '<path d="M3 21l1.6-4.5A8.4 8.4 0 1 1 8 20.2z"/><path d="M8.5 9.2c.2 1.4 1 2.6 2 3.5s2.2 1.5 3.5 1.7l1-1.4 1.8.9-.3 1.6c-1.9.4-4-.5-5.6-2s-2.4-3.7-2-5.6l1.6-.3.9 1.8z"/>',
    "pencil": '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    "box": '<path d="M21 8v8a2 2 0 0 1-1 1.7l-7 4a2 2 0 0 1-2 0l-7-4A2 2 0 0 1 3 16V8a2 2 0 0 1 1-1.7l7-4a2 2 0 0 1 2 0l7 4A2 2 0 0 1 21 8z"/><path d="m3.3 7 8.7 5 8.7-5M12 22V12"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "truck": '<path d="M1 3h13v13H1zM14 8h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="2"/><circle cx="17.5" cy="18.5" r="2"/>',
    "lock": '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "chart": '<path d="M3 3v18h18M7 15l3-4 3 3 5-7"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0 5.3 5.3l-8 8a2.8 2.8 0 0 1-4-4z"/>',
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "check": '<path d="m5 13 4 4L19 7"/>',
}


def icon(name, size=24, cls=""):
    body = I.get(name, I["cube"])
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true"{f" class={cls}" if cls else ""}>{body}</svg>')


ARROW = icon("arrow", 17)

# --------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------
NAV = [
    ("products.html", "Products"),
    ("services.html", "Services"),
    ("oem.html", "OEM &amp; Bulk"),
    ("capabilities.html", "Capabilities"),
    ("gallery.html", "Gallery"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

FOOTER_LINKS = [
    ("Explore", [
        ("index.html", "Home"),
        ("products.html", "Products"),
        ("services.html", "Services"),
        ("gallery.html", "Gallery"),
        ("capabilities.html", "Capabilities"),
    ]),
    ("Business", [
        ("oem.html", "OEM &amp; white-label"),
        ("oem.html#bulk", "Bulk orders"),
        ("services.html#contract", "Contract manufacturing"),
        ("services.html#corporate", "Corporate gifting"),
        ("services.html#development", "Product development"),
    ]),
]


def nav_html(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<a class="nav__link" href="{href}"{cur}>{label}</a>')
    links_html = "\n          ".join(links)
    return f"""  <div class="progress-rail"><div class="progress-rail__fill"></div></div>
  <header class="nav">
    <div class="shell nav__inner">
      <a class="nav__logo" href="index.html" aria-label="All Things 3D — home">
        <img src="assets/img/logo/atd-logo-horizontal-transparent.png" alt="All Things 3D" width="954" height="299">
      </a>
      <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="navLinks" aria-label="Menu"><span></span></button>
      <nav class="nav__links" id="navLinks" aria-label="Main">
          {links_html}
        <a class="btn btn--ember btn--sm nav__cta" href="order.html">Upload your idea</a>
      </nav>
    </div>
  </header>"""


def footer_html():
    cols = []
    for title, items in FOOTER_LINKS:
        li = "\n            ".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items)
        cols.append(f"""        <div>
          <h4>{title}</h4>
          <ul>
            {li}
          </ul>
        </div>""")
    cols_html = "\n".join(cols)
    return f"""  <footer class="footer">
    <div class="shell">
      <div class="footer__grid">
        <div>
          <img class="footer__logo" src="assets/img/logo/atd-logo-horizontal-white.png" alt="All Things 3D" width="954" height="299">
          <p>{TAGLINE}. Custom 3D printing, product development and small-batch manufacturing — from a single keepsake to a thousand-piece corporate order.</p>
          <div class="footer__social">
            <a data-ig href="{INSTAGRAM}" aria-label="Instagram">{icon('instagram', 19)}</a>
            <a data-wa href="#" aria-label="WhatsApp">{icon('whatsapp', 19)}</a>
            <a data-mail href="mailto:{EMAIL}" aria-label="Email">{icon('mail', 19)}</a>
          </div>
        </div>
{cols_html}
        <div>
          <h4>Talk to us</h4>
          <ul>
            <li><a data-mail="text" href="mailto:{EMAIL}">{EMAIL}</a></li>
            <li><a data-tel="text" href="tel:+917666004531">{PHONE_DISPLAY}</a></li>
            <li><a data-wa href="#">WhatsApp us</a></li>
            <li><a data-ig href="{INSTAGRAM}">@allthings3d.in</a></li>
            <li style="margin-top:14px"><a href="order.html">Upload your idea &rarr;</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <span>&copy; <span data-year>2026</span> All Things 3D. Mumbai, India.</span>
        <span><a href="faq.html">FAQ</a> &nbsp;·&nbsp; <a href="contact.html">Contact</a> &nbsp;·&nbsp; <a href="order.html">Get a quote</a></span>
      </div>
    </div>
  </footer>"""


JSONLD = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "All Things 3D",
    "slogan": "Because your ideas deserve to exist",
    "description": "Custom 3D printing in Mumbai — corporate orders, end-to-end product development, contract manufacturing, bulk orders and OEM white-label production.",
    "url": "https://allthings3d.com",
    "email": "info.allthings3d@gmail.com",
    "telephone": "+91-76660-04531",
    "image": "https://allthings3d.com/assets/img/logo/atd-logo-full-transparent.png",
    "logo": "https://allthings3d.com/assets/img/logo/atd-logo-horizontal-transparent.png",
    "address": { "@type": "PostalAddress", "addressLocality": "Mumbai", "addressRegion": "Maharashtra", "addressCountry": "IN" },
    "areaServed": "IN",
    "sameAs": ["https://www.instagram.com/allthings3d.in"],
    "priceRange": "₹₹"
  }
  </script>"""


def page(slug, title, description, body, extra_js="", active=None, og_type="website"):
    active = active if active is not None else slug
    canonical = f"{DOMAIN}/" if slug == "index.html" else f"{DOMAIN}/{slug}"
    scripts = '\n  <script src="assets/js/atd-3d.js" defer></script>\n  <script src="assets/js/atd.js" defer></script>'
    if extra_js:
        scripts += f'\n  <script src="{extra_js}" defer></script>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#0166AE">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="All Things 3D">
  <meta property="og:image" content="{DOMAIN}/assets/img/logo/atd-logo-full-transparent.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/img/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="assets/img/favicon.png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
  <link rel="stylesheet" href="assets/css/atd.css">
{JSONLD}{scripts}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
{nav_html(active)}
  <main id="main">
{body}
  </main>
{footer_html()}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Reusable blocks
# --------------------------------------------------------------------------
def pagehead(crumb, eyebrow, h1, lede):
    return f"""    <section class="pagehead">
      <div class="shell">
        <p class="crumbs"><a href="index.html">Home</a> &nbsp;/&nbsp; {crumb}</p>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p>{lede}</p>
      </div>
    </section>"""


def cta_band(title="Tell us what you want to make.",
             text="Send a sketch, a photo, a CAD file or just a paragraph describing it. "
                  "You get a feasibility check and a price back within one working day.",
             primary=("order.html", "Upload your idea")):
    return f"""    <section class="section section--blue cta-band">
      <div class="shell center">
        <p class="eyebrow">Start here</p>
        <h2>{title}</h2>
        <p class="lede">{text}</p>
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn--ember" href="{primary[0]}">{primary[1]} {ARROW}</a>
          <a class="btn btn--onDark" data-wa href="#">WhatsApp us {icon('whatsapp', 17)}</a>
        </div>
      </div>
    </section>"""


def card(icon_name, title, text, num=None, dark=False, tilt=True):
    cls = "card tilt" if tilt else "card"
    if dark:
        cls += " card--dark"
    numhtml = f'<span class="card__num">{num}</span>' if num else ""
    return f"""        <article class="{cls} reveal">
          {numhtml}<div class="card__icon">{icon(icon_name, 25)}</div>
          <h3>{title}</h3>
          <p>{text}</p>
        </article>"""


def tile(model, kicker, title, text, cat="all", spin="0.7"):
    return f"""        <article class="tile reveal" data-cat="{cat}">
          <div class="tile__art"><canvas data-model="{model}" data-spin="{spin}" aria-hidden="true"></canvas></div>
          <div class="tile__body">
            <span class="tile__kicker">{kicker}</span>
            <h3>{title}</h3>
            <p>{text}</p>
          </div>
        </article>"""


def acc(items, start_open=0):
    out = ['      <div class="acc reveal">']
    for i, (q, a) in enumerate(items):
        open_cls = " is-open" if i == start_open else ""
        expanded = "true" if i == start_open else "false"
        paras = "".join(f"<p>{p}</p>" for p in ([a] if isinstance(a, str) else a))
        out.append(f"""        <div class="acc__item{open_cls}">
          <h3 style="margin:0"><button class="acc__q" type="button" aria-expanded="{expanded}">{q}</button></h3>
          <div class="acc__a"><div>{paras}</div></div>
        </div>""")
    out.append("      </div>")
    return "\n".join(out)


def table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"""      <div class="table-wrap reveal">
        <table>
          <thead><tr>{th}</tr></thead>
          <tbody>{trs}</tbody>
        </table>
      </div>"""


def steps_block(items, dark=False):
    out = ['      <div class="steps">', '        <div class="steps__fill"></div>']
    for i, (t, d) in enumerate(items, 1):
        out.append(f"""        <div class="step reveal">
          <div class="step__dot">{i:02d}</div>
          <div><h3>{t}</h3><p>{d}</p></div>
        </div>""")
    out.append("      </div>")
    return "\n".join(out)


MARQUEE_ITEMS = [
    "FDM printing", "Resin / SLA detail", "Lithophane lamps", "Corporate gifting",
    "Contract manufacturing", "OEM &amp; white-label", "Bulk orders", "3D scanning to print",
    "CAD &amp; design", "Rapid prototyping", "Jigs &amp; fixtures", "Short-run production",
    "Post-processing &amp; paint", "Packaging &amp; dispatch",
]


def marquee():
    items = "".join(f'<span class="marquee__item">{t}</span>' for t in MARQUEE_ITEMS)
    return f"""    <div class="marquee" aria-hidden="true">
      <div class="marquee__track"><div class="marquee__group">{items}</div></div>
    </div>"""


# ==========================================================================
# PAGE: HOME
# ==========================================================================
HOME = f"""    <section class="hero">
      <div class="shell hero__grid">
        <div>
          <p class="hero__badge"><span class="dot"></span> Mumbai &nbsp;·&nbsp; Shipping across India</p>
          <h1>If you can imagine it,<br><span class="grad">we can print it.</span></h1>
          <p class="hero__lede">Upload a photo, a sketch, a CAD file — or just tell us the idea in a sentence.
            We handle design, printing, finishing and delivery. One piece or ten thousand.</p>
          <div class="btn-row" style="margin-top:30px">
            <a class="btn btn--ember" href="order.html">Upload your idea {ARROW}</a>
            <a class="btn btn--onDark" href="products.html">See what we make</a>
          </div>
          <div class="hero__stats">
            <div class="hero__stat"><b data-count="24" data-suffix="h">24h</b><span>Quote turnaround</span></div>
            <div class="hero__stat"><b data-count="10" data-suffix="+">10+</b><span>Materials</span></div>
            <div class="hero__stat"><b>1 pc</b><span>Minimum order</span></div>
            <div class="hero__stat"><b>7&ndash;10</b><span>Days typical lead</span></div>
          </div>
        </div>
        <div>
          <div class="stage reveal">
            <span class="stage__tag">Live print preview</span>
            <canvas id="heroPrint" aria-label="Animation of an object being 3D printed layer by layer"></canvas>
            <div class="stage__hud">
              <span>Model <b id="hudName">Twisted vase</b></span>
              <span>Layer <b id="hudLayer">0/54</b></span>
              <span><b id="hudPct">0%</b></span>
            </div>
          </div>
        </div>
      </div>
    </section>

{marquee()}

    <section class="section section--mist">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">What we do</p>
          <h2>One workshop, from a single keepsake to a production run</h2>
          <p class="lede">Most people find us for a gift. Most businesses stay for the manufacturing.
            Both start the same way — you send us the idea, we tell you exactly what it will cost and how long it takes.</p>
        </div>
        <div class="grid grid--3">
{card('gift', 'Corporate orders', 'Branded gifting, awards, desk pieces, event giveaways and onboarding kits — designed around your logo and produced to a deadline you can plan around.')}
{card('spark', 'End-to-end product development', 'Napkin sketch to shelf-ready product. Concept, CAD, prototype, iteration, tooling-free production and packaging, all under one roof.')}
{card('factory', 'Contract manufacturing', 'You own the design, we own the machines. Recurring production of your parts to a fixed spec, drawing and quality standard.')}
{card('box', 'Bulk orders', 'Hundreds to thousands of identical pieces at per-unit rates that fall as volume rises. Staggered dispatch if you would rather not warehouse it all.')}
{card('layers', 'OEM &amp; white-label', 'Printed, finished and packed under your brand. Your box, your insert, your label — no mention of us anywhere in it.')}
{card('pencil', 'Custom one-offs', 'Lithophane lamps, keepsakes, replacement parts, cosplay props, models. The pieces that only exist because somebody asked.')}
        </div>
        <div class="center" style="margin-top:34px">
          <a class="link-arrow reveal" href="services.html">See how each one works {ARROW}</a>
        </div>
      </div>
    </section>

    <section class="section section--white">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">The simple version</p>
            <h2>Three steps. No jargon.</h2>
            <p class="lede">You do not need a CAD file, a technical drawing, or any idea what PETG is.
              If you can describe it or show us a picture of it, that is enough to start.</p>
            <div class="note" style="margin:24px 0">
              <strong>No file? No problem.</strong> Roughly half of what leaves our workshop started as a
              WhatsApp photo or a hand sketch. We model it for you and show you a render before anything is printed.
            </div>
            <div class="btn-row">
              <a class="btn" href="order.html">Start your order</a>
              <a class="btn btn--ghost" href="faq.html">Read the FAQ</a>
            </div>
          </div>
          <div>
{steps_block([
  ('Send us the idea', 'A photo, a sketch, a link, an STL, a paragraph. Whatever you have. Upload it on the order page or send it straight to WhatsApp.'),
  ('We come back with a price', 'Within one working day: whether it can be printed, the material we recommend, the finish, the lead time and a firm quote.'),
  ('It gets made and delivered', 'You approve, we print, finish and quality-check it, then it ships anywhere in India. Bulk orders can be staggered across dates.'),
])}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--cloud">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">Products</p>
          <h2>A sample of what comes off the bed</h2>
          <p class="lede">Every one of these started as somebody's idea. Hover a piece to spin it.</p>
        </div>
        <div class="tiles">
{tile('lamp', 'Personalised', 'Lithophane lamps &amp; frames', 'Your photograph, printed as a thin panel that reveals itself in full detail the moment the light goes on.')}
{tile('tag', 'Gifting', 'Keychains &amp; name tags', 'Names, logos, dates, QR codes. The easiest first order, and the one that turns into a bulk order.')}
{tile('gear', 'Functional', 'Working parts &amp; spares', 'Gears, brackets, housings, jigs and the discontinued part nobody stocks any more.')}
{tile('figurine', 'Keepsakes', 'Figurines &amp; miniatures', 'Characters, mascots, cake toppers, wedding couples and gaming miniatures in fine-detail resin.')}
{tile('planter', 'Home', 'Planters &amp; decor', 'Vases, planters, lamp shades, wall panels and organisers in a finish that suits the room.')}
{tile('dome', 'Professional', 'Architectural models', 'Massing models, site plans and presentation pieces at the scale your client needs to see.')}
        </div>
        <div class="center" style="margin-top:36px">
          <a class="btn btn--ghost reveal" href="products.html">Browse all products {ARROW}</a>
        </div>
      </div>
    </section>

    <section class="section section--dark">
      <div class="shell">
        <div class="split split--rev">
          <div class="reveal">
            <p class="eyebrow">For business</p>
            <h2>Manufacturing without the tooling bill</h2>
            <p class="lede">Injection moulding makes sense at fifty thousand pieces. Below that, the mould
              costs more than the parts. 3D printing skips the tooling entirely — so a design change on Tuesday
              is in production on Wednesday, and a run of two hundred is genuinely viable.</p>
            <ul class="stack-sm" style="list-style:none;padding:0;margin:22px 0">
              <li>{icon('check', 18)} &nbsp;No mould cost, no minimum of ten thousand</li>
              <li>{icon('check', 18)} &nbsp;Design revisions between batches at no tooling penalty</li>
              <li>{icon('check', 18)} &nbsp;NDA signed before your files ever open</li>
              <li>{icon('check', 18)} &nbsp;Consistent spec, batch after batch, with dimensional checks</li>
            </ul>
            <div class="btn-row">
              <a class="btn" href="oem.html">OEM &amp; bulk orders {ARROW}</a>
              <a class="btn btn--onDark" href="capabilities.html">Machines &amp; materials</a>
            </div>
          </div>
          <div class="grid grid--2">
{card('lock', 'Confidential by default', 'Mutual NDA on request before any file is opened. Your designs are never shown as our work without written permission.', dark=True)}
{card('shield', 'Checked, not hoped', 'Dimensional check against your drawing, fit test where a mating part exists, and a photo set before dispatch.', dark=True)}
{card('chart', 'Pricing that falls with volume', 'Per-unit rates step down at 10, 25, 50, 100, 250 and 500 pieces. The quote shows every break.', dark=True)}
{card('truck', 'Delivered on a date', 'Committed dispatch dates, staggered deliveries for large runs, and dispatch photos for every batch.', dark=True)}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--mist">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">Why people come back</p>
          <h2>The boring things, done properly</h2>
        </div>
        <div class="stats reveal">
          <div class="stat"><b data-count="24" data-suffix="h">24h</b><span>Quote turnaround</span></div>
          <div class="stat"><b data-count="10" data-suffix="+">10+</b><span>Materials in stock</span></div>
          <div class="stat"><b data-count="0.05" data-suffix=" mm">0.05 mm</b><span>Finest layer</span></div>
          <div class="stat"><b>1&ndash;10k</b><span>Order size range</span></div>
        </div>
        <div class="grid grid--3" style="margin-top:24px">
{card('clock', 'We answer', 'An enquiry that goes unanswered for four days is a lost job for you as much as for us. Ours come back within one working day, with a real answer.')}
{card('search', 'We tell you when it is a bad idea', 'If a wall is too thin to survive shipping, or resin is wrong for a part that lives in a car, you hear it before you pay, not after.')}
{card('wrench', 'We fix it if it is wrong', 'A part that does not match the approved spec gets reprinted at our cost. That is the whole policy.')}
        </div>
      </div>
    </section>

    <section class="section section--sand section--tight">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">Common questions</p>
          <h2>Before you ask</h2>
        </div>
{acc([
  ('I do not have a 3D file. Can you still make it?',
   'Yes, and that is most orders. Send a photograph, a sketch on paper, a product link or a written description. We build the 3D model for you and share a render for approval before printing. Modelling is quoted separately only when the part is complex — simple pieces are usually absorbed into the job.'),
  ('What is the smallest order you accept?',
   'One piece. There is no minimum quantity. There is a minimum order value so that a two-rupee keychain does not cost us more in packing than it earns, and it is small.'),
  ('How long does it take?',
   'Typically 7 to 10 working days from design approval for a normal order. Simple pieces already modelled can be faster; large bulk runs and painted finishes take longer. You get a committed date with the quote, not an estimate.'),
  ('Can you match a specific colour or brand palette?',
   'Within reason on raw filament, and closely on painted parts. For brand-critical colours we paint to a supplied reference and send a photo of the sample before the batch runs.'),
  ('Do you sign NDAs?',
   'Yes. For product development, contract manufacturing and OEM work we will sign yours, or send ours, before any file is opened.'),
])}
        <div class="center" style="margin-top:26px">
          <a class="link-arrow reveal" href="faq.html">All questions answered {ARROW}</a>
        </div>
      </div>
    </section>

{cta_band()}
"""

# ==========================================================================
# PAGE: PRODUCTS
# ==========================================================================
PRODUCT_ROWS = [
    ("lamp", "Signature", "Lithophane lamps &amp; photo frames",
     "A photograph printed as a graded panel — flat and pale in daylight, then astonishing when it is backlit. "
     "Made as table lamps, night lights, heart and arch frames, keyrings and moon lamps. The single most "
     "given gift that leaves this workshop, and the one people photograph and send back to us."),
    ("tag", "Everyday", "Keychains, name tags &amp; badges",
     "Names, initials, logos, dates, registration numbers, QR codes that actually scan. Single pieces for a "
     "gift, or five hundred for a conference. Two-colour printing means the text is a different colour to the "
     "body without a drop of paint."),
    ("nameplate", "Home &amp; office", "Nameplates, signage &amp; wall art",
     "Door nameplates, house numbers, reception signage, layered wall panels and 3D typography. Printed in "
     "wood-fill, metal-fill or painted finishes so it reads as a made object rather than a printed one."),
    ("figurine", "Keepsakes", "Figurines, miniatures &amp; cake toppers",
     "Wedding couples, mascots, pets, gaming miniatures, anime and comic characters, cricket trophies. "
     "Fine-detail resin where the face matters; painted by hand where you want it finished."),
    ("planter", "Living", "Planters, vases &amp; organisers",
     "Geometric planters, spiral vases, desk organisers, cable trays and drawer inserts. Printed in one piece, "
     "in a size that suits your shelf rather than whatever the shop had."),
    ("gear", "Functional", "Working parts, spares &amp; enclosures",
     "The knob that snapped, the bracket that does not exist, the housing for your electronics, the gear for a "
     "machine whose manufacturer stopped answering in 2011. Printed in PETG, ABS or nylon so it survives real use."),
    ("bracket", "Industrial", "Jigs, fixtures &amp; assembly aids",
     "Drill guides, alignment jigs, soft jaws, go/no-go gauges, packing formers and line fixtures. The parts "
     "that pay for themselves in a fortnight of saved assembly time."),
    ("dome", "Professional", "Architectural &amp; scale models",
     "Massing models, site plans, sectional models, terrain and presentation pieces for architects, developers "
     "and students. Printed to a stated scale, in matte white or painted to your scheme."),
    ("ring", "Fashion", "Jewellery, bangles &amp; accessories",
     "Statement pieces, lightweight bangles, pendants, hair accessories and costume jewellery in resin or "
     "metal-look finishes. Also masters for casting when the final piece is going into metal."),
    ("vase", "Events", "Wedding &amp; event favours",
     "Personalised favours at guest-list quantities: hampers tags, place-card holders, mandap miniatures, "
     "return gifts and save-the-date pieces. Priced per piece, delivered before the date, not on it."),
]


def product_rows():
    out = []
    for i, (model, kicker, title, text) in enumerate(PRODUCT_ROWS):
        rev = " split--rev" if i % 2 else ""
        out.append(f"""      <div class="split{rev}" style="margin-bottom:clamp(48px,7vw,88px)">
        <div class="reveal">
          <p class="eyebrow">{kicker}</p>
          <h2 style="font-size:clamp(24px,3.4vw,34px)">{title}</h2>
          <p>{text}</p>
          <a class="link-arrow" href="order.html">Get this quoted {ARROW}</a>
        </div>
        <div class="tile tile--solo reveal" style="max-width:460px">
          <div class="tile__art" style="aspect-ratio:1/1"><canvas data-model="{model}" data-spin="{0.4 + i * 0.3:.1f}" aria-hidden="true"></canvas></div>
        </div>
      </div>""")
    return "\n".join(out)


PRODUCTS = f"""{pagehead('Products', 'Products', 'Everything on this page started as somebody&rsquo;s idea',
  'This is not a catalogue you order from — it is a sample of what has been made. If the thing you want is not here, that is the normal case, not the exception. Send it over.')}

{marquee()}

    <section class="section section--mist">
      <div class="shell">
{product_rows()}
      </div>
    </section>

    <section class="section section--white section--tight">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">Not listed?</p>
          <h2>That is the usual case</h2>
          <p class="lede">Restoration parts, medical models, prosthetic aids, RC and drone components, camera rigs,
            aquarium fittings, kitchen gadgets, museum replicas, teaching aids, packaging prototypes, stall props.
            If it fits on a print bed — and often when it does not, because we print it in sections and join it — it can be made.</p>
          <div class="btn-row center" style="margin-top:24px">
            <a class="btn btn--ember" href="order.html">Describe what you want {ARROW}</a>
          </div>
        </div>
      </div>
    </section>

{cta_band('Send the idea. We will tell you if it works.',
          'Feasibility, material recommendation, finish options and a firm price — back with you inside one working day.')}
"""

# ==========================================================================
# PAGE: SERVICES
# ==========================================================================
SERVICES = f"""{pagehead('Services', 'Services', 'Five ways businesses use us',
  'Corporate orders, end-to-end product development, contract manufacturing, bulk orders and OEM. Same workshop, same people, different commercial shape.')}

    <section class="section section--mist" id="corporate">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">01 &nbsp;·&nbsp; Corporate orders</p>
            <h2>Gifting your team will not quietly leave behind</h2>
            <p class="lede">Branded pieces made for your company rather than bought with your logo stuck on afterwards.</p>
            <p>Onboarding kits, milestone awards, Diwali and new-year gifting, conference giveaways, desk pieces,
              trophies, dealer recognition, client hampers. We work from your logo files and brand palette, produce a
              sample for sign-off, then run the quantity to a committed date.</p>
            <p><b>Typical run:</b> 25 to 2,000 pieces. <b>Lead time:</b> 2 to 4 weeks including sample approval.
              <b>Comes with:</b> individual polybagging, custom inserts and boxes, name personalisation per piece if you want it.</p>
            <div class="btn-row"><a class="btn" href="order.html">Brief us on a gifting run {ARROW}</a></div>
          </div>
          <div class="grid grid--2">
{card('gift', 'Personalised per recipient', 'Every piece can carry a different name, date or employee ID at no extra setup — the machine does not care that piece 340 says something different.')}
{card('box', 'Packed and ready to hand out', 'Sleeved, boxed, labelled and sorted by branch or department, so nobody spends a Saturday packing them.')}
{card('pencil', 'Designed, not just printed', 'If you have a concept, we refine it. If you have only a logo, we design around it and show you three directions.')}
{card('clock', 'Dated, not estimated', 'Corporate gifting has a date attached to it. Yours gets a committed dispatch date in writing on the quotation.')}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--white" id="development">
      <div class="shell">
        <div class="split split--rev">
          <div class="reveal">
            <p class="eyebrow">02 &nbsp;·&nbsp; End-to-end product development</p>
            <h2>From a sketch on the back of a bill to something you can sell</h2>
            <p class="lede">The whole path, with one team accountable for it — so nothing gets lost between the designer, the printer and the packer.</p>
            <p>Most people who come to us with a product idea have a clear picture in their head and no drawing.
              We turn that into CAD, print a first physical prototype, put it in your hands, and change it until it is right.
              Then we produce it — without a mould, so the tenth revision costs no more than the first.</p>
            <div class="note" style="margin:22px 0"><strong>Where this saves real money:</strong>
              tooling for injection moulding runs into lakhs and locks the design. Printed production lets you launch,
              sell a few hundred, learn what is wrong, and fix it before committing to a mould — if you ever need one at all.</div>
            <div class="btn-row"><a class="btn" href="order.html">Talk through an idea {ARROW}</a></div>
          </div>
          <div>
{steps_block([
  ('Discovery', 'What it must do, who buys it, what it can cost to make, and the constraints that are non-negotiable.'),
  ('Concept &amp; CAD', 'Sketch directions, then a parametric 3D model. You see renders before anything is printed.'),
  ('Prototype', 'A physical part in your hands, usually within days. This is where most assumptions quietly change.'),
  ('Iterate', 'Revise, reprint, retest. As many rounds as the design needs — there is no tooling to write off.'),
  ('Pilot run', 'A small batch to a final spec, so you can sell, test the market and get real feedback.'),
  ('Production', 'Repeat batches to a frozen spec, with packaging, labelling and dispatch handled here.'),
])}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--dark" id="contract">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">03 &nbsp;·&nbsp; Contract manufacturing</p>
            <h2>Your design, our machines, your schedule</h2>
            <p class="lede">For companies who already have the drawing and need it made, repeatedly, without buying a printer farm and hiring someone to run it.</p>
            <p>You send the file and the specification. We agree the material, tolerance, finish and inspection
              standard once, freeze it as a control document, and every batch after that is measured against it.
              Reorder by email; the spec does not drift.</p>
            <ul class="stack-sm" style="list-style:none;padding:0;margin:22px 0">
              <li>{icon('check', 18)} &nbsp;Fixed spec sheet agreed before the first batch</li>
              <li>{icon('check', 18)} &nbsp;Dimensional inspection against your drawing, batch by batch</li>
              <li>{icon('check', 18)} &nbsp;Held stock and call-off schedules for regular volumes</li>
              <li>{icon('check', 18)} &nbsp;GST invoicing, delivery challans and documentation your accounts team expects</li>
            </ul>
            <div class="btn-row"><a class="btn" href="order.html">Send a drawing {ARROW}</a>
              <a class="btn btn--onDark" href="capabilities.html">See tolerances</a></div>
          </div>
          <div class="grid grid--2">
{card('shield', 'Repeatability', 'The same printer profile, the same filament batch where possible, the same operator checklist. Batch 9 matches batch 1.', dark=True)}
{card('lock', 'Your IP stays yours', 'NDA first. Your files are not reused, not shown, and not printed for anyone else.', dark=True)}
{card('truck', 'Call-off delivery', 'Produce once, deliver in instalments against your schedule instead of filling your store room.', dark=True)}
{card('chart', 'Costed openly', 'Material, machine time and finishing are itemised so you can see exactly what a design change would save.', dark=True)}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--cloud" id="bulk">
      <div class="shell">
        <div class="split split--rev">
          <div class="reveal">
            <p class="eyebrow">04 &nbsp;·&nbsp; Bulk orders</p>
            <h2>Per-unit prices that fall as the quantity rises</h2>
            <p class="lede">Hundreds to thousands of identical pieces, printed in parallel across the farm and delivered on a schedule you set.</p>
            <p>Volume changes the economics in your favour: setup is amortised, machines run continuously, and
              material is bought in for the job. The quotation shows every price break so you can decide whether
              stretching from 400 to 500 pieces is worth it — usually it is.</p>
            <div class="btn-row"><a class="btn" href="oem.html">Bulk pricing &amp; MOQs {ARROW}</a></div>
          </div>
          <div>
{table(['Quantity', 'Indicative per-unit', 'Typical use'], [
  ['1 &ndash; 9', 'Base rate', 'Samples, one-offs, prototypes'],
  ['10 &ndash; 24', '&minus;12%', 'Small gifting sets, test batches'],
  ['25 &ndash; 49', '&minus;20%', 'Event giveaways, dealer gifts'],
  ['50 &ndash; 99', '&minus;28%', 'Team gifting, retail first run'],
  ['100 &ndash; 249', '&minus;36%', 'Conference kits, product launches'],
  ['250 &ndash; 499', '&minus;44%', 'Retail production, distributor stock'],
  ['500 +', '&minus;52%', 'Full production runs, OEM supply'],
])}
            <p class="muted" style="font-size:14.5px;margin-top:14px">Indicative only. The real number depends on part size,
              material, finish and how efficiently the piece nests on a bed — send the file and the quotation will be exact.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--white" id="oem">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">05 &nbsp;·&nbsp; OEM &amp; white-label</p>
            <h2>Made here. Sold as yours.</h2>
            <p class="lede">Your brand on the product, your box, your insert, your label. Nothing in the package says All Things 3D.</p>
            <p>Retailers, gifting companies, design studios and e-commerce brands use us as the workshop behind
              their catalogue. You take the order, we make and pack it — including drop-shipping directly to your
              customer with your branding on the parcel if that suits your model better.</p>
            <div class="btn-row"><a class="btn btn--ember" href="oem.html">The full OEM page {ARROW}</a></div>
          </div>
          <div class="grid grid--2">
{card('tag', 'Your branding throughout', 'Embossed or printed logo on the part, your packaging, your care card, your barcode label.')}
{card('truck', 'Blind drop-ship', 'Parcels go straight to your customer with your name as sender. We never appear in the transaction.')}
{card('layers', 'Catalogue support', 'Product photography of the pieces we make for you, ready for your listings and lookbook.')}
{card('lock', 'Exclusivity where agreed', 'A design developed for you can be contracted as exclusive to you. Put it in writing and we will hold it.')}
          </div>
        </div>
      </div>
    </section>

{cta_band('Which of the five is yours?',
          'If you are not sure, describe the job in a sentence and we will tell you which shape fits and what it costs.')}
"""

# ==========================================================================
# PAGE: OEM
# ==========================================================================
OEM = f"""{pagehead('OEM &amp; Bulk', 'OEM · Bulk · Contract', 'The workshop behind other people&rsquo;s brands',
  'White-label production, contract manufacturing and bulk supply — with an NDA, a frozen specification, price breaks that reward volume, and packaging that carries your name instead of ours.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="grid grid--4">
{card('lock', 'NDA first', 'Signed before your files are opened. Yours or ours, whichever your legal team prefers.')}
{card('layers', 'White-label', 'Your logo on the part, your box, your insert. Nothing identifies us.')}
{card('chart', 'Volume pricing', 'Seven price breaks from 10 pieces to 500+. Every break shown on the quote.')}
{card('truck', 'Blind dispatch', 'Drop-shipped to your customer under your brand, with tracking passed back to you.')}
        </div>
      </div>
    </section>

    <section class="section section--white">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">How an OEM engagement runs</p>
          <h2>Six stages, and you always know which one you are in</h2>
        </div>
        <div class="split">
          <div>
{steps_block([
  ('NDA and brief', 'Mutual NDA, then a written brief: what the part is, quantities, target landed cost, packaging and the date it must exist by.'),
  ('Feasibility and costing', 'We confirm it is printable at your target cost, or tell you what would have to change. You get a costed quotation with volume breaks.'),
  ('Golden sample', 'One approved physical piece, photographed and measured. It becomes the reference every batch is judged against.'),
  ('Specification freeze', 'Material, colour, layer height, infill, finish, tolerance, packaging and inspection points, written down and signed.'),
  ('Pilot batch', 'A small production run against the frozen spec, inspected and dispatched, to prove the process before the volume commits.'),
  ('Rolling production', 'Repeat batches on your call-off schedule, each with an inspection record and dispatch photographs.'),
])}
          </div>
          <div class="reveal">
            <div class="card card--flat" style="margin-bottom:20px">
              <h3>What we need from you</h3>
              <ul class="stack-sm">
                <li>The 3D file (STL, STEP, OBJ or 3MF) — or a sample part we can measure and model</li>
                <li>A drawing or note marking any dimension that is critical, and to what tolerance</li>
                <li>Quantity, and whether it is one-off, recurring or a call-off schedule</li>
                <li>Colour, finish and any brand-critical reference</li>
                <li>Packaging requirement — bulk, individually bagged, boxed, or your own artwork</li>
                <li>The date it must be delivered by, and whether that date is hard</li>
              </ul>
            </div>
            <div class="note note--ember">
              <strong>Vendor registration.</strong> If your company needs us on your approved-vendor list first,
              ask and we will send the GST registration, PAN, bank details and a company profile in whatever
              format your procurement portal wants.
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--dark" id="bulk">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">Bulk orders</p>
          <h2>What volume actually changes</h2>
          <p class="lede">Three things drive the per-unit price: how long a piece occupies a machine, how much
            material it eats, and how much handling it needs afterwards. Volume attacks all three.</p>
        </div>
        <div class="grid grid--3">
{card('layers', 'Nesting', 'At quantity we lay parts out to fill the bed rather than printing them one at a time. The same eight hours produces twelve pieces instead of one.', dark=True)}
{card('box', 'Material buying', 'Filament and resin bought in for a specific run costs less per kilo than stock pulled off the shelf.', dark=True)}
{card('wrench', 'Setup amortised', 'File prep, slicing, test print and first-article inspection are a fixed cost. Across 500 pieces it disappears.', dark=True)}
        </div>
        <div style="margin-top:34px">
{table(['Break', 'Per-unit', 'Setup', 'Typical dispatch'], [
  ['10 pcs', '&minus;12%', 'Charged once', '5 &ndash; 8 working days'],
  ['25 pcs', '&minus;20%', 'Charged once', '7 &ndash; 10 working days'],
  ['50 pcs', '&minus;28%', 'Charged once', '10 &ndash; 14 working days'],
  ['100 pcs', '&minus;36%', 'Waived', '2 &ndash; 3 weeks'],
  ['250 pcs', '&minus;44%', 'Waived', '3 &ndash; 4 weeks, staggered'],
  ['500 pcs', '&minus;52%', 'Waived', '4 &ndash; 6 weeks, staggered'],
  ['1,000 pcs +', 'Quoted individually', 'Waived', 'Scheduled against your calendar'],
])}
        <p class="muted" style="font-size:14.5px;margin-top:14px">Indicative structure, not a rate card. Send the part and the
          quantity and you will get real numbers — small parts often beat these breaks, large ones can fall short of them.</p>
        </div>
      </div>
    </section>

    <section class="section section--cloud">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">Straight answers</p>
          <h2>The questions procurement always asks</h2>
        </div>
{acc([
  ('Will anything identify you as the manufacturer?',
   'No. On a white-label order the part carries your mark or none at all, the packaging is yours, and dispatch documents show your brand as sender. We do not insert cards, stickers or QR codes of our own.'),
  ('Can we get exclusivity on a design you develop for us?',
   'Yes, where it is agreed in writing before development starts. A design commissioned and paid for by you is not offered to anyone else. Designs that already existed in our catalogue before you asked are not exclusive.'),
  ('What happens if a batch fails inspection?',
   'It is reprinted at our cost and the dispatch date is protected wherever the schedule allows. If it cannot be, you hear about it the day we know, not the day it was due.'),
  ('Do you hold stock for us?',
   'For recurring orders, yes. We produce to an agreed level and release against your call-offs. Storage terms are agreed as part of the contract.'),
  ('What are the payment terms?',
   'For first orders, an advance against a proforma invoice with the balance before dispatch. For established accounts and repeat production, terms are agreed case by case. Everything is GST-invoiced.'),
  ('Can you handle assembly, inserts or mixed-material parts?',
   'Yes — heat-set threaded inserts, magnets, fasteners, multi-part assembly and packing of kits are all normal work here. Specify it in the brief and it is priced as part of the piece.'),
])}
      </div>
    </section>

{cta_band('Send us a part and a quantity.',
          'NDA, feasibility check and a costed quotation with volume breaks — back inside one working day.',
          ('order.html', 'Start an OEM enquiry'))}
"""

# ==========================================================================
# PAGE: CAPABILITIES
# ==========================================================================
CAPABILITIES = f"""{pagehead('Capabilities', 'Machines · Materials · Tolerances', 'What the workshop can actually do',
  'The honest version: what we print on, what we print with, how accurate it is, and where 3D printing is the wrong answer.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="grid grid--2">
{card('layers', 'FDM &mdash; fused filament', 'The workhorse. Strong, economical, available in a wide range of engineering and decorative filaments. Best for functional parts, larger pieces, jigs, enclosures and volume gifting. Layer heights from 0.08 to 0.32 mm.')}
{card('spark', 'Resin &mdash; SLA / MSLA', 'For detail the eye can see. Miniatures, jewellery masters, dental and medical models, textured surfaces and anything where a layer line would ruin it. Layer heights from 0.02 to 0.05 mm.')}
        </div>
      </div>
    </section>

    <section class="section section--white">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">Materials</p>
          <h2>Pick by what the part has to survive</h2>
          <p class="lede">Most people over-specify. A desk piece does not need nylon; a part that lives in a
            parked car in May absolutely does not want PLA. This is the short version of that conversation.</p>
        </div>
{table(['Material', 'Choose it for', 'Watch out for', 'Heat limit'], [
  ['PLA', 'Display pieces, gifting, models, lithophanes. Best surface finish, widest colour range.', 'Softens in a hot car or direct summer sun. Not for load-bearing outdoor use.', '~55&nbsp;&deg;C'],
  ['PETG', 'Everyday functional parts, enclosures, brackets, anything that lives outdoors.', 'Slightly softer detail than PLA; stringing on fine features.', '~75&nbsp;&deg;C'],
  ['ABS / ASA', 'Automotive, tooling, parts that see heat or UV. ASA holds colour outdoors.', 'Can warp on large flat parts; needs an enclosed printer.', '~95&nbsp;&deg;C'],
  ['TPU', 'Flexible parts, gaskets, grips, phone cases, shock mounts.', 'Slower to print, so unit cost is higher.', '~70&nbsp;&deg;C'],
  ['Nylon / PA-CF', 'Structural parts, gears, jigs, clips that must flex thousands of times.', 'Absorbs moisture; costlier. Reserved for parts that need it.', '~110&nbsp;&deg;C'],
  ['Wood &amp; metal fill', 'Nameplates, decor, awards — reads as a made object, not a printed one.', 'Abrasive on nozzles, so it carries a small surcharge.', '~55&nbsp;&deg;C'],
  ['Standard resin', 'Miniatures, jewellery, high-detail models, master patterns.', 'Brittle under impact; not for functional load.', '~60&nbsp;&deg;C'],
  ['Tough / ABS-like resin', 'Detail parts that also need to survive handling.', 'More expensive than standard resin.', '~70&nbsp;&deg;C'],
])}
      </div>
    </section>

    <section class="section section--cloud">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">Accuracy</p>
            <h2>What tolerance you can hold us to</h2>
            <p class="lede">Printed parts are not machined parts. These are the numbers we will put in writing —
              if your drawing needs tighter than this on a critical feature, tell us and we will either machine that
              feature after printing or tell you it is the wrong process.</p>
            <ul class="stack-sm" style="margin-top:20px">
              <li><b>FDM dimensional:</b> &plusmn;0.3&nbsp;mm or &plusmn;0.3% of the dimension, whichever is greater</li>
              <li><b>Resin dimensional:</b> &plusmn;0.1&nbsp;mm or &plusmn;0.15%, whichever is greater</li>
              <li><b>Minimum wall:</b> 1.2&nbsp;mm on FDM, 0.6&nbsp;mm on resin</li>
              <li><b>Minimum readable text:</b> 2.5&nbsp;mm embossed on FDM, 1&nbsp;mm on resin</li>
              <li><b>Holes:</b> print undersized by design; reamed or drilled to size when the fit is critical</li>
              <li><b>Threads:</b> heat-set brass inserts recommended over printed threads for anything that is undone more than once</li>
            </ul>
          </div>
          <div class="grid grid--2">
{card('box', 'Build volume', 'Up to 300 &times; 300 &times; 400 mm in a single FDM piece, and up to 220 &times; 120 &times; 250 mm in resin. Larger objects are split, printed in sections and joined — a joint line, planned properly, is invisible.')}
{card('search', 'Inspection', 'Vernier and micrometer checks against your drawing, fit tests against a mating part where one exists, and a photograph set with every dispatch.')}
{card('wrench', 'Post-processing', 'Support removal, sanding, priming, spray and hand painting, vapour smoothing on ABS, gluing and multi-part assembly, insert setting, polishing and clear coating.')}
{card('shield', 'Files we accept', 'STL, OBJ, 3MF, STEP, IGES, and native SolidWorks or Fusion files. Or a photo, a sketch, a drawing, a PDF, or the physical part itself for us to measure.')}
          </div>
        </div>
      </div>
    </section>

    <section class="section section--dark">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">Honesty section</p>
          <h2>When 3D printing is the wrong answer</h2>
          <p class="lede">We would rather lose a job than take one that was always going to disappoint you.</p>
        </div>
        <div class="grid grid--3">
{card('chart', 'Very high volumes', 'Past roughly ten to fifteen thousand identical simple parts, injection moulding usually wins on unit cost even after the tooling. We will say so — and we can print the pre-tooling pilot run that de-risks that mould.', dark=True)}
{card('shield', 'Food, skin and load-critical parts', 'Layer lines trap bacteria, and a printed part in a safety-critical load path is not something to guess at. We will suggest a food-safe liner, a coating, or a different process.', dark=True)}
{card('clock', 'Very large single pieces', 'Above the build volume, a part is printed in sections and bonded. That is often perfect — but if a seamless one-metre piece is the requirement, casting or fabrication is the honest answer.', dark=True)}
        </div>
      </div>
    </section>

{cta_band('Not sure which material or process?',
          'Send the part and how it will be used. The recommendation comes back with the quote, and it costs nothing.')}
"""

# ==========================================================================
# PAGE: GALLERY
# ==========================================================================
GALLERY_ITEMS = [
    ("lamp", "gifting personal", "Lithophane", "Backlit photo lamp", "A single photograph, graded into a 3 mm panel and lit from behind."),
    ("tag", "gifting corporate", "Keychain", "Logo keyring, 500-piece run", "Two-colour, individually bagged, delivered before the conference."),
    ("figurine", "personal", "Figurine", "Wedding cake topper", "Modelled from two photographs, printed in detail resin, hand painted."),
    ("gear", "functional industrial", "Spare part", "Discontinued drive gear", "Measured from the broken original, reprinted in nylon."),
    ("planter", "home", "Planter", "Faceted planter set", "Printed in one piece, sealed for indoor watering."),
    ("nameplate", "home corporate", "Signage", "Reception nameplate", "Layered, wood-fill body with brushed-metal lettering."),
    ("bracket", "functional industrial", "Fixture", "Assembly-line jig", "Cut assembly time on a repetitive station by a third."),
    ("dome", "professional", "Model", "Site massing model", "1:200 presentation model for a developer pitch."),
    ("ring", "personal", "Jewellery", "Statement bangle", "Resin master, cast in brass by the client's jeweller."),
    ("vase", "home gifting", "Decor", "Spiral vase", "Single-wall spiral print, watertight with a liner."),
    ("figurine", "corporate", "Award", "Annual sales trophy", "Custom trophy series, personalised per winner."),
    ("tag", "gifting", "Favour", "Wedding return gift", "350 personalised pieces, one per guest, named individually."),
]

GALLERY_FILTERS = [
    ("all", "Everything"), ("gifting", "Gifting"), ("corporate", "Corporate"),
    ("personal", "Personal"), ("functional", "Functional"),
    ("industrial", "Industrial"), ("home", "Home"), ("professional", "Professional"),
]


def gallery_body():
    fl = "".join(
        f'<button class="filter{" is-active" if k == "all" else ""}" data-filter="{k}">{lab}</button>'
        for k, lab in GALLERY_FILTERS)
    tiles = "\n".join(
        tile(m, k, t, d, cat=c, spin=f"{0.3 + i * 0.4:.1f}")
        for i, (m, c, k, t, d) in enumerate(GALLERY_ITEMS))
    return fl, tiles


_gf, _gt = gallery_body()

GALLERY = f"""{pagehead('Gallery', 'Selected work', 'Things that exist because somebody asked',
  'Hover any piece to spin it. These are representative of the categories we work in — the pieces themselves belong to the people who commissioned them.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="filters reveal">{_gf}</div>
        <div class="tiles">
{_gt}
        </div>
        <div class="note" style="margin-top:34px">
          <strong>Photographs coming soon.</strong> The shapes above are rendered live in your browser by the same
          little 3D engine that runs the animation on the home page. Real product photography from finished orders is
          being added — follow <a data-ig href="{INSTAGRAM}">@allthings3d.in</a> for the latest pieces as they come off the bed.
        </div>
      </div>
    </section>

{cta_band('Want yours in here?',
          'Send us the idea and it starts the same way every piece above did — a photo, a sketch, or a sentence.')}
"""

# ==========================================================================
# PAGE: ORDER
# ==========================================================================
ORDER = f"""{pagehead('Upload your idea', 'Upload · Quote · Print', 'Upload your idea',
  'Drop a 3D file and watch it render right here, or just describe what you want. Either way you get a real price and a real date back within one working day.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="split" style="align-items:stretch">
          <div class="reveal">
            <form id="orderForm" novalidate>
              <div class="card card--flat" style="margin-bottom:22px">
                <p class="eyebrow" style="margin-bottom:10px">Step 1</p>
                <h3>Your file, or your idea</h3>
                <p class="muted" style="font-size:15px">STL and OBJ files preview instantly below and measure themselves.
                  STEP, 3MF, images, PDFs and ZIPs are accepted too — we just open them at our end.</p>
                <div class="dropzone" id="dropzone">
                  <div class="dropzone__icon">{icon('upload', 34)}</div>
                  <strong>Drop a file here, or tap to browse</strong>
                  <small>STL · OBJ · 3MF · STEP · JPG · PNG · PDF · ZIP</small>
                  <input type="file" id="fileInput" name="file" accept=".stl,.obj,.3mf,.step,.stp,.igs,.iges,.jpg,.jpeg,.png,.pdf,.zip,.svg,.dxf">
                </div>
                <p class="mono hidden" id="fileLabel" style="margin:12px 0 0;font-size:13px;color:var(--blue-700)"></p>

                <div class="viewer" id="viewer">
                  <canvas id="viewerCanvas"></canvas>
                  <div class="viewer__hint" id="viewerHint">Your model appears here</div>
                  <div class="viewer__meta hidden" id="viewerMeta"></div>
                </div>

                <div class="field" style="margin-top:20px">
                  <label for="brief">Tell us about it</label>
                  <span class="hint">What it is, what it is for, how it will be used, and anything that must be exact.
                    If you have no file at all, describe it here — that is enough to start.</span>
                  <textarea id="brief" name="brief_text" placeholder="Example: I want 120 keychains with our company logo and each person's name on the back, for a sales conference on the 14th of next month. Blue and white if possible."></textarea>
                </div>
              </div>

              <div class="card card--flat" style="margin-bottom:22px">
                <p class="eyebrow" style="margin-bottom:10px">Step 2</p>
                <h3>How you want it made</h3>
                <p class="muted" style="font-size:15px">Not sure? Leave the defaults — the estimate updates live and
                  we will recommend the right combination when we quote.</p>

                <div class="field--row" style="margin-top:18px">
                  <div class="field">
                    <label for="material">Material</label>
                    <select id="material" name="material">
                      <option value="pla" selected>PLA — display, gifting, best finish</option>
                      <option value="petg">PETG — everyday functional, outdoor</option>
                      <option value="abs">ABS / ASA — heat and UV resistant</option>
                      <option value="tpu">TPU — flexible, rubber-like</option>
                      <option value="pacf">Nylon / PA-CF — structural, hard-wearing</option>
                      <option value="resin">Resin — fine detail, miniatures</option>
                    </select>
                  </div>
                  <div class="field">
                    <label for="quality">Layer height</label>
                    <select id="quality" name="quality">
                      <option value="draft">0.28 mm — draft, fastest</option>
                      <option value="standard" selected>0.20 mm — standard</option>
                      <option value="fine">0.12 mm — fine</option>
                      <option value="ultra">0.08 mm — ultra detail</option>
                    </select>
                  </div>
                </div>

                <div class="field--row">
                  <div class="field">
                    <label for="finish">Finish</label>
                    <select id="finish" name="finish">
                      <option value="raw">As printed</option>
                      <option value="cleaned" selected>Cleaned, supports removed</option>
                      <option value="sanded">Sanded smooth</option>
                      <option value="painted">Primed and painted</option>
                    </select>
                  </div>
                  <div class="field">
                    <label for="qty">Quantity</label>
                    <input type="number" id="qty" name="qty" min="1" step="1" value="1" placeholder="1">
                  </div>
                </div>

                <div class="field">
                  <label for="infill">Infill &mdash; <span class="mono" id="infillOut">20%</span></label>
                  <span class="hint">Low for display pieces, high for parts that take load. 20% suits almost everything.</span>
                  <input type="range" id="infill" name="infill" min="0" max="100" step="5" value="20">
                </div>

                <div class="field">
                  <label>Approximate size in mm <span class="hint" style="font-weight:400">(filled in automatically if you upload an STL or OBJ)</span></label>
                  <div class="field--row" style="grid-template-columns:repeat(3,1fr)">
                    <input type="number" id="dimX" name="dimX" placeholder="Length" min="0" step="0.1">
                    <input type="number" id="dimY" name="dimY" placeholder="Width" min="0" step="0.1">
                    <input type="number" id="dimZ" name="dimZ" placeholder="Height" min="0" step="0.1">
                  </div>
                </div>
              </div>

              <div class="card card--flat">
                <p class="eyebrow" style="margin-bottom:10px">Step 3</p>
                <h3>Where to send the quote</h3>
                <div class="field--row" style="margin-top:18px">
                  <div class="field">
                    <label for="name">Your name <span class="req">*</span></label>
                    <input type="text" id="name" name="name" autocomplete="name" placeholder="Name" required>
                  </div>
                  <div class="field">
                    <label for="phone">Phone / WhatsApp <span class="req">*</span></label>
                    <input type="tel" id="phone" name="phone" autocomplete="tel" placeholder="10-digit mobile" required>
                  </div>
                </div>
                <div class="field--row">
                  <div class="field">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" autocomplete="email" placeholder="you@example.com">
                  </div>
                  <div class="field">
                    <label for="company">Company <span class="hint" style="font-weight:400">(if this is a business order)</span></label>
                    <input type="text" id="company" name="company" autocomplete="organization" placeholder="Company name">
                  </div>
                </div>
                <div class="field--row">
                  <div class="field">
                    <label for="orderType">Type of order</label>
                    <select id="orderType" name="orderType">
                      <option>Personal / one-off</option>
                      <option>Gift or keepsake</option>
                      <option>Corporate gifting</option>
                      <option>Prototype / product development</option>
                      <option>Bulk order</option>
                      <option>Contract manufacturing</option>
                      <option>OEM / white-label</option>
                      <option>Spare or replacement part</option>
                    </select>
                  </div>
                  <div class="field">
                    <label for="deadline">Needed by</label>
                    <input type="date" id="deadline" name="deadline">
                  </div>
                </div>

                <p class="note note--ember hidden" id="formNote" style="margin-top:18px"></p>

                <div class="btn-row" style="margin-top:22px">
                  <button class="btn btn--ember" type="button" id="sendWhatsApp">Send on WhatsApp {icon('whatsapp', 17)}</button>
                  <button class="btn btn--ghost" type="button" id="sendEmail">Send by email</button>
                  <button class="btn btn--ghost" type="button" id="copyBrief">Copy the brief</button>
                </div>
                <p class="muted" style="font-size:14px;margin:16px 0 0">
                  WhatsApp is fastest — the message opens pre-filled with everything above, and you attach your
                  file in the chat. Nothing on this page is sent anywhere until you press one of these buttons.
                </p>

                <div class="note hidden" id="afterSend" style="margin-top:18px">
                  <strong>One last step:</strong> attach your file in the chat or email that just opened, and send it.
                  We reply within one working day.
                </div>
              </div>
            </form>
          </div>

          <div>
            <div class="order-aside">
            <div class="estimate reveal" id="estimateBox">
              <p class="eyebrow" style="margin-bottom:8px">Live estimate</p>
              <p class="mono" style="font-size:12px;letter-spacing:.1em;color:var(--ink-400);margin:0">INDICATIVE RANGE</p>
              <p class="estimate__num estimate__num--empty" id="estRange">Add a size to see a number</p>
              <p class="mono" id="estUnit" style="font-size:13px;color:var(--blue-200);margin:0 0 18px">&mdash;</p>
              <div class="estimate__row"><span>Quantity</span><b id="estQty">&mdash;</b></div>
              <div class="estimate__row"><span>Material used</span><b id="estWeight">&mdash;</b></div>
              <div class="estimate__row"><span>Machine time</span><b id="estTime">&mdash;</b></div>
              <p class="mono hidden" id="estEmpty" style="font-size:12px;color:var(--ink-400);margin-top:16px;letter-spacing:.06em">
                UPLOAD A FILE OR ENTER A SIZE TO SEE A NUMBER
              </p>
              <p style="font-size:13.5px;color:var(--ink-400);margin:18px 0 0;line-height:1.55">
                A guide, not a quotation. It does not know about supports, multi-colour work, assembly, inserts
                or packaging. Your real price comes back within one working day and is usually close to this.
              </p>
            </div>

            <div class="card card--flat reveal" style="margin-top:20px">
              <h3 style="font-size:19px">Rather just talk?</h3>
              <ul class="contact-list" style="margin-top:14px">
                <li class="contact-row">
                  <span class="contact-row__icon">{icon('whatsapp', 20)}</span>
                  <span><b>WhatsApp</b><a data-wa href="#">{PHONE_DISPLAY}</a></span>
                </li>
                <li class="contact-row">
                  <span class="contact-row__icon">{icon('mail', 20)}</span>
                  <span><b>Email</b><a data-mail="text" href="mailto:{EMAIL}">{EMAIL}</a></span>
                </li>
                <li class="contact-row">
                  <span class="contact-row__icon">{icon('instagram', 20)}</span>
                  <span><b>Instagram</b><a data-ig href="{INSTAGRAM}">@allthings3d.in</a></span>
                </li>
              </ul>
            </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--white section--tight">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">What happens next</p>
          <h2>After you press send</h2>
        </div>
        <div class="grid grid--4">
{card('search', 'We read it properly', 'A person looks at your file or description and checks it can actually be printed the way you want it.', num='01')}
{card('chat', 'You get a real answer', 'Within one working day: material recommendation, finish, lead time and a firm price. Questions if we have any.', num='02')}
{card('check', 'You approve', 'Nothing is printed and nothing is charged until you have said yes to the price and the date.', num='03')}
{card('truck', 'It gets made and sent', 'Printed, finished, checked, photographed and dispatched anywhere in India.', num='04')}
        </div>
      </div>
    </section>
"""

# ==========================================================================
# PAGE: ABOUT
# ==========================================================================
ABOUT = f"""{pagehead('About', 'About us', 'Because your ideas deserve to exist',
  'All Things 3D is a custom 3D printing workshop in Mumbai. We started by making the things people could not buy, and grew into the workshop that makes them at quantity for other businesses.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="split">
          <div class="reveal">
            <p class="eyebrow">Our story</p>
            <h2>It started with things that did not exist yet</h2>
            <p>Almost every first order we take is something you cannot buy. A photograph of a grandmother,
              turned into a lamp. A knob that snapped off a machine nobody makes parts for any more. A trophy with
              a specific person's name on it. A prototype somebody needed to hold before they could explain it to
              an investor.</p>
            <p>What we noticed is that those orders keep coming back bigger. The person who ordered one keychain
              for a friend comes back in March asking for four hundred for their company. The founder who wanted one
              prototype now needs a thousand units a quarter. So the workshop grew in that direction — same care on a
              single keepsake, but with the process, documentation and capacity to run production behind it.</p>
            <p class="lede">That is the whole business, really: take the idea seriously, whatever size it arrives in.</p>
          </div>
          <div class="stage" style="background:linear-gradient(160deg,#02243D,#22272A);aspect-ratio:1/1">
            <canvas data-model="vase" data-spin="0.9" aria-hidden="true" style="width:100%;height:100%"></canvas>
            <div class="stage__hud"><span>All Things 3D</span><span class="mono">Mumbai, India</span></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--white">
      <div class="shell">
        <div class="sec-head center">
          <p class="eyebrow">How we work</p>
          <h2>Four things we do not compromise on</h2>
        </div>
        <div class="grid grid--4">
{card('chat', 'We answer quickly', 'One working day, every enquiry, with a real answer rather than an acknowledgement.', num='01')}
{card('search', 'We say when it will not work', 'Before you pay. A thin wall that will crack in transit, a material that will warp in a car — you hear it early.', num='02')}
{card('shield', 'We check before we ship', 'Measured against the drawing, fit-tested where there is a mating part, photographed before it is packed.', num='03')}
{card('wrench', 'We put it right', 'A piece that does not match what was approved is remade at our cost. No argument, no invoice.', num='04')}
        </div>
      </div>
    </section>

    <section class="section section--dark">
      <div class="shell">
        <div class="sec-head">
          <p class="eyebrow">Who we work with</p>
          <h2>Four kinds of people send us files</h2>
        </div>
        <div class="grid grid--2">
{card('gift', 'People with something to give', 'A photograph that should be a lamp, a name that should be on a keyring, a moment that should be an object. Usually one piece. Often the start of a much bigger order.', dark=True)}
{card('spark', 'Founders with a product', 'An idea that needs to become a thing that can be held, tested, photographed and sold — without spending a fortune on tooling to find out whether it works.', dark=True)}
{card('factory', 'Companies who need it made', 'Manufacturers, engineering firms and design studios who have the drawing and need consistent batches, on schedule, to a written spec.', dark=True)}
{card('layers', 'Brands who need a workshop', 'Retailers and gifting companies selling under their own name, with production, packing and dispatch handled quietly behind them.', dark=True)}
        </div>
      </div>
    </section>

    <section class="section section--sand">
      <div class="shell">
        <div class="split split--rev">
          <div class="reveal">
            <p class="eyebrow">The name</p>
            <h2>Why &ldquo;All Things&rdquo;</h2>
            <p>Because the honest answer to &ldquo;can you print this?&rdquo; is almost always yes, and the interesting
              part of the conversation is everything that comes after — which material, what finish, how thick that
              wall needs to be, and whether it should be one piece or four.</p>
            <p>The tagline underneath the logo is not decoration. <b>Because your ideas deserve to exist</b> is a
              statement about what a workshop is for. Most good ideas die as descriptions. Ours is the job of making
              them into objects.</p>
            <div class="btn-row" style="margin-top:24px">
              <a class="btn" href="order.html">Send us yours {ARROW}</a>
              <a class="btn btn--ghost" data-ig href="{INSTAGRAM}">See our Instagram</a>
            </div>
          </div>
          <div class="grid grid--2">
{card('pin', 'Based in Mumbai', 'Working out of Mumbai, Maharashtra, and shipping finished orders across India.')}
{card('truck', 'Delivering everywhere', 'Courier dispatch nationwide, with tracking. Local Mumbai orders can be collected or hand-delivered.')}
{card('clock', 'Reachable', 'WhatsApp and email are the fastest routes in. Both are answered by the people who do the work.')}
{card('lock', 'Discreet', 'NDA on request, and your designs are never shown as our work without written permission.')}
          </div>
        </div>
      </div>
    </section>

{cta_band()}
"""

# ==========================================================================
# PAGE: CONTACT
# ==========================================================================
CONTACT = f"""{pagehead('Contact', 'Get in touch', 'Talk to a person, not a ticket',
  'WhatsApp is the fastest way in and is answered by the people who actually do the printing. Email works just as well if you would rather write it all down.')}

    <section class="section section--mist">
      <div class="shell">
        <div class="split" style="align-items:start">
          <div class="reveal">
            <h2>Reach us</h2>
            <ul class="contact-list" style="margin-top:22px">
              <li class="contact-row">
                <span class="contact-row__icon">{icon('whatsapp', 21)}</span>
                <span><b>WhatsApp &mdash; fastest</b><a data-wa href="#">{PHONE_DISPLAY}</a></span>
              </li>
              <li class="contact-row">
                <span class="contact-row__icon">{icon('phone', 21)}</span>
                <span><b>Phone</b><a data-tel="text" href="tel:+917666004531">{PHONE_DISPLAY}</a></span>
              </li>
              <li class="contact-row">
                <span class="contact-row__icon">{icon('mail', 21)}</span>
                <span><b>Email</b><a data-mail="text" href="mailto:{EMAIL}">{EMAIL}</a></span>
              </li>
              <li class="contact-row">
                <span class="contact-row__icon">{icon('instagram', 21)}</span>
                <span><b>Instagram</b><a data-ig href="{INSTAGRAM}">@allthings3d.in</a></span>
              </li>
              <li class="contact-row">
                <span class="contact-row__icon">{icon('pin', 21)}</span>
                <span><b>Workshop</b><span>Mumbai, Maharashtra, India</span></span>
              </li>
            </ul>

            <div class="note" style="margin-top:26px">
              <strong>Sending a file?</strong> Use the <a href="order.html">order page</a> instead — it previews STL
              and OBJ files, measures them, gives you an indicative price, and builds a complete brief you can send in
              one tap.
            </div>
          </div>

          <div class="grid" style="gap:20px">
            <div class="card reveal">
              <div class="card__icon">{icon('clock', 25)}</div>
              <h3>When we reply</h3>
              <p>Enquiries are answered within one working day, usually much sooner. Messages that arrive on Sunday
                are answered on Monday.</p>
            </div>
            <div class="card reveal">
              <div class="card__icon">{icon('chat', 25)}</div>
              <h3>What to include</h3>
              <p>What you want made, roughly how big, how many, and when you need it. A photo or sketch instead of
                any of that is completely fine.</p>
            </div>
            <div class="card reveal">
              <div class="card__icon">{icon('factory', 25)}</div>
              <h3>Business enquiries</h3>
              <p>For OEM, contract manufacturing or vendor registration, mention it in the first message and the
                NDA and company documents come back with the reply. <a href="oem.html">See the OEM page.</a></p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--white section--tight">
      <div class="shell center">
        <p class="eyebrow">Quickest route</p>
        <h2>One tap and you are talking to us</h2>
        <div class="btn-row center" style="margin-top:22px">
          <a class="btn btn--ember" data-wa href="#">Open WhatsApp {icon('whatsapp', 17)}</a>
          <a class="btn btn--ghost" href="order.html">Upload a file instead</a>
        </div>
      </div>
    </section>
"""

# ==========================================================================
# PAGE: FAQ
# ==========================================================================
FAQ_ITEMS = [
    ("I do not have a 3D file. Can you still make it?",
     ["Yes, and that describes most orders. Send a photograph, a sketch on paper, a link to something similar, a technical drawing, or just a written description.",
      "We build the 3D model for you and send a render for approval before anything is printed. For simple pieces the modelling is usually absorbed into the job; for complex parts it is quoted as a separate line so you can see exactly what it costs."]),
    ("How much does it cost?",
     ["It depends on how long the piece occupies a machine, how much material it uses, and what finishing it needs. A small keychain is a few hundred rupees; a large detailed piece runs into thousands.",
      "The estimator on the order page gives you an indicative range in seconds. The real quotation comes back within one working day and is usually close to it."]),
    ("What is the minimum order?",
     "One piece. There is no minimum quantity. There is a small minimum order value so that packing and dispatch are covered on very small items."),
    ("How long will it take?",
     "Typically 7 to 10 working days from design approval. Pieces already modelled can go much faster, and large bulk runs or painted finishes take longer. Every quotation carries a committed dispatch date rather than a vague estimate. If you have a hard deadline, say so in the first message — it changes how we schedule it."),
    ("Do you deliver outside Mumbai?",
     "Yes, anywhere in India by courier with tracking. Mumbai orders can also be collected or hand-delivered. Shipping is shown as a separate line on the quotation."),
    ("Which material should I choose?",
     ["If it sits on a desk or a shelf, PLA. If it lives outdoors or takes daily handling, PETG. If it goes in a car or near heat, ABS or ASA. If it must bend, TPU. If it is a fine-detail miniature or jewellery piece, resin.",
      "You do not have to decide — tell us how it will be used and the recommendation comes back with the quote. The <a href='capabilities.html'>capabilities page</a> has the full comparison."]),
    ("Can you print in more than one colour?",
     "Yes. Multi-colour is done either by printing components separately and assembling, by pausing and swapping filament at a set layer, or by painting after printing. Which method suits depends on the design, and it is priced with the quote."),
    ("How accurate are printed parts?",
     "We work to ±0.3 mm or ±0.3% on FDM and ±0.1 mm or ±0.15% on resin, whichever is greater. If a feature on your drawing needs tighter than that, mark it and we will either machine it after printing or tell you honestly that a different process is the right one."),
    ("Can you copy or repair an existing part?",
     "Usually. Send photographs with a ruler or vernier reading alongside, or post us the part and we will measure it. Broken parts can often be reconstructed. We do not reproduce parts that are still commercially available under someone else's design rights."),
    ("Will you sign an NDA?",
     "Yes, for any development, contract manufacturing or OEM work. Send yours or ask for ours. Files under NDA are not shown, not reused and not printed for anyone else."),
    ("Do you provide GST invoices?",
     "Yes. Business orders are invoiced with GST, with delivery challans and the documentation your accounts team will ask for. For vendor registration we can supply company documents in whatever format your procurement portal needs."),
    ("What if something arrives damaged or wrong?",
     "Tell us within 48 hours with a photograph. If it does not match what was approved, or it was damaged in transit, it is remade and resent at our cost. That is the entire policy — there is no form."),
    ("Can you handle a thousand pieces? Ten thousand?",
     "A thousand, comfortably, on a scheduled run. Ten thousand is possible and we will talk you through whether printing is still the right process at that point — past roughly ten to fifteen thousand simple identical parts, injection moulding usually wins on unit cost, and we would rather say so."),
    ("Do you do the design work too?",
     "Yes — concept, CAD modelling, design for manufacture, and iterating a product until it is right. That is the end-to-end product development service on the <a href='services.html'>services page</a>."),
]

FAQ = f"""{pagehead('FAQ', 'Questions', 'Everything people ask before ordering',
  'And a few things they only think to ask afterwards. If yours is not here, WhatsApp it — the answer takes a minute.')}

    <section class="section section--mist">
      <div class="shell" style="max-width:900px">
{acc(FAQ_ITEMS)}
      </div>
    </section>

{cta_band('Still unsure whether it can be made?',
          'That is exactly the question to send us. Describe it in a sentence and you will have a straight answer within a working day.')}
"""

# ==========================================================================
# PAGE: THANK YOU / 404
# ==========================================================================
THANKS = f"""    <section class="pagehead" style="min-height:52vh;display:flex;align-items:center">
      <div class="shell center">
        <p class="eyebrow" style="justify-content:center">Received</p>
        <h1>Thank you &mdash; it is with us</h1>
        <p style="margin-inline:auto">We read every enquiry properly rather than auto-replying to it. You will hear
          back within one working day with feasibility, a material recommendation, a lead time and a price.</p>
        <div class="btn-row center" style="margin-top:30px">
          <a class="btn btn--onDark" href="products.html">Browse products</a>
          <a class="btn btn--onDark" data-ig href="{INSTAGRAM}">See our Instagram</a>
        </div>
      </div>
    </section>

    <section class="section section--mist section--tight">
      <div class="shell">
        <div class="grid grid--3">
{card('search', 'We check it', 'A person opens your file and confirms it can be printed the way you want it.', num='01')}
{card('chat', 'We price it', 'Material, finish, lead time and a firm number — inside one working day.', num='02')}
{card('truck', 'We make it', 'On your approval. Printed, finished, checked and dispatched.', num='03')}
        </div>
      </div>
    </section>
"""

NOTFOUND = f"""    <section class="pagehead" style="min-height:62vh;display:flex;align-items:center">
      <div class="shell center">
        <p class="eyebrow" style="justify-content:center">Error 404</p>
        <h1>This page failed to print</h1>
        <p style="margin-inline:auto">The page you were looking for is not here &mdash; it may have moved, or the
          link may have a typo in it. Everything else is still on the bed.</p>
        <div class="btn-row center" style="margin-top:30px">
          <a class="btn btn--ember" href="index.html">Back to the home page</a>
          <a class="btn btn--onDark" href="order.html">Upload your idea</a>
        </div>
      </div>
    </section>
"""

# ==========================================================================
# Build
# ==========================================================================
PAGES = [
    ("index.html", "All Things 3D — Custom 3D Printing in Mumbai | Upload your idea, we make it",
     "Custom 3D printing in Mumbai. Corporate orders, end-to-end product development, contract manufacturing, bulk orders and OEM white-label production. Upload a file or just describe the idea — quote back in one working day.",
     HOME, ""),
    ("products.html", "Products — Lithophane lamps, keychains, models & functional parts | All Things 3D",
     "Lithophane lamps, personalised keychains, nameplates, figurines, planters, working spare parts, jigs, architectural models and event favours — all made to order in Mumbai.",
     PRODUCTS, ""),
    ("services.html", "Services — Corporate gifting, product development, contract manufacturing | All Things 3D",
     "Five ways businesses use All Things 3D: corporate orders, end-to-end product development, contract manufacturing, bulk orders and OEM white-label production.",
     SERVICES, ""),
    ("oem.html", "OEM, Bulk Orders & Contract Manufacturing | All Things 3D",
     "White-label 3D printing production under your brand. NDA, golden sample, frozen specification, volume price breaks from 10 to 1,000+ pieces, blind drop-shipping and vendor registration documents.",
     OEM, ""),
    ("capabilities.html", "Capabilities — Machines, materials and tolerances | All Things 3D",
     "FDM and resin 3D printing capabilities: materials from PLA to nylon carbon fibre, tolerances, build volumes, post-processing, accepted file formats — and where 3D printing is the wrong answer.",
     CAPABILITIES, ""),
    ("gallery.html", "Gallery — Selected 3D printed work | All Things 3D",
     "A sample of what comes off the print bed: lithophane lamps, corporate keyrings, cake toppers, spare parts, jigs, architectural models, jewellery and event favours.",
     GALLERY, ""),
    ("order.html", "Upload your idea — instant 3D preview and price estimate | All Things 3D",
     "Drop an STL or OBJ file and see it rendered instantly with a live price estimate, or simply describe what you want. Quote and lead time back within one working day.",
     ORDER, "assets/js/atd-order.js"),
    ("about.html", "About All Things 3D — Custom 3D printing workshop in Mumbai",
     "All Things 3D is a custom 3D printing workshop in Mumbai making everything from single keepsakes to production runs for other brands. Because your ideas deserve to exist.",
     ABOUT, ""),
    ("contact.html", "Contact All Things 3D — WhatsApp, email and enquiries",
     "Talk to All Things 3D in Mumbai. WhatsApp, phone, email and Instagram — enquiries answered within one working day.",
     CONTACT, ""),
    ("faq.html", "FAQ — Costs, lead times, materials and minimum orders | All Things 3D",
     "Answers on pricing, lead times, minimum order quantity, materials, accuracy, NDAs, GST invoicing, delivery and what happens if something arrives wrong.",
     FAQ, ""),
    ("thank-you.html", "Thank you — your enquiry is with us | All Things 3D",
     "Your 3D printing enquiry has been received. All Things 3D replies within one working day.",
     THANKS, ""),
    ("404.html", "Page not found | All Things 3D",
     "That page could not be found. Head back to the All Things 3D home page.",
     NOTFOUND, ""),
]


def build():
    written = []
    for slug, title, desc, body, extra in PAGES:
        active = slug
        if slug in ("thank-you.html", "404.html", "faq.html", "order.html"):
            active = None if slug in ("faq.html", "order.html") else None
        html = page(slug, title, desc, body, extra_js=extra, active=slug)
        path = os.path.join(ROOT, slug)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        written.append(slug)

    # sitemap
    today = datetime.date.today().isoformat()
    urls = []
    for slug, *_ in PAGES:
        if slug in ("404.html", "thank-you.html"):
            continue
        loc = f"{DOMAIN}/" if slug == "index.html" else f"{DOMAIN}/{slug}"
        prio = "1.0" if slug == "index.html" else ("0.9" if slug in ("order.html", "products.html", "oem.html") else "0.7")
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap)

    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")

    with open(os.path.join(ROOT, "CNAME"), "w", encoding="utf-8") as fh:
        fh.write("allthings3d.com\n")

    manifest = """{
  "name": "All Things 3D",
  "short_name": "All Things 3D",
  "description": "Custom 3D printing in Mumbai — because your ideas deserve to exist.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F2F7FB",
  "theme_color": "#0166AE",
  "icons": [
    { "src": "assets/img/favicon.png", "sizes": "528x655", "type": "image/png", "purpose": "any" }
  ]
}
"""
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as fh:
        fh.write(manifest)

    print("Built %d pages + sitemap.xml, robots.txt, CNAME, site.webmanifest" % len(written))
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    build()
