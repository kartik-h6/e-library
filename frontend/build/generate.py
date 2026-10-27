#!/usr/bin/env python3
"""Static site generator for the TechStudyHubCore Pharmacy (P0).

Reads data/catalogue.json and writes the public static site:
home, about, semesters, search, contribute, contact, one page per semester,
one page per subject, a 404 page, plus shared assets and data/schema.json.

Run from the repository root:  python3 build/generate.py
"""
import json, os, re, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, "data", "catalogue.json"), encoding="utf-8"))

# How each kind of material is labelled on a subject page.
KIND_LABEL = {"notes": "Notes", "paper": "Question paper", "manual": "Lab manual",
              "book": "Reference book", "other": "Material"}
# Optional: the hosted backend's sign-in URL. Empty hides the "Sign in" link in the nav.
SIGN_IN_URL = os.environ.get("SIGN_IN_URL", "")
# Optional: the staff service's base URL. When set, subject pages load published material live
# from its public API, so students see updates without a rebuild.
API_BASE = os.environ.get("API_BASE", "")


TYPE_LABEL = {"theory": "Theory", "practical": "Practical", "aec": "AEC — Ability Enhancement",
              "sec": "SEC — Skill Enhancement", "vac": "VAC — Value Added",
              "internship": "Internship", "project": "Research Project"}
GROUP_ORDER = [("theory", "Core theory"), ("practical", "Core practicals"),
               ("aec", "Ability Enhancement Courses (AEC)"), ("sec", "Skill Enhancement Courses (SEC)"),
               ("vac", "Value Added Courses (VAC)"), ("internship", "Internship"),
               ("project", "Research Project")]


def write(relpath, content):
    path = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- CSS
TOKENS = """:root{
  --bg:#eef2f6; --surface:#ffffff; --surface-2:#f8fafc;
  --ink:#1f2937; --ink-soft:#4b5563; --muted:#6b7280; --line:#e2e8f0;
  --primary:#0f766e; --primary-strong:#0d9488; --primary-soft:#f0fdfa;
  --header-from:#0f172a; --header-to:#134e4a;
  --radius:16px; --radius-sm:10px; --radius-pill:999px;
  --shadow:0 1px 3px rgba(15,23,42,.08),0 8px 24px rgba(15,23,42,.06);
  --shadow-sm:0 1px 2px rgba(15,23,42,.08);
  --space:1rem; --maxw:1100px;
  --font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}"""

BASE = """*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--font);background:var(--bg);color:var(--ink);line-height:1.55;font-size:16px}
img,svg{max-width:100%;display:block}
h1,h2,h3,h4{line-height:1.25;margin:0 0 .5rem;font-weight:700}
h1{font-size:1.7rem}h2{font-size:1.35rem}h3{font-size:1.08rem}
p{margin:0 0 .8rem}
a{color:var(--primary);text-decoration:none}
a:hover{text-decoration:underline}
ul{margin:0 0 .8rem;padding-left:1.15rem}
:focus-visible{outline:3px solid var(--primary-strong);outline-offset:2px;border-radius:4px}
.visually-hidden{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.skip-link{position:absolute;left:-999px;top:0;background:#fff;padding:.6rem 1rem;z-index:100}
.skip-link:focus{left:.5rem;top:.5rem}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}"""

LAYOUT = """.site-header{background:linear-gradient(120deg,var(--header-from),var(--header-to));color:#fff}
.header-inner{max-width:var(--maxw);margin:0 auto;padding:.9rem 1rem;display:flex;align-items:center;justify-content:space-between;gap:1rem}
.brand{display:flex;align-items:center;gap:.65rem;color:#fff}
.brand:hover{text-decoration:none}
.brand .brand-mark{width:42px;height:42px;flex:0 0 auto}
.brand b{font-size:1.12rem;display:block;line-height:1.1}
.brand span{font-size:.74rem;color:#a7f3d0;letter-spacing:.02em}
.nav-toggle{display:inline-flex;flex-direction:column;gap:5px;background:none;border:0;padding:.5rem;cursor:pointer}
.nav-toggle span{width:24px;height:2px;background:#fff;display:block}
.site-nav{border-top:1px solid rgba(255,255,255,.14);background:rgba(0,0,0,.16)}
.site-nav ul{max-width:var(--maxw);margin:0 auto;padding:.55rem 1rem;list-style:none;display:flex;flex-wrap:wrap;gap:.35rem}
.site-nav a{color:#e6fffb;padding:.35rem .7rem;border-radius:var(--radius-pill);font-size:.92rem}
.site-nav a:hover{background:rgba(255,255,255,.14);text-decoration:none}
.site-nav a[aria-current="page"]{background:#fff;color:var(--primary)}
@media (min-width:760px){.nav-toggle{display:none}}
@media (max-width:759px){.site-nav[data-open="false"]{display:none}}
.wrap{max-width:var(--maxw);margin:0 auto;padding:1.4rem 1rem 2.5rem}
.breadcrumbs{font-size:.85rem;color:var(--muted);margin-bottom:1rem}
.breadcrumbs ol{list-style:none;display:flex;flex-wrap:wrap;gap:.4rem;padding:0;margin:0}
.breadcrumbs li+li::before{content:"/";margin-right:.4rem;color:var(--line)}
.site-footer{max-width:var(--maxw);margin:0 auto;padding:1.2rem 1rem 2rem;color:var(--muted);font-size:.82rem;text-align:center}
.grid{display:grid;gap:.9rem}
.grid-2{grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.grid-3{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fill,minmax(190px,1fr))}
.section{margin-top:1.8rem}
.stack>*+*{margin-top:.9rem}"""

