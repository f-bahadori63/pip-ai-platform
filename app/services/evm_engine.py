"""Earned Value Management (EVM) engine for PIP AI Platform.

Deterministic, derived-on-read engine: EVM values are always computed
from schedule progress and cost data already present in PostgreSQL.
The engine never writes to the database.

Standard EVM relationships used here:

    PV   = BAC * planned_progress / 100
    EV   = BAC * actual_progress  / 100
    SV   = EV - PV        SPI = EV / PV        (guard: PV > 0)
    CV   = EV - AC        CPI = EV / AC        (guard: AC > 0)
    EAC  = BAC / CPI      ETC = EAC - AC       VAC = BAC - EAC
    TCPI = (BAC - EV) / (BAC - AC)             (guard: BAC != AC)

Projects are compared on the weighted average (by duration_days) of
activity progress, exactly like the schedule-control KPI layer.
"""

from __future__ import annotations

from typing import Any


def _weighted_mix(
    schedule_data: list[dict[str, Any]],
) -> tuple[float | None, float | None]:
    """Weighted (by duration) average planned/actual progress (%).

    Activities without a usable duration receive equal weight (1.0) so
    that progress-only rows still contribute to the project average.
    """

    total_weight = 0.0
    weighted_planned = 0.0
    weighted_actual = 0.0
    rows = 0

    for item in schedule_data or []:
        planned = item.get("planned_progress")
        actual = item.get("actual_progress")

        if planned is None and actual is None:
            continue

        if planned is None:
            planned = actual

        if actual is None:
            actual = planned

        try:
            weight = float(item.get("duration_days") or 0)
        except (TypeError, ValueError):
            weight = 0.0

        if weight <= 0:
            weight = 1.0

        total_weight += weight
        weighted_planned += float(planned or 0.0) * weight
        weighted_actual += float(actual or 0.0) * weight
        rows += 1

    if rows == 0 or total_weight <= 0:
        return None, None

    return (
        round(weighted_planned / total_weight, 2),
        round(weighted_actual / total_weight, 2),
    )


def compute_evm(
    schedule_data: list[dict[str, Any]],
    budget: float | None,
    actual_cost: float | None = None,
    budget_source: str = "project_costs",
) -> dict[str, Any]:
    """Compute the EVM bundle for a project.

    :param schedule_data: schedule analysis rows (``planned_progress``,
        ``actual_progress``, ``duration_days``, ...).
    :param budget: Budget At Completion (BAC). ``None`` when unknown.
    :param actual_cost: Actual Cost (AC) entered so far.
    :param budget_source: provenance of the budget value.
    """

    planned_pct, actual_pct = _weighted_mix(schedule_data)

    result: dict[str, Any] = {
        "planned_progress": planned_pct,
        "actual_progress": actual_pct,
        "budget_source": budget_source,
        "bac": round(float(budget), 2) if budget is not None else None,
        "ac": round(float(actual_cost or 0.0), 2),
    }

    if planned_pct is None:
        result["status"] = "no_schedule"
        result["message"] = (
            "No schedule activities available for EVM calculation. "
            "Upload a schedule first."
        )
        return result

    if not budget or budget <= 0:
        result["status"] = "no_budget"
        result["message"] = (
            "No budget data available. Enter planned cost in the Cost "
            "section or set the project contract value."
        )
        return result

    bac = float(budget)
    ac = float(actual_cost or 0.0)

    pv = bac * planned_pct / 100.0
    ev = bac * actual_pct / 100.0

    sv = round(ev - pv, 2)
    spi = round(ev / pv, 4) if pv > 0 else None

    cv = round(ev - ac, 2)
    cpi = round(ev / ac, 4) if ac and ac > 0 else None

    eac = round(bac / cpi, 2) if cpi else None
    etc = round(eac - ac, 2) if eac is not None else None
    vac = round(bac - eac, 2) if eac is not None else None
    tcpi = round((bac - ev) / (bac - ac), 4) if bac != ac else None

    if pv <= 0:
        status = "NO_BASELINE"
    else:
        status = "GREEN"

        if spi is not None and spi < 0.9:
            status = "RED"
        elif spi is not None and spi < 1.0:
            status = "YELLOW"

    if cpi is not None and cpi < 1.0:
        status = "RED" if cpi < 0.9 else "YELLOW"

    result.update(
        {
            "status": status,
            "pv": round(pv, 2),
            "ev": round(ev, 2),
            "sv": sv,
            "spi": spi,
            "cv": cv,
            "cpi": cpi,
            "eac": eac,
            "etc": etc,
            "vac": vac,
            "tcpi": tcpi,
        }
    )

    return result
