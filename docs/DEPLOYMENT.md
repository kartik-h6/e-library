# Deployment runbook

Two things deploy, independently:

| Part | Where | How |
|---|---|---|
| `frontend/` | GitHub Pages | automatic — `.github/workflows/pages.yml` on every push to `main` |
| `backend/` | a small host + PostgreSQL | manual, below |

The frontend is **already live**. This runbook is for the backend, which is optional: without it
the site works fully static, and students simply don't get live material.

---

## 1. Prerequisites

- A host account — Render, Fly.io or Railway (free tiers exist).
- A PostgreSQL database — the host's own, or Neon / Supabase free tier.
- The Drive folder for material (you handle that).

## 2. Deploy the backend

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
   | `SESSION_SECRET` | a long random string (`python -c "import secrets;print(secrets.token_urlsafe(48))"`) |
   | `DEPT_MASTER_PASSWORD` | a strong password for every department master |
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
  good commit SHA in the release checklist *before* deploying.
- **Database:** take a backup before any schema change (`pg_dump`, or the host's backup feature).

---

## 6. Budget

Approximate, and free tiers change often — **verify current pricing before committing.**

| Item | Typical free tier | When it starts costing |
|---|---|---|
| GitHub Pages | free for public repos | never |
| Web service | free instance that **sleeps when idle** | ~$7/mo for always-on |
| PostgreSQL | free tier is often **time-limited or small** | ~$7/mo for a persistent instance |

**Realistic range: ₹0/month** if you accept the free tier (the service sleeps, so the first
request after idle takes ~30 s to wake), up to roughly **₹600–1,200/month** for always-on
service plus a persistent database.

Ways to keep it at zero: keep the database on a provider whose free tier doesn't expire (Neon and
Supabase both offer one), keep the web service on a free instance, and accept the cold-start.
There is no other recurring cost — no CDN, no email service, no paid API.

## 7. Maintenance

| Cadence | Task | Time |
|---|---|---|
| Weekly | Glance at the Security workflow result; nothing to do if green | 2 min |
| Monthly | `pip list --outdated` in `backend/`; update and redeploy | 15 min |
| Monthly | Review the audit trail (`revisions`); rotate `DEPT_MASTER_PASSWORD` if a staff member leaves | 5 min |
| Per term | Refresh the catalogue when RIPER's official syllabus arrives | 30 min |
| Ad hoc | Back up the database before schema changes | 10 min |

Steady state: **under an hour a month**, most of it dependency updates.

## 8. If something goes wrong

- **Site down:** Pages → check the last workflow run. The frontend is static; a bad deploy is
  reverted by reverting the commit.
- **Backend down:** students are unaffected — subject pages fall back to their static content.
  Only staff lose the dashboard.
- **Credential leak:** rotate `SESSION_SECRET` and `DEPT_MASTER_PASSWORD`, redeploy, and check the
  audit trail for unexpected writes.
