# Privacy, terms and guardrails

The source of truth for the policies published on the site (`/privacy/`, `/terms/`) and for the
safety rules the project holds itself to.

---

## 1. Privacy

**Students are anonymous.** There are no student accounts, no sign-in, no profile, no tracking
cookie, and no analytics on the public site. Reading the library leaves no trace beyond ordinary
web-server logs.

**What is held**

| Data | Who | Why | Where |
|---|---|---|---|
| Staff name, email, hashed password | staff accounts only | to sign in | backend database |
| Content and its history | the library | to publish and to audit | backend database |
| Standard request logs (IP, path, time) | the host | security and abuse only | host's log retention |

Passwords are hashed with PBKDF2-HMAC-SHA256 and never stored or transmitted in plain text.
There is no personal data about students because none is collected.

**What we do not do**

- No third-party analytics, ads, or trackers.
- No third-party CDN, fonts, or scripts — styles and icons are served locally, so a reader's
  browser talks only to this site.
- No collection of names, phone numbers, marks, attendance, or any student record.
- No selling or sharing of data with anyone.

**Material** lives in a shared Google Drive folder. Google's own terms and privacy policy apply to
that folder; this project stores only links to it.

**Children.** The library is intended for college-level students. It is not directed at children,
and no data is knowingly collected from them.

**Requests.** To ask about or correct anything held, use the Contact page.

---

## 2. Terms of use

- This is an **independent study platform**, not affiliated with or endorsed by the Pharmacy Council of
  India or any college or university.
- The course structure follows the **PCI B.Pharm syllabus 2026 (NEP 2020)** as an *interim source*
  until your institution's official syllabus is supplied and verified. Always check against the official syllabus.
- Material is provided **as-is, without warranty**. Verify anything you rely on — especially for
  exams, clinical work, or anything with real consequences.
- **Contributions:** do not submit copyrighted material you have no right to share, paid coaching
  material, restricted institutional files, or any personal or confidential data.
- The maintainer may edit, move or remove any content, and may suspend access, at any time.
- The maintainer is not liable for any loss arising from use of the site or its material.

---

## 3. Safety and security guardrails

**Authorisation**
- Every staff action is authorised **server-side**, in the route handler. There is no client-side
  gate and no client-side password (ADR-003).
- A department master sees only their own department's subjects plus the shared Common Courses
  pool — never another department's. Verified by test on every change.
- The public API exposes **only published material** and nothing else — no drafts, no accounts, no
  audit data.

**Secrets and configuration**
- No secrets in the repository or its history; everything comes from environment variables.
- `.env`, `*.db` and `uploads/` are gitignored.
- CI (`security/check.py`) scans every pull request for secrets, missing ignores, client-side
  credentials, a broken catalogue and failing tests.

**Content**
- Nothing reaches the public site unless its status is `published`; every change is recorded in the
  `revisions` audit trail.
- Uploads are stored under randomised filenames, never executed, and served as static files.

**Before wide staff use**
- Add rate limiting on `/login` and 2FA for the Super Admin.
- Move uploads to object storage.
- Add a database backup schedule.

**If a credential leaks**
Rotate `SESSION_SECRET`, reset the administrator's credentials with the `app.manage` CLI,
redeploy, and review the audit trail for unexpected writes.

---

## 4. Known limits (stated plainly)

- The **public site is open to anyone**. The library is not gated; that is a deliberate choice
  (students are anonymous), so treat everything published as public.
- Anything in the **Drive folder is effectively public** if the folder is shared "anyone with the
  link" — which it must be for students to open the files.
- The backend is a **scaffold**: no rate limiting or 2FA yet, SQLite by default, local file
  uploads. Fine for a pilot; harden it before it holds anything sensitive.
- There is **no guarantee of availability**. If the backend sleeps or fails, students still see
  the static site.
