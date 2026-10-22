# backend/

A small FastAPI service that implements the design in
[`docs/DASHBOARD_DESIGN.md`](../docs/DASHBOARD_DESIGN.md): server-enforced roles, CRUD for
subjects / units / resources, a review workflow, source upload, and a **Publish** action that
writes the frontend's catalogue.

This is a **scaffold** — enough to put in front of a department — not a finished product.

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

## Accounts

| Role | Login | Password | Scope |
|---|---|---|---|
| Super Admin | `admin@riper.test` | `admin123` | everything |
| Department master | `master.pce@dept.riper.test` | `dept123` | CRUD own department's subjects, upload sources |
| Department master | `master.pco@dept.riper.test` | `dept123` | …and so on for pch, pgr, ppr, gen |
| SME (demo) | `sme.pharmacology@riper.test` | `sme123` | own department, submit only, cannot publish |
| **Student (shared)** | `student` | `library2026` | read-only library |

The **student login is one universal credential shared by every student** — the same ID and
password for all, as the college's existing digital library worked. Students land on a read-only
`/library` listing published material; they cannot reach any admin page.

> Demo credentials only. Change them, and set `STUDENT_PASSWORD` / `DEPT_MASTER_PASSWORD` in the
> environment before real use.

## What's implemented

- **Auth** — email + password, PBKDF2 hashes, signed session cookie, CSRF on every POST.
- **Roles** — `super_admin`, `hod` (department master), `sme`, `contributor`, `student` — enforced
  in the route handlers, never in the browser.
- **Department scoping** — a department master only sees and acts on their own department.
- **CRUD** — create subjects, add/remove units, create resources; soft-delete.
- **Source upload** — upload a file to a subject; it is stored under `uploads/` and added as a draft.
- **Workflow** — `draft → needs-review → verified → published → archived`, with role checks and an
  audit trail in `revisions`.
- **Student library** — read-only `/library` view of published material.
- **Publish** — exports every published resource into the frontend's `data/catalogue.json`.

## What's deliberately not here

- Per-subject SME assignment (scoping is by department).
- Password reset, email verification, 2FA.
- Object storage — uploads are local files; move to S3-compatible storage before real use.
- Alembic migrations (tables are created from the models on start).

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./elib.db` | database connection |
| `SESSION_SECRET` | `dev-secret-change-me` | signs the session cookie — **change it** |
| `STUDENT_ID` | `student` | the universal student login |
| `STUDENT_PASSWORD` | `library2026` | the universal student password |
| `DEPT_MASTER_PASSWORD` | `dept123` | password for every department master |
| `CATALOGUE_SRC` | `../frontend/data/catalogue.json` | seed source |
| `PUBLISH_PATH` | `../frontend/data/catalogue.json` | publish target |

## Tests

```bash
python3 test_smoke.py
```

Covers login, CSRF, role scoping, the resource workflow, publish, the universal student login and
source upload (24 checks).
