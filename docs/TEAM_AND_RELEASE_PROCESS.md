# TechStudyHubCore Pharmacy — Contributor & Release Process

How work reaches this repository: who contributes, who reviews what, and what must pass before a
change merges.

---

## 1. How contributions work here

This is a **solo-maintained project**. The maintainer built it end to end — idea, planning,
design, implementation, deployment and hosting — and **holds the only write access to the
repository**.

Contributors do **not** get collaborator access. Every contribution arrives one of two ways:

1. **An issue** — a bug report, a QA finding, or a suggestion.
2. **A pull request from a fork** — branch off your fork, make the change, open a PR.

The maintainer reviews and merges. Nothing is merged without review.

This keeps the project's integrity with one person while giving contributors real, reviewable
practice with the GitHub workflow (fork → branch → PR → review).

---

## 2. Roles — review responsibilities, not access levels

These describe **who reviews what** when a contribution touches their area. They are not
repository permissions and do not confer write access. Every contribution still goes through a
fork and a pull request, and the maintainer makes the final call.

| # | Role | Person | Reviews |
|---|---|---|---|
| 1 | **Master Orchestrator / Maintainer** | Kartik H (`@kartik-h6`) | Approves design, prioritises findings, reviews everything, merges and releases. Sole write access. |
| 2 | **Technical Product Architect / Implementer** | `@mahidrafiq` | Architecture; implements approved changes. |
| 3 | **Functional QA** | `@shyam4123` | Navigation and workflows. |
| 4 | **UI & Accessibility QA** | `@Lakshsharma777` | Responsive layouts and accessibility. |
| 5 | **Catalogue & Build QA** | `@arjungupta001` | Content integrity, JSON, generator compatibility, publication. |
| 6 | **Security Reviewer / Release Validator** | Anzer (handle TBD) | Authorisation, regression, deployment readiness, rollback evidence. |

> The composition of this group is still forming. Roles are a description of intent, not a fixed
> allocation — they can change as people find what they're good at.

---

## 3. Flow

```
idea / finding
      │
      ▼
issue (or a fork + PR for a concrete change)
      │
      ▼
maintainer triages & prioritises
      │
      ▼
contributor opens a PR from their fork
      │
      ▼
review against the checklists below
      │
      ▼
maintainer approves & merges  ──►  deploy
```

---

## 4. Merge gates

A pull request should not merge until:

- [ ] It does what the linked issue asked, and nothing unrelated.
- [ ] The relevant checklists below have been walked.
- [ ] The catalogue validates and the generator still runs (for anything touching content or build).
- [ ] No secrets are added.
- [ ] The maintainer approves.

The `main` branch is protected: changes must arrive by pull request.

---

## 5. Review checklists

### 5.1 Functional
- [ ] Home → Browse → Semester → Subject → Unit renders on desktop and phone.
- [ ] Search matches known items; no-results state is clear; clearing restores the semester grid.
- [ ] Breadcrumbs and browser back behave consistently.
- [ ] A deep URL (e.g. `/semester-1/bp102t-general-pharmacy/`) works on refresh.
- [ ] Empty states are honest (no "coming soon" promises).

### 5.2 UI & accessibility
- [ ] Layout holds at 360px, 768px and 1280px+ widths.
- [ ] Full keyboard journey with visible focus; no keyboard traps.
- [ ] Semantic landmarks and logical heading order.
- [ ] Contrast is sufficient; nothing relies on colour alone.
- [ ] Reduced-motion preference respected.
- [ ] Form labels present.

### 5.3 Catalogue & build
- [ ] `frontend/data/catalogue.json` validates against `frontend/data/schema.json`.
- [ ] `python3 frontend/build/generate.py` runs clean and produces the expected page count.
- [ ] No orphaned or duplicate routes.
- [ ] No broken internal links on the pages touched.

### 5.4 Security & release
- [ ] Authorisation is server-side on every admin route (ADR-003); no client-side gate.
- [ ] No secrets in the repo or its history; `.env` and `*.db` ignored.
- [ ] Regression: `python3 backend/test_smoke.py` passes (currently 19 checks).
- [ ] Deployment readiness and a rollback path are recorded for a release.

---

## 6. Branching and releases

- Branch names: `feat/…`, `fix/…`, `qa/…`, `docs/…`.
- All work reaches `main` through a pull request.
- Releases are tagged `vX.Y`, with notes listing what changed.

---

## 7. Raising findings

- **Non-sensitive:** GitHub issues using the templates in `.github/ISSUE_TEMPLATE/`.
- **Security:** never a public issue — see `SECURITY.md`.
- Findings are triaged and prioritised by the maintainer before work starts.
