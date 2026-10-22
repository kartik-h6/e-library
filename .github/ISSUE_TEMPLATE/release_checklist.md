---
name: Release checklist
about: Prepare and sign off a release
title: "[Release] v"
labels: release
---

**Target version:** vX.Y
**Commit to release:**

## Gates

- [ ] Functional QA signed off
- [ ] UI & Accessibility QA signed off
- [ ] Catalogue & Build QA signed off
- [ ] Security / Release Validator signed off
- [ ] Master Orchestrator approved

## Deployment readiness

- [ ] Static site builds and deploys (Pages green)
- [ ] Admin config and hosting documented (if part of this release)
- [ ] No secrets in the repository or its history

## Rollback

- [ ] Previous good commit SHA recorded:
- [ ] Revert path tested or documented
