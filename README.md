# RIPER e-Library

A semester-wise B.Pharm study library for students of RIPER (Raghavendra Institute of
Pharmaceutical Education and Research, Anantapur), built on the **PCI B.Pharm syllabus 2026
(NEP 2020)** as an interim source until the college's own syllabus is supplied.

This is a small monorepo: a public static site, a backend service, and a security-check lane.

## Layout

| Folder | What it is | Deployed how |
|---|---|---|
| `frontend/` | The public static site (home → browse → semester → subject → units + material) | GitHub Pages, from `frontend/` |
| `backend/` | FastAPI service: roles, CRUD for subjects/units/resources, review workflow, source upload, publish | Self-hosted (Render/Fly/VPS) with PostgreSQL |
| `security/` | Security & release checks (`python3 security/check.py`) | Runs in CI on every PR |
| `docs/` | Design and process documentation | — |

## Frontend

The static site is generated from a JSON catalogue — the single source of truth for the structure.

```bash
cd frontend
python3 build/generate.py       # regenerates every page from data/catalogue.json
```

Live at **https://kartik-h6.github.io/e-library/**, deployed by `.github/workflows/pages.yml`.

## Backend

A small FastAPI service: server-enforced roles, CRUD, a `draft → needs-review → verified →
published` workflow, source upload, and a **Publish** action that writes the frontend's catalogue.

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

Accounts created on first start:

| Role | Login | Password | Can |
|---|---|---|---|
| Super Admin | `admin@riper.test` | `admin123` | everything |
| Department master (one per department) | `master.pce@dept.riper.test` (etc.) | `dept123` | CRUD that department's subjects + upload sources |
| SME (demo) | `sme.pharmacology@riper.test` | `sme123` | submit material, cannot publish |

**Students have no accounts** — they read the public site anonymously. Material is kept in one
shared Google Drive folder (`DRIVE_FOLDER_URL`); the catalogue links to it.

> These are demo credentials. Change them, and set `DEPT_MASTER_PASSWORD` in the environment
> before any real use.

## Security checks

```bash
python3 security/check.py
```

## Documentation

- `docs/DASHBOARD_DESIGN.md` — the backend's design
- `docs/TEAM_AND_RELEASE_PROCESS.md` — how contributions and releases work
- `docs/CURRICULUM_AND_CONTENT.md` — curriculum governance and content rules

## Principles

1. Official curriculum is the source of truth; unverified data stays unpublished.
2. Stable routes: semester → subject → unit.
3. Mobile-first, low-bandwidth, keyboard-accessible.
4. Show source, language, rights and verification status for material.
5. No secrets, and no client-side pseudo-authentication.
6. Publish only content the project may share.