COMPONENTS = """.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem 1.1rem;box-shadow:var(--shadow-sm);display:block;color:inherit}
a.card{transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}
a.card:hover{transform:translateY(-2px);border-color:var(--primary-strong);box-shadow:var(--shadow);text-decoration:none}
.card .code{font-size:.74rem;font-weight:700;color:var(--primary);letter-spacing:.03em}
.card .title{font-weight:600;margin:.15rem 0 .35rem;color:var(--ink)}
.card .sub{font-size:.82rem;color:var(--muted)}
.card .row{display:flex;justify-content:space-between;gap:.75rem;align-items:flex-start}
.badge{font-size:.72rem;background:var(--surface-2);border:1px solid var(--line);color:var(--ink-soft);border-radius:var(--radius-pill);padding:.15rem .6rem;white-space:nowrap}
.chip{display:inline-flex;align-items:center;gap:.35rem;font-size:.78rem;border-radius:var(--radius-pill);padding:.2rem .65rem;background:#f1f5f9;color:#64748b;border:1px solid var(--line)}
.chip.soon{opacity:.75}
.btn{display:inline-flex;align-items:center;gap:.4rem;background:var(--primary);color:#fff;border:0;border-radius:var(--radius-sm);padding:.6rem 1rem;font:inherit;font-weight:600;cursor:pointer}
.btn:hover{background:var(--primary-strong);text-decoration:none}
.btn.secondary{background:var(--surface);color:var(--primary);border:1px solid var(--line)}
.empty{border:1px dashed var(--line);border-radius:var(--radius);padding:1.3rem;text-align:center;color:var(--muted);background:var(--surface-2)}
.notice{background:var(--primary-soft);border:1px solid #99f6e4;border-radius:var(--radius);padding:.9rem 1rem;font-size:.88rem;color:#115e59}
.hero{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1.5rem;box-shadow:var(--shadow-sm)}
.hero h1{margin-bottom:.4rem}
.hero p{color:var(--ink-soft);max-width:60ch;margin:0}
.units{list-style:none;padding:0;margin:0}
.units li{display:flex;gap:.7rem;padding:.6rem .2rem;border-bottom:1px solid var(--line);font-size:.94rem}
.units li:last-child{border-bottom:0}
.units .u-no{flex:0 0 3.4rem;font-weight:700;color:var(--primary);font-size:.82rem}
.search-box{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem}
.search-box input{flex:1;min-width:220px;padding:.7rem .9rem;border:1px solid var(--line);border-radius:var(--radius-sm);font:inherit}
.meta{font-size:.82rem;color:var(--muted)}
.pill-row{display:flex;flex-wrap:wrap;gap:.4rem}
.options{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius-sm);padding:.7rem .9rem;font-size:.9rem}
.landing-hero{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:2.4rem 1.5rem;box-shadow:var(--shadow-sm);text-align:center}
.landing-hero .eyebrow{font-size:.76rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--primary);margin:0 0 .6rem}
.landing-hero h1{font-size:2rem;max-width:26ch;margin:0 auto .7rem}
.landing-hero .lead{color:var(--ink-soft);max-width:62ch;margin:0 auto 1.3rem}
.hero-cta{display:flex;gap:.6rem;justify-content:center;flex-wrap:wrap}
.stat-band{display:grid;grid-template-columns:repeat(2,1fr);gap:.8rem;margin-top:1.1rem}
@media(min-width:640px){.stat-band{grid-template-columns:repeat(4,1fr)}}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:1rem;text-align:center}
.stat b{display:block;font-size:1.7rem;color:var(--primary)}
.stat span{font-size:.8rem;color:var(--muted)}
.sem-strip{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.7rem}
.sem-chip{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-sm);padding:.75rem .9rem;display:block;color:inherit}
.sem-chip:hover{border-color:var(--primary-strong);text-decoration:none}
.sem-chip b{display:block;color:var(--primary);font-size:.95rem}
.sem-chip span{font-size:.76rem;color:var(--muted)}
.feature h3{margin:.55rem 0 .3rem}
.feature p{margin:0;color:var(--ink-soft);font-size:.9rem}
.f-ico{width:30px;height:30px;border-radius:8px;background:var(--primary-soft);color:var(--primary);display:flex;align-items:center;justify-content:center;font-weight:700}
.steps{margin:0;padding-left:1.2rem;color:var(--ink-soft)}
.steps li{margin-bottom:.4rem}
.cta-band{background:linear-gradient(120deg,var(--header-from),var(--header-to));color:#fff;border-radius:var(--radius);padding:1.4rem 1.5rem;display:flex;gap:1rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.cta-band h2{color:#fff;margin:0 0 .2rem}
.cta-band p{margin:0;color:#a7f3d0}
.footer-nav a{margin:0 .4rem;color:var(--primary)}
/* material, filed under the unit it belongs to */
.unit{justify-content:space-between;flex-wrap:wrap}
.unit .u-title{flex:1 1 15rem}
.unit-links{display:flex;gap:.5rem;flex-wrap:wrap;justify-content:flex-end;align-items:center}
.res-inline{list-style:none;padding:0;margin:0;display:flex;gap:.5rem;flex-wrap:wrap;justify-content:flex-end}
.res-item{display:inline-flex;align-items:center;gap:.45rem;background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:.2rem .25rem .2rem .7rem;font-size:.84rem}
.res-kind{color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.03em}
.res-title{font-weight:500}
.open-btn{display:inline-flex;align-items:center;background:var(--primary);color:#fff;font-weight:600;font-size:.8rem;padding:.25rem .7rem;border-radius:999px}
.open-btn:hover{text-decoration:none;filter:brightness(1.1)}
.none{color:var(--muted);font-size:.84rem}
.subject-material{list-style:none;padding:0;margin:0;display:flex;gap:.5rem;flex-wrap:wrap}
.empty-mini{font-size:.86rem;color:var(--muted);margin:0 0 .6rem}
.sem-note{margin-bottom:1.2rem}
"""


