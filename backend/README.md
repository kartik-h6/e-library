# backend/

A small FastAPI service where **faculty** manage the library's material: server-enforced roles,
CRUD for subjects / units / resources, a review workflow, and a **Publish** action that writes the
frontend's catalogue. See [`docs/DASHBOARD_DESIGN.md`](../docs/DASHBOARD_DESIGN.md).

This is a **scaffold** — enough to put in front of a department — not a finished product.

## Who uses it

- **Students do not have accounts.** They read the public site anonymously.
- **Staff** sign in to manage their department's subjects and material.

## Where material lives

Source files are kept in **one shared Google Drive folder** (set `DRIVE_FOLDER_URL`, and staff see
a link to it on every subject page). A resource in the library is a **link** to a file in that
folder — the catalogue stores the URL, not the bytes. Access control therefore lives in Drive's
sharing settings, and the library is a curated index over it.

## Stack

- **FastAPI** + **SQLAlchemy 2** + **Jinja2** templates
- **SQLite** for the demo; PostgreSQL via `DATABASE_URL`
- PBKDF2-HMAC-SHA256 password hashing (standard library)
- Signed-cookie sessions; **all authorisation is server-side** (ADR-003)

## Quick start

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# optional: cp .env.example .env  and edit
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

The database is created and seeded on first start from `../frontend/data/catalogue.json` — the
real 8-semester, 88-subject catalogue — distributed by department.

## Sign in

One staff login page at `/login`. Accounts:

| Role | Login | Password | Can |
|---|---|---|---|
| Super Admin | `admin@riper.test` | `admin123` | everything |
| Department master | `master.pce@dept.riper.test` | `dept123` | CRUD own department's subjects, upload sources |
| Department master | `master.pco@dept.riper.test` | `dept123` | …and so on for pch, pgr, ppr, gen |
| SME (demo) | `sme.pharmacology@riper.test` | `sme123` | own department, submit only, cannot publish |

> Demo credentials only. Change them, and set `DEPT_MASTER_PASSWORD` in the environment before
> real use.

## What's implemented

- **Auth** — email + password, PBKDF2 hashes, signed session cookie, CSRF on every POST.
- **Roles** — `super_admin`, `hod` (department master), `sme`, `contributor` — enforced in the
  route handlers, never in the browser.
- **Department scoping** — a department master only sees and acts on their own department.
- **CRUD** — create subjects, add/remove units, create resources; soft-delete.
- **Source upload** — upload a file, or add a link to the shared Drive folder.
- **Workflow** — `draft → needs-review → verified → published → archived`, with role checks and an
  audit trail in `revisions`.
- **Published preview** — a read-only `/library` showing exactly what the public site shows.
- **Publish** — exports every published resource into the frontend's `data/catalogue.json`.
- **Public API** — `GET /api/public/library` returns published material grouped by subject code,
  with no authentication. The frontend calls it at page load so students see new material live.
  CORS is enabled for it (`CORS_ORIGINS`, default `*` — it is public, read-only data).

## What's deliberately not here

- Per-subject SME assignment (scoping is by department).
- Password reset, email verification, 2FA.
- Object storage — uploads are local files; the Drive folder is the intended store.
- Alembic migrations (tables are created from the models on start).

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./elib.db` | database connection |
| `SESSION_SECRET` | `dev-secret-change-me` | signs the session cookie — **change it** |
| `DEPT_MASTER_PASSWORD` | `dept123` | password for every department master |
| `DRIVE_FOLDER_URL` | *(empty)* | shared Drive folder link shown to staff |
| `CATALOGUE_SRC` | `../frontend/data/catalogue.json` | seed source |
| `PUBLISH_PATH` | `../frontend/data/catalogue.json` | publish target |

## Tests

```bash
python3 test_smoke.py
```

Covers login, CSRF, role scoping, the resource workflow, publish and source upload.
