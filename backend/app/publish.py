"""Export the published catalogue — the build artifact the static site consumes.

Only resources with status == "published" (and not archived) are written out.
"""
import json
import os
from pathlib import Path

from .models import Resource, Semester, Subject, Unit

from .paths import catalogue_src, publish_path

DEFAULT_PATH = str(publish_path())


def curriculum_meta() -> dict:
    try:
        cat = json.loads(catalogue_src().read_text(encoding="utf-8"))
        return cat.get("curriculum", {})
    except Exception:
        return {"programme": "B.Pharm", "status": "provisional"}


def build_catalogue(db) -> dict:
    out = {"schemaVersion": 1, "curriculum": curriculum_meta(), "semesters": []}
    for sem in db.query(Semester).order_by(Semester.number).all():
        subjects = (db.query(Subject)
                    .filter(Subject.semester_id == sem.id, Subject.archived.is_(False))
                    .order_by(Subject.code).all())
        subj_out = []
        for sub in subjects:
            unit_rows = (db.query(Unit).filter(Unit.subject_id == sub.id)
                         .order_by(Unit.seq).all())
            units = [u.title for u in unit_rows]
            unit_of = {u.id: u for u in unit_rows}
            resources = (db.query(Resource)
                         .filter(Resource.subject_id == sub.id,
                                 Resource.status == "published",
                                 Resource.archived.is_(False)).all())
            subj_out.append({
                "id": sub.code.lower(),
                "code": sub.code,
                "slug": sub.slug,
                "title": sub.title,
                "credits": sub.credits,
                "type": sub.type,
                "units": units,
                "resources": [{
                    "title": r.title, "type": r.type, "language": r.language,
                    "source": r.source, "url": r.url, "rights": r.rights,
                    "status": r.status, "lastChecked": r.last_checked,
                    # which unit this belongs to, so the site can file it under that unit
                    "unitSeq": unit_of[r.unit_id].seq if r.unit_id in unit_of else None,
                    "unit": unit_of[r.unit_id].title if r.unit_id in unit_of else "",
                } for r in resources],
            })
        out["semesters"].append({
            "id": f"semester-{sem.number}", "number": sem.number,
            "label": sem.label, "credits": sem.credits, "subjects": subj_out,
        })
    return out


def write_catalogue(db, path: str | None = None) -> dict:
    path = path or DEFAULT_PATH
    data = build_catalogue(db)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data
