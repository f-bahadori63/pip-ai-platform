"""Project analysis orchestrator for PIP AI Platform.

Runs after a schedule upload (or on demand) and produces the
management intelligence package used by the Dashboard / WBS / Cost
sections:

    1. WBS  - derive/assure the project WBS from imported activities
    2. EVM  - compute Earned Value from schedule progress + cost data
    3. Report - schedule health, alerts, recovery + management summary

Deterministic first: every value here is derived from PostgreSQL data
already validated by the import pipeline. AI is only consulted through
the existing project-control-center path (with rule-engine fallback).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.schedule import ScheduleActivity
from app.models.wbs import WBSItem
from app.services.ai.project_control_center import build_project_control_center
from app.services.dashboard_service import build_dashboard_response
from app.services.evm_engine import compute_evm


def _derive_wbs_prefix(activity_code: str) -> str | None:
    """Derive a deterministic WBS package code from an activity code.

    Examples:
        "1.2.3"    -> "1.2"      (dotted numeric hierarchy)
        "1.2"      -> "1"
        "ENG-001"  -> "ENG"      (letters + numeric suffix)
        "ENG_001"  -> "ENG"
        "ENG001"   -> "ENG"
        "A.12"     -> "A"
        "1001"     -> None       (no hierarchy information)
    """

    code = (activity_code or "").strip()

    if not code:
        return None

    if re.fullmatch(r"\d+(\.\d+)+", code):
        parts = code.split(".")
        return ".".join(parts[:-1]) if len(parts) > 1 else None

    match = re.match(r"^([A-Za-z][A-Za-z0-9]*?)[\-_.]*\d+$", code)

    if match:
        prefix = match.group(1).strip("._-")

        if prefix:
            return prefix.upper()

    match = re.match(r"^([A-Za-z]+)$", code)

    if match:
        return match.group(1).upper()

    return None


def ensure_project_wbs(
    db: Session,
    project_id: int,
) -> dict:
    """Assure WBS items exist for the project and link activities to them.

    Existing items are never modified. Activities that already carry a
    ``wbs_id`` are only counted; activities without one are linked to the
    derived package (a new ``wbs_items`` row when missing).
    """

    existing = {
        item.code: item
        for item in (
            db.query(WBSItem)
            .filter(WBSItem.project_id == project_id)
            .all()
        )
    }

    activities = (
        db.query(ScheduleActivity)
        .filter(ScheduleActivity.project_id == project_id)
        .all()
    )

    created = 0
    linked = 0
    activity_count_by_code: dict[str, int] = {}

    for activity in activities:

        if activity.wbs_id is not None:

            item = (
                db.query(WBSItem)
                .filter(
                    WBSItem.id == activity.wbs_id,
                    WBSItem.project_id == project_id,
                )
                .first()
            )

            if item is not None:
                activity_count_by_code[item.code] = (
                    activity_count_by_code.get(item.code, 0) + 1
                )

            continue

        prefix = _derive_wbs_prefix(
            activity.activity_code
        )

        if not prefix:
            continue

        item = existing.get(prefix)

        if item is None:

            item = WBSItem(
                project_id=project_id,
                parent_id=None,
                code=prefix,
                name=prefix,
                level=1,
            )

            db.add(item)
            db.flush()

            existing[prefix] = item

            created += 1

        activity.wbs_id = item.id
        linked += 1

        activity_count_by_code[prefix] = (
            activity_count_by_code.get(prefix, 0) + 1
        )

    items = (
        db.query(WBSItem)
        .filter(WBSItem.project_id == project_id)
        .order_by(WBSItem.code)
        .all()
    )

    tree = [
        {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "parent_id": item.parent_id,
            "level": item.level,
            "activity_count": activity_count_by_code.get(
                item.code,
                0,
            ),
        }
        for item in items
    ]

    return {
        "created": created,
        "linked_activities": linked,
        "total_items": len(items),
        "items": tree,
    }


def _evm_summary(control: dict) -> dict:
    costs = control.get("costs", {}) or {}

    evm = costs.get("evm") or {}

    if evm:
        return evm

    # Fallback: compute EVM directly when the control-center path did
    # not include it (defensive; cost engine now always provides it).
    schedule = control.get("schedule", {}) or {}
    schedule_data = schedule.get("schedule_data", []) or []

    project_costs = costs.get("planned_cost") or 0.0

    return compute_evm(
        schedule_data,
        budget=project_costs or None,
        actual_cost=costs.get("actual_cost") or 0.0,
    )


def run_project_analysis(
    db: Session,
    project_id: int,
) -> dict:
    """Full project analysis: WBS + EVM + management report."""

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:
        raise ValueError(f"Project {project_id} not found")

    wbs = ensure_project_wbs(
        db,
        project_id,
    )

    control = build_project_control_center(
        db,
        project_id,
    )

    dashboard = build_dashboard_response(
        project_id,
        control,
    ).model_dump()

    evm = _evm_summary(
        control
    )

    db.commit()

    kpis = control.get("kpis", {}) or {}

    alerts = dashboard.get("alerts", []) or []

    recovery = dashboard.get("recovery", {}) or {}

    schedule = control.get("schedule", {}) or {}

    schedule_data = schedule.get("schedule_data", []) or []

    return {
        "project_id": project_id,
        "generated_at": datetime.now(
            UTC
        ).isoformat(),
        "project": {
            "code": project.project_code,
            "name": project.name,
            "client": project.client,
            "contract_value": project.contract_value,
            "currency": project.currency,
        },
        "wbs": wbs,
        "evm": evm,
        "schedule": {
            "health": kpis.get(
                "schedule_health",
                "UNKNOWN",
            ),
            "planned_progress": kpis.get(
                "planned_progress",
            ),
            "actual_progress": kpis.get(
                "actual_progress",
            ),
            "variance": kpis.get(
                "schedule_variance",
            ),
            "delay_index": dashboard.get(
                "schedule",
                {},
            ).get("delay_index"),
            "critical_activities": kpis.get(
                "critical_activities",
                0,
            ),
            "total_activities": len(
                schedule_data
            ),
        },
        "alerts": alerts,
        "recovery": recovery,
    }
