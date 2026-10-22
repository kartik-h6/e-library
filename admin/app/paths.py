"""Locate the shared catalogue.

The admin app is designed to live inside the e-library repository at `admin/`,
next to the static site's `data/catalogue.json`. It also runs standalone (e.g.
from the scaffold zip), in which case it falls back to a local `data/` folder.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # the admin/ folder


def _candidates():
    for base in (BASE_DIR, BASE_DIR.parent, BASE_DIR.parent.parent):
        yield base / "data" / "catalogue.json"


def _pick(env_var: str) -> Path:
    env = os.environ.get(env_var)
    if env:
        return Path(env)
    for p in _candidates():
        if p.exists():
            return p
    return BASE_DIR / "data" / "catalogue.json"


def catalogue_src() -> Path:
    """Where the seed catalogue is read from."""
    return _pick("CATALOGUE_SRC")


def publish_path() -> Path:
    """Where the published catalogue is written to (the static site's data file)."""
    return _pick("PUBLISH_PATH")
