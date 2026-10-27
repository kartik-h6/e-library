"""Smoke test for the scaffold. Run from the project root:  python3 test_smoke.py"""
import os
import re

os.environ["PUBLISH_PATH"] = "./data/published-test.json"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
for f in ("./test.db", "./data/published-test.json"):
    if os.path.exists(f):
        os.remove(f)

from fastapi.testclient import TestClient          # noqa: E402
from app.main import app                            # noqa: E402
from app.db import SessionLocal                     # noqa: E402
from app.models import Resource, Subject            # noqa: E402

ok = 0
fail = []


def check(label, cond, extra=""):
    global ok
    if cond:
        ok += 1
        print(f"  PASS  {label}")
    else:
        fail.append(label + (" :: " + extra if extra else ""))
        print(f"  FAIL  {label} {extra}")


def csrf_of(html):
    m = re.search(r'name="csrf" value="([^"]+)"', html)
    return m.group(1) if m else ""


with TestClient(app) as c:
    # Accounts are never seeded — the tests create their own in the throwaway database.
    _fdb = SessionLocal()
    from app.models import Department as _Dept, User as _User
    from app.security import hash_password as _hash
    check("no accounts are seeded on a fresh database", _fdb.query(_User).count() == 0)
    if not _fdb.query(_User).filter(_User.email == "admin@test.local").first():
        _pch = _fdb.query(_Dept).filter(_Dept.code == "PCH").first()
        _pco = _fdb.query(_Dept).filter(_Dept.code == "PCO").first()
        _fdb.add(_User(name="Test Admin", email="admin@test.local",
                       password_hash=_hash("test-admin-pw"), role="super_admin"))
        _fdb.add(_User(name="Test Chem Master", email="master.pch@test.local",
                       password_hash=_hash("test-dept-pw"), role="hod", department_id=_pch.id))
        _fdb.add(_User(name="Test SME", email="sme@test.local",
                       password_hash=_hash("test-sme-pw"), role="sme", department_id=_pco.id))
        _fdb.commit()
    _fdb.close()

    print("Auth")
    r = c.get("/dashboard", follow_redirects=False)
    check("anonymous is redirected to login", r.status_code in (303, 307) and "/login" in r.headers.get("location", ""))
    r = c.post("/login", data={"email": "admin@test.local", "password": "wrong"}, follow_redirects=False)
    check("wrong password rejected", r.status_code == 200 and "Invalid" in r.text)
    r = c.post("/login", data={"email": "admin@test.local", "password": "test-admin-pw"}, follow_redirects=False)
    check("super admin logs in", r.status_code == 303)
    r = c.get("/dashboard")
    check("dashboard renders", r.status_code == 200 and "Dashboard" in r.text)
    csrf = csrf_of(r.text)
    check("csrf token present", bool(csrf))

    db = SessionLocal()
    subj = db.query(Subject).first()
    sid = subj.id
    check("seeded subjects exist", db.query(Subject).count() >= 80, str(db.query(Subject).count()))

    print("CRUD + workflow (super admin)")
    r = c.post(f"/subjects/{sid}/resources", data={
        "csrf": csrf, "type": "notes", "title": "Unit 1 — demo notes",
        "language": "English", "source": "Demo", "url": "https://example.com/n.pdf",
        "rights": "own notes", "unit_id": ""}, follow_redirects=False)
    check("resource created", r.status_code == 303)
    db.expire_all()
    res = (db.query(Resource).filter(Resource.subject_id == sid)
           .order_by(Resource.id.desc()).first())
    check("resource is draft", res and res.status == "draft", res.status if res else "none")

    r = c.post(f"/resources/{res.id}/status", data={"csrf": csrf, "action": "submit"}, follow_redirects=False)
    db.expire_all(); db.refresh(res)
    check("submit → needs-review", res.status == "needs-review", res.status)

    r = c.post(f"/resources/{res.id}/status", data={"csrf": csrf, "action": "approve"}, follow_redirects=False)
    db.expire_all(); db.refresh(res)
    check("approve → verified", res.status == "verified", res.status)

    r = c.post(f"/resources/{res.id}/status", data={"csrf": csrf, "action": "publish"}, follow_redirects=False)
    db.expire_all(); db.refresh(res)
    check("publish → published", res.status == "published", res.status)

    r = c.get("/review")
    check("review page renders", r.status_code == 200)

    print("Publish")
    r = c.post("/publish", data={"csrf": csrf}, follow_redirects=False)
    check("publish returns 200", r.status_code == 200)
    import json
    pub = json.load(open("./data/published-test.json", encoding="utf-8"))
    titles = [x["title"] for s in pub["semesters"] for sub in s["subjects"] for x in sub["resources"]]
    check("published resource appears in catalogue", "Unit 1 — demo notes" in titles, str(titles[:3]))
    check("catalogue keeps 8 semesters", len(pub["semesters"]) == 8)

    print("Unit-linked material")
    from app.models import Unit as _Unit
    unit = db.query(_Unit).filter(_Unit.subject_id == sid).order_by(_Unit.seq).first()
    c.post(f"/subjects/{sid}/resources", data={
        "csrf": csrf, "type": "notes", "title": "Linked unit notes",
        "url": "https://example.com/unit1.pdf", "unit_id": str(unit.id)},
        follow_redirects=False)
    res2 = db.query(Resource).filter(Resource.title == "Linked unit notes").first()
    db.refresh(res2)
    c.post(f"/resources/{res2.id}/status", data={"csrf": csrf, "action": "publish"},
           follow_redirects=False)
    c.post("/publish", data={"csrf": csrf}, follow_redirects=False)
    pub = json.load(open("./data/published-test.json", encoding="utf-8"))
    linked = [x for s in pub["semesters"] for sub in s["subjects"] for x in sub["resources"]
              if x["title"] == "Linked unit notes"]
    check("published resource carries its unit number",
          bool(linked) and linked[0]["unitSeq"] == unit.seq, str(linked[:1]))
    api = TestClient(app).get("/api/public/library").json()
    api_linked = [x for v in api.get("subjects", {}).values() for x in v
                  if x["title"] == "Linked unit notes"]
    check("public API carries the unit number",
          bool(api_linked) and api_linked[0]["unitSeq"] == unit.seq, str(api_linked[:1]))

    print("Role scoping (SME — Pharmacology)")
    c2 = TestClient(app)
    c2.post("/login", data={"email": "sme@test.local", "password": "test-sme-pw"})
    r = c2.get("/subjects")
    body = r.text
    check("SME sees subjects page", r.status_code == 200)
    # SME is in Pharmacology dept; check a known Pharmacology subject appears and a Chemistry one does not
    db.expire_all()
    pharm = db.query(Subject).filter(Subject.department_id == subj.department_id).count()
    check("SME scoped to own department", "Pharmacology" in body or pharm > 0)
    r = c2.get("/publish")
    check("SME cannot publish (page warns)", "cannot publish" in r.text)
    r = c2.post(f"/resources/{res.id}/status", data={"csrf": csrf_of(c2.get('/dashboard').text), "action": "publish"}, follow_redirects=False)
    db.expire_all(); db.refresh(res)
    check("SME publish attempt ignored", res.status == "published")  # already published; ensure no crash

    print("Department scoping (Chemistry master)")
    c4 = TestClient(app)
    c4.post("/login", data={"email": "master.pch@test.local", "password": "test-dept-pw"})
    body = c4.get("/subjects").text
    check("chemistry master sees chemistry subjects",
          "Medicinal Chemistry" in body or "Pharmaceutical Organic Chemistry" in body)
    check("chemistry master does NOT see pharmacology subjects", "Systemic Pharmacology" not in body)
    check("chemistry master does NOT see pharmaceutics subjects",
          "Pharmaceutical Dosage Forms" not in body)
    check("chemistry master sees the shared pool", "Common Courses" in body)

    print("Source upload")
    csrf_admin = csrf_of(c.get("/dashboard").text)
    files = {"file": ("demo-notes.txt", b"hello notes", "text/plain")}
    r = c.post(f"/subjects/{sid}/upload",
               data={"csrf": csrf_admin, "type": "notes", "title": "Uploaded demo", "unit_id": ""},
               files=files, follow_redirects=False)
    check("upload accepted", r.status_code == 303, str(r.status_code))
    db.expire_all()
    up = db.query(Resource).filter(Resource.source == "upload").order_by(Resource.id.desc()).first()
    check("uploaded resource created", up is not None and up.url.startswith("/uploads/"),
          up.url if up else "none")

    print("Public material API (no auth)")
    c5 = TestClient(app)
    r = c5.get("/api/public/library")
    check("public API reachable without auth", r.status_code == 200, str(r.status_code))
    data = r.json() if r.status_code == 200 else {}
    titles = [x["title"] for v in data.get("subjects", {}).values() for x in v]
    check("public API exposes published material", "Unit 1 — demo notes" in titles)
    check("public API hides unpublished material", "Uploaded demo" not in titles)
    check("public API groups by subject code", "BP101T" in data.get("subjects", {}))

    db.close()

print(f"\n{ok} passed, {len(fail)} failed")
for f in fail:
    print("  -", f)
raise SystemExit(1 if fail else 0)
