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
about/  contact/  404.html
assets/css  assets/js  assets/logo
data/catalogue.json     single source of truth for the structure
data/schema.json        JSON Schema for the catalogue
build/generate.py       the generator
resources/              rights-cleared files only
```

## Deployment

Served by GitHub Pages at <https://kartik-h6.github.io/e-library/> via
`.github/workflows/pages.yml`, which publishes this folder as the site root.

## Notes

- No build step beyond `generate.py` — no framework, no bundler.
- No third-party CDN: styles and icons are local.
- The catalogue is written by the backend's **Publish** action; the database is the source of
  truth and this file is a build artifact.