# ---------------------------------------------------------------- JS
JS_CATALOGUE = """/* catalogue.js — loads and caches the public catalogue */
window.Catalogue = (function(){
  var cache=null, inflight=null;
  function root(){ return document.body.getAttribute('data-root') || ''; }
  function load(){
    if(cache) return Promise.resolve(cache);
    if(inflight) return inflight;
    inflight = fetch(root()+'data/catalogue.json',{cache:'no-cache'})
      .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
      .then(function(j){ cache=j; return j; });
    return inflight;
  }
  return { load: load, root: root };
})();"""

JS_NAVIGATION = """/* navigation.js — mobile menu, active link, back buttons */
window.Nav = (function(){
  function init(){
    var toggle=document.querySelector('.nav-toggle'), nav=document.getElementById('site-nav');
    if(toggle&&nav){ toggle.addEventListener('click',function(){
      var open=nav.getAttribute('data-open')==='true';
      nav.setAttribute('data-open', open?'false':'true');
      toggle.setAttribute('aria-expanded', open?'false':'true');
    }); }
    document.querySelectorAll('[data-back]').forEach(function(b){
      b.addEventListener('click',function(e){ e.preventDefault(); if(history.length>1){history.back();} else {location.href=window.Catalogue.root()+'index.html';} });
    });
    var here=location.pathname.replace(/index\\.html$/,'');
    document.querySelectorAll('.site-nav a').forEach(function(a){
      var href=a.getAttribute('href')||'';
      var norm=href.replace(/index\\.html$/,'').replace(/^\\.\\.\\//g,'');
      if(norm && here.endsWith(norm)){ a.setAttribute('aria-current','page'); }
    });
  }
  return { init: init };
})();"""

JS_SEARCH = """/* search.js — client-side search over published catalogue metadata */
window.Search = (function(){
  function esc(s){ return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];}); }
  function subjectUrl(sem, sub){
    return window.Catalogue.root()+'semester-'+sem.number+'/'+sub.slug+'/';
  }
  function render(items, q){
    var box=document.getElementById('results'); var count=document.getElementById('result-count');
    count.textContent = items.length + (items.length===1?' result':' results');
    if(!items.length){
      box.innerHTML='<div class="empty"><p>No matches for <b>'+esc(q)+'</b>.</p><p class="meta">Try a subject name, a course code like <b>BP102T</b>, or a topic such as <b>pharmacology</b>.</p></div>';
      return;
    }
    box.innerHTML=items.map(function(it){
      var s=it.subject, sem=it.semester;
      return '<a class="card" href="'+subjectUrl(sem,s)+'">'+
        '<div class="code">'+esc(s.code)+' &middot; '+esc(sem.label)+'</div>'+
        '<div class="title">'+esc(s.title)+'</div>'+
        '<div class="sub">'+esc(it.typeLabel)+(s.units&&s.units.length?(' &middot; '+s.units.length+' units'):'')+'</div></a>';
    }).join('');
  }
  function init(){
    var input=document.getElementById('q'); if(!input) return;
    window.Catalogue.load().then(function(cat){
      var idx=[];
      cat.semesters.forEach(function(sem){
        sem.subjects.forEach(function(s){
          idx.push({semester:sem, subject:s, typeLabel:(s.type.charAt(0).toUpperCase()+s.type.slice(1)),
            hay:[s.code,s.title,sem.label,(s.options||[]).join(' '),(s.units||[]).join(' ')].join(' ').toLowerCase()});
        });
      });
      var grid=document.getElementById('semesters');
      function run(){
        var raw=(input.value||'').trim();
        if(grid){ grid.style.display = raw ? 'none' : ''; }
        var rc=document.getElementById('result-count');
        if(!raw){ document.getElementById('results').innerHTML=''; if(rc) rc.textContent=''; return; }
        render(idx.filter(function(it){return it.hay.indexOf(raw.toLowerCase())>=0;}), raw);
      }
      input.addEventListener('input', run); run();
    }).catch(function(e){
      document.getElementById('results').innerHTML='<div class="empty">Could not load the catalogue. '+esc(e.message)+'</div>';
    });
  }
  return { init: init };
})();"""

JS_APP = """/* app.js — page bootstrap */
document.addEventListener('DOMContentLoaded', function(){
  var y=document.getElementById('year'); if(y){ y.textContent=new Date().getFullYear(); }
  if(window.Nav) window.Nav.init();
  if(document.getElementById('q') && window.Search) window.Search.init();
});"""

