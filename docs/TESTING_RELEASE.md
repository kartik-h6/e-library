# Testing and release checklist

## Before a milestone
- [ ] Official syllabus received and programme/cohort confirmed.
- [ ] Curriculum labels cross-checked against the source.
- [ ] Published resources have rights/source metadata.
- [ ] No secrets or personal data in the repository.
- [ ] Direct URLs work on refresh.
- [ ] Breadcrumbs and browser back are consistent.
- [ ] Search matches known items and handles no results.
- [ ] Resource links/PDF actions checked.
- [ ] Missing files/network errors produce a helpful state.
- [ ] Mobile and desktop layouts tested.
- [ ] Keyboard-only journey tested.
- [ ] HTML and JSON validated.
- [ ] Browser console checked for errors.
- [ ] Deployment preview reviewed.

## Smoke-test journey
1. Open home.
2. Select a verified semester.
3. Open a verified subject.
4. Open a unit.
5. Open a resource and return with browser back.
6. Search for the same resource and open it from results.
7. Load the deep URL directly in a new tab.

## Release
Use small commits, preview before changing the live entry point, keep legacy files until replacement passes review, document limitations, and verify the deployed URL.
