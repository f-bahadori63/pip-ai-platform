"""PIP AI Platform - Project Analysis Script.

Runs the full management-intelligence analysis for a project directly
against the database (no web server required):

    1. WBS   - assures/derives the project WBS from imported activities
    2. EVM   - computes Earned Value from schedule progress + costs
    3. Report - schedule health, alerts, recovery recommendations

Usage (from the project root, with the project virtualenv active):

    python scripts/analyze_project.py --project-id 1
    python scripts/analyze_project.py --project-id 1 --json
    python scripts/analyze_project.py --list-projects

The script is idempotent: it never duplicates WBS items or cost rows.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database.session import SessionLocal  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.services.analysis_service import run_project_analysis  # noqa: E402

SEPARATOR = "=" * 62


def _money(value, currency: str = "IRR") -> str:
    if value is None:
        return "N/A"

    return f"{value:,.0f} {currency}"


def _pct(value, suffix_digits: int = 1) -> str:
    if value is None:
        return "N/A"

    return f"{value:.{suffix_digits}f}%"


def _num(value, digits: int = 2) -> str:
    if value is None:
        return "N/A"

    return f"{value:,.{digits}f}"


def _health_color(status: str | None) -> str:
    value = (status or "").upper()

    if value in ("RED", "CRITICAL"):
        return "\033[91m"  # red

    if value in ("YELLOW", "WARNING", "NO_BASELINE"):
        return "\033[93m"  # yellow

    return "\033[92m"  # green


def _reset() -> str:
    return "\033[0m"


def print_report(report: dict, use_color: bool = True) -> None:
    project = report["project"]
    evm = report["evm"] or {}
    schedule = report["schedule"] or {}
    wbs = report["wbs"] or {}
    alerts = report["alerts"] or []
    recovery = report["recovery"] or {}

    color = _health_color if use_color else (lambda _: lambda: "")
    end = _reset() if use_color else ""

    print(SEPARATOR)
    print("PIP AI PLATFORM - MANAGEMENT INTELLIGENCE REPORT")
    print(SEPARATOR)

    print(f"\nProject : {project.get('code', '')} - {project.get('name', '')}")
    print(f"Client  : {project.get('client') or 'N/A'}")
    print(
        f"Budget  : {_money(project.get('contract_value'), project.get('currency') or 'IRR')}"
    )
    print(f"Analysis: {report.get('generated_at', '')}")

    print("\n--- 1) WBS (Work Breakdown Structure) -----------------------")
    print(f"Total WBS items : {wbs.get('total_items', 0)}")
    print(f"Auto-created    : {wbs.get('created', 0)}")
    print(f"Activities linked: {wbs.get('linked_activities', 0)}")

    for item in wbs.get("items", []) or []:
        print(
            f"  [{item.get('code')}] {item.get('name')}"
            f"  ({item.get('activity_count', 0)} activities)"
        )

    if not wbs.get("items"):
        print("  (no WBS items - upload a schedule first)")

    print("\n--- 2) SCHEDULE HEALTH -------------------------------------")
    status = schedule.get("health", "UNKNOWN")
    print(f"Health      : {color(status)}{status}{end}")
    print(f"Total       : {schedule.get('total_activities', 0)} activities")
    print(f"Planned     : {_pct(schedule.get('planned_progress'))}")
    print(f"Actual      : {_pct(schedule.get('actual_progress'))}")
    print(f"Variance    : {_pct(schedule.get('variance'))}")
    print(f"Delay index : {_num(schedule.get('delay_index'))}")
    print(f"Critical    : {schedule.get('critical_activities', 0)}")

    print("\n--- 3) EVM (Earned Value Management) ------------------------")
    evm_status = evm.get("status")
    print(f"Status      : {color(evm_status)}{evm_status or 'N/A'}{end}")

    if evm.get("message"):
        print(f"Note        : {evm['message']}")

    print(f"Progress    : planned {_pct(evm.get('planned_progress'))}"
          f" / actual {_pct(evm.get('actual_progress'))}")
    print(
        f"BAC         : {_money(evm.get('bac'), project.get('currency') or 'IRR')}"
        f"  (source: {evm.get('budget_source', 'N/A')})"
    )
    print(f"PV          : {_money(evm.get('pv'), project.get('currency') or 'IRR')}")
    print(f"EV          : {_money(evm.get('ev'), project.get('currency') or 'IRR')}")
    print(f"AC          : {_money(evm.get('ac'), project.get('currency') or 'IRR')}")
    print(f"SV          : {_money(evm.get('sv'), project.get('currency') or 'IRR')}")
    print(f"SPI         : {_num(evm.get('spi'))}")
    print(f"CV          : {_money(evm.get('cv'), project.get('currency') or 'IRR')}")
    print(f"CPI         : {_num(evm.get('cpi'))}")
    print(f"EAC         : {_money(evm.get('eac'), project.get('currency') or 'IRR')}")
    print(f"ETC         : {_money(evm.get('etc'), project.get('currency') or 'IRR')}")
    print(f"VAC         : {_money(evm.get('vac'), project.get('currency') or 'IRR')}")
    print(f"TCPI        : {_num(evm.get('tcpi'))}")

    print("\n--- 4) ALERTS ------------------------------------------------")
    if alerts:
        for alert in alerts:
            print(f"  [{alert.get('level')}] {alert.get('title')}: {alert.get('message')}")
    else:
        print("  (no active alerts)")

    print("\n--- 5) RECOVERY ----------------------------------------------")
    if recovery.get("required"):
        print(f"Priority    : {recovery.get('priority') or 'N/A'}")
        print(f"Plan        : {recovery.get('recommendation') or 'N/A'}")
    else:
        print("  (no recovery action required)")

    print(SEPARATOR)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="PIP project analysis: WBS + EVM + management report.",
    )

    parser.add_argument(
        "--project-id",
        type=int,
        default=1,
        help="Project id to analyze (default: 1)",
    )

    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="List existing projects and exit",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw analysis payload as JSON",
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        if args.list_projects:
            projects = db.query(Project).order_by(Project.id).all()

            print("Existing projects:")

            for project in projects:
                print(
                    f"  {project.id}  {project.project_code}  {project.name}"
                )

            return 0

        if args.json:
            report = run_project_analysis(db, args.project_id)
            print(json.dumps(report, ensure_ascii=False, indent=2))

            return 0

        report = run_project_analysis(db, args.project_id)
        print_report(report)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
