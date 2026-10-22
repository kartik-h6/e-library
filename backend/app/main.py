"""RIPER e-Library — admin dashboard (scaffold).

A small FastAPI service with server-enforced roles and CRUD for subjects,
units and resources, plus a review workflow and a publish action that writes
the static site's catalogue. See docs/DASHBOARD_DESIGN.md.

    uvicorn app.main:app --reload
"""
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from . import publish, security
from .db import SessionLocal, engine, get_db
from .models import (Base, Department, Resource, Revision, Semester, Subject,
                     Unit, User)
from .seed import seed

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
# Where material is stored. Shown to staff as a link; empty hides it.
DRIVE_FOLDER = os.environ.get("DRIVE_FOLDER_URL", "")
# The public library site, linked from the staff header.
PUBLIC_SITE = os.environ.get("PUBLIC_SITE_URL", "https://kartik-h6.github.io/e-library/")

ACTION_STATUS = {"submit": "needs-review", "approve": "verified",
                 "publish": "published", "archive": "archived", "reopen": "draft"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    seed()
    yield


app = FastAPI(title="RIPER e-Library Admin (scaffold)", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET, same_site="lax")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


# ---------------------------------------------------------------- helpers

def page(request: Request, db, name: str, **extra):
    user = security.current_user(request, db)
    ctx = {"request": request, "user": user, "csrf": security.csrf_token(request),
           "drive_folder": DRIVE_FOLDER, "public_site": PUBLIC_SITE}
    ctx.update(extra)
    return templates.TemplateResponse(request, name, ctx)


def gate(request: Request, db):
    """Return (user, None) or (None, redirect). Any signed-in user passes."""
    user = security.current_user(request, db)
    if not user or not user.active:
        return None, RedirectResponse("/login", status_code=303)
    return user, None


def log(db, entity, entity_id, action, actor_id, payload=""):
    db.add(Revision(entity=entity, entity_id=entity_id, action=action,
                    actor_id=actor_id, payload=payload))


def scoped_subjects(db, user):
    q = db.query(Subject).filter(Subject.archived.is_(False))
    if user.role != "super_admin":
        q = q.filter(Subject.department_id == user.department_id)
    return q.order_by(Subject.code).all()


# ---------------------------------------------------------------- auth

@app.get("/")
def home(request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, db=Depends(get_db)):
    return page(request, db, "login.html")


@app.post("/login")
def login(request: Request, db=Depends(get_db),
          email: str = Form(...), password: str = Form(...)):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not security.verify_password(password, user.password_hash) or not user.active:
        return page(request, db, "login.html", error="Invalid email or password.")
    security.login_session(request, user)
    return RedirectResponse("/dashboard", status_code=303)


@app.post("/logout")
def logout(request: Request, csrf: str = Form("")):
    security.check_csrf(request, csrf)
    security.logout_session(request)
    return RedirectResponse("/login", status_code=303)


# ---------------------------------------------------------------- dashboard

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    subjects = scoped_subjects(db, user)
    ids = [s.id for s in subjects]
    res = (db.query(Resource).filter(Resource.subject_id.in_(ids)).all() if ids else [])
    counts = {k: sum(1 for r in res if r.status == k)
              for k in ("draft", "needs-review", "verified", "published", "archived")}
    return page(request, db, "dashboard.html", subjects=subjects, counts=counts,
                total_resources=len(res))


# ---------------------------------------------------------------- subjects

@app.get("/subjects", response_class=HTMLResponse)
def subjects(request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    return page(request, db, "subjects.html", subjects=scoped_subjects(db, user),
                semesters=db.query(Semester).order_by(Semester.number).all(),
                can_manage=security.can_manage_subjects(user))


@app.post("/subjects")
def create_subject(request: Request, db=Depends(get_db),
                   csrf: str = Form(""), code: str = Form(...), title: str = Form(...),
                   semester_id: int = Form(...), credits: int = Form(0), type: str = Form("theory")):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    if not security.can_manage_subjects(user):
        return RedirectResponse("/subjects", status_code=303)
    from .seed import department_code_for, slugify
    code_dep = department_code_for(title)
    dep = db.query(Department).filter(Department.code == code_dep).first()
    subject = Subject(semester_id=semester_id, code=code.strip().upper(), title=title.strip(),
                      credits=credits, type=type, slug=slugify(f"{code} {title}"),
                      department_id=dep.id if dep else None)
    db.add(subject)
    db.flush()
    log(db, "subject", subject.id, "create", user.id, title)
    db.commit()
    return RedirectResponse(f"/subjects/{subject.id}", status_code=303)


@app.get("/subjects/{sid}", response_class=HTMLResponse)
def subject_detail(sid: int, request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    subject = db.get(Subject, sid)
    if not subject:
        return RedirectResponse("/subjects", status_code=303)
    units = db.query(Unit).filter(Unit.subject_id == sid).order_by(Unit.seq).all()
    resources = (db.query(Resource)
                 .filter(Resource.subject_id == sid, Resource.archived.is_(False))
                 .order_by(Resource.id.desc()).all())
    return page(request, db, "subject.html", subject=subject, units=units, resources=resources,
                in_scope=security.in_scope(user, subject),
                can_edit=security.can_edit_resources(user),
                can_approve=security.can_approve(user), can_publish=security.can_publish(user))


@app.post("/subjects/{sid}/units")
def add_unit(sid: int, request: Request, db=Depends(get_db),
             csrf: str = Form(""), title: str = Form(...)):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    subject = db.get(Subject, sid)
    if subject and security.in_scope(user, subject) and security.can_edit_resources(user):
        nxt = db.query(Unit).filter(Unit.subject_id == sid).count() + 1
        db.add(Unit(subject_id=sid, seq=nxt, title=title.strip()))
        log(db, "unit", sid, "create", user.id, title)
        db.commit()
    return RedirectResponse(f"/subjects/{sid}", status_code=303)


@app.post("/units/{uid}/delete")
def delete_unit(uid: int, request: Request, db=Depends(get_db), csrf: str = Form("")):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    unit = db.get(Unit, uid)
    if unit and security.can_edit_resources(user):
        sid = unit.subject_id
        db.delete(unit)
        log(db, "unit", uid, "delete", user.id, unit.title)
        db.commit()
        return RedirectResponse(f"/subjects/{sid}", status_code=303)
    return RedirectResponse("/subjects", status_code=303)


# ---------------------------------------------------------------- resources

@app.post("/subjects/{sid}/resources")
def create_resource(sid: int, request: Request, db=Depends(get_db),
                    csrf: str = Form(""), type: str = Form("notes"), title: str = Form(...),
                    language: str = Form("English"), source: str = Form(""),
                    url: str = Form(""), rights: str = Form(""), unit_id: str = Form("")):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    subject = db.get(Subject, sid)
    if subject and security.in_scope(user, subject) and security.can_edit_resources(user):
        db.add(Resource(subject_id=sid, unit_id=int(unit_id) if unit_id else None, type=type,
                        title=title.strip(), language=language, source=source, url=url.strip(),
                        rights=rights, status="draft", created_by=user.id))
        log(db, "resource", sid, "create", user.id, title)
        db.commit()
    return RedirectResponse(f"/subjects/{sid}", status_code=303)


@app.post("/resources/{rid}/status")
def change_status(rid: int, request: Request, db=Depends(get_db),
                  csrf: str = Form(""), action: str = Form(...)):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    res = db.get(Resource, rid)
    if not res or action not in ACTION_STATUS:
        return RedirectResponse("/subjects", status_code=303)
    subject = db.get(Subject, res.subject_id)
    allowed = security.in_scope(user, subject) and (
        (action in ("submit", "reopen") and security.can_edit_resources(user)) or
        (action in ("approve", "publish", "archive") and security.can_approve(user)))
    if allowed:
        res.status = ACTION_STATUS[action]
        if action in ("approve", "publish"):
            res.reviewer_id = user.id
        log(db, "resource", rid, action, user.id, res.title)
        db.commit()
    return RedirectResponse(f"/subjects/{res.subject_id}", status_code=303)


@app.post("/resources/{rid}/delete")
def delete_resource(rid: int, request: Request, db=Depends(get_db), csrf: str = Form("")):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    res = db.get(Resource, rid)
    if res:
        subject = db.get(Subject, res.subject_id)
        if security.in_scope(user, subject) and security.can_edit_resources(user):
            res.archived = True
            log(db, "resource", rid, "archive", user.id, res.title)
            db.commit()
        return RedirectResponse(f"/subjects/{res.subject_id}", status_code=303)
    return RedirectResponse("/subjects", status_code=303)


# ---------------------------------------------------------------- upload & published preview

@app.post("/subjects/{sid}/upload")
async def upload_source(sid: int, request: Request, db=Depends(get_db),
                        csrf: str = Form(""), type: str = Form("notes"), title: str = Form(""),
                        unit_id: str = Form(""), file: UploadFile = File(...)):
    """A department master (or the maintainer) uploads a source file for a subject."""
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    subject = db.get(Subject, sid)
    if not (subject and security.in_scope(user, subject) and security.can_edit_resources(user)):
        return RedirectResponse(f"/subjects/{sid}", status_code=303)
    safe = os.path.basename(file.filename or "file")
    name = f"{uuid.uuid4().hex[:8]}-{safe}"
    (UPLOAD_DIR / name).write_bytes(await file.read())
    db.add(Resource(subject_id=sid, unit_id=int(unit_id) if unit_id else None, type=type,
                    title=(title.strip() or safe), url=f"/uploads/{name}", source="upload",
                    status="draft", created_by=user.id))
    log(db, "resource", sid, "upload", user.id, name)
    db.commit()
    return RedirectResponse(f"/subjects/{sid}", status_code=303)


@app.get("/library", response_class=HTMLResponse)
def library(request: Request, db=Depends(get_db)):
    """Read-only view of published material — exactly what the public site shows."""
    user, redir = gate(request, db)
    if redir:
        return redir
    rows = (db.query(Resource)
            .filter(Resource.status == "published", Resource.archived.is_(False))
            .order_by(Resource.subject_id, Resource.id.desc()).all())
    groups = {}
    for r in rows:
        groups.setdefault(r.subject_id, []).append(r)
    subjects = {s.id: s for s in db.query(Subject).all()}
    return page(request, db, "library.html", groups=groups, subjects=subjects, total=len(rows))


# ---------------------------------------------------------------- review & publish

@app.get("/review", response_class=HTMLResponse)
def review(request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    ids = [s.id for s in scoped_subjects(db, user)]
    queue = (db.query(Resource)
             .filter(Resource.subject_id.in_(ids), Resource.archived.is_(False),
                     Resource.status.in_(("needs-review", "verified"))).all() if ids else [])
    return page(request, db, "review.html", queue=queue,
                can_approve=security.can_approve(user), can_publish=security.can_publish(user))


@app.get("/publish", response_class=HTMLResponse)
def publish_page(request: Request, db=Depends(get_db)):
    user, redir = gate(request, db)
    if redir:
        return redir
    return page(request, db, "publish.html", can_publish=security.can_publish(user),
                path=str(publish.DEFAULT_PATH))


@app.post("/publish")
def do_publish(request: Request, db=Depends(get_db), csrf: str = Form("")):
    user, redir = gate(request, db)
    if redir:
        return redir
    security.check_csrf(request, csrf)
    if not security.can_publish(user):
        return RedirectResponse("/publish", status_code=303)
    data = publish.write_catalogue(db)
    n = sum(len(sub["resources"]) for s in data["semesters"] for sub in s["subjects"])
    log(db, "catalogue", 0, "publish", user.id, f"{n} resources")
    db.commit()
    return page(request, db, "publish.html", can_publish=True, path=str(publish.DEFAULT_PATH),
                published=n)
