/* =========================================================================
   All Things 3D — site behaviour
   Edit ATD_CONFIG below to change contact details site-wide.
   ========================================================================= */
window.ATD_CONFIG = {
  /* --- contact: change here, changes everywhere JS builds a link --- */
  phone: '917666004531',                     /* country code + number, digits only */
  phoneDisplay: '+91 76660 04531',
  email: 'info.allthings3d@gmail.com',
  instagram: 'https://www.instagram.com/allthings3d.in',
  domain: 'allthings3d.com',

  /* --- optional: paste a Formspree / Netlify / Google Apps Script URL here
         and the order form will POST to it (with the file) instead of only
         handing off to WhatsApp or email. Leave empty to keep the handoff. */
  formEndpoint: '',

  /* --- indicative pricing used by the estimator on the order page.
         All figures in INR. Change these, not the code. --- */
  pricing: {
    setupFee: 150,                 /* per job: file prep, slicing, bed setup */
    minOrder: 300,
    machineRatePerHour: 90,        /* printer time */
    materials: {                   /* rate per gram, and density g/cm3 */
      pla:   { label: 'PLA',                  rate: 3.2, density: 1.24 },
      petg:  { label: 'PETG',                 rate: 3.8, density: 1.27 },
      abs:   { label: 'ABS / ASA',            rate: 4.0, density: 1.05 },
      tpu:   { label: 'TPU (flexible)',       rate: 6.5, density: 1.21 },
      pacf:  { label: 'Nylon / PA-CF',        rate: 12.0, density: 1.15 },
      resin: { label: 'Resin (SLA, detail)',  rate: 9.0, density: 1.10 }
    },
    quality: {                     /* layer height -> time multiplier */
      draft:    { label: '0.28 mm — draft',    mult: 0.72 },
      standard: { label: '0.20 mm — standard', mult: 1.00 },
      fine:     { label: '0.12 mm — fine',     mult: 1.65 },
      ultra:    { label: '0.08 mm — ultra',    mult: 2.40 }
    },
    finishes: {
      raw:      { label: 'As printed',              add: 0 },
      cleaned:  { label: 'Cleaned + supports off',  add: 0.10 },
      sanded:   { label: 'Sanded smooth',           add: 0.35 },
      painted:  { label: 'Primed + painted',        add: 0.85 }
    },
    /* quantity discount: [minQty, multiplier] */
    volumeBreaks: [[1, 1], [10, 0.88], [25, 0.80], [50, 0.72], [100, 0.64], [250, 0.56], [500, 0.48]]
  }
};

