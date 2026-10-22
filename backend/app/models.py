"""Data model — see docs/DASHBOARD_DESIGN.md.

Tables: departments, users, semesters, subjects, units, resources, revisions.
Content is soft-deleted (`archived`) so history is never lost.
"""
from datetime import datetime

from sqlalchemy import (Boolean, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


ROLES = ("super_admin", "hod", "sme", "contributor")
RESOURCE_TYPES = ("notes", "paper", "manual", "book", "other")
STATUSES = ("draft", "needs-review", "verified", "published", "archived")


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(24), unique=True)
    name: Mapped[str] = mapped_column(String(120))


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(24))            # one of ROLES
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    department = relationship("Department")


class Semester(Base):
    __tablename__ = "semesters"
    id: Mapped[int] = mapped_column(primary_key=True)
    programme: Mapped[str] = mapped_column(String(40), default="B.Pharm")
    number: Mapped[int] = mapped_column(Integer, unique=True)
    label: Mapped[str] = mapped_column(String(40))
    credits: Mapped[int] = mapped_column(Integer, default=0)


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semesters.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(24), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(Integer, default=0)
    type: Mapped[str] = mapped_column(String(20), default="theory")
    slug: Mapped[str] = mapped_column(String(200), default="")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    semester = relationship("Semester")
    department = relationship("Department")
    units = relationship("Unit", back_populates="subject", order_by="Unit.seq")
    resources = relationship("Resource", back_populates="subject")


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    seq: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(300))

    subject = relationship("Subject", back_populates="units")


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="notes")   # one of RESOURCE_TYPES
    title: Mapped[str] = mapped_column(String(300))
    language: Mapped[str] = mapped_column(String(40), default="English")
    source: Mapped[str] = mapped_column(String(200), default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    rights: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # one of STATUSES
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    last_checked: Mapped[str] = mapped_column(String(20), default="")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    subject = relationship("Subject", back_populates="resources")


class Revision(Base):
    __tablename__ = "revisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(40))
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    payload: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
