# Architecture proposal

## Status
Proposed target architecture, not yet implemented. Curriculum routes depend on the official syllabus applicable at RIPER.

## Goals
- Static-first delivery for affordable, reliable read access.
- Separate content, layout, styles, and behaviour.
- Stable paths for semester, subject, unit, and resource pages.
- Reusable shared CSS/JS without requiring a frontend framework at first.
- Keep public content separate from any future private maintainer tools.

## Phased design

### Phase 1 — Static public library
Use HTML pages, shared CSS/JS, a version-controlled JSON catalogue, and PDFs or external links that may lawfully be shared. Hosting can be chosen after deployment requirements are confirmed.

Responsibilities:
- Browser UI: navigation, search, filters, breadcrumbs, accessible dialogs.
- Catalogue: published metadata in JSON.
- Resources: host files only where rights/storage permit; otherwise link to an authoritative source.
- Local preferences: optional device-local bookmarks/progress, clearly labelled as not syncing.

### Phase 2 — Contribution workflow (if needed)
Use reviewed GitHub issues/pull requests, a monitored form service, or a small backend. `mailto:` and localStorage are not shared submission databases.

### Phase 3 — Authenticated management (only if justified)
Use trusted identity, server-side authorization, database/object storage, auditability, backups, retention, and recovery plans. Do not build a password gate in static client JavaScript.

## Data flow
1. Browser loads a page and public catalogue.
2. Student navigates by stable URL or searches metadata.
3. Resource page shows verified metadata and access action.
4. Resource opens at its configured source.
5. Optional local preference data remains on-device unless a transparent sync service is added.

## Route proposal
Exact curriculum slugs are deliberately not invented:
- `/` home
- `/about/` about
- `/semesters/` semester index
- `/semester-{n}/` verified semester
- `/semester-{n}/{subject-slug}/` verified subject
- `/semester-{n}/{subject-slug}/units/{unit-slug}/` unit/resources
- `/search/` search
- `/contribute/` contribution guidance
- `/contact/` contact/corrections

These can be real directories or be served from a shared template, but routes should remain stable and testable.

## First-milestone non-goals
- Secure admin panel
- Student accounts or cross-device tracking
- AI-generated study notes or clinical advice
- Arbitrary direct uploads into production
- Claims of institutional endorsement without approval

## Existing prototype migration
Keep `index.html` and `index1.html` as legacy references until their behaviour is reviewed and a migration passes testing. Avoid competing home pages. Preserve a copy/tag before future replacement.
