# Feature specification

## P0 — First usable journey
- Responsive home page and clear scope.
- Semester index generated from verified curriculum data.
- Semester page with verified subjects and sourced course metadata.
- Subject page organized by officially stated units/modules.
- Resource cards listing title, type, language, source, verification date, and access action.
- PDF open/download action; identify external links.
- Breadcrumbs and browser back support.
- Search across published metadata.
- Helpful empty states when a subject/unit has no resources.
- Mobile navigation, keyboard focus, semantic HTML.
- Page titles, descriptions, favicon/custom logo, and consistent footer.
- A contribution/correction path that does not pretend to be an unimplemented shared database.

## P1 — Quality
- Filters by semester, subject, unit, type, language, and verification status.
- Resource last-checked labels and broken-link checklist.
- Optional device-local bookmarks, disclosed as local-only.
- Print-friendly resource lists.
- Source/licence details.
- Helpful 404 and unavailable-resource pages.
- Structured data only where the page content supports it accurately.

## P2 — Only if demand supports it
- Maintainer dashboard with server-side authorization.
- Shared contribution intake and moderation.
- Privacy-reviewed analytics with minimal retention.
- Offline caching/PWA after storage/update tests.
- Multilingual interface with reviewed translations.

## Acceptance criteria for P0
- Student can navigate Home → Semester → Subject → Unit → PDF without instruction.
- Each page can be refreshed and shared directly.
- Navigation works on narrow screens and with keyboard only.
- Search handles matches and no-results state.
- No unverified course/resource is represented as official.
- External links are identifiable and safe to open.
- Missing PDFs fail gracefully.
- No secrets or client-side pseudo-authentication ship.
