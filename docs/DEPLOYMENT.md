# Deployment runbook

Two things deploy, independently:

| Part | Where | How |
|---|---|---|
| `frontend/` | GitHub Pages | automatic — `.github/workflows/pages.yml` on every push to `main` |
| `backend/` | a small host | manual, below |

The frontend is **already live**. This runbook is for the backend, which is optional: without it
the site works fully static, and students simply don't get live material.

---

## 1. Prerequisites

- An Oracle Cloud account (recommended), or any host — Render, Fly.io, Railway.
- No database to buy: the recommended setup uses one SQLite file.
- The Drive folder for material (you handle that).

## 2. Deploy the backend

**Recommended: an Oracle Cloud Always Free VM — the whole kit is in
[`backend/deploy/`](../backend/deploy/README.md).** It gives an always-on machine at ₹0, one
setup script, nginx with TLS, a systemd service and nightly backups, and the database stays a
single SQLite file. It also avoids the cold starts that free app-hosting tiers impose.

The steps below are the generic managed-host alternative (Render, Fly, Railway).

1. **Create the database.** On your host, create a PostgreSQL instance and copy its connection
   URL. Rewrite the scheme for SQLAlchemy: `postgres://…` → `postgresql+psycopg://…`.
2. **Create the web service**, pointing at this repository:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Set environment variables** (never commit these):

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | the PostgreSQL URL from step 1 |
   | `SESSION_SECRET` | a long random string |
   | `COOKIE_SECURE` | `1` — send the session cookie only over HTTPS |
   | `DRIVE_FOLDER_URL` | your shared Drive folder link |
   | `PUBLIC_SITE_URL` | `https://kartik-h6.github.io/e-library/` |
   | `CORS_ORIGINS` | `https://kartik-h6.github.io` |

4. **Deploy.** On first boot the app creates its tables and seeds departments, accounts and the
   88-subject catalogue.
5. **Verify:** open `https://<service>/login`, sign in as the Super Admin, confirm the dashboard
   lists 88 subjects. Then sign in as a department master and confirm you see only that
   department's subjects plus Common Courses.

## 3. Connect the site to it

```bash
cd frontend
API_BASE=https://<service> SIGN_IN_URL=https://<service>/login python3 build/generate.py
```

Commit and push — Pages redeploys, the **Staff** link now points at the real portal, and subject
pages load material live.

## 4. Post-deploy smoke test

- [ ] `https://<service>/login` loads over HTTPS.
- [ ] Super Admin sees all 88 subjects; a department master sees only theirs + Common.
- [ ] Publishing a resource makes it appear on the public subject page (refresh).
- [ ] `python3 security/check.py` is green.

## 5. Rollback

- **Frontend:** revert the commit; Pages redeploys from the previous commit.
- **Backend:** roll back to the previous deploy from the host's dashboard. Record the previous
  good commit SHA before deploying.
- **Database:** take a backup before any schema change (nightly backups run automatically).

---

## 6. Budget

Approximate, and free tiers change often — **verify current pricing before committing.**

| Item | Typical free tier | When it starts costing |
|---|---|---|
| GitHub Pages | free for public repos | never |
| **Oracle Always Free VM** (recommended) | free, always on | never |
| Web service (Render/Fly) | free instance that **sleeps when idle** | ~$7/mo for always-on |
| PostgreSQL (managed) | free tier is often **time-limited or small** | ~$7/mo for a persistent instance |

**Do not host this on a service with an ephemeral filesystem** — Render's free tier is the common
trap: a local SQLite database and uploaded files are erased on every deploy, restart or spin-down.
The recommended VM has a persistent disk, and so does a VPS.

**Realistic range: ₹0/month** on the recommended stack, up to roughly **₹600–1,200/month** if you
want managed, always-on hosting plus a persistent database.

There is no other recurring cost — no CDN, no email service, no paid API.

## 7. Maintenance

| Cadence | Task | Time |
|---|---|---|
| Weekly | Glance at the Security workflow result; nothing to do if green | 2 min |
| Monthly | `pip list --outdated` in `backend/`; update and redeploy | 15 min |
| Monthly | Review the audit trail (`revisions`); rotate staff credentials with the `app.manage` CLI | 5 min |
| Per term | Refresh the catalogue when your institution's official syllabus arrives | 30 min |
| Ad hoc | Back up the database before schema changes | 10 min |

Steady state: **under an hour a month**, most of it dependency updates.

## 8. If something goes wrong

- **Site down:** Pages → check the last workflow run. The frontend is static; a bad deploy is
  reverted by reverting the commit.
- **Backend down:** students are unaffected — subject pages fall back to their static content.
  Only staff lose the dashboard.
- **Leaked secret:** rotate `SESSION_SECRET`, reset the administrator's credentials with the
  `app.manage` CLI, redeploy, and check the audit trail for unexpected writes.