JS_MATERIAL = """/* material.js — live material for a subject page.
   Fetches published resources from the staff library and files each one under its unit, so
   students see updates without a rebuild. No-ops when no API base is configured. */
(function () {
  var box = document.querySelector('[data-material]');
  if (!box) return;
  var api = (box.getAttribute('data-api') || '').replace(/\\/+$/, '');
  var code = box.getAttribute('data-code');
  if (!api || !code) return;
  var note = document.getElementById('live-note');
  var LABEL = { notes: 'Notes', paper: 'Question paper', manual: 'Lab manual',
                book: 'Reference book', other: 'Material' };

  function safeUrl(u) {
    return (typeof u === 'string' && /^(https?:\\/\\/|\\/)/.test(u)) ? u : '';
  }
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = (s == null ? '' : String(s));
    return d.innerHTML;
  }
  function item(r) {
    var url = safeUrl(r.url);
    var btn = url
      ? '<a class="open-btn" href="' + esc(url) + '" target="_blank" rel="noopener">Open</a>'
      : '<span class="none">link missing</span>';
    return '<li class="res-item"><span class="res-kind">' + (LABEL[r.type] || 'Material') +
           '</span><span class="res-title">' + esc(r.title) + '</span>' + btn + '</li>';
  }

  fetch(api + '/api/public/library', { headers: { 'Accept': 'application/json' } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data || !data.subjects) return;
      var items = data.subjects[code] || [];
      var byUnit = {}, general = [];
      items.forEach(function (it) {
        if (it.unitSeq) { (byUnit[it.unitSeq] = byUnit[it.unitSeq] || []).push(it); }
        else { general.push(it); }
      });
      box.querySelectorAll('[data-unit]').forEach(function (li) {
        var list = byUnit[li.getAttribute('data-unit')] || [];
        var body = li.querySelector('[data-unit-body]');
        if (body && list.length) {
          body.innerHTML = '<ul class="res-inline">' + list.map(item).join('') + '</ul>';
        }
      });
      var sb = box.querySelector('[data-subject-body]');
      if (sb && general.length) {
        sb.innerHTML = '<ul class="subject-material">' + general.map(item).join('') + '</ul>';
      }
      if (note) {
        var n = items.length;
        note.textContent = n
          ? 'Live — ' + n + ' item' + (n === 1 ? '' : 's') + ' from the staff library, updated as departments publish.'
          : 'No material has been published for this subject yet.';
      }
    })
    .catch(function () { /* not configured or offline: keep the static fallback */ });
})();"""

LOGO = """<svg class="brand-mark" viewBox="0 0 100 100" role="img" aria-label="TechStudyHubCore Pharmacy logo" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="tshcGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00f3ff"/>
      <stop offset="50%" stop-color="#22d3ee"/>
      <stop offset="100%" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
  <polygon points="50,5 88,27 88,73 50,95 12,73 12,27" fill="none" stroke="url(#tshcGrad)" stroke-width="4" stroke-linejoin="round"/>
  <g stroke="url(#tshcGrad)" stroke-width="3" fill="none" stroke-linejoin="round">
    <polygon points="50,28 68,38 50,48 32,38"/>
    <polygon points="32,38 50,48 50,68 32,58"/>
    <polygon points="68,38 50,48 50,68 68,58"/>
  </g>
</svg>"""

