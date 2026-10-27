# TechStudyHubCore Pharmacy — Admin Dashboard (Design)

**Status:** design proposal (Stage 3). Not built. This document defines *what* would be built and *why*, so the decision to build it can be made on evidence rather than impulse.

---

## 1. Purpose

Today the library is static: `frontend/data/catalogue.json` is edited by hand and the site is regenerated. That does not scale to 88 subjects across departments, and it makes one person the bottleneck for every correction.

This design proposes a small admin dashboard so that each department's **HOD** or a **subject-matter expert (SME)** can manage their own subjects' material through CRUD operations, with a review step before anything reaches the public site.

The goal is not a school ERP. It is a content tool with roles.

---

## 2. What we borrow from the reference app (`4jean/lav_sms`)

The reference is a Laravel school management system. We take its *patterns*, not its code or its domain.

**Borrow**
- Role-based access enforced in **server-side middleware** — never in the browser.
- One controller per entity with `index / store / update / destroy`.
- One migration per table, with explicit foreign keys.
- A "Support Team" tier that maps cleanly onto "HOD / SME".
- A recorded trail of who changed what.

**Do not borrow**
- The school-ERP domain: students, marks, fees, timetables, dormitories.
- The dated stack (Laravel 8, Bootstrap 4, jQuery, Vue 2 — all end-of-life).
- 2,700 files of scaffolding for a much smaller problem.

---

## 3. Roles and permissions

| Capability | Super Admin | HOD | SME / Editor | Contributor | Public |
|---|:--:|:--:|:--:|:--:|:--:|
| Manage departments & semesters | ✔ | – | – | – | – |
| Manage subjects | ✔ | own dept | assigned | – | – |
| Create / edit resources | ✔ | own dept | assigned | – | – |
| Submit material (draft) | ✔ | own dept | assigned | ✔ | – |
| Approve / reject submissions | ✔ | own dept | – | – | – |
| Publish / archive | ✔ | own dept | – | – | – |
| Manage users & roles | ✔ | – | – | – | – |
| View audit log | ✔ | own dept | own actions | own actions | – |
| Read the public library | ✔ | ✔ | ✔ | ✔ | ✔ |

**Roles**
- **Super Admin** — the project owner. Manages structure and users; can override anything.
- **HOD (Department Head)** — manages subjects and resources for *their own department*; approves or rejects SME submissions for that department.
- **SME / Editor** — creates and edits units and resources for *assigned* subjects; submits for review.
- **Contributor** — may submit material as a draft, scoped to their subjects; cannot publish.
- **Public** — no login; reads the published static site.

Every role except Public is enforced on the **server** (ADR-003).

---

## 4. Data model

Extends the existing catalogue schema (see `DATA_MODEL.md`).

| Entity | Key fields |
|---|---|
| `user` | id, name, email, password_hash, role, department_id, active |
| `department` | id, code, name |
| `programme` | id, code, name (B.Pharm; later Pharm.D, M.Pharm) |
| `semester` | id, programme_id, number, label, credits |
| `subject` | id, semester_id, code, title, credits, type, department_id, slug |
| `unit` | id, subject_id, seq, title |
| `resource` | id, subject_id, unit_id (nullable), type, title, language, source, url, rights, status, reviewer_id, last_checked, created_by |
| `revision` | id, entity, entity_id, action, actor_id, payload, created_at |

`resource.type` is one of `notes | paper | manual | book | other` — the same four sections the public site already renders.

The public site consumes a **published projection** of this model (today: `frontend/data/catalogue.json`).

---

## 5. Content workflow

```
draft  →  needs-review  →  verified  →  published  →  archived
```

Aligned with `CURRICULUM_AND_CONTENT.md`.

- Only `published` rows appear on the public site.
- An HOD approves a transition to `verified` / `published` for their department.
- Every transition is written to `revision`.

---

## 6. CRUD per entity

| Entity | Create | Read | Update | Delete | Who |
|---|:--:|:--:|:--:|:--:|---|
| Department | ✔ | ✔ | ✔ | soft | Super Admin |
| Semester | ✔ | ✔ | ✔ | soft | Super Admin |
| Subject | ✔ | ✔ | ✔ | soft | Super Admin, HOD (own dept) |
| Unit | ✔ | ✔ | ✔ | soft | HOD, SME (assigned) |
| Resource | ✔ | ✔ | ✔ | soft | HOD, SME, Contributor (draft only) |
| User / role | ✔ | ✔ | ✔ | deactivate | Super Admin |

Deletes are soft (archived) so history is never lost.

---

## 7. Authentication and security

- **Server-side sessions** (or JWT) — never a client-side check (ADR-003).
- Passwords hashed (bcrypt / argon2).
- CSRF protection; rate-limited login; optional 2FA for Super Admin.
- Role middleware on **every** route, mirroring the reference app's `teamSA` / `teamSAT` gates.
- Audit log of every write; soft deletes.
- No secrets in the repository; configuration via environment variables.
- HTTPS only.

---

## 8. Routes / API surface

```
POST   /login                      POST   /logout
GET    /api/me

GET    /api/departments            POST /api/departments
GET    /api/subjects               POST /api/subjects
PUT    /api/subjects/{id}          DELETE /api/subjects/{id}
GET    /api/units                  POST /api/units
PUT    /api/units/{id}             DELETE /api/units/{id}
GET    /api/resources              POST /api/resources
PUT    /api/resources/{id}         DELETE /api/resources/{id}

POST   /api/resources/{id}/submit      (draft → needs-review)
POST   /api/resources/{id}/approve     (needs-review → verified)
POST   /api/resources/{id}/publish     (verified → published)
POST   /api/resources/{id}/archive

GET    /api/catalogue/published     (public, read-only)
GET    /api/audit                   (scoped by role)
```

---

## 9. Technology options

**Option A — purpose-built service (recommended).** A small **FastAPI + PostgreSQL** service, reusing the stack the project already runs for PMAS. Around ten tables, one service, no framework sprawl.

**Option B — slimmed Laravel app.** If the maintainer prefers PHP, take only the reference app's auth + role middleware + CRUD scaffolding and build the e-library domain on top. Faster to start, but carries an end-of-life framework and more files to keep current.

Either way the shape is the same: one small service, server-enforced roles, an audit trail.

---

## 10. How it connects to the static site

**Option 1 — build-time (recommended).** The dashboard writes to the database. A **Publish** action exports the `published` rows to `frontend/data/catalogue.json` and commits it; the existing generator rebuilds the static pages. The site stays static, fast and free; there is no runtime API to secure or pay for.

**Option 2 — runtime.** The site fetches a read-only JSON API. More moving parts and a permanent service to keep alive; only worth it if genuinely live updates are needed.

Recommendation: **Option 1**. The database becomes the source of truth; `catalogue.json` becomes a build artifact.

---

## 11. Non-goals

- Student accounts, marks, fees, attendance — that is an ERP, not a library.
- Cross-device tracking of readers.
- AI-generated study content.

---

## 12. Rollout

1. Schema + migrations.
2. Auth, roles and audit.
3. CRUD for subjects, units and resources.
4. Review / publish workflow.
5. Publish → `catalogue.json` → regenerate.
6. Pilot with one department, then open to the rest.

---

## 13. Risks

- **Two sources of truth.** Resolved by making the database authoritative and `catalogue.json` a build artifact.
- **Scope creep toward an ERP.** Guarded by the non-goals above.
- **Maintainer bandwidth.** The entire point of the tool is to distribute editing away from one person — but it only works if HODs and SMEs actually adopt it, which is why the rollout ends with a single-department pilot rather than a big-bang launch.
