/* =========================================================================
   All Things 3D — order page: file drop, live 3D preview, price estimator,
   and the enquiry handoff (WhatsApp / email / optional form endpoint).
   Pricing constants live in ATD_CONFIG.pricing (assets/js/atd.js).
   ========================================================================= */
(function () {
  'use strict';
  var A = window.ATD3D;
  var C = window.ATD_CONFIG;
  if (!document.getElementById('orderForm')) return;

  function $(s) { return document.querySelector(s); }
  var reduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ------------------------------------------------------------- state */
  var state = {
    mesh: null,
    file: null,
    fileName: '',
    dims: null            /* [x, y, z] in mm, from file or manual entry */
  };

  /* --------------------------------------------------------- 3D preview */
  var viewer = $('#viewer');
  var canvas = $('#viewerCanvas');
  var hint = $('#viewerHint');
  var meta = $('#viewerMeta');
  var spin = 0.6, pitch = 0.62, dragging = false, lastX = 0, lastY = 0, raf = null;

  function paint() {
    if (!state.mesh) return;
    var f = A.fitCanvas(canvas);
    A.drawMesh(f.ctx, f.w, f.h, state.mesh, { spin: spin, pitch: pitch, wire: state.mesh.tris.length < 4000 });
  }

  function autoSpin() {
    if (reduced || !state.mesh) { raf = null; return; }
    if (!dragging) { spin += 0.006; paint(); }
    raf = requestAnimationFrame(autoSpin);
  }

  if (canvas) {
    canvas.addEventListener('pointerdown', function (e) {
      dragging = true; lastX = e.clientX; lastY = e.clientY;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      spin += (e.clientX - lastX) * 0.01;
      pitch = A.clamp(pitch + (e.clientY - lastY) * 0.008, -1.4, 1.4);
      lastX = e.clientX; lastY = e.clientY;
      paint();
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (ev) {
      canvas.addEventListener(ev, function () { dragging = false; });
    });
    window.addEventListener('resize', paint);
  }

  /* ------------------------------------------------------------ file in */
  var input = $('#fileInput');
  var drop = $('#dropzone');
  var fileLabel = $('#fileLabel');

  function humanSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(0) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function handleFile(file) {
    if (!file) return;
    state.file = file;
    state.fileName = file.name;
    if (fileLabel) {
      fileLabel.textContent = file.name + ' — ' + humanSize(file.size);
      fileLabel.classList.remove('hidden');
    }

    var ext = (file.name.split('.').pop() || '').toLowerCase();
    var previewable = (ext === 'stl' || ext === 'obj');

    if (!previewable) {
      state.mesh = null;
      if (hint) {
        hint.classList.remove('hidden');
        hint.textContent = ext ? ('.' + ext + ' received — we will open it at our end') :
          'File received';
      }
      if (meta) meta.classList.add('hidden');
      recalc();
      return;
    }

    if (file.size > 60 * 1024 * 1024) {
      if (hint) { hint.classList.remove('hidden'); hint.textContent = 'File too large to preview — send it anyway'; }
      recalc();
      return;
    }

    var reader = new FileReader();
    reader.onload = function (e) {
      try {
        state.mesh = (ext === 'stl') ? A.parseSTL(e.target.result)
                                     : A.parseOBJ(new TextDecoder().decode(e.target.result));
      } catch (err) {
        state.mesh = null;
      }
      if (!state.mesh || !state.mesh.tris.length) {
        if (hint) { hint.classList.remove('hidden'); hint.textContent = 'Could not read that mesh — send it and we will check'; }
        recalc();
        return;
      }
      state.dims = state.mesh.dims;
      if (hint) hint.classList.add('hidden');
      if (meta) {
        meta.classList.remove('hidden');
        meta.innerHTML =
          '<span>Size <b>' + state.mesh.dims.map(function (d) { return d.toFixed(1); }).join(' × ') + ' mm</b></span>' +
          '<span>Volume <b>' + (state.mesh.volume / 1000).toFixed(1) + ' cm³</b></span>' +
          '<span>Triangles <b>' + state.mesh.tris.length.toLocaleString('en-IN') + '</b></span>' +
          '<span class="muted">drag to rotate</span>';
      }
      /* mirror the measured size into the manual fields */
      ['dimX', 'dimY', 'dimZ'].forEach(function (id, i) {
        var el = document.getElementById(id);
        if (el) el.value = Math.round(state.mesh.dims[i] * 10) / 10;
      });
      paint();
      if (!raf) raf = requestAnimationFrame(autoSpin);
      recalc();
    };
    reader.readAsArrayBuffer(file);
  }

  if (input) input.addEventListener('change', function (e) { handleFile(e.target.files[0]); });
  if (drop) {
    ['dragenter', 'dragover'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('is-over'); });
    });
    drop.addEventListener('drop', function (e) {
      var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
      if (f) {
        handleFile(f);
        try {                                  /* keep the real input in sync */
          var dt = new DataTransfer();
          dt.items.add(f);
          input.files = dt.files;
        } catch (err) { /* older browsers: the file is still in state */ }
      }
    });
  }

  /* ----------------------------------------------------------- estimator */
  var P = C.pricing;

  function val(id) { var el = document.getElementById(id); return el ? el.value : ''; }
  function num(id, dflt) {
    var v = parseFloat(val(id));
    return isNaN(v) ? dflt : v;
  }

  function volumeBreak(qty) {
    var m = 1;
    for (var i = 0; i < P.volumeBreaks.length; i++) {
      if (qty >= P.volumeBreaks[i][0]) m = P.volumeBreaks[i][1];
    }
    return m;
  }

  function estimate() {
    var mat = P.materials[val('material')] || P.materials.pla;
    var qual = P.quality[val('quality')] || P.quality.standard;
    var fin = P.finishes[val('finish')] || P.finishes.cleaned;
    var qty = Math.max(1, Math.round(num('qty', 1)));
    var infill = A.clamp(num('infill', 20), 0, 100) / 100;

    /* solid volume in cm³ — measured from the mesh when we have one,
       otherwise from the bounding box with a shape allowance. */
    var solidCm3;
    if (state.mesh && state.mesh.volume > 0) {
      solidCm3 = state.mesh.volume / 1000;
    } else {
      var x = num('dimX', 0), y = num('dimY', 0), z = num('dimZ', 0);
      if (!x || !y || !z) return null;
      solidCm3 = (x * y * z) / 1000 * 0.34;      /* typical part fills ~1/3 of its box */
    }
    if (solidCm3 <= 0) return null;

    /* material actually extruded: perimeters + infill */
    var matFraction = A.clamp(0.16 + 0.84 * infill, 0.18, 1);
    if (val('material') === 'resin') matFraction = 1;
    var usedCm3 = solidCm3 * matFraction;
    var grams = usedCm3 * mat.density;

    /* printer time: throughput ~12 cm³/h at 0.20 mm, plus handling per part */
    var hours = (usedCm3 / 12) * qual.mult + 0.15;

    var unit = grams * mat.rate + hours * P.machineRatePerHour;
    unit = unit * (1 + fin.add);
    unit = unit * volumeBreak(qty);

    var total = unit * qty + P.setupFee;
    if (total < P.minOrder) total = P.minOrder;

    return {
      unit: unit, total: total, qty: qty, grams: grams * qty,
      hours: hours * qty, material: mat.label, finish: fin.label,
      quality: qual.label,
      low: Math.max(total * 0.85, P.minOrder), high: total * 1.2,
      infill: Math.round(infill * 100)
    };
  }

  function inr(n) {
    return '₹' + Math.round(n).toLocaleString('en-IN');
  }

  var out = {
    box: $('#estimateBox'), range: $('#estRange'), unit: $('#estUnit'),
    weight: $('#estWeight'), time: $('#estTime'), qty: $('#estQty'), empty: $('#estEmpty')
  };

  function recalc() {
    var e = estimate();
    if (!out.box) return;
    if (!e) {
      if (out.empty) out.empty.classList.remove('hidden');
      if (out.range) {
        out.range.textContent = 'Add a size to see a number';
        out.range.classList.add('estimate__num--empty');
      }
      ['unit', 'weight', 'time', 'qty'].forEach(function (k) {
        if (out[k]) out[k].textContent = '—';
      });
      return;
    }
    if (out.empty) out.empty.classList.add('hidden');
    out.range.classList.remove('estimate__num--empty');
    out.range.textContent = inr(e.low) + ' – ' + inr(e.high);
    out.unit.textContent = inr(e.unit) + ' / piece';
    out.weight.textContent = e.grams.toFixed(0) + ' g';
    out.time.textContent = e.hours < 1 ? Math.round(e.hours * 60) + ' min' : e.hours.toFixed(1) + ' h';
    out.qty.textContent = e.qty + ' pc' + (e.qty > 1 ? 's' : '');
  }

  ['material', 'quality', 'finish', 'qty', 'infill', 'dimX', 'dimY', 'dimZ'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) { el.addEventListener('input', recalc); el.addEventListener('change', recalc); }
  });

  var infillOut = $('#infillOut');
  var infillEl = $('#infill');
  if (infillEl && infillOut) {
    var sync = function () { infillOut.textContent = infillEl.value + '%'; };
    infillEl.addEventListener('input', sync); sync();
  }

  /* -------------------------------------------------------- the handoff */
  function brief() {
    var e = estimate();
    var lines = [];
    lines.push('*New enquiry from allthings3d.com*');
    lines.push('');
    lines.push('Name: ' + (val('name') || '—'));
    lines.push('Phone: ' + (val('phone') || '—'));
    lines.push('Email: ' + (val('email') || '—'));
    if (val('company')) lines.push('Company: ' + val('company'));
    lines.push('Order type: ' + (val('orderType') || '—'));
    lines.push('');
    lines.push('File: ' + (state.fileName || 'to be sent in this chat'));
    if (state.mesh) {
      lines.push('Measured: ' + state.mesh.dims.map(function (d) { return d.toFixed(1); }).join(' x ') +
        ' mm, ' + (state.mesh.volume / 1000).toFixed(1) + ' cm3');
    } else if (num('dimX', 0)) {
      lines.push('Approx size: ' + num('dimX', 0) + ' x ' + num('dimY', 0) + ' x ' + num('dimZ', 0) + ' mm');
    }
    lines.push('Material: ' + (e ? e.material : val('material')));
    lines.push('Layer height: ' + (e ? e.quality : val('quality')));
    lines.push('Infill: ' + (infillEl ? infillEl.value + '%' : '—'));
    lines.push('Finish: ' + (e ? e.finish : val('finish')));
    lines.push('Quantity: ' + (val('qty') || '1'));
    if (val('deadline')) lines.push('Needed by: ' + val('deadline'));
    if (e) lines.push('Site estimate: ' + inr(e.low) + ' - ' + inr(e.high) + ' (indicative)');
    if (val('brief')) { lines.push(''); lines.push('Brief: ' + val('brief')); }
    return lines.join('\n');
  }

  function required() {
    var missing = [];
    if (!val('name').trim()) missing.push('name');
    if (!val('phone').trim()) missing.push('phone');
    return missing;
  }

  function flagMissing(missing) {
    var note = $('#formNote');
    if (note) {
      note.textContent = 'Please add your ' + missing.join(' and ') + ' so we can reply.';
      note.classList.remove('hidden');
    }
    var first = document.getElementById(missing[0]);
    if (first) first.focus();
  }

  var waBtn = $('#sendWhatsApp');
  if (waBtn) {
    waBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var missing = required();
      if (missing.length) return flagMissing(missing);
      var note = $('#formNote');
      if (note) note.classList.add('hidden');
      window.open('https://wa.me/' + C.phone + '?text=' + encodeURIComponent(brief()), '_blank', 'noopener');
      var after = $('#afterSend');
      if (after) after.classList.remove('hidden');
    });
  }

  var mailBtn = $('#sendEmail');
  if (mailBtn) {
    mailBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var missing = required();
      if (missing.length) return flagMissing(missing);
      var note = $('#formNote');
      if (note) note.classList.add('hidden');
      var body = brief().replace(/\*/g, '');
      window.location.href = 'mailto:' + C.email +
        '?subject=' + encodeURIComponent('3D printing enquiry — ' + (val('name') || 'website')) +
        '&body=' + encodeURIComponent(body + '\n\n(Please attach your file to this email.)');
      var after = $('#afterSend');
      if (after) after.classList.remove('hidden');
    });
  }

  var copyBtn = $('#copyBrief');
  if (copyBtn) {
    copyBtn.addEventListener('click', function (ev) {
      ev.preventDefault();
      var text = brief().replace(/\*/g, '');
      var done = function () {
        copyBtn.textContent = 'Copied';
        setTimeout(function () { copyBtn.textContent = 'Copy the brief'; }, 2000);
      };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done);
      else {
        var ta = document.createElement('textarea');
        ta.value = text; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch (e) {}
        document.body.removeChild(ta); done();
      }
    });
  }

  /* Real form POST — only active once a form endpoint is configured. */
  var form = $('#orderForm');
  if (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var missing = required();
      if (missing.length) return flagMissing(missing);
      if (!C.formEndpoint) { if (waBtn) waBtn.click(); return; }

      var data = new FormData(form);
      data.append('brief', brief());
      var btn = $('#formSubmit');
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      fetch(C.formEndpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('bad status');
          window.location.href = 'thank-you.html';
        })
        .catch(function () {
          var note = $('#formNote');
          if (note) {
            note.textContent = 'That did not go through. Please send it on WhatsApp instead.';
            note.classList.remove('hidden');
          }
          if (btn) { btn.disabled = false; btn.textContent = 'Send my enquiry'; }
        });
    });
  }

  recalc();
})();
