"""Seed the database from the existing catalogue, plus demo users.

Idempotent: safe to run on every start.
"""
import json
import os
import re
from pathlib import Path

from .db import SessionLocal, engine
from .models import Base, Department, Semester, Subject, Unit, User
from .paths import catalogue_src
from .security import hash_password

DEPARTMENTS = [
    ("PCE", "Pharmaceutics"),
    ("PCH", "Pharmaceutical Chemistry"),
    ("PCO", "Pharmacology"),
    ("PGR", "Pharmacognosy"),
    ("PPR", "Pharmacy Practice"),
    ("GEN", "General"),
]

USERS = [
    ("Super Admin", "admin@riper.test", "admin123", "super_admin", None),
    ("HOD — Pharmaceutics", "hod.pharmaceutics@riper.test", "hod123", "hod", "PCE"),
    ("HOD — Pharmacology", "hod.pharmacology@riper.test", "hod123", "hod", "PCO"),
    ("SME — Pharmacology", "sme.pharmacology@riper.test", "sme123", "sme", "PCO"),
    ("Contributor", "contributor@riper.test", "cont123", "contributor", "GEN"),
]


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def department_code_for(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("pharmacognosy", "herbal", "natural product", "phytochem")):
        return "PGR"
    if any(k in t for k in ("pharmacology", "pathophysi", "pharmacotherap", "pharmacovigilance")):
        return "PCO"
    if any(k in t for k in ("chemistry", "medicinal", "inorganic", "organic", "analysis", "analytical")):
        return "PCH"
    if any(k in t for k in ("pharmacy practice", "social", "jurisprudence", "regulatory",
                            "management", "startup", "marketing")):
        return "PPR"
    if any(k in t for k in ("pharmaceutics", "dosage", "engineering", "biopharmaceutics",
                            "biotechnology", "quality", "physical pharm")):
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

        if db.query(User).count() == 0:
            dept_by_code = {d.code: d.id for d in db.query(Department).all()}
            for name, email, pw, role, dept in USERS:
                db.add(User(name=name, email=email, password_hash=hash_password(pw),
                            role=role, department_id=dept_by_code.get(dept) if dept else None))
            db.commit()

        src = catalogue_src()
        if db.query(Subject).count() == 0 and src.exists():
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
