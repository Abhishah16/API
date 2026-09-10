# All Things 3D — website

The public website for **allthings3d.com**. Plain HTML, CSS and JavaScript —
no build step to deploy, no framework, no npm install, no external services.
Drop the folder on any host and it works.

---

## What is in here

| Path | What it is |
|---|---|
| `index.html` | Home — animated hero, services, products preview, process, FAQ |
| `products.html` | The ten product categories, each with a live 3D render |
| `services.html` | Corporate orders · product development · contract manufacturing · bulk · OEM |
| `oem.html` | The full OEM / white-label / bulk page, with the volume price-break table |
| `capabilities.html` | Machines, materials, tolerances, file formats, and when printing is the wrong answer |
| `gallery.html` | Filterable selected work |
| `order.html` | **Upload your idea** — drag-drop file, live 3D preview, price estimator, WhatsApp handoff |
| `about.html`, `contact.html`, `faq.html` | Company, contact, questions |
| `thank-you.html`, `404.html` | Post-submit page and error page |
| `assets/css/atd.css` | The whole stylesheet |
| `assets/css/atd-tokens.css` | Brand tokens as CSS custom properties (reference copy) |
| `assets/js/atd.js` | **Site config** (contacts + pricing) and all page behaviour |
| `assets/js/atd-3d.js` | The 3D engine — layer-by-layer print renderer and STL/OBJ parser |
| `assets/js/atd-order.js` | Order page: file drop, mesh preview, estimator, enquiry handoff |
| `assets/img/logo/` | The brand logo files |
| `_build/build.py` | Optional page generator (see below) |
| `CNAME`, `robots.txt`, `sitemap.xml`, `site.webmanifest` | Hosting and SEO files |

---

## The things you will actually want to change

### 1. Phone number, email, Instagram

All in one place — the top of **`assets/js/atd.js`**:

```js
window.ATD_CONFIG = {
  phone: '917666004531',            // country code + number, digits only
  phoneDisplay: '+91 76660 04531',
  email: 'info.allthings3d@gmail.com',
  instagram: 'https://www.instagram.com/allthings3d.in',
  ...
```

Every WhatsApp link, `tel:` link, `mailto:` link and Instagram link on the site
is built from those four values at page load. Change them once, they change
everywhere.

> **Two phone numbers are in circulation on existing All Things 3D creatives**
> (`7666004531` on the lithophane poster and `7048138715` on the Mother's Day
> post). The site currently uses the first. Confirm which one is correct and
> update `phone` and `phoneDisplay`.

### 2. Prices in the estimator

Also in `ATD_CONFIG`, under `pricing`. Per-gram material rates, machine rate
per hour, setup fee, minimum order, layer-height multipliers, finish uplifts
and the quantity price breaks are all plain numbers with comments. Nothing in
the estimator is hard-coded elsewhere.

The estimator deliberately shows a **range**, labelled as indicative, and the
page says a real quotation follows within one working day.

### 3. Making the order form email you directly

Out of the box the order form builds a complete brief and hands it to WhatsApp
or the visitor's email client. That works today with no account anywhere, and
WhatsApp is the natural place for someone to then attach their file.

If you would rather receive the enquiry as an email with the file attached,
sign up at [formspree.io](https://formspree.io) (free tier is enough to start),
and paste the endpoint into `ATD_CONFIG`:

```js
formEndpoint: 'https://formspree.io/f/xxxxxxx',
```

The form then POSTs the fields **and the uploaded file** there, and sends the
visitor to `thank-you.html`. The WhatsApp and email buttons keep working
alongside it. If the POST fails, the visitor is told to use WhatsApp instead —
an enquiry is never silently lost.

On Netlify you can instead add `netlify` and `data-netlify="true"` to the
`<form>` tag in `order.html` and use Netlify Forms.

### 4. Text on any page

Either edit the `.html` file directly, or edit `_build/build.py` and run
`python3 _build/build.py` to regenerate every page with a consistent header,
footer and meta tags. **Pick one.** If you edit the HTML by hand and then run
the generator, your hand edits are overwritten.

---

## Publishing it on allthings3d.com

The site is static, so anything that serves files will host it.

### Netlify (easiest, free, custom domain included)

1. Sign in at netlify.com and choose **Add new site → Deploy manually**.
2. Drag the `allthings3d-website` folder onto the page.
3. **Site settings → Domain management → Add custom domain →** `allthings3d.com`.
4. Point the domain's DNS at Netlify as instructed (an `A` record and a `CNAME`
   for `www`). HTTPS is issued automatically.
5. Set the custom 404 by keeping `404.html` where it is — Netlify picks it up.

### GitHub Pages

1. Push the contents of this folder to a repository (the files must sit at the
   repository root, or in `/docs`).
2. **Settings → Pages →** deploy from that branch.
3. The included `CNAME` file already contains `allthings3d.com`, so Pages will
   claim the domain once the DNS records point at GitHub.

### Any normal web host (cPanel, Hostinger, GoDaddy)

Upload the contents of this folder into `public_html`. That is the whole
process — there is nothing to install or configure.

---

## What still needs your input

These are placeholders or unverified details that should be checked before the
site goes live:

1. **Phone number** — two are in circulation; confirm one (see above).
2. **Instagram handle** — the site links `instagram.com/allthings3d.in`, taken
   from the link you supplied. The brand file lists `@all_things_3d.ind`.
   Confirm which account is current.
3. **Workshop address** — the site says "Mumbai, Maharashtra" only. Add the
   full address in `contact.html` and in the `LocalBusiness` structured data in
   `_build/build.py` when you are happy for it to be public.
4. **GSTIN and company details** — not printed anywhere on the site yet. Needed
   if you want them on the contact or OEM page for vendor registration.
5. **Real photographs.** The 3D shapes throughout are rendered live in the
   browser and look good, but photographs of finished pieces will always sell
   better. The gallery is built so each tile's `<div class="tile__art">` can
   have its `<canvas>` swapped for an `<img>` with no other change.
6. **Capability numbers** — build volume (300 × 300 × 400 mm FDM,
   220 × 120 × 250 mm resin) and the tolerance figures on `capabilities.html`
   are sensible defaults for a workshop of this type. Confirm they match your
   actual machines before quoting against them.
7. **Testimonials** — deliberately not included, because inventing them would
   be dishonest. Three real quotes with names would strengthen the home page a
   lot; send them over and they can be added.

---

## Technical notes

- **No dependencies.** The only external request is the Google Fonts
  stylesheet. If it fails, the fonts fall back to system faces and the layout
  is unaffected.
- **The 3D is hand-written.** `assets/js/atd-3d.js` is about 7 KB and does its
  own projection, painter's-algorithm sorting and flat shading on a 2D canvas.
  It also parses binary and ASCII STL and OBJ files, and computes the mesh
  volume by signed-tetrahedron summation — that volume is what feeds the price
  estimator.
- **Nothing leaves the browser.** Uploaded files are read locally with
  `FileReader` for the preview. Nothing is transmitted anywhere until the
  visitor presses a send button.
- **Accessibility.** Skip link, keyboard-operable nav and accordions, visible
  focus rings, `prefers-reduced-motion` respected (animations stop, content
  still appears), and every colour pair on the site meets WCAG AA.
- **Brand.** Colours, type and the 60/30/10 discipline follow All Things 3D
  colour system v1.0 — Print Blue `#0166AE`, Filament Black `#22272A`, Ember
  `#EA6A32` used only for the primary call to action.
