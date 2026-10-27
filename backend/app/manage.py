"""Staff account management.

Accounts are **never seeded**, so a fresh install cannot come up with a known password.
Create the administrator here instead. Run from the `backend/` directory:

    python -m app.manage create-admin --email you@example.com
    python -m app.manage set-password --email you@example.com
    python -m app.manage list-users

Passwords are typed at a hidden prompt (or piped with --password-stdin) and are never echoed,
logged, or written to a file.
"""
import argparse
import getpass
import sys

from .db import SessionLocal, engine
from .models import Base, User
from .security import hash_password

MIN_LENGTH = 10


def _read_password(args) -> str:
    if args.password_stdin:
        pw = sys.stdin.readline().rstrip("\n")
    else:
        pw = getpass.getpass("New password ")
        if getpass.getpass("Repeat password ") != pw:
            sys.exit("Passwords do not match.")
    if len(pw) < MIN_LENGTH:
        sys.exit(f"Use at least {MIN_LENGTH} characters.")
    return pw


def cmd_create_admin(args) -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.role == "super_admin").count():
            sys.exit("A super admin already exists. Reset it with: set-password --email <that address>")
        if db.query(User).filter(User.email == args.email).first():
            sys.exit(f"{args.email} already exists. Use set-password instead.")
        db.add(User(name=args.name, email=args.email,
                    password_hash=hash_password(_read_password(args)),
                    role="super_admin", department_id=None))
        db.commit()
        print(f"Created super admin: {args.email}")
    finally:
        db.close()


def cmd_set_password(args) -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            sys.exit(f"No account for {args.email}. Create the first one with create-admin.")
        user.password_hash = hash_password(_read_password(args))
        db.commit()
        print(f"Password updated for {args.email}")
    finally:
        db.close()


def cmd_list_users(args) -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.role, User.email).all()
        if not users:
            print("No accounts yet. Create the first one:")
            print("  python -m app.manage create-admin --email you@example.com")
            return
        for u in users:
            dept = getattr(getattr(u, "department", None), "code", None) or "-"
            flag = "" if u.active else "  (inactive)"
            print(f"{u.role:<12} {u.email:<40} {u.name}  [{dept}]{flag}")
    finally:
        db.close()


def main() -> None:
    p = argparse.ArgumentParser(prog="python -m app.manage", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("create-admin", help="create the first super admin")
    a.add_argument("--email", required=True)
    a.add_argument("--name", default="Super Admin")
    a.add_argument("--password-stdin", action="store_true", help="read the password from stdin")
    a.set_defaults(func=cmd_create_admin)

    b = sub.add_parser("set-password", help="reset an account's password")
    b.add_argument("--email", required=True)
    b.add_argument("--password-stdin", action="store_true")
    b.set_defaults(func=cmd_set_password)

    c = sub.add_parser("list-users", help="list accounts")
    c.set_defaults(func=cmd_list_users)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