SCHEMA = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TechStudyHubCore Pharmacy catalogue",
  "type": "object",
  "required": ["schemaVersion", "curriculum", "semesters"],
  "properties": {
    "schemaVersion": {"type": "integer", "const": 1},
    "curriculum": {
      "type": "object",
      "required": ["programme", "authority", "sourceUrl", "checkedAt", "status"],
      "properties": {
        "programme": {"type": "string"},
        "institution": {"type": "string"},
        "awardingUniversity": {"type": "string"},
        "documentTitle": {"type": "string"},
        "documentVersion": {"type": ["string", "null"]},
        "authority": {"type": "string"},
        "sourceUrl": {"type": ["string", "null"]},
        "checkedAt": {"type": ["string", "null"]},
        "status": {"enum": ["draft", "needs-review", "verified", "published", "archived", "provisional"]},
        "note": {"type": "string"}
      }
    },
    "semesters": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "number", "label", "subjects"],
        "properties": {
          "id": {"type": "string"}, "number": {"type": "integer"},
          "label": {"type": "string"}, "credits": {"type": "integer"},
          "subjects": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "code", "slug", "title", "type"],
              "properties": {
                "id": {"type": "string"}, "code": {"type": "string"}, "slug": {"type": "string"},
                "title": {"type": "string"},
                "credits": {"type": "integer"},
                "type": {"enum": ["theory", "practical", "aec", "sec", "vac", "internship", "project"]},
                "options": {"type": "array", "items": {"type": "string"}},
                "units": {"type": "array", "items": {"type": "string"}},
                "resources": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": ["title", "type", "url"],
                    "properties": {
                      "id": {"type": "string"}, "title": {"type": "string"},
                      "type": {"enum": ["notes", "paper", "manual", "book", "other"]},
                      "language": {"type": "string"}, "source": {"type": "string"},
                      "url": {"type": "string"}, "rights": {"type": "string"},
                      "status": {"enum": ["draft", "needs-review", "verified", "published", "archived"]},
                      "reviewer": {"type": "string"}, "lastChecked": {"type": "string"},
                      "unitSeq": {"type": ["integer", "null"]}, "unit": {"type": "string"}
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}


# ---------------------------------------------------------------- HTML
def shell(title, desc, root, body, active="", extra_scripts="", data_root=None):
    dr = data_root if data_root is not None else root
    nav = [("index.html", "Home", "home"), ("semesters/index.html", "Browse", "browse"),
           ("about/index.html", "About", "about"), ("contact/index.html", "Contact", "contact")]
    links = "".join(
        '<li><a href="%s%s"%s>%s</a></li>' % (root, h, ' aria-current="page"' if k == active else '', n)
        for h, n, k in nav)
    # Staff access: straight to the portal when configured, otherwise an explainer page.
    staff_href = SIGN_IN_URL if SIGN_IN_URL else root + "staff/index.html"
    links += '<li><a class="nav-staff" href="%s"%s>Staff</a></li>' % (
        staff_href, ' aria-current="page"' if active == "staff" else '')
    footer_links = " · ".join('<a href="%s%s">%s</a>' % (root, h, n) for h, n, k in nav)
    footer_links += ' · <a href="%s">Staff</a>' % staff_href
    footer_links += (' · <a href="%sprivacy/index.html">Privacy</a>'
                     ' · <a href="%sterms/index.html">Terms</a>') % (root, root)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="{root}assets/logo/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{root}assets/css/tokens.css">
<link rel="stylesheet" href="{root}assets/css/base.css">
<link rel="stylesheet" href="{root}assets/css/layout.css">
<link rel="stylesheet" href="{root}assets/css/components.css">
</head>
<body data-root="{dr}">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{root}index.html">{LOGO}<span><b>TechStudyHubCore</b><span>Pharmacy &middot; B.Pharm (PCI 2026)</span></span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span><span class="visually-hidden">Menu</span></button>
  </div>
  <nav class="site-nav" id="site-nav" data-open="false" aria-label="Primary">
    <ul>{links}</ul>
  </nav>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site-footer">
  <p class="footer-nav">{footer_links}</p>
  <p>TechStudyHubCore Pharmacy &middot; an independent study platform for pharmacy students. Not affiliated with the Pharmacy Council of India or any institution.</p>
  <p>Course structure from the PCI B.Pharm syllabus 2026 (NEP 2020), used as an interim source pending your institution's official syllabus. &copy; <span id="year"></span></p>
</footer>
<script src="{root}assets/js/catalogue.js"></script>
<script src="{root}assets/js/navigation.js"></script>
<script src="{root}assets/js/search.js"></script>
<script src="{root}assets/js/app.js"></script>
{extra_scripts}
</body>
</html>
"""


def breadcrumbs(root, trail):
    """trail: list of (label, href-or-None)"""
    li = []
    for label, href in trail:
        if href:
            li.append(f'<li><a href="{root}{href}">{esc(label)}</a></li>')
        else:
            li.append(f'<li aria-current="page">{esc(label)}</li>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + "".join(li) + "</ol></nav>"


def subject_card(root, sem, s):
    n = len(s.get("units") or [])
    sub = TYPE_LABEL[s["type"]] + (f" &middot; {n} units" if n else "")
    return (f'<a class="card" href="{root}semester-{sem["number"]}/{s["slug"]}/">'
            f'<div class="row"><div><div class="code">{esc(s["code"])}</div>'
            f'<div class="title">{esc(s["title"])}</div></div>'
            f'<span class="badge">{s["credits"]} cr</span></div>'
            f'<div class="sub">{sub}</div></a>')


def build_home():
    sem_strip = "".join(
        f'<a class="sem-chip" href="semester-{sm["number"]}/"><b>{esc(sm["label"])}</b>'
        f'<span>{len(sm["subjects"])} subjects &middot; {sm["credits"]} cr</span></a>'
        for sm in CAT["semesters"])
    n_subj = sum(len(sm["subjects"]) for sm in CAT["semesters"])
    n_units = sum(len(s.get("units") or []) for sm in CAT["semesters"] for s in sm["subjects"])
    n_cred = sum(sm["credits"] for sm in CAT["semesters"])
    body = f"""
<section class="landing-hero">
  <p class="eyebrow">TechStudyHubCore &middot; B.Pharm study library</p>
  <h1>Every subject, its official units, and the notes — in one place.</h1>
  <p class="lead">TechStudyHubCore Pharmacy organises B.Pharm study material the way the syllabus does: by semester,
  by subject, by unit. No hunting through chat groups or scattered drives — pick your semester and go.</p>
  <div class="hero-cta">
    <a class="btn" href="semesters/index.html">Browse the library</a>
    <a class="btn secondary" href="about/index.html">How it works</a>
  </div>
</section>

<section class="stat-band">
  <div class="stat"><b>8</b><span>Semesters</span></div>
  <div class="stat"><b>{n_subj}</b><span>Subjects</span></div>
  <div class="stat"><b>{n_units}</b><span>Units mapped</span></div>
  <div class="stat"><b>{n_cred}</b><span>Credits covered</span></div>
</section>

<section class="section">
  <h2>Jump to your semester</h2>
  <div class="sem-strip">{sem_strip}</div>
</section>

<section class="section">
  <h2>What you'll find</h2>
  <div class="grid grid-3">
    <div class="card feature"><div class="f-ico">1</div><h3>Semester-wise structure</h3>
      <p>All eight semesters laid out as the PCI B.Pharm syllabus prescribes — codes, titles and credits included.</p></div>
    <div class="card feature"><div class="f-ico">2</div><h3>Official units</h3>
      <p>Each theory subject lists its official unit headings, so you can see the whole course before you start.</p></div>
    <div class="card feature"><div class="f-ico">3</div><h3>Notes &amp; PDFs</h3>
      <p>Material is added subject by subject and reviewed before it appears. Where none exists yet, the page says so.</p></div>
  </div>
</section>

<section class="section">
  <h2>How it works</h2>
  <ol class="steps">
    <li><b>Pick your semester</b> from the browse page.</li>
    <li><b>Open a subject</b> — theory, practical, or an elective.</li>
    <li><b>Read the units</b> and open any notes or PDFs attached to them.</li>
  </ol>
</section>

<section class="section">
  <div class="notice">
    <b>About the curriculum.</b> The course structure follows the <b>PCI B.Pharm syllabus 2026 (NEP 2020)</b>,
    used as an <b>interim source</b> until your institution's official syllabus for your cohort is supplied and verified.
    The first NEP 2020 batch was admitted in 2026, so only the earliest semesters have a cohort in session — later
    semesters are shown for reference, and no previous question papers exist yet.
  </div>
</section>

<section class="section">
  <div class="cta-band">
    <div><h2>Missing something?</h2>
      <p>If a subject has no notes yet, or you spot a wrong unit title, let us know.</p></div>
    <a class="btn" href="contact/index.html">Contact &amp; corrections</a>
  </div>
</section>"""
    write("index.html", shell("TechStudyHubCore Pharmacy — B.Pharm study library",
          "A semester-wise B.Pharm study library for pharmacy students, mapped to the PCI 2026 syllabus.", "", body, active="home"))


def build_semesters():
    rows = "".join(
        f'<a class="card" href="../semester-{sm["number"]}/"><div class="row"><div>'
        f'<div class="code">{esc(sm["label"])}</div>'
        f'<div class="title">{len(sm["subjects"])} subjects</div></div>'
        f'<span class="badge">{sm["credits"]} cr</span></div>'
        f'<div class="sub">{esc(", ".join(s["title"] for s in sm["subjects"][:3]))}…</div></a>'
        for sm in CAT["semesters"])
    body = f"""{breadcrumbs('../', [("Home","index.html"),("Browse",None)])}
<h1>Browse the library</h1>
<p class="meta">Search by subject, course code or topic — or pick a semester below.</p>
<div class="search-box">
  <label class="visually-hidden" for="q">Search the library</label>
  <input id="q" type="search" placeholder="Search a subject, course code or topic…" autocomplete="off">
</div>
<p class="meta" id="result-count" role="status" aria-live="polite"></p>
<div id="results" class="grid grid-2"></div>
<div id="semesters">
  <h2>All semesters</h2>
  <div class="grid grid-2">{rows}</div>
</div>"""
    write("semesters/index.html", shell("Browse — TechStudyHubCore Pharmacy",
          "Browse and search all eight B.Pharm semesters in the TechStudyHubCore Pharmacy.", "../", body, active="browse"))


def build_semester(sm):
    root = "../"
    groups = []
    for t, label in GROUP_ORDER:
        items = [s for s in sm["subjects"] if s["type"] == t]
        if not items:
            continue
        cards = "".join(subject_card(root, sm, s) for s in items)
        groups.append(f'<section class="section"><h2>{label}</h2><div class="grid grid-2">{cards}</div></section>')
    note = ""
    if sm["number"] > 1:
        note = ('<div class="notice sem-note">No batch is studying this semester yet — the first NEP 2020 cohort was '
                'admitted in 2026 and has just begun. The structure is shown for reference.</div>')
    body = f"""{breadcrumbs(root, [("Home","index.html"),("Browse","semesters/index.html"),(sm["label"],None)])}
<h1>{esc(sm["label"])}</h1>
<p class="meta">{len(sm["subjects"])} subjects &middot; {sm["credits"]} credits</p>
{note}
{''.join(groups)}"""
    write(f'semester-{sm["number"]}/index.html',
          shell(f'{sm["label"]} — TechStudyHubCore Pharmacy',
                f'{sm["label"]} subjects in the TechStudyHubCore Pharmacy (PCI 2026 B.Pharm).', root, body))


def build_subject(sm, s):
    root = "../../"
    trail = [("Home", "index.html"), ("Browse", "semesters/index.html"),
             (sm["label"], f'semester-{sm["number"]}/'), (s["code"], None)]
    # material, filed under the unit it belongs to
    res = s.get("resources") or []
    by_unit, general = {}, []
    for r in res:
        seq = r.get("unitSeq")
        (by_unit.setdefault(seq, []) if seq else general).append(r)

    def link(r):
        url = r.get("url") or ""
        kind = KIND_LABEL.get(r.get("type") or "notes", "Material")
        btn = (f'<a class="open-btn" href="{esc(url)}" target="_blank" rel="noopener">Open</a>'
               if url else '<span class="none">link missing</span>')
        return (f'<li class="res-item"><span class="res-kind">{esc(kind)}</span>'
                f'<span class="res-title">{esc(r.get("title") or "")}</span>{btn}</li>')

    # options
    opt = ""
    if s.get("options"):
        opt = '<div class="options"><b>Choose one:</b> ' + esc(" · ".join(s["options"])) + "</div>"

    # units — each row carries its own Open buttons
    if s.get("units"):
        rows = []
        for i, u in enumerate(s["units"]):
            seq = i + 1
            items = by_unit.get(seq, [])
            inner = (f'<ul class="res-inline">{"".join(link(r) for r in items)}</ul>'
                     if items else '<span class="none">No material yet</span>')
            rows.append(
                f'<li class="unit" data-unit="{seq}">'
                f'<span class="u-no">Unit {["I","II","III","IV","V"][i] if i < 5 else seq}</span>'
                f'<span class="u-title">{esc(u)}</span>'
                f'<span class="unit-links" data-unit-body>{inner}</span></li>')
        units_block = ('<section class="section"><h2>Units</h2>'
                       f'<ol class="units">{"".join(rows)}</ol></section>')
    else:
        units_block = ('<section class="section"><h2>Units</h2>'
                       '<div class="empty"><p>Unit breakdown is not yet available for this subject.</p>'
                       '<p class="meta">It will be added from the official syllabus.</p></div></section>')

    # material that is not tied to a single unit
    gen_inner = (f'<ul class="subject-material">{"".join(link(r) for r in general)}</ul>'
                 if general else
                 '<div class="empty"><p>No material has been published for this subject yet.</p>'
                 '<p class="meta">It appears here, unit by unit, as departments publish it.</p></div>')
    subject_block = ('<section class="section"><h2>Whole-subject material</h2>'
                     f'<div data-subject-body>{gen_inner}</div></section>')

    material = (f'<div data-material data-code="{esc(s["code"])}" data-api="{esc(API_BASE)}">'
                '<p class="meta" id="live-note">Material is added unit by unit and reviewed before it '
                'appears. Open a unit to read its notes and papers.</p>'
                f'{units_block}{subject_block}</div>')
    body = f"""{breadcrumbs(root, trail)}
<div class="row" style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap">
  <div>
    <div class="code" style="color:var(--primary);font-weight:700;font-size:.8rem">{esc(s["code"])} &middot; {esc(sm["label"])}</div>
    <h1 style="margin-top:.2rem">{esc(s["title"])}</h1>
    <p class="meta">{TYPE_LABEL[s["type"]]} &middot; {s["credits"]} credits</p>
  </div>
  <button class="btn secondary" data-back>← Back</button>
</div>
{opt}
{material}
<section class="section">
  <p class="meta">Structure sourced from the PCI B.Pharm syllabus 2026 (NEP 2020) — interim source.
  Corrections welcome via the <a href="{root}contact/index.html">contact page</a>.</p>
</section>"""
    scripts = '<script src="../../assets/js/material.js"></script>' if API_BASE else ""
    write(f'semester-{sm["number"]}/{s["slug"]}/index.html',
          shell(f'{s["code"]} {s["title"]} — TechStudyHubCore Pharmacy',
                f'{s["title"]} ({s["code"]}), {sm["label"]} — units and study material.',
                root, body, extra_scripts=scripts))


def build_about():
    c = CAT["curriculum"]
    body = f"""{breadcrumbs('../', [("Home","index.html"),("About",None)])}
<h1>About this library</h1>
<div class="stack">
<p><b>TechStudyHubCore Pharmacy</b> is a free study platform for <b>B.Pharm</b> students. Its job is simple:
give a predictable path from a semester to a subject to a unit, so material is easy to find instead of scattered.</p>
<h2>Curriculum source</h2>
<p>The structure in this build comes from <b>{esc(c["documentTitle"])}</b> issued by the
<b>{esc(c["authority"])}</b>. It is used as an <b>interim source</b> (status: {esc(c["status"])}) until your institution's
official syllabus for the applicable cohort is supplied and verified.</p>
<ul class="meta">
  <li>Authority: {esc(c["authority"])}</li>
  <li>Document: {esc(c["documentTitle"])} ({esc(c.get("documentVersion") or "n/a")})</li>
  <li>Source: <a href="{esc(c.get("sourceUrl") or "#")}" rel="noopener" target="_blank">{esc(c.get("sourceUrl") or "—")}</a></li>
  <li>Checked: {esc(c.get("checkedAt") or "—")}</li>
</ul>
<h2>How content is handled</h2>
<ul>
  <li>Only the official course structure is shown as curriculum; nothing is invented.</li>
  <li>Study material is added subject by subject and reviewed before it appears.</li>
  <li>We do not mirror copyrighted textbooks — material is linked from its lawful source.</li>
  <li>This is a static site: there is no login and no shared upload database.</li>
</ul>
<p class="meta">An independent study platform. Not affiliated with the Pharmacy Council of India or any institution.</p>
</div>"""
    write("about/index.html", shell("About — TechStudyHubCore Pharmacy",
          "About the TechStudyHubCore Pharmacy, its curriculum source and content policy.", "../", body, active="about"))


def build_contact():
    body = f"""{breadcrumbs('../', [("Home","index.html"),("Contact",None)])}
<h1>Contact &amp; corrections</h1>
<div class="stack">
<p>Found a broken link, a wrong unit title, or a subject that should be listed? Tell us — corrections are welcome.</p>
<h2>Report a correction</h2>
<ul>
  <li>Open an issue in the project's GitHub repository (preferred for non-sensitive items).</li>
  <li>For anything sensitive, use a private channel to the maintainer rather than a public issue.</li>
</ul>
<h2>Contribute material</h2>
<p>Have notes, a previous question paper, or a lab manual for a subject? Send it through either channel above and
it will be reviewed before it appears.</p>
<p><b>We can publish:</b> your own notes, openly licensed material, and links to lawful sources.</p>
<p><b>We can't publish:</b> copyrighted textbooks, paid coaching material, restricted institutional files, or personal data.</p>
<div class="notice">
  This is a static site — there is no shared upload database and no login, so a form here could not store submissions.
  Please use the issue tracker or email, which reach a maintainer.
</div>
<p class="meta">See <a href="https://github.com/kartik-h6/e-library/blob/main/CONTRIBUTING.md">CONTRIBUTING</a> in the repository for the full guide.</p>
<p class="meta">Do not post credentials or personal data in public issues.</p>
</div>"""
    write("contact/index.html", shell("Contact — TechStudyHubCore Pharmacy",
          "Contact and corrections for the TechStudyHubCore Pharmacy.", "../", body, active="contact"))


def build_404():
    body = """
<section class="hero">
  <h1>Page not found</h1>
  <p>That page doesn't exist — it may have moved, or the link may be mistyped.</p>
  <p style="margin-top:.9rem"><a class="btn" href="index.html">Go to the home page</a>
  <a class="btn secondary" href="semesters/index.html">Browse the library</a></p>
</section>"""
    write("404.html", shell("Page not found — TechStudyHubCore Pharmacy",
          "The page could not be found.", "", body, data_root=""))


def build_assets():
    write("assets/css/tokens.css", TOKENS)
    write("assets/css/base.css", BASE)
    write("assets/css/layout.css", LAYOUT)
    write("assets/css/components.css", COMPONENTS)
    write("assets/js/catalogue.js", JS_CATALOGUE)
    write("assets/js/navigation.js", JS_NAVIGATION)
    write("assets/js/search.js", JS_SEARCH)
    write("assets/js/app.js", JS_APP)
    write("assets/js/material.js", JS_MATERIAL)
    write("assets/logo/logo.svg", LOGO)
    write("assets/logo/favicon.svg", LOGO)
    write("data/schema.json", json.dumps(SCHEMA, indent=2))
    write("resources/README.md",
          "# resources/\n\nPlace only rights-cleared files here (your own notes, openly licensed material).\n"
          "Prefer linking to a lawful external source over storing a copy. Never commit personal or\n"
          "confidential institutional data, or copyrighted material you do not have permission to share.\n")




def build_staff():
    if SIGN_IN_URL:
        cta = f'<a class="btn" href="{SIGN_IN_URL}">Staff sign in</a>'
    else:
        cta = ('<div class="notice">The staff portal link has not been set yet. The maintainer '
               'adds it (the <span class="mono">SIGN_IN_URL</span> setting) once the staff service '
               'is hosted.</div>')
    body = f"""{breadcrumbs('../', [("Home","index.html"),("Staff",None)])}
<h1>Access</h1>
<p class="lead">Two audiences, two clear paths.</p>
<section class="section">
  <h2>Students</h2>
  <p>No account, no sign-in. The library is open —
     <a href="../semesters/index.html">browse by semester</a>.</p>
</section>
<section class="section">
  <h2>Staff</h2>
  <p>Department staff sign in to add and manage their subjects' material.</p>
  {cta}
</section>"""
    write("staff/index.html", shell("Staff access — TechStudyHubCore Pharmacy",
          "How students and staff access the TechStudyHubCore Pharmacy.", "../", body, active="staff"))


def build_privacy():
    body = f"""{breadcrumbs('../', [("Home","index.html"),("Privacy",None)])}
<h1>Privacy</h1>
<p class="lead">Short version: students are anonymous, and there is nothing to collect.</p>
<section class="section">
  <h2>What we collect</h2>
  <p>Nothing about students. There are no student accounts, no sign-in, no tracking cookies and no
  analytics on this site. Reading the library leaves no trace beyond ordinary web-server logs.</p>
</section>
<section class="section">
  <h2>What is held</h2>
  <ul>
    <li><b>Staff accounts</b> — name, email and a hashed password, so staff can sign in.
      Passwords are hashed (PBKDF2) and never stored in plain text.</li>
    <li><b>Content and its history</b> — the material, plus an audit trail of who changed what.</li>
    <li><b>Standard server logs</b> — IP, path and time, kept by the host for security only.</li>
  </ul>
</section>
<section class="section">
  <h2>What we do not do</h2>
  <ul>
    <li>No analytics, ads or trackers.</li>
    <li>No third-party CDN, fonts or scripts — everything is served from this site.</li>
    <li>No names, phone numbers, marks, attendance or any student record.</li>
    <li>Nothing is sold or shared with anyone.</li>
  </ul>
</section>
<section class="section">
  <h2>Material</h2>
  <p>Study material is kept in a shared Google Drive folder; Google's own terms and privacy policy
  apply to that folder. This site stores only links to it.</p>
</section>
<section class="section">
  <h2>Questions</h2>
  <p>To ask about or correct anything held, use the <a href="../contact/index.html">contact page</a>.</p>
</section>"""
    write("privacy/index.html", shell("Privacy — TechStudyHubCore Pharmacy",
          "Privacy: students are anonymous; nothing is collected about them.", "../", body))


def build_terms():
    body = f"""{breadcrumbs('../', [("Home","index.html"),("Terms",None)])}
<h1>Terms of use</h1>
<section class="section">
  <ul>
    <li>This is an <b>independent study platform</b>, not affiliated with or endorsed by the Pharmacy
      Council of India or any college or university.</li>
    <li>The course structure follows the <b>PCI B.Pharm syllabus 2026 (NEP 2020)</b> as an interim
      source until your institution's official syllabus is supplied and verified. Always check the official syllabus.</li>
    <li>Material is provided <b>as-is, without warranty</b>. Verify anything you rely on.</li>
    <li>Do not submit copyrighted material you have no right to share, paid coaching material,
      restricted institutional files, or personal or confidential data.</li>
    <li>The maintainer may edit, move or remove content, and may suspend access, at any time.</li>
    <li>The maintainer is not liable for any loss arising from use of this site or its material.</li>
  </ul>
</section>
<p class="meta">See also the <a href="../privacy/index.html">privacy notice</a>.</p>"""
    write("terms/index.html", shell("Terms — TechStudyHubCore Pharmacy",
          "Terms of use for the TechStudyHubCore Pharmacy.", "../", body))


def main():
    build_assets()
    build_home()
    build_semesters()
    build_about()
    build_contact()
    build_staff()
    build_privacy()
    build_terms()
    build_404()
    # remove pages that no longer exist in this information architecture
    for stale in ("search", "contribute"):
        d = os.path.join(ROOT, stale)
        if os.path.isdir(d):
            shutil.rmtree(d)
    for sm in CAT["semesters"]:
        build_semester(sm)
        for s in sm["subjects"]:
            build_subject(sm, s)
    print("generated:", len(CAT["semesters"]), "semesters,",
          sum(len(s["subjects"]) for s in CAT["semesters"]), "subject pages")


if __name__ == "__main__":
    main()
