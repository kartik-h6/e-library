#!/usr/bin/env python3
"""Static site generator for the RIPER e-Library (P0).

Reads data/catalogue.json and writes the public static site:
home, about, semesters, search, contribute, contact, one page per semester,
one page per subject, a 404 page, plus shared assets and data/schema.json.

Run from the repository root:  python3 build/generate.py
"""
import json, os, re, shutil, datetime
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, "data", "catalogue.json"), encoding="utf-8"))

KINDS = [("notes", "Notes & PDFs", ""),
         ("paper", "Previous question papers",
          "None yet — the 2026 (NEP 2020) batch is the first cohort, so no papers have been set."),
         ("manual", "Lab manuals", ""), ("book", "Reference books", "")]
ISSUES_URL = "https://github.com/kartik-h6/e-library/issues/new"
# Optional: the hosted backend's sign-in URL. Empty hides the "Sign in" link in the nav.
SIGN_IN_URL = os.environ.get("SIGN_IN_URL", "")


def issue_url(s, sm, kind_label):
    title = f"[Material] {s['code']} {s['title']} — {sm['label']}"
    body = (f"Subject: {s['code']} {s['title']}\nSemester: {sm['label']}\nType: {kind_label}\n\n"
            "Link (Google Drive, etc.):\n\nSource / licence:\n\nNotes for the reviewer:\n")
    return ISSUES_URL + "?" + urlencode({"title": title, "body": body})


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
.brand .brand-mark{width:38px;height:38px;flex:0 0 auto}
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
.res-grid{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.res-col{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius-sm);padding:.9rem 1rem}
.res-col h3{font-size:.98rem;margin:0 0 .5rem;display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.res-list{list-style:none;padding:0;margin:0 0 .6rem}
.res-list li{display:flex;justify-content:space-between;gap:.6rem;padding:.35rem 0;border-bottom:1px solid var(--line);font-size:.9rem}
.empty-mini{font-size:.86rem;color:var(--muted);margin:0 0 .6rem}
.res-submit{font-size:.84rem;font-weight:600}
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

LOGO = """<svg class="brand-mark" viewBox="0 0 48 48" role="img" aria-label="RIPER e-Library logo">
<rect x="2" y="2" width="44" height="44" rx="12" fill="#0d9488"/>
<path d="M13 34V15.5c0-1.4 1.1-2.5 2.5-2.5H24v21h-8.5A2.5 2.5 0 0 1 13 31.5z" fill="#ffffff" opacity=".95"/>
<path d="M24 13h8.5c1.4 0 2.5 1.1 2.5 2.5v18.5a2.5 2.5 0 0 1-2.5 2.5H24z" fill="#99f6e4"/>
<path d="M24 13v21" stroke="#0f766e" stroke-width="1.6"/>
</svg>"""

SCHEMA = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RIPER e-Library catalogue",
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
                      "reviewer": {"type": "string"}, "lastChecked": {"type": "string"}
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
    <a class="brand" href="{root}index.html">{LOGO}<span><b>RIPER e-Library</b><span>B.Pharm &middot; PCI 2026 syllabus</span></span></a>
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
  <p>RIPER e-Library &middot; a student-built study library. Not an official publication of RIPER.</p>
  <p>Course structure from the PCI B.Pharm syllabus 2026 (NEP 2020), used as an interim source pending the college's official syllabus. &copy; <span id="year"></span></p>
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
  <p class="eyebrow">RIPER &middot; B.Pharm study library</p>
  <h1>Every subject, its official units, and the notes — in one place.</h1>
  <p class="lead">The RIPER e-Library organises B.Pharm study material the way the syllabus does: by semester,
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
    used as an <b>interim source</b> until RIPER's official syllabus for your cohort is supplied and verified.
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
    write("index.html", shell("RIPER e-Library — B.Pharm study library",
          "A semester-wise B.Pharm study library for RIPER students, mapped to the PCI 2026 syllabus.", "", body, active="home"))


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
    write("semesters/index.html", shell("Browse — RIPER e-Library",
          "Browse and search all eight B.Pharm semesters in the RIPER e-Library.", "../", body, active="browse"))


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
          shell(f'{sm["label"]} — RIPER e-Library',
                f'{sm["label"]} subjects in the RIPER e-Library (PCI 2026 B.Pharm).', root, body))


