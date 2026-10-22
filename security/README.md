# security/

Independent security and release checks for the repository. This is the lane the
Security Reviewer / Release Validator runs.

## Run it

```bash
python3 security/check.py
```

Exit code `0` = all checks passed; `1` = something failed. It runs on every pull request via
`.github/workflows/security.yml`.

## What it checks

| Check | Why it matters |
|---|---|
| No secrets in tracked files | API keys, tokens and private keys must never be committed. |
| `.env`, `*.db` and `uploads/` are ignored | Local state and secrets stay out of the repository. |
| The frontend ships no credentials | The static site must never carry a password (ADR-003). |
| `catalogue.json` validates against `schema.json` | Bad catalogue data cannot reach the published site. |
| Catalogue is 8 semesters / 88 subjects | Guards against an accidental structural regression. |
| Backend smoke tests pass | Login, roles, workflow, publish, student access and upload still work. |

## Manual checks it cannot do

- **Authorisation is server-side.** Confirm every new admin route uses `gate_staff` and that
  permissions come from `security.py` — never from the browser.
- **No client-side gate.** The frontend must not implement a login.
- **Rollback path.** Before a release, record the previous good commit SHA and confirm it can be
  redeployed.

See `docs/TEAM_AND_RELEASE_PROCESS.md` for the full release checklist.
