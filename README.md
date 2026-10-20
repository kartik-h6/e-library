# RIPER e-Library

A student-first digital study library for RIPER B.Pharm students.

**Status:** P0 implemented. The public static library (home → semester → subject → unit, with search,
breadcrumbs and accessible markup) is generated from a version-controlled JSON catalogue.

## Curriculum source
- Authority: Pharmacy Council of India
- Document: Syllabus — Bachelor of Pharmacy (B.Pharm) 2026, as per NEP 2020
- Status: **provisional** — interim source, pending RIPER's official syllabus for the cohort.

## Repository layout
```
index.html              home
semesters/index.html    semester index
semester-N/index.html   semester page
semester-N/<subject>/   subject page (units + study material)
search/  about/  contribute/  contact/   404.html
assets/css  assets/js  assets/logo
data/catalogue.json     single source of truth for the structure
data/schema.json        JSON Schema for the catalogue
build/generate.py       regenerates all pages from the catalogue
resources/              rights-cleared files only
docs/                   project documentation
```

## Regenerating the site
Edit `data/catalogue.json`, then from the repository root:

```bash
python3 build/generate.py
```

## Principles
1. Official curriculum is the source of truth; unverified data stays unpublished.
2. Stable routes: semester → subject → unit.
3. Mobile-first, low-bandwidth, keyboard-accessible.
4. Show source, language, rights and verification status for material.
5. No secrets, and no client-side pseudo-authentication.
6. Publish only content the project may share.

See `docs/` for the full specification.
