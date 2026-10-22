# frontend/

The public static site for the RIPER e-Library — home, browse/search, semester and subject
pages, and an honest empty state wherever material doesn't exist yet.

It is **generated** from a JSON catalogue, so the structure lives in one place.

## Regenerate

```bash
python3 build/generate.py
```

Reads `data/catalogue.json` and writes every page: `index.html`, `404.html`, `about/`,
`semesters/`, `semester-N/`, `semester-N/<subject>/`, plus `assets/`.

## Structure

```
index.html              home (landing)
semesters/index.html    browse + search
semester-N/index.html   semester page
semester-N/<subject>/   subject page (units + material sections)
about/  contact/  staff/  404.html
assets/css  assets/js  assets/logo
data/catalogue.json     single source of truth for the structure
data/schema.json        JSON Schema for the catalogue
build/generate.py       the generator
resources/              rights-cleared files only
```

## Access

- **Students** read the site anonymously — no account, no sign-in.
- **Staff** reach their portal from the **Staff** link in the nav. That link points to
  `SIGN_IN_URL` when set (the hosted staff service); otherwise it opens `staff/index.html`, which
  explains the two paths. Set `SIGN_IN_URL` before launch:

```bash
SIGN_IN_URL=https://<staff-service>/login python3 build/generate.py
```

## Live material

Subject pages can load published material **live** from the staff service, so students see
updates the moment a department publishes — no rebuild. Set `API_BASE` and regenerate:

```bash
API_BASE=https://<staff-service> python3 build/generate.py
```

With it set, each subject page includes `assets/js/material.js`, which calls
`<API_BASE>/api/public/library` and fills the material sections. If the service is unreachable,
the page falls back to whatever the catalogue contains. With `API_BASE` empty, the pages are
fully static.

## Deployment

Served by GitHub Pages at <https://kartik-h6.github.io/e-library/> via
`.github/workflows/pages.yml`, which publishes this folder as the site root.

## Notes

- No build step beyond `generate.py` — no framework, no bundler.
- No third-party CDN: styles and icons are local.
- The catalogue is written by the backend's **Publish** action; the database is the source of
  truth and this file is a build artifact.
