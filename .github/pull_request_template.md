<!--
  Every change reaches main through a pull request.
  See docs/TEAM_AND_RELEASE_PROCESS.md for the gates and per-role checklists.
-->

## What this changes

<!-- One or two sentences. Link the issue: "Closes #12" -->

## Type

- [ ] Fix
- [ ] Feature
- [ ] Content / catalogue
- [ ] Docs / process
- [ ] Security

## QA gates — all must be ticked before merge

**Functional QA (@shyam4123)**
- [ ] Navigation and workflows verified
- [ ] Search, breadcrumbs and deep-link refresh verified
- [ ] Admin workflow (draft → needs-review → verified → published) verified

**UI & Accessibility QA (@Lakshsharma777)**
- [ ] Responsive at 360 / 768 / 1280px
- [ ] Keyboard-only journey with visible focus
- [ ] Contrast, semantics and labels checked

**Catalogue & Build QA (@arjungupta001)**
- [ ] `frontend/data/catalogue.json` validates against `frontend/data/schema.json`
- [ ] `python3 frontend/build/generate.py` runs clean
- [ ] Publish path verified (if touched)

**Security / Release Validator**
- [ ] Server-side authorisation intact; no client-side gate
- [ ] No secrets added; `.env` / `*.db` ignored
- [ ] `python3 backend/test_smoke.py` passes
- [ ] Rollback: previous good commit recorded

## Orchestrator approval

- [ ] Approved to merge (Master Orchestrator)
