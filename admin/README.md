# RIPER e-Library — Admin Dashboard (scaffold)

A small, runnable scaffold of the content dashboard designed in
[`docs/DASHBOARD_DESIGN.md`](../docs/DASHBOARD_DESIGN.md): server-enforced roles, CRUD for
subjects / units / resources, a review workflow, and a publish action that writes the static
site's catalogue.

This is a **demo scaffold** — enough to put in front of one HOD, not a finished product.

It lives at `admin/` inside the e-library repository, next to the static site, and shares the
repository's `data/catalogue.json` — read for seeding, written on publish.

## Stack

- **FastAPI** + **SQLAlchemy 2** + **Jinja2** templates
- **SQLite** for the demo; PostgreSQL by setting `DATABASE_URL`
- Password hashing with PBKDF2-HMAC-SHA256 (standard library, no extra dependency)
- Sessions via a signed cookie; **all authorisation is server-side** (ADR-003)

## Quick start

```bash
cd admin
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# optional: cp .env.example .env  and edit
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000> and sign in. The database is created and seeded on first start
from `data/catalogue.json` (the real 8-semester, 88-subject catalogue).

## Demo accounts

| Role | Email | Password | Scope |
|---|---|---|---|
| Super Admin | `admin@riper.test` | `admin123` | everything |
| HOD — Pharmaceutics | `hod.pharmaceutics@riper.test` | `hod123` | own department |
| HOD — Pharmacology | `hod.pharmacology@riper.test` | `hod123` | own department |
| SME — Pharmacology | `sme.pharmacology@riper.test` | `sme123` | own department, cannot publish |
| Contributor | `contributor@riper.test` | `cont123` | own department, drafts only |

> These credentials are for the local demo only. Never ship them.

## What's implemented

- **Auth** — email + password, PBKDF2 hashes, signed session cookie, CSRF on every POST.
- **Roles** — `super_admin`, `hod`, `sme`, `contributor`, enforced in the route handlers.
- **Department scoping** — non-super-admins only see and act on their own department.
- **CRUD** — create subjects, add/remove units, create resources; soft-delete resources.
- **Workflow** — `draft → needs-review → verified → published → archived`, with role checks
  on each transition and an entry written to `revisions` (the audit trail).
- **Publish** — exports every *published* resource into `data/catalogue.json`, ready for the
  static site generator to rebuild.

## What's deliberately not here

- Per-subject SME assignment (scoping is by department in this scaffold).
- Password reset, email verification, 2FA.
- File uploads — resources are links (Drive, etc.), which is the honest model for now.
- Alembic migrations (tables are created from the models on start).
- Any real data. The catalogue is seeded; resources start empty.

## How publish works

```
dashboard DB  --publish-->  data/catalogue.json  --generate.py-->  static site
```

The database becomes the source of truth; `catalogue.json` becomes a build artifact. It writes
the repository's `data/catalogue.json` by default — run the site's `build/generate.py`
afterwards to rebuild the pages.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./elib.db` | database connection |
| `SESSION_SECRET` | `dev-secret-change-me` | signs the session cookie — **change it** |
| `CATALOGUE_SRC` | repository `data/catalogue.json` | seed source |
| `PUBLISH_PATH` | repository `data/catalogue.json` | publish target |

## Tests

```bash
python3 test_smoke.py
```

Covers login, CSRF, role scoping, the full resource workflow and publish (19 checks).

## Before this goes anywhere real

- Change `SESSION_SECRET`; use HTTPS; put it behind a reverse proxy.
- Move to PostgreSQL and add migrations.
- Add rate-limited login and 2FA for the Super Admin.
- Add password reset and per-subject SME assignment.
- Decide hosting and backups.
