"""Seed the database: departments, accounts, and the NEP catalogue distributed by department.

Idempotent: safe to run on every start.

Accounts created
----------------
* Super Admin        — one, full control.
* Department master  — one per department; CRUD on that department's subjects and sources.
* Student (shared)   — a single universal student login used by every student.
* SME (demo)         — a subject-matter expert who can submit but not publish.
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

# One master account per department. Change before any real use.
DEPT_MASTER_PASSWORD = os.environ.get("DEPT_MASTER_PASSWORD", "dept123")
DEPT_MASTER_EMAIL = "master.{code}@dept.riper.test"

# The universal student login — the same credentials for every student.
STUDENT_ID = os.environ.get("STUDENT_ID", "student")
STUDENT_PASSWORD = os.environ.get("STUDENT_PASSWORD", "library2026")


def slugify(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def department_code_for(title: str) -> str:
    """Map a subject title to a department. The NEP syllabus is distributed on this basis."""
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

            # the maintainer
            db.add(User(name="Super Admin", email="admin@riper.test",
                        password_hash=hash_password("admin123"),
                        role="super_admin", department_id=None))

            # one master per department
            for code, name in DEPARTMENTS:
                db.add(User(name=f"{name} — Master",
                            email=DEPT_MASTER_EMAIL.format(code=code.lower()),
                            password_hash=hash_password(DEPT_MASTER_PASSWORD),
                            role="hod", department_id=dept_by_code.get(code)))

            # one demo SME
            db.add(User(name="SME — Pharmacology", email="sme.pharmacology@riper.test",
                        password_hash=hash_password("sme123"),
                        role="sme", department_id=dept_by_code.get("PCO")))

            # the shared student login
            db.add(User(name="Student (shared)", email=STUDENT_ID,
                        password_hash=hash_password(STUDENT_PASSWORD),
                        role="student", department_id=None))
            db.commit()

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
