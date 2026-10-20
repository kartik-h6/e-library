# Proposed repository structure

This is a target layout, not a claim that all paths exist now. Add curriculum-specific paths only after syllabus verification.

```text
e-library/
├── index.html
├── about/index.html
├── semesters/index.html
├── search/index.html
├── contribute/index.html
├── contact/index.html
├── assets/
│   ├── css/
│   │   ├── tokens.css
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── components.css
│   ├── js/
│   │   ├── app.js
│   │   ├── navigation.js
│   │   ├── search.js
│   │   └── catalogue.js
│   ├── images/
│   ├── icons/
│   └── logo/
├── data/
│   ├── catalogue.json
│   └── schema.json
├── resources/README.md
├── docs/
│   ├── PROJECT_VISION.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── REPOSITORY_STRUCTURE.md
│   ├── CURRICULUM_AND_CONTENT.md
│   ├── DATA_MODEL.md
│   ├── SECURITY_PRIVACY.md
│   ├── ACCESSIBILITY_UX.md
│   ├── TESTING_RELEASE.md
│   ├── ROADMAP.md
│   └── DECISIONS.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

## Conventions
- Lowercase kebab-case paths.
- Keep curriculum metadata in JSON rather than duplicating it in pages.
- Keep visual styles out of HTML and behaviour out of CSS.
- Host only rights-cleared resources.
- Never commit credentials, student personal data, or unreviewed uploads.
- Avoid empty semester/subject directories until course structure is verified.
