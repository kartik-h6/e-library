# Integration plan — one platform, one repository

Goal: one repository, one platform, one admin, on the TechStudyHubCore subdomain. No payments.

---

## 1. What exists today

| Thing | What it is | State |
|---|---|---|
| **This repository** | PCI 2026 (NEP 2020) catalogue — 8 semesters, 88 subjects, 240 units — plus a static site, a FastAPI staff backend, a deploy kit and docs | Working, tested |
| **Your existing subdomain app** (`index1.html`) | A single-file "B.Pharm Notes" SPA: 218 unit labels from the **older RGUHS / PCI-2014** list, an admin panel, search, progress tracking | Prototype — see §2 |
| **Documentation package** | The original docs set | Superseded by `docs/` |

## 2. The blocker in the existing app

Three things make it unusable as a shared library, regardless of how it looks:

1. **Content lives in each visitor's browser.** Everything is stored under `localStorage['bpn_data']`. When you add notes in the admin panel, they are saved in *your* browser only. A student opening the site sees nothing you added. There is no server, no database, and no sharing between users.
2. **The admin password is `'password'`, in the page source.** `const ADMIN_PASSWORD = 'password'` — anyone who views source can open the admin panel. It is client-side only, so it cannot be fixed without a server.
3. **Its syllabus is the older list.** Subject names like "Pharmaceutics - I" and "Pharmaceutical Analysis - I" come from the RGUHS / PCI-2014 structure, not the PCI 2026 (NEP 2020) one this repository is built on.

**No payment code exists** in either the app or the documentation package — nothing to remove. If a payment page exists somewhere else, point me at it.

## 3. Decision: keep this repository as the base, absorb the good ideas

| From the old app | Action | Why |
|---|---|---|
| Per-student progress (`visitedSubjects`, `downloadedNotes`) | **Absorb** | Genuinely useful, and correctly belongs in the browser — no server needed |
| Clean semester → subject → unit browsing | Already have | Ours is generated, indexed and searchable |
| Search | Already have | — |
| 218 unit labels (RGUHS/PCI-2014) | **Do not merge** | Conflicting syllabus; ours is newer and authoritative |
| Admin panel + `'password'` login | **Drop** | Replaced by the real backend with a database |
| localStorage content storage | **Drop** | Replaced by the database + public API |
| Tailwind / Font Awesome CDNs | **Drop** | We ship local CSS; no third-party requests |

## 4. Target architecture

One virtual machine, one repository, one deploy — everything on the TechStudyHubCore domain:

```
pharmacy.techstudyhubcore.in   →  public site (static files from this repo)
elibrary.techstudyhubcore.in   →  staff login + public API
                                  (same VM, routed by nginx)
```

Why this and not GitHub Pages plus a server: with both on one machine there is **no CORS**, and no "publish writes a file that cannot reach the other host" confusion. One deploy updates everything.

An alternative is a single subdomain with the staff app under `/admin`, but that needs a path-prefix rewrite and breaks generated links easily. Not recommended.

## 5. Single admin

- Remove the department-master and SME demo accounts from seeding.
- Keep **one** super admin, whose password is set at deploy time — never seeded, never printed.
- This also closes the currently-open login on the live portal.

## 6. Phases

| Phase | Work | Outcome |
|---|---|---|
| **0. Security** | Single admin, no seeded passwords, `Secure` cookie, stop serving `/uploads` publicly | The portal can be public safely |
| **1. Consolidate hosting** | One VM serving both subdomains; `API_BASE` becomes same-origin | One deploy, no CORS, no split publishing |
| **2. Absorb features** | Per-student progress (visited units, download count) in localStorage; keep search and per-unit Open buttons | The old app's good parts, on a real foundation |
| **3. Cutover** | Point the subdomain at the new site; retire `index1.html` | One platform, one entry point |
| **4. Docs** | One-admin runbook; remove two-host language | A maintainer can follow it |

## 7. Open questions

1. **Syllabus** — PCI 2026 only (recommended), or keep the older RGUHS list as a second option?
2. **Subdomain** — two subdomains (recommended), or one with `/admin`?
3. **Payment** — confirm there is nothing to remove; none was found.
