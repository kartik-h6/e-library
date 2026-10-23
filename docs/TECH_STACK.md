# Tech stack — options and recommendation

The question this answers: **what is the best stack for the whole project, without depending on
paid services?**

The short answer: almost every layer has a free, open-source option, and the project can run at
**₹0/month with no vendor lock-in**. The one real weakness in the current plan isn't the software —
it's that *free hosting tiers sleep*. Fix the hosting and the rest holds.

---

## 1. What the project actually needs

| Need | Real requirement |
|---|---|
| Public library | fast, static, works on cheap phones, no login |
| Staff admin | a few dozen users; add/edit material; roles by department |
| Auth | email + password for staff; no student accounts |
| Storage | PDFs and notes; links are acceptable |
| Database | hundreds of rows, not millions |
| Hosting | cheap, ideally free; low traffic |
| Privacy | no tracking, no third-party scripts |

Scale is small: **under a hundred staff, a few thousand students, thousands of rows.** That matters
— it rules out heavy stacks as much as it rules out expensive ones.

## 2. Options, layer by layer

### Frontend

| Option | Licence | Free hosting | Verdict |
|---|---|---|---|
| **Static HTML/CSS/JS + generator** (current) | own code | GitHub Pages | **Best** — no build server, instant loads, works everywhere |
| Astro / Eleventy / Hugo | MIT | GitHub Pages | Good, but adds machinery for no gain here |
| Next.js / Nuxt | MIT | Vercel / Node host | Overkill; needs a running server |

### Backend, admin UI, auth and storage

| Option | Licence | Runs as | Free tier | Verdict |
|---|---|---|---|---|
| **FastAPI** (current) | MIT | Python process | self-host | **Keep** — built, tested, tailored |
| **PocketBase** | MIT | **one Go binary** | self-host | **Best alternative** — SQLite + admin dashboard + auth + file storage + realtime in a single file |
| **Supabase** | Apache-2.0 | managed / self-host | 500 MB DB, 1 GB storage, 50k MAU — **pauses after 1 week idle** | Strong, but the pause hurts a low-traffic tool |
| Appwrite | BSD-3 | Docker | self-host | Capable, more moving parts |
| Nhost / Directus / Strapi | OSS | Docker | self-host | Built for content teams; heavier than needed |
| Firebase | proprietary | managed | free tier | **Excluded** — closed source, lock-in |

PocketBase deserves the detail: it is a single executable that gives you an embedded SQLite
database with realtime subscriptions, built-in files and users management, an admin dashboard UI,
and a REST-ish API. Download, run, done. Backups are a folder copy.

### Database

| Option | Licence | Free | Verdict |
|---|---|---|---|
| **SQLite** | public domain | yes, a file | **Best** at this scale — zero ops |
| PostgreSQL (self-hosted) | PostgreSQL licence | yes | Right when concurrency or size grows |
| Neon / Supabase Postgres | OSS / managed | free tier | Good managed Postgres |
| Turso (libSQL), Cloudflare D1 | OSS / proprietary | free tier | Edge SQLite; more lock-in |

### File storage

| Option | Free | Verdict |
|---|---|---|
| **Google Drive folder** (current) | yes | **Best** — you already run it |
| PocketBase file storage | yes (your disk) | Clean if you adopt PocketBase |
| Cloudflare R2 | 10 GB, no egress fees | Good object storage, some lock-in |
| Supabase Storage | 1 GB | Fine if you adopt Supabase |

### Hosting

| Option | Cost | Always on? | Verdict |
|---|---|---|---|
| GitHub Pages (frontend) | ₹0 | yes | **Best** |
| **Oracle Cloud Always Free VM** | ₹0 | **yes** | **Best for the backend** — a real always-on machine, not a sleeping container |
| Fly.io / Render / Railway / Koyeb | ₹0 tiers | often sleeps | Fine to start; cold starts annoy staff |
| Indian VPS (e.g. 1 GB) | ~₹250–400/mo | yes | Cheap, always on, no signup hoops |
| Cloudflare Pages / Workers | ₹0 | yes | Excellent, but a proprietary runtime |

### Everything else

- **CI/CD:** GitHub Actions — free for public repositories. Already in use.
- **Analytics:** **none.** Privacy-first, and the privacy notice promises no trackers.
- **Error monitoring:** optional; a free self-hosted Sentry or GlitchTip, or just host logs.
- **Email** (password reset, if added): any free SMTP tier, or a transactional provider's free
  allowance.

## 3. Recommendation

**Do not rewrite the software. Fix the hosting.**

```
frontend/   static site            → GitHub Pages                ₹0
backend/    FastAPI + SQLite       → Oracle Cloud Always Free VM ₹0
material    Google Drive folder    → Drive                       ₹0
CI          GitHub Actions         → Actions                     ₹0
analytics   none                   → —                           ₹0
```

This keeps everything already built and tested, and removes the only genuine flaw in the current
plan — free app-hosting tiers that sleep or pause. A real always-on VM means the staff dashboard
is simply *there*, and the site's live material never waits for a cold start.

**Then, in order, if the need appears:**

1. **PocketBase** — the cleanest way to delete our custom backend. It replaces the API, the admin
   UI, auth, file storage and realtime with one binary. Adopt it when maintaining the admin code
   starts to cost more than learning PocketBase would. Caveat: it is still pre-1.0, so pin the
   version.
2. **Supabase** — if you'd rather not run a server at all. Postgres, RLS, Auth, Storage, Realtime
   and a table-editor admin out of the box. Accept the weekly pause on the free plan, or pay
   ~$25/month to remove it.
3. **PostgreSQL** — when concurrency or data size outgrows a single SQLite file.

## 4. What stays the same no matter what

This is the useful part: **the backend is the only swappable layer.**

- `frontend/` — the static site, its design and its generator.
- `frontend/data/catalogue.json` — the syllabus structure and the publish target.
- The **public API contract** — one endpoint, `GET /api/public/library`, returning published
  material grouped by subject code. Reimplementing that on PocketBase or Supabase is a small,
  bounded job; nothing else in the frontend changes.
- `security/check.py`, the workflows, the docs.

## 5. Migration path, phased

| Phase | Trigger | Work |
|---|---|---|
| 0 | now | Host FastAPI on an always-on free VM; set `API_BASE` and `SIGN_IN_URL`; back up the SQLite file on a schedule |
| 1 | staff start using it | Add password reset and rate limiting on `/login` |
| 2 | admin maintenance outweighs its value | Move to PocketBase: collections + API rules; delete our templates |
| 3 | concurrency or size grows | Move to PostgreSQL |

## 6. Cost summary

| Path | Monthly |
|---|---|
| Recommended (static + FastAPI on a free VM + Drive) | **₹0** |
| Same, on a paid Indian VPS | ~₹250–400 |
| Supabase Pro (no pausing) | ~$25 |
| PocketBase on a free VM | **₹0** |

Every option above is open source and self-hostable, so no choice here locks the project in.