def build_subject(sm, s):
    root = "../../"
    trail = [("Home", "index.html"), ("Browse", "semesters/index.html"),
             (sm["label"], f'semester-{sm["number"]}/'), (s["code"], None)]
    # units
    if s.get("units"):
        units = '<ul class="units">' + "".join(
            f'<li><span class="u-no">Unit {["I","II","III","IV","V"][i] if i<5 else i+1}</span>'
            f'<span>{esc(u)}</span></li>' for i, u in enumerate(s["units"])) + "</ul>"
        units_block = f'<section class="section"><h2>Units</h2>{units}</section>'
    else:
        units_block = ('<section class="section"><h2>Units</h2>'
                       '<div class="empty"><p>Unit breakdown is not yet available for this subject.</p>'
                       '<p class="meta">It will be added from the official syllabus.</p></div></section>')
    # options
    opt = ""
    if s.get("options"):
        opt = '<div class="options"><b>Choose one:</b> ' + esc(" · ".join(s["options"])) + "</div>"
    # resources — the same four sections exist for every subject
    res = s.get("resources") or []
    cols = []
    for kind, label, note in KINDS:
        items = [r for r in res if (r.get("type") or "notes") == kind]
        submit = (f'<a class="res-submit" href="{esc(issue_url(s, sm, label))}" target="_blank" rel="noopener">'
                  f'Submit {label.lower()} →</a>')
        if items:
            inner = '<ul class="res-list">' + "".join(
                f'<li><span>{esc(r["title"])}</span> <a href="{esc(r["url"])}" target="_blank" rel="noopener">Open</a></li>'
                for r in items) + "</ul>"
        elif note:
            inner = f'<p class="empty-mini">{esc(note)}</p>'
            submit = ""
        else:
            inner = '<p class="empty-mini">Nothing added yet.</p>'
        cols.append(
            f'<div class="res-col"><h3>{label} <span class="badge">{len(items)}</span></h3>'
            f'{inner}{submit}</div>')
    res_block = '<div class="res-grid">' + "".join(cols) + "</div>"
    res_head = ('<p class="meta">Material is added subject by subject and reviewed before it appears. '
                'Nothing here yet? Use a submit link — it opens a prefilled issue on GitHub.</p>')
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
{units_block}
<section class="section"><h2>Study material</h2>{res_head}{res_block}</section>
<section class="section">
  <p class="meta">Structure sourced from the PCI B.Pharm syllabus 2026 (NEP 2020) — interim source.
  Corrections welcome via the <a href="{root}contact/index.html">contact page</a>.</p>
</section>"""
    write(f'semester-{sm["number"]}/{s["slug"]}/index.html',
          shell(f'{s["code"]} {s["title"]} — RIPER e-Library',
                f'{s["title"]} ({s["code"]}), {sm["label"]} — units and study material.', root, body))


def build_about():
    c = CAT["curriculum"]
    body = f"""{breadcrumbs('../', [("Home","index.html"),("About",None)])}
<h1>About this library</h1>
<div class="stack">
<p>The <b>RIPER e-Library</b> is a free, student-run study library for <b>B.Pharm</b> students. Its job is simple:
give a predictable path from a semester to a subject to a unit, so material is easy to find instead of scattered.</p>
<h2>Curriculum source</h2>
<p>The structure in this build comes from <b>{esc(c["documentTitle"])}</b> issued by the
<b>{esc(c["authority"])}</b>. It is used as an <b>interim source</b> (status: {esc(c["status"])}) until RIPER's
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
<p class="meta">This is not an official publication of RIPER.</p>
</div>"""
    write("about/index.html", shell("About — RIPER e-Library",
          "About the RIPER e-Library, its curriculum source and content policy.", "../", body, active="about"))


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
    write("contact/index.html", shell("Contact — RIPER e-Library",
          "Contact and corrections for the RIPER e-Library.", "../", body, active="contact"))


def build_404():
    body = """
<section class="hero">
  <h1>Page not found</h1>
  <p>That page doesn't exist — it may have moved, or the link may be mistyped.</p>
  <p style="margin-top:.9rem"><a class="btn" href="index.html">Go to the home page</a>
  <a class="btn secondary" href="semesters/index.html">Browse the library</a></p>
</section>"""
    write("404.html", shell("Page not found — RIPER e-Library",
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
    write("staff/index.html", shell("Staff access — RIPER e-Library",
          "How students and staff access the RIPER e-Library.", "../", body, active="staff"))


def main():
    build_assets()
    build_home()
    build_semesters()
    build_about()
    build_contact()
    build_staff()
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