(function () {
  'use strict';
  var C = window.ATD_CONFIG;
  var reduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* ------------------------------------------------- contact link wiring */
  function wireContacts() {
    $$('[data-tel]').forEach(function (el) {
      el.href = 'tel:+' + C.phone;
      if (el.dataset.tel === 'text') el.textContent = C.phoneDisplay;
    });
    $$('[data-mail]').forEach(function (el) {
      var subject = el.dataset.subject || 'Enquiry from allthings3d.com';
      el.href = 'mailto:' + C.email + '?subject=' + encodeURIComponent(subject);
      if (el.dataset.mail === 'text') el.textContent = C.email;
    });
    $$('[data-wa]').forEach(function (el) {
      var msg = el.dataset.wa || 'Hi All Things 3D — I have an idea I would like printed.';
      el.href = 'https://wa.me/' + C.phone + '?text=' + encodeURIComponent(msg);
      el.target = '_blank'; el.rel = 'noopener';
    });
    $$('[data-ig]').forEach(function (el) {
      el.href = C.instagram; el.target = '_blank'; el.rel = 'noopener';
    });
    $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }

  /* ---------------------------------------------------------------- nav */
  function nav() {
    var bar = $('.nav');
    var toggle = $('.nav__toggle');
    var links = $('.nav__links');
    if (toggle && links) {
      toggle.addEventListener('click', function () {
        var open = links.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        document.body.style.overflow = open && window.innerWidth <= 1040 ? 'hidden' : '';
      });
      links.addEventListener('click', function (e) {
        if (e.target.closest('a') && window.innerWidth <= 1040) {
          links.classList.remove('is-open');
          toggle.setAttribute('aria-expanded', 'false');
          document.body.style.overflow = '';
        }
      });
      window.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && links.classList.contains('is-open')) toggle.click();
      });
    }
    if (bar) {
      var onScroll = function () { bar.classList.toggle('is-stuck', window.scrollY > 8); };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
    var rail = $('.progress-rail__fill');
    if (rail) {
      window.addEventListener('scroll', function () {
        var h = document.documentElement.scrollHeight - window.innerHeight;
        rail.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
      }, { passive: true });
    }
  }

  /* ------------------------------------------------------------- reveal */
  function reveal() {
    var items = $$('.reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window) || reduced) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        var delay = parseFloat(el.dataset.delay || 0);
        setTimeout(function () { el.classList.add('is-in'); }, delay * 1000);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ----------------------------------------------------------- counters */
  function counters() {
    var nums = $$('[data-count]');
    if (!nums.length || !('IntersectionObserver' in window)) {
      nums.forEach(function (el) { el.textContent = el.dataset.count + (el.dataset.suffix || ''); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        io.unobserve(el);
        var target = parseFloat(el.dataset.count);
        var suffix = el.dataset.suffix || '';
        var prefix = el.dataset.prefix || '';
        if (reduced) { el.textContent = prefix + target + suffix; return; }
        var dur = 1400, t0 = performance.now();
        (function tick(now) {
          var p = Math.min(1, (now - t0) / dur);
          var eased = 1 - Math.pow(1 - p, 3);
          var val = target * eased;
          el.textContent = prefix + (target % 1 === 0 ? Math.round(val) : val.toFixed(1)) + suffix;
          if (p < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: 0.4 });
    nums.forEach(function (el) { io.observe(el); });
  }

  /* --------------------------------------------------------------- tilt */
  function tilt() {
    if (reduced || window.matchMedia('(pointer: coarse)').matches) return;
    $$('.tilt').forEach(function (el) {
      var raf = null;
      el.addEventListener('mousemove', function (e) {
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = null;
          var r = el.getBoundingClientRect();
          var px = (e.clientX - r.left) / r.width - 0.5;
          var py = (e.clientY - r.top) / r.height - 0.5;
          el.style.transform = 'perspective(900px) rotateX(' + (-py * 6).toFixed(2) +
            'deg) rotateY(' + (px * 8).toFixed(2) + 'deg) translateY(-6px)';
        });
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------------- accordion */
  function accordion() {
    $$('.acc__q').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item = btn.closest('.acc__item');
        var open = item.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ------------------------------------------------------ step timeline */
  function steps() {
    var wraps = $$('.steps');
    if (!wraps.length) return;
    function update() {
      wraps.forEach(function (wrap) {
        var fill = $('.steps__fill', wrap);
        var r = wrap.getBoundingClientRect();
        if (!r.height) return;
        var mid = window.innerHeight * 0.62;
        var p = Math.max(0, Math.min(1, (mid - r.top) / r.height));
        if (fill) fill.style.height = (p * (r.height - 24)) + 'px';
        $$('.step', wrap).forEach(function (s) {
          s.classList.toggle('is-active', s.getBoundingClientRect().top < mid);
        });
      });
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  /* ------------------------------------------------------ gallery filter */
  function filters() {
    var bar = $('.filters');
    if (!bar) return;
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('.filter');
      if (!btn) return;
      $$('.filter', bar).forEach(function (b) { b.classList.remove('is-active'); });
      btn.classList.add('is-active');
      var key = btn.dataset.filter;
      $$('.tile').forEach(function (tile) {
        var match = key === 'all' || (tile.dataset.cat || '').split(' ').indexOf(key) > -1;
        tile.classList.toggle('is-hidden', !match);
        if (match) {
          tile.style.animation = 'none';
          void tile.offsetWidth;
          tile.style.animation = '';
        }
      });
    });
  }

  /* ---------------------------------------------------------- marquee */
  function marquee() {
    $$('.marquee__track').forEach(function (track) {
      var group = $('.marquee__group', track);
      if (group && track.children.length === 1) {
        var clone = group.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        track.appendChild(clone);
      }
    });
  }

  /* ------------------------------------------------------- hero printer */
  function heroPrinter() {
    var canvas = $('#heroPrint');
    if (!canvas || !window.ATD3D) return;
    var A = window.ATD3D;
    var order = ['vase', 'lamp', 'gear', 'figurine', 'planter'];
    var idx = 0;
    var t0 = performance.now();
    var CYCLE = 9000;         /* ms per model: build, hold, swap */
    var hud = {
      layer: $('#hudLayer'), pct: $('#hudPct'), name: $('#hudName')
    };
    var visible = true;

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { visible = e[0].isIntersecting; },
        { threshold: 0.05 }).observe(canvas);
    }

    function frame(now) {
      requestAnimationFrame(frame);
      if (!visible) { t0 += 16; return; }

      var f = A.fitCanvas(canvas);
      var elapsed = now - t0;
      if (elapsed > CYCLE) { t0 = now; elapsed = 0; idx = (idx + 1) % order.length; }

      var model = A.MODELS[order[idx]];
      var buildT = A.clamp(elapsed / (CYCLE * 0.62), 0, 1);
      var progress = A.easeOut(buildT);
      var spin = reduced ? 0.6 : (elapsed / 1000) * 0.42 + idx * 1.1;
      var scale = (Math.min(f.w, f.h) / f.dpr) / 215 * f.dpr;

      A.drawPrint(f.ctx, f.w, f.h, {
        model: model, progress: progress, spin: spin,
        scale: scale, time: elapsed / 1000, baseline: 0.74
      });

      if (hud.layer) {
        var built = Math.round(progress * model.layers);
        hud.layer.textContent = built + '/' + model.layers;
        hud.pct.textContent = Math.round(progress * 100) + '%';
        hud.name.textContent = model.label;
      }
    }
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------- product / gallery renders */
  function tileArt() {
    var canvases = $$('canvas[data-model]');
    if (!canvases.length || !window.ATD3D) return;
    var A = window.ATD3D;

    canvases.forEach(function (canvas) {
      var model = A.MODELS[canvas.dataset.model] || A.MODELS.vase;
      var spin = parseFloat(canvas.dataset.spin || '0.7');
      var hovering = false, raf = null, drawn = false;

      function paint(spinNow) {
        var f = A.fitCanvas(canvas);
        var scale = (Math.min(f.w, f.h) / f.dpr) / 205 * f.dpr;
        A.drawPrint(f.ctx, f.w, f.h, {
          model: model, progress: 1, spin: spinNow, scale: scale,
          time: 0, nozzle: false, ghost: false, baseline: 0.78, seg: 56
        });
      }

      function loop(now) {
        if (!hovering) { raf = null; return; }
        spin += 0.012;
        paint(spin);
        raf = requestAnimationFrame(loop);
      }

      var host = canvas.closest('.tile') || canvas.parentElement;
      if (!reduced) {
        host.addEventListener('mouseenter', function () {
          hovering = true;
          if (!raf) raf = requestAnimationFrame(loop);
        });
        host.addEventListener('mouseleave', function () { hovering = false; });
      }

      if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (en) {
          if (en[0].isIntersecting && !drawn) { drawn = true; paint(spin); io.disconnect(); }
        }, { threshold: 0.1 });
        io.observe(canvas);
      } else { paint(spin); }

      window.addEventListener('resize', function () { paint(spin); });
    });
  }

  /* ------------------------------------------------------------- boot */
  function boot() {
    wireContacts(); nav(); reveal(); counters(); tilt();
    accordion(); steps(); filters(); marquee(); heroPrinter(); tileArt();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
