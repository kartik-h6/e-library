"""Seed the database: departments and the NEP catalogue distributed by department.

Idempotent: safe to run on every start.

**No accounts are created here.** A fresh install must never come up with a known password.
Create the administrator deliberately with:

    python -m app.manage create-admin --email you@example.com

Students do not have accounts at all: they read the public site anonymously.
"""
import json
import os
import re
from pathlib import Path

from .db import SessionLocal, engine
from .models import Base, Department, Semester, Subject, Unit, User
from .paths import catalogue_src

DEPARTMENTS = [
    ("PCE", "Pharmaceutics"),
    ("PCH", "Pharmaceutical Chemistry"),
    ("PCO", "Pharmacology"),
    ("PGR", "Pharmacognosy"),
    ("PPR", "Pharmacy Practice"),
    ("GEN", "Common Courses"),
]

def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def department_code_for(title: str) -> str:
    """Map a subject title to a department, following the NEP 2020 distribution.

    `GEN` is the shared pool: internships, research projects, generic electives and
    college-wide courses that don't belong to a single department. It is visible to every
    department master as well as the super admin, so nothing is orphaned.
    """
    t = title.lower()
    # shared / college-wide
    if "choose one" in t or "internship" in t or "research project" in t:
        return "GEN"
    if any(k in t for k in ("environmental science", "universal human values")):
        return "GEN"
    # pharmacognosy
    if any(k in t for k in ("pharmacognosy", "herbal", "natural product", "phytochem")):
        return "PGR"
    # pharmacology
    if any(k in t for k in ("pharmacology", "pathophysi", "pharmacotherap",
                            "pharmacovigilance", "human anatomy")):
        return "PCO"
    # pharmaceutical chemistry
    if any(k in t for k in ("chemistry", "medicinal", "inorganic", "organic", "analysis",
                            "analytical", "biochemistry")):
        return "PCH"
    # pharmacy practice
    if any(k in t for k in ("pharmacy practice", "social pharmacy", "public health",
                            "jurisprudence", "regulatory", "management", "startup",
                            "marketing", "intellectual property", "biostatistics",
                            "research methodology", "psychology", "ai in clinical",
                            "translational")):
        return "PPR"
    # pharmaceutics
    if any(k in t for k in ("pharmaceutics", "dosage", "engineering", "biopharmaceutics",
                            "biotechnology", "quality", "physical pharm", "general pharmacy",
                            "microbiology", "cosmetic", "industrial pharmacy", "sterile",
                            "machine learning", "python", "ai application")):
        return "PCE"
    return "GEN"


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(Department).count() == 0:
            for code, name in DEPARTMENTS:
                db.add(Department(code=code, name=name))
            db.commit()

        # No accounts are created here — deliberately. See the module docstring.

        if db.query(Subject).count() == 0:
            src = catalogue_src()
            if src.exists():
                cat = json.loads(src.read_text(encoding="utf-8"))
                dept_by_code = {d.code: d.id for d in db.query(Department).all()}
                for sem in cat.get("semesters", []):
                    semester = Semester(number=sem["number"], label=sem["label"],
                                        credits=sem.get("credits", 0))
                    db.add(semester)
                    db.flush()
                    for sub in sem.get("subjects", []):
                        code = department_code_for(sub["title"])
                        subject = Subject(
                            semester_id=semester.id, code=sub["code"], title=sub["title"],
                            credits=sub.get("credits", 0), type=sub.get("type", "theory"),
                            slug=sub.get("slug") or slugify(f'{sub["code"]} {sub["title"]}'),
                            department_id=dept_by_code.get(code),
                        )
                        db.add(subject)
                        db.flush()
                        for i, unit_title in enumerate(sub.get("units", []), start=1):
                            db.add(Unit(subject_id=subject.id, seq=i, title=unit_title))
                db.commit()
    finally:
        db.close()
