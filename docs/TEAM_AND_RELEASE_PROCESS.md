# RIPER e-Library — Team & Release Process

How the six-person team works on this repository: who owns what, what must pass before a
change merges, and what evidence a release needs.

---

## 1. Roles

| # | Role | Person | Owns |
|---|---|---|---|
| 1 | **Master Orchestrator** | Kartik H (`@kartik-h6`) | Approves the target design, prioritises findings, controls releases. Final call on what ships. |
| 2 | **Technical Product Architect / Implementer** | `@mahidrafiq` | Owns architecture and implements fixes approved by the Orchestrator. |
| 3 | **Tester 1 — Functional QA** | `@shyam4123` | Verifies navigation and workflows. |
| 4 | **Tester 2 — UI & Accessibility QA** | `@Lakshsharma777` | Tests responsive layouts and accessibility. |
| 5 | **Tester 3 — Catalogue & Build QA** | `@arjungupta001` | Checks content integrity, JSON, generator compatibility and publication. |
| 6 | **Security Reviewer / Release Validator** | _to be named_ | Independently checks authorisation, regression results, deployment readiness and rollback evidence. |

> Role 6 is deliberately **independent** of the Implementer: the person who writes a change
> must not be the only person who validates its security and release readiness.

---

## 2. Flow

```
finding / request
      │
      ▼
Orchestrator triages  ──►  issue created & prioritised
      │
      ▼
Implementer builds on a branch  ──►  pull request
      │
      ├─► Functional QA        (navigation & workflows)
      ├─► UI & Accessibility QA (responsive & a11y)
      └─► Catalogue & Build QA  (JSON, generator, publish)
      │
      ▼
Security / Release Validator  (authorisation, regression, deployment, rollback)
      │
      ▼
Orchestrator approves  ──►  merge to main  ──►  deploy
```

---

## 3. Merge gates

A pull request may not merge until **all** of these are true:

- [ ] **Functional QA** signs off — navigation and workflows verified.
- [ ] **UI & Accessibility QA** signs off — responsive and accessibility verified.
- [ ] **Catalogue & Build QA** signs off — catalogue validates, generator runs, publish works.
- [ ] **Security / Release Validator** signs off — authorisation intact, no secrets, rollback plan recorded.
- [ ] **Master Orchestrator** approves.

Any lane may block. A block is recorded as a review comment on the PR, not a private message.

---

## 4. Per-role checklists

### 4.1 Functional QA — `@shyam4123`

- [ ] Home → Browse → Semester → Subject → Unit renders on desktop and phone.
- [ ] Search matches known items; no-results state is clear; clearing restores the semester grid.
- [ ] Breadcrumbs and browser back behave consistently.
- [ ] A deep URL (e.g. `/semester-1/bp102t-general-pharmacy/`) works on refresh.
- [ ] Empty states are honest (no "coming soon" promises).
- [ ] Admin: login, role visibility, CRUD, `draft → needs-review → verified → published`, publish.

### 4.2 UI & Accessibility QA — `@Lakshsharma777`

- [ ] Layout holds at 360px, 768px and 1280px+ widths.
- [ ] Full keyboard journey with visible focus; no keyboard traps.
- [ ] Semantic landmarks (`header/nav/main/footer`) and logical heading order.
- [ ] Contrast is sufficient; nothing relies on colour alone.
- [ ] Reduced-motion preference respected.
- [ ] One screen-reader spot check on the Browse and Subject pages.
- [ ] Form labels present on the admin login and resource form.

### 4.3 Catalogue & Build QA — `@arjungupta001`

- [ ] `data/catalogue.json` validates against `data/schema.json`.
- [ ] `python3 build/generate.py` runs clean; expected page count produced.
- [ ] No orphaned or duplicate routes after a change.
- [ ] Admin **Publish** writes a catalogue the generator accepts; site rebuilds.
- [ ] No broken internal links on the pages touched.

### 4.4 Security / Release Validator — role 6

- [ ] Authorisation is server-side on every admin route (ADR-003); no client-side gate.
- [ ] No secrets in the repo or its history; `.env` and `*.db` ignored.
- [ ] Regression: `python3 admin/test_smoke.py` passes (currently 19 checks).
- [ ] Deployment readiness: Pages build green; admin config and hosting documented.
- [ ] Rollback: the previous good commit SHA is recorded, and a revert path exists.

---

## 5. Branching and releases

- Branch names: `feat/…`, `fix/…`, `qa/…`, `docs/…`.
- All work reaches `main` through a pull request — no direct pushes.
- Reviews: at least one QA lane plus the Security/Release Validator for anything touching
  `admin/`, `.github/`, or the publish path.
- Releases are tagged `vX.Y`. Release notes list the merged PRs and the QA sign-off for each gate.

---

## 6. Raising findings

- **Non-sensitive bugs and QA findings:** GitHub issues using the templates in
  `.github/ISSUE_TEMPLATE/` (bug report, QA finding, release checklist).
- **Security issues:** never a public issue. Use a private channel to the Orchestrator and the
  Security/Release Validator.
- Findings are triaged and prioritised by the Orchestrator before work starts.

---

## 7. Open items

- Name and handle for **role 6**.
- `@mahidrafiq`, `@shyam4123`, `@Lakshsharma777`, `@arjungupta001` need **write access** to the
  repository for `CODEOWNERS` review requests and PRs to work.
- Decide whether to protect `main` (require PR + review before merge).
