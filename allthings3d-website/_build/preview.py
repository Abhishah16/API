#!/usr/bin/env python3
"""
All Things 3D — single-file preview builder.

Bundles the whole generated site into ONE self-contained .html file: every
page, the stylesheet, the JavaScript and the logos are inlined, and a tiny
hash router swaps pages in place. The result opens by double-clicking it,
works with no web server and no internet, and can be emailed or dropped in
a chat as a single attachment.

It is a VIEWING COPY, not the site. The real site is the folder of separate
pages — that is what gets deployed to allthings3d.com. Regenerate this file
after any content change:

    python3 _build/build.py      # first, rebuild the pages
    python3 _build/preview.py    # then, rebundle the preview

Output: preview/allthings3d-preview.html
"""

import base64
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGES = [
    ("index", "Home"),
    ("products", "Products"),
    ("services", "Services"),
    ("oem", "OEM & Bulk"),
    ("capabilities", "Capabilities"),
    ("gallery", "Gallery"),
    ("order", "Upload your idea"),
    ("about", "About"),
    ("contact", "Contact"),
    ("faq", "FAQ"),
    ("thank-you", "Thank you"),
    ("404", "Not found"),
]

LOGOS = {
    "assets/img/logo/atd-logo-horizontal-transparent.png": None,
    "assets/img/logo/atd-logo-horizontal-white.png": None,
}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def data_uri(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def inline_logos(html):
    for path, uri in LOGOS.items():
        html = html.replace('src="%s"' % path, 'src="%s"' % uri)
    return html


def to_hash_links(html):
    """page.html -> #page, keeping links working inside one document."""
    html = re.sub(r'href="([a-z0-9\-]+)\.html(#[a-z0-9\-]+)?"', r'href="#\1"', html)
    return html


def grab(html, tag_open, tag_close):
    i = html.index(tag_open)
    j = html.index(tag_close, i)
    return html[i:j + len(tag_close)]


def build():
    for path in LOGOS:
        LOGOS[path] = data_uri(path)

    css = read("assets/css/atd.css")
    js_3d = read("assets/js/atd-3d.js")
    js_site = read("assets/js/atd.js")
    js_order = read("assets/js/atd-order.js")

    index_html = read("index.html")
    nav = to_hash_links(inline_logos(
        grab(index_html, '  <div class="progress-rail">', "  </header>")))
    footer = to_hash_links(inline_logos(
        grab(index_html, '  <footer class="footer">', "  </footer>")))

    sections = []
    for slug, label in PAGES:
        page = read("%s.html" % slug)
        main = grab(page, '  <main id="main">', "  </main>")
        main = main.replace('<main id="main">', "").replace("</main>", "")
        main = to_hash_links(inline_logos(main))
        sections.append(
            '<section class="pv-page" id="pg-%s" data-label="%s" hidden>%s</section>'
            % (slug, label, main))

    parts = []
    parts.append("<title>All Things 3D</title>")
    parts.append("<style>\n%s\n</style>" % css)
    parts.append("""<style>
/* Preview shell only — none of this exists on the real site. */
.pv-bar {
  position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%);
  z-index: 300; display: flex; align-items: center; gap: 10px;
  background: rgba(34, 39, 42, .93); color: #fff;
  border: 1px solid rgba(255,255,255,.16); border-radius: 999px;
  padding: 8px 8px 8px 16px; box-shadow: 0 14px 40px rgba(2, 36, 61, .34);
  backdrop-filter: blur(10px);
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .12em;
  text-transform: uppercase; max-width: calc(100vw - 24px);
}
.pv-bar b { color: #A9CFEC; font-weight: 500; }
.pv-bar select {
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .08em;
  background: rgba(255,255,255,.1); color: #fff; border: 1px solid rgba(255,255,255,.22);
  border-radius: 999px; padding: 7px 12px; cursor: pointer; max-width: 46vw;
}
.pv-bar select option { background: #22272A; color: #fff; }
@media (max-width: 520px) { .pv-bar { font-size: 10px; padding-left: 12px; } .pv-bar .pv-hide { display: none; } }
/* keep the floating bar clear of the last footer line */
.footer__bottom { padding-bottom: 74px; }
@media print { .pv-bar { display: none; } }
</style>""")
    parts.append(nav)
    parts.append('<main id="main">')
    parts.extend(sections)
    parts.append("</main>")
    parts.append(footer)
    parts.append("""<div class="pv-bar" role="region" aria-label="Preview navigation">
  <span class="pv-hide"><b>Preview</b> &nbsp;allthings3d.com</span>
  <label class="sr-only" for="pvJump">Jump to page</label>
  <select id="pvJump">%s</select>
</div>""" % "".join(
        '<option value="%s">%s</option>' % (s, l) for s, l in PAGES))

    parts.append("<script>\n%s\n</script>" % js_3d)
    parts.append("<script>\n%s\n</script>" % js_site)
    parts.append("<script>\n%s\n</script>" % js_order)
    parts.append("""<script>
/* Hash router. Every page of the site lives in this one document; showing
   one and hiding the rest is the whole mechanism. The site's own scripts
   are untouched — IntersectionObserver re-fires when a hidden section
   becomes visible, so animations and canvases start on arrival. */
(function () {
  var pages = Array.prototype.slice.call(document.querySelectorAll('.pv-page'));
  var jump = document.getElementById('pvJump');

  function slugFromHash() {
    var h = (location.hash || '').replace(/^#/, '');
    return document.getElementById('pg-' + h) ? h : 'index';
  }

  function show(slug) {
    pages.forEach(function (p) { p.hidden = (p.id !== 'pg-' + slug); });
    var active = document.getElementById('pg-' + slug);
    if (active) {
      /* Guarantee the page is readable the instant it appears, rather than
         waiting on a scroll observer that may never fire above the fold. */
      active.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('is-in'); });
    }
    document.querySelectorAll('.nav__link').forEach(function (a) {
      var t = (a.getAttribute('href') || '').replace(/^#/, '');
      if (t === slug) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    if (jump) jump.value = slug;
    window.scrollTo(0, 0);
    window.dispatchEvent(new Event('scroll'));
    window.dispatchEvent(new Event('resize'));
  }

  window.addEventListener('hashchange', function () { show(slugFromHash()); });
  if (jump) {
    jump.addEventListener('change', function () { location.hash = jump.value; });
  }
  show(slugFromHash());
})();
</script>""")

    out_dir = os.path.join(ROOT, "preview")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "allthings3d-preview.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n")

    kb = os.path.getsize(out) / 1024
    print("Wrote %s (%d pages, %.0f KB)" % (out, len(PAGES), kb))


if __name__ == "__main__":
    build()
