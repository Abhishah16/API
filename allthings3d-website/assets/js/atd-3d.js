/* =========================================================================
   All Things 3D — tiny 3D engine (no libraries, no CDN, ~7 KB)
   Renders parametric models as stacked print layers on a 2D canvas, plus a
   triangle-mesh renderer used by the STL/OBJ viewer on the order page.
   ========================================================================= */
(function (global) {
  'use strict';

  var PALETTE = {
    blue: '#0166AE', blue300: '#74B0DE', blue200: '#A9CFEC', blue700: '#014678',
    blue900: '#02243D', ember: '#EA6A32', ember300: '#F3A175', ink: '#22272A',
    grid: 'rgba(116,176,222,0.22)', white: '#FFFFFF'
  };

  var reduced = global.matchMedia &&
    global.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- utils */
  function fitCanvas(canvas) {
    var dpr = Math.min(global.devicePixelRatio || 1, 2);
    var r = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(r.width * dpr));
    var h = Math.max(1, Math.round(r.height * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    return { ctx: canvas.getContext('2d'), w: w, h: h, dpr: dpr };
  }

  function lerp(a, b, t) { return a + (b - a) * t; }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

  /* Accepts "#rrggbb" or the "rgb(r,g,b)" this function itself returns, so
     mixes can be chained without the second pass silently producing NaN. */
  function mixHex(a, b, t) {
    function p(h) {
      if (h.charAt(0) === '#') {
        return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
      }
      var m = h.match(/-?\d+/g);
      return [+m[0], +m[1], +m[2]];
    }
    var A = p(a), B = p(b);
    return 'rgb(' + Math.round(lerp(A[0], B[0], t)) + ',' + Math.round(lerp(A[1], B[1], t)) +
      ',' + Math.round(lerp(A[2], B[2], t)) + ')';
  }

  /* Piecewise-linear silhouette: heights 0..1 mapped to radius multipliers.
     Easier to read — and to redraw on paper — than stacked gaussians. */
  function ramp(ts, rs) {
    return function (t) {
      var i = 0;
      while (i < ts.length - 2 && t > ts[i + 1]) i++;
      var span = ts[i + 1] - ts[i] || 1;
      return rs[i] + (rs[i + 1] - rs[i]) * clamp((t - ts[i]) / span, 0, 1);
    };
  }

  /* --------------------------------------------------------------- models */
  /* A model is a radius function r(theta, t) where t is 0..1 up the height,
     plus a layer count and a height. Everything the site draws is built from
     these — vases, gears, lamps, tags, planters. */
  var MODELS = {
    vase: {
      label: 'Twisted vase', layers: 60, height: 138, radius: 38,
      profile: ramp([0, 0.06, 0.34, 0.60, 0.82, 0.93, 1],
                    [0.60, 0.74, 1.00, 0.80, 0.52, 0.50, 0.62]),
      r: function (a, t) {
        return this.profile(t) * (1 + 0.10 * Math.sin(6 * a + t * 8));
      }
    },
    lamp: {
      label: 'Lithophane lamp', layers: 46, height: 104, radius: 44,
      r: function (a, t) {
        var sq = 1 / Math.pow(Math.pow(Math.abs(Math.cos(a)), 6) +
          Math.pow(Math.abs(Math.sin(a)), 6), 1 / 6);
        var taper = 0.80 + 0.20 * Math.sin(Math.PI * (0.25 + t * 0.55));
        return sq * taper * 0.78;
      }
    },
    gear: {
      label: 'Gear / flange', layers: 16, height: 34, radius: 52,
      r: function (a) {
        var teeth = 14;
        var w = Math.sin(a * teeth);
        return 0.80 + 0.20 * (w > 0 ? Math.min(1, w * 3) : Math.max(-1, w * 3)) * 0.5 + 0.1;
      },
      hole: 0.30
    },
    tag: {
      label: 'Keychain tag', layers: 8, height: 16, radius: 54,
      r: function (a) {
        var sq = 1 / Math.pow(Math.pow(Math.abs(Math.cos(a) * 0.85), 8) +
          Math.pow(Math.abs(Math.sin(a) * 1.7), 8), 1 / 8);
        return Math.min(sq, 1.2) * 0.62;
      },
      hole: 0.12, holeOffset: 0.50
    },
    planter: {
      label: 'Planter', layers: 42, height: 96, radius: 44,
      profile: ramp([0, 0.08, 0.90, 1], [0.52, 0.60, 0.96, 1.00]),
      r: function (a, t) { return this.profile(t) * (1 + 0.09 * Math.sin(9 * a)); }
    },
    bracket: {
      label: 'Functional part', layers: 26, height: 58, radius: 50,
      r: function (a, t) {
        var sq = 1 / Math.pow(Math.pow(Math.abs(Math.cos(a)), 10) +
          Math.pow(Math.abs(Math.sin(a)), 10), 1 / 10);
        var notch = (t > 0.45 && Math.cos(a) > 0.25) ? 0.55 : 1;
        return sq * notch * 0.82;
      },
      hole: 0.22
    },
    ring: {
      label: 'Bangle / ring', layers: 14, height: 30, radius: 54,
      r: function (a) { return 0.92 + 0.05 * Math.sin(24 * a); },
      hole: 0.66
    },
    figurine: {
      label: 'Figurine', layers: 54, height: 124, radius: 34,
      profile: ramp([0, 0.05, 0.10, 0.34, 0.56, 0.63, 0.70, 0.82, 0.92, 1],
                    [0.78, 0.82, 0.56, 0.66, 0.58, 0.30, 0.46, 0.54, 0.40, 0.10]),
      r: function (a, t) { return this.profile(t) * (1 + 0.05 * Math.sin(3 * a)); }
    },
    nameplate: {
      label: 'Nameplate', layers: 10, height: 20, radius: 58,
      r: function (a) {
        var sq = 1 / Math.pow(Math.pow(Math.abs(Math.cos(a) * 1.9), 12) +
          Math.pow(Math.abs(Math.sin(a) * 0.7), 12), 1 / 12);
        return Math.min(sq, 1.5) * 0.55;
      }
    },
    dome: {
      label: 'Architectural model', layers: 44, height: 92, radius: 50,
      r: function (a, t) {
        var d = Math.sqrt(Math.max(0, 1 - t * t)) * 0.95;
        return Math.max(d, 0.18) * (1 + 0.06 * Math.sin(12 * a));
      }
    }
  };

  /* ------------------------------------------------------------ projection */
  function makeProjector(o) {
    var cos = Math.cos(o.spin), sin = Math.sin(o.spin);
    return function (x, y, z) {
      var rx = x * cos - y * sin;
      var ry = x * sin + y * cos;
      return {
        x: o.cx + rx * o.scale,
        y: o.cy - z * o.scale * o.zk + ry * o.scale * o.tilt,
        d: ry
      };
    };
  }

  function layerPath(ctx, model, t, radius, project, seg) {
    ctx.beginPath();
    for (var i = 0; i <= seg; i++) {
      var a = (i / seg) * Math.PI * 2;
      var r = model.r(a, t) * radius;
      var p = project(Math.cos(a) * r, Math.sin(a) * r, 0);
      if (i === 0) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
  }

  /* --------------------------------------------------------- print render */
  /* Draws a model as printed layers. progress 0..1 controls how much of the
     object exists yet — that is the whole "watch it being printed" effect. */
  function drawPrint(ctx, W, H, opts) {
    var model = opts.model;
    var progress = clamp(opts.progress, 0, 1);
    var spin = opts.spin || 0;
    var scale = opts.scale;
    var cx = W / 2, cy = H * (opts.baseline || 0.72);
    var tilt = 0.42, zk = 0.78;
    var seg = opts.seg || 72;
    var nLayers = model.layers;
    var built = Math.floor(progress * nLayers);
    var partial = progress * nLayers - built;

    ctx.clearRect(0, 0, W, H);

    /* --- print bed grid --- */
    if (opts.bed !== false) {
      var bedR = model.radius * scale * 1.75;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.scale(1, tilt);
      ctx.strokeStyle = PALETTE.grid;
      ctx.lineWidth = Math.max(1, scale * 0.012);
      var stepPx = bedR / 5;
      for (var g = -5; g <= 5; g++) {
        ctx.beginPath();
        var off = g * stepPx;
        var half = Math.sqrt(Math.max(0, bedR * bedR - off * off));
        ctx.moveTo(-half, off); ctx.lineTo(half, off);
        ctx.moveTo(off, -half); ctx.lineTo(off, half);
        ctx.stroke();
      }
      ctx.beginPath();
      ctx.arc(0, 0, bedR, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(116,176,222,0.42)';
      ctx.lineWidth = Math.max(1.2, scale * 0.02);
      ctx.stroke();
      ctx.restore();
    }

    var project = makeProjector({ cx: cx, cy: cy, scale: scale, spin: spin, tilt: tilt, zk: zk });
    var layerH = model.height / nLayers;

    /* --- ghost of what has not printed yet --- */
    if (opts.ghost !== false && built < nLayers) {
      ctx.save();
      ctx.strokeStyle = 'rgba(169,207,236,0.20)';
      ctx.lineWidth = Math.max(0.8, scale * 0.008);
      for (var gi = built; gi < nLayers; gi += Math.max(1, Math.round(nLayers / 14))) {
        var gt = gi / (nLayers - 1);
        ctx.save();
        ctx.translate(0, -gi * layerH * scale * zk);
        layerPath(ctx, model, gt, model.radius, project, 40);
        ctx.restore();
        ctx.stroke();
      }
      ctx.restore();
    }

    /* --- printed layers, bottom to top (painter's algorithm) --- */
    for (var i = 0; i <= built && i < nLayers; i++) {
      var t = i / (nLayers - 1);
      var isTop = (i === built);
      var shade = 0.18 + 0.62 * (i / Math.max(1, nLayers - 1));
      var fill = mixHex(PALETTE.blue900, PALETTE.blue300, shade);
      var fresh = built - i;
      if (isTop) fill = mixHex(fill, PALETTE.blue200, 0.45);
      else if (fresh < 3 && built < nLayers) fill = mixHex(fill, PALETTE.ember, (3 - fresh) * 0.09);

      ctx.save();
      ctx.translate(0, -i * layerH * scale * zk);
      if (isTop && partial > 0 && partial < 1) ctx.globalAlpha = 0.35 + partial * 0.65;

      layerPath(ctx, model, t, model.radius, project, seg);
      ctx.fillStyle = fill;
      ctx.fill();

      ctx.strokeStyle = isTop ? PALETTE.ember300 : 'rgba(2,36,61,0.55)';
      ctx.lineWidth = isTop ? Math.max(1.4, scale * 0.022) : Math.max(0.6, scale * 0.009);
      ctx.stroke();

      if (model.hole) {
        var hr = model.radius * model.hole;
        var ox = model.holeOffset ? model.radius * model.holeOffset : 0;
        ctx.beginPath();
        for (var k = 0; k <= 28; k++) {
          var ha = (k / 28) * Math.PI * 2;
          var hp = project(ox + Math.cos(ha) * hr, Math.sin(ha) * hr, 0);
          if (k === 0) ctx.moveTo(hp.x, hp.y); else ctx.lineTo(hp.x, hp.y);
        }
        ctx.closePath();
        ctx.fillStyle = 'rgba(2,20,34,0.92)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(116,176,222,0.35)';
        ctx.lineWidth = Math.max(0.6, scale * 0.008);
        ctx.stroke();
      }
      ctx.restore();
    }

    /* --- nozzle riding the top layer --- */
    if (opts.nozzle !== false && built < nLayers) {
      var nt = built / Math.max(1, nLayers - 1);
      var na = (opts.time || 0) * 3.4;
      var nr = model.r(na, nt) * model.radius;
      var np = project(Math.cos(na) * nr, Math.sin(na) * nr, 0);
      var ny = np.y - built * layerH * scale * zk;
      var s = scale * 0.9;

      ctx.save();
      /* filament thread from the head down to the layer */
      ctx.strokeStyle = PALETTE.ember;
      ctx.lineWidth = Math.max(1.4, s * 0.035);
      ctx.beginPath();
      ctx.moveTo(np.x, ny - s * 0.30);
      ctx.lineTo(np.x, ny);
      ctx.stroke();

      /* hot end */
      ctx.fillStyle = '#2E3437';
      ctx.strokeStyle = 'rgba(169,207,236,0.55)';
      ctx.lineWidth = Math.max(1, s * 0.014);
      ctx.beginPath();
      ctx.moveTo(np.x - s * 0.09, ny - s * 0.30);
      ctx.lineTo(np.x + s * 0.09, ny - s * 0.30);
      ctx.lineTo(np.x + s * 0.03, ny - s * 0.16);
      ctx.lineTo(np.x - s * 0.03, ny - s * 0.16);
      ctx.closePath();
      ctx.fill(); ctx.stroke();
      ctx.fillRect(np.x - s * 0.20, ny - s * 0.62, s * 0.40, s * 0.32);
      ctx.strokeRect(np.x - s * 0.20, ny - s * 0.62, s * 0.40, s * 0.32);

      /* glow at the nozzle tip */
      var glow = ctx.createRadialGradient(np.x, ny, 0, np.x, ny, s * 0.22);
      glow.addColorStop(0, 'rgba(234,106,50,0.55)');
      glow.addColorStop(1, 'rgba(234,106,50,0)');
      ctx.fillStyle = glow;
      ctx.beginPath(); ctx.arc(np.x, ny, s * 0.22, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }
  }

  /* ------------------------------------------------------- mesh (STL/OBJ) */
  /* Flat-shaded painter's-algorithm renderer for an uploaded triangle mesh. */
  function drawMesh(ctx, W, H, mesh, opts) {
    ctx.clearRect(0, 0, W, H);
    if (!mesh || !mesh.tris.length) return;

    var spin = opts.spin || 0, pitch = opts.pitch != null ? opts.pitch : 0.5;
    var cs = Math.cos(spin), sn = Math.sin(spin);
    var cp = Math.cos(pitch), sp = Math.sin(pitch);
    var c = mesh.center, size = mesh.size;
    var scale = (Math.min(W, H) * 0.72) / (size || 1);
    var cx = W / 2, cy = H / 2;

    function proj(v) {
      var x = v[0] - c[0], y = v[1] - c[1], z = v[2] - c[2];
      var rx = x * cs - y * sn;
      var ry = x * sn + y * cs;
      var ry2 = ry * cp - z * sp;
      var rz2 = ry * sp + z * cp;
      return [cx + rx * scale, cy + ry2 * scale, rz2, rx, ry2, rz2];
    }

    var list = [], i, t;
    for (i = 0; i < mesh.tris.length; i++) {
      t = mesh.tris[i];
      var a = proj(t[0]), b = proj(t[1]), d = proj(t[2]);
      list.push({ a: a, b: b, c: d, z: (a[2] + b[2] + d[2]) / 3 });
    }
    list.sort(function (p, q) { return p.z - q.z; });

    var light = [0.45, -0.62, 0.65];
    for (i = 0; i < list.length; i++) {
      var tri = list[i];
      var ux = tri.b[0] - tri.a[0], uy = tri.b[1] - tri.a[1], uz = tri.b[2] - tri.a[2];
      var vx = tri.c[0] - tri.a[0], vy = tri.c[1] - tri.a[1], vz = tri.c[2] - tri.a[2];
      var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      var len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
      var lam = clamp((nx / len) * light[0] + (ny / len) * light[1] + (nz / len) * light[2], -1, 1);
      var shade = clamp(0.30 + 0.70 * Math.abs(lam), 0, 1);

      ctx.beginPath();
      ctx.moveTo(tri.a[0], tri.a[1]);
      ctx.lineTo(tri.b[0], tri.b[1]);
      ctx.lineTo(tri.c[0], tri.c[1]);
      ctx.closePath();
      ctx.fillStyle = mixHex(PALETTE.blue900, PALETTE.blue200, shade);
      ctx.fill();
      if (opts.wire) {
        ctx.strokeStyle = 'rgba(169,207,236,0.14)';
        ctx.lineWidth = 0.6;
        ctx.stroke();
      }
    }
  }

  /* ------------------------------------------------------------ STL / OBJ */
  function parseSTL(buffer) {
    var view = new DataView(buffer);
    var tris = [];
    var isBinary = true;

    /* An ASCII STL starts with "solid"; but so do some binary ones, so the
       trustworthy check is whether the byte count matches the triangle count. */
    if (buffer.byteLength >= 84) {
      var n = view.getUint32(80, true);
      isBinary = (84 + n * 50) === buffer.byteLength;
    } else {
      isBinary = false;
    }

    if (isBinary) {
      var count = view.getUint32(80, true);
      var off = 84;
      for (var i = 0; i < count; i++) {
        var base = off + i * 50 + 12;
        tris.push([
          [view.getFloat32(base, true), view.getFloat32(base + 4, true), view.getFloat32(base + 8, true)],
          [view.getFloat32(base + 12, true), view.getFloat32(base + 16, true), view.getFloat32(base + 20, true)],
          [view.getFloat32(base + 24, true), view.getFloat32(base + 28, true), view.getFloat32(base + 32, true)]
        ]);
      }
    } else {
      var text = new TextDecoder().decode(buffer);
      var re = /vertex\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)/g;
      var pts = [], m;
      while ((m = re.exec(text)) !== null) {
        pts.push([parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])]);
      }
      for (var k = 0; k + 2 < pts.length; k += 3) tris.push([pts[k], pts[k + 1], pts[k + 2]]);
    }
    return finishMesh(tris);
  }

  function parseOBJ(text) {
    var verts = [], tris = [], lines = text.split('\n');
    for (var i = 0; i < lines.length; i++) {
      var l = lines[i].trim();
      if (l.charCodeAt(0) === 118 && l.charCodeAt(1) === 32) { /* "v " */
        var p = l.split(/\s+/);
        verts.push([parseFloat(p[1]), parseFloat(p[2]), parseFloat(p[3])]);
      } else if (l.charCodeAt(0) === 102 && l.charCodeAt(1) === 32) { /* "f " */
        var f = l.split(/\s+/).slice(1).map(function (s) {
          var idx = parseInt(s.split('/')[0], 10);
          return idx < 0 ? verts.length + idx : idx - 1;
        });
        for (var j = 1; j + 1 < f.length; j++) {
          if (verts[f[0]] && verts[f[j]] && verts[f[j + 1]]) {
            tris.push([verts[f[0]], verts[f[j]], verts[f[j + 1]]]);
          }
        }
      }
    }
    return finishMesh(tris);
  }

  /* Bounding box, centre, and a signed-volume sum — the volume is what the
     price estimator needs, and it is exact for a closed mesh. */
  function finishMesh(tris) {
    var min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
    var vol = 0, area = 0;
    for (var i = 0; i < tris.length; i++) {
      var t = tris[i];
      for (var v = 0; v < 3; v++) {
        for (var d = 0; d < 3; d++) {
          if (t[v][d] < min[d]) min[d] = t[v][d];
          if (t[v][d] > max[d]) max[d] = t[v][d];
        }
      }
      var a = t[0], b = t[1], c = t[2];
      vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) -
              a[1] * (b[0] * c[2] - b[2] * c[0]) +
              a[2] * (b[0] * c[1] - b[1] * c[0])) / 6;
      var ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2];
      var vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
      var nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      area += Math.sqrt(nx * nx + ny * ny + nz * nz) / 2;
    }
    if (!tris.length) { min = [0, 0, 0]; max = [0, 0, 0]; }
    var dims = [max[0] - min[0], max[1] - min[1], max[2] - min[2]];
    return {
      tris: tris,
      dims: dims,
      center: [(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2],
      size: Math.max(dims[0], dims[1], dims[2]) || 1,
      volume: Math.abs(vol),          /* model units cubed — mm³ for STL */
      area: area
    };
  }

  global.ATD3D = {
    MODELS: MODELS,
    PALETTE: PALETTE,
    reduced: reduced,
    fitCanvas: fitCanvas,
    drawPrint: drawPrint,
    drawMesh: drawMesh,
    parseSTL: parseSTL,
    parseOBJ: parseOBJ,
    easeOut: easeOut,
    clamp: clamp
  };
})(window);
