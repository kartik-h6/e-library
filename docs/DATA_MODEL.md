# Data model proposal

The initial catalogue is proposed as version-controlled JSON. This document contains no real syllabus entries.

## Entities
- **Programme:** identifier, display name, curriculum reference.
- **Semester:** identifier, programme, sequence number, label.
- **Subject:** identifier, semester, official code/title, credits only when confirmed, course type only when sourced.
- **Unit:** identifier, subject, official unit/module label and title.
- **Resource:** identifier, subject/unit, title, type, language, source/author, URL/path, rights/licence, status, reviewer, last-checked date.

## Example JSON shape
```json
{
  "schemaVersion": 1,
  "curriculum": {
    "programme": "To be confirmed from official document",
    "documentTitle": "To be supplied",
    "documentVersion": null,
    "sourceUrl": null,
    "checkedAt": null,
    "status": "unverified"
  },
  "resources": []
}
```

## Rules
- Use unique stable IDs separate from display titles.
- Keep official title and URL slug separate.
- Represent unknown values as `null` or omit them; never guess.
- Validate catalogue JSON before publishing.
- Keep credentials, private student information, and private notes out of public data.
