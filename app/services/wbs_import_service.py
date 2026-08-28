"""Build project WBS data from the latest uploaded schedule.

An accepted schedule upload is the source of truth for both schedule activities
and their WBS.  This module replaces (rather than appends to) the WBS belonging
to the selected project and links the newly imported activities to the new
project-scoped database IDs.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Any

from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.schedule import ScheduleActivity
from app.models.wbs import WBSItem


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none", "null"}:
        return None

    # Keep identifier formatting exactly as supplied by Excel. In many WBS
    # conventions ``2.0`` is the level-one package and ``2.1`` is its child;
    # converting ``2.0`` to ``2`` would lose source information.
    return text or None


def derive_wbs_code(activity_code: str | None) -> str | None:
    """Derive a package code when the workbook has no explicit WBS column."""

    code = _clean_text(activity_code)

    if not code:
        return None

    if re.fullmatch(r"\d+(\.\d+)+", code):
        parts = code.split(".")
        return ".".join(parts[:-1]) if len(parts) > 1 else None

    match = re.match(r"^([A-Za-z][A-Za-z0-9]*?)[\-_.]*\d+$", code)

    if match:
        prefix = match.group(1).strip("._-")
        return prefix.upper() if prefix else None

    if re.fullmatch(r"[A-Za-z]+", code):
        return code.upper()

    return None


def _parent_code(
    code: str,
    available_codes: set[str] | None = None,
) -> str | None:
    """Resolve a dotted WBS parent, including the common ``x.0`` style.

    Examples from uploaded schedules:
        2.0 -> None
        2.1 -> 2.0  (when 2.0 exists)
        1.2.3 -> 1.2
    """

    if "." not in code or re.fullmatch(r"[^.]+\.0", code):
        return None

    base = code.rsplit(".", 1)[0].strip()

    if not base:
        return None

    if available_codes:
        if base in available_codes:
            return base

        zero_parent = f"{base}.0"

        if zero_parent in available_codes:
            return zero_parent

    return base


def _level(code: str) -> int:
    if re.fullmatch(r"[^.]+\.0", code):
        return 1

    return code.count(".") + 1


def _natural_code_key(code: str) -> tuple:
    parts = re.split(r"(\d+)", code.lower())
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in parts
        if part != ""
    )


def clear_project_wbs(db: Session, project_id: int) -> int:
    """Delete one project's WBS safely without committing the transaction.

    Legacy imports treated the workbook's ``wbs_id`` as a database primary
    key. That allowed activities or risks belonging to another project to
    reference this project's WBS rows. References are therefore cleared by
    target WBS ID, not only by the referencing row's project ID.
    """

    wbs_ids = [
        item_id
        for (item_id,) in (
            db.query(WBSItem.id)
            .filter(WBSItem.project_id == project_id)
            .all()
        )
    ]

    if not wbs_ids:
        return 0

    db.query(ScheduleActivity).filter(
        ScheduleActivity.wbs_id.in_(wbs_ids)
    ).update(
        {ScheduleActivity.wbs_id: None},
        synchronize_session="fetch",
    )

    db.query(Risk).filter(
        Risk.wbs_item_id.in_(wbs_ids)
    ).update(
        {Risk.wbs_item_id: None},
        synchronize_session="fetch",
    )

    # Break any self-referencing parent links first. This also supports legacy
    # databases where the self foreign key was created with RESTRICT behavior.
    db.query(WBSItem).filter(
        WBSItem.id.in_(wbs_ids)
    ).update(
        {WBSItem.parent_id: None},
        synchronize_session="fetch",
    )

    db.flush()

    deleted = db.query(WBSItem).filter(
        WBSItem.id.in_(wbs_ids)
    ).delete(synchronize_session="fetch")

    db.flush()

    return int(deleted or 0)


def replace_project_wbs_from_schedule(
    db: Session,
    project_id: int,
    normalized_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replace stale WBS rows with data from the latest normalized workbook.

    Preferred workbook fields are ``wbs_code`` and ``wbs_name``.  When no WBS
    code is supplied, a deterministic package code is derived from the
    activity code (for example ``ENG-001`` -> ``ENG``).
    """

    # Preserve insertion order from the uploaded file while collecting enough
    # information to choose a useful name for each package.
    packages: OrderedDict[str, dict[str, Any]] = OrderedDict()
    activity_to_wbs: dict[str, str] = {}

    for row in normalized_rows:
        activity_code = _clean_text(row.get("activity_code"))
        source_wbs_code = _clean_text(
            row.get("wbs_code")
            if row.get("wbs_code") is not None
            else row.get("wbs_id")  # backward-compatible normalized input
        )
        wbs_code = source_wbs_code or derive_wbs_code(activity_code)

        if not wbs_code:
            continue

        package = packages.setdefault(
            wbs_code,
            {
                "explicit_name": None,
                "activity_names": [],
            },
        )

        explicit_name = _clean_text(row.get("wbs_name"))
        activity_name = _clean_text(row.get("activity_name"))

        if explicit_name and not package["explicit_name"]:
            package["explicit_name"] = explicit_name

        if activity_name and activity_name not in package["activity_names"]:
            package["activity_names"].append(activity_name)

        if activity_code:
            activity_to_wbs[activity_code] = wbs_code

    # A dotted child requires its parent to exist. Add missing ancestors, but
    # never invent a descriptive title for them. Codes ending in .0 are
    # treated as level-one packages; for example 2.1 attaches to 2.0 when the
    # uploaded file contains both values.
    source_codes = set(packages)

    for code in list(packages):
        parent = _parent_code(code, source_codes)

        while parent:
            packages.setdefault(
                parent,
                {
                    "explicit_name": None,
                    "activity_names": [],
                },
            )
            source_codes.add(parent)
            parent = _parent_code(parent, source_codes)

    deleted_count = clear_project_wbs(db, project_id)

    code_to_item: dict[str, WBSItem] = {}
    created_count = 0

    ordered_codes = sorted(
        packages,
        key=lambda code: (_level(code), _natural_code_key(code)),
    )

    for code in ordered_codes:
        package = packages[code]
        activity_names = package["activity_names"]
        name = package["explicit_name"]

        # If exactly one activity belongs to a WBS code, its uploaded name is
        # a better label than repeating the code. For shared packages, retain
        # the code unless the workbook provides a dedicated WBS name.
        if not name and len(activity_names) == 1:
            name = activity_names[0]

        if not name:
            name = code

        parent = code_to_item.get(
            _parent_code(code, set(packages)) or ""
        )

        item = WBSItem(
            project_id=project_id,
            parent_id=parent.id if parent else None,
            code=code,
            name=name,
            level=_level(code),
        )

        db.add(item)
        db.flush()

        code_to_item[code] = item
        created_count += 1

    linked_count = 0

    if activity_to_wbs:
        activities = db.query(ScheduleActivity).filter(
            ScheduleActivity.project_id == project_id
        ).all()

        for activity in activities:
            source_code = _clean_text(activity.activity_code)
            wbs_code = activity_to_wbs.get(source_code or "")
            item = code_to_item.get(wbs_code or "")

            if item is not None:
                activity.wbs_id = item.id
                linked_count += 1

    db.flush()

    return {
        "source": "latest_upload",
        "replaced_count": deleted_count,
        "created_count": created_count,
        "linked_activities": linked_count,
        "total_items": created_count,
    }
