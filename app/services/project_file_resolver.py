"""Resolve an upload target project from the uploaded filename."""

from __future__ import annotations

import re
import unicodedata
from pathlib import PurePosixPath

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project


def project_name_from_filename(filename: str) -> str:
    """Return a readable project name from a browser-supplied filename.

    The extension is removed and underscores/hyphens are converted to spaces.
    Original letter casing and Unicode project names are preserved.
    """

    safe_path = str(filename or "").replace("\\", "/")
    basename = PurePosixPath(safe_path).name
    stem = basename.rsplit(".", 1)[0] if "." in basename else basename
    name = re.sub(r"[_-]+", " ", stem)
    name = re.sub(r"\s+", " ", name).strip()

    if not name:
        raise ValueError("Could not derive a project name from the filename")

    return name


def _project_code_base(project_name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", project_name).encode(
        "ascii", "ignore"
    ).decode("ascii")
    code = re.sub(r"[^A-Za-z0-9]+", "-", ascii_name).strip("-").upper()
    return (code or "PROJECT")[:50]


def _unique_project_code(db: Session, project_name: str) -> str:
    base = _project_code_base(project_name)
    candidate = base
    counter = 2

    while db.query(Project.id).filter(Project.project_code == candidate).first():
        suffix = f"-{counter}"
        candidate = f"{base[: 50 - len(suffix)]}{suffix}"
        counter += 1

    return candidate


def resolve_project_from_filename(
    db: Session,
    filename: str,
) -> tuple[Project, bool]:
    """Find a case-insensitive name match or create a pending project row.

    The caller owns the transaction. A successful schedule import commits the
    new project and its imported data atomically; failed validation can roll
    the pending project back.
    """

    project_name = project_name_from_filename(filename)

    existing = (
        db.query(Project)
        .filter(func.lower(func.trim(Project.name)) == project_name.lower())
        .order_by(Project.id)
        .first()
    )

    if existing is not None:
        return existing, False

    project = Project(
        project_code=_unique_project_code(db, project_name),
        name=project_name,
        status="Planning",
    )
    db.add(project)
    db.flush()

    return project, True


def project_resolution_payload(project: Project, created: bool) -> dict:
    return {
        "id": project.id,
        "project_code": project.project_code,
        "name": project.name,
        "created": created,
        "resolved_from": "filename",
    }
