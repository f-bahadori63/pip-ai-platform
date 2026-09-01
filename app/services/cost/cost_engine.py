from sqlalchemy.orm import Session

from app.models.cost.cost import ProjectCost
from app.models.project import Project
from app.services.ai.schedule_analyzer import analyze_project_schedule
from app.services.evm_engine import compute_evm


def calculate_cost_kpis(
    db: Session,
    project_id: int
):

    # --------------------------------------------------------------
    # Cost data priority:
    #   1. Auto-detected from an uploaded cost-loaded schedule
    #      (source="schedule_import") - most current & granular.
    #   2. Manually entered snapshots (source="manual"), summed.
    #   3. Fall back to the project's contract_value as an estimated
    #      budget, driven purely by schedule progress.
    # --------------------------------------------------------------

    auto_cost = (
        db.query(ProjectCost)
        .filter(
            ProjectCost.project_id == project_id,
            ProjectCost.source == "schedule_import",
        )
        .first()
    )

    manual_costs = (
        db.query(ProjectCost)
        .filter(
            ProjectCost.project_id == project_id,
            ProjectCost.source == "manual",
        )
        .all()
    )

    # Schedule progress is the EVM driver: EVM is derived on read from
    # the project's schedule analysis + entered cost data.
    schedule_analysis = analyze_project_schedule(
        db,
        project_id
    )

    schedule_data = (
        schedule_analysis.get(
            "schedule_data",
            []
        )
        or []
    )

    if auto_cost is not None:

        planned_cost = auto_cost.planned_cost or 0
        actual_cost = auto_cost.actual_cost or 0
        earned_value = auto_cost.earned_value or 0
        cost_source = "schedule_import"

    else:

        planned_cost = sum(
            c.planned_cost or 0
            for c in manual_costs
        )

        actual_cost = sum(
            c.actual_cost or 0
            for c in manual_costs
        )

        earned_value = sum(
            c.earned_value or 0
            for c in manual_costs
        )

        cost_source = "manual" if manual_costs else None

    if (
        auto_cost is None
        and not manual_costs
        and not schedule_data
    ):

        return {
            "cost_health": "UNKNOWN",
            "message": "No cost data available",
            "evm": compute_evm(
                [],
                None,
            ),
        }

    cost_variance = (
        earned_value - actual_cost
    )

    remaining_cost = (
        planned_cost - actual_cost
    )

    if cost_variance < 0:

        health = "RED"

    elif (
        planned_cost
        and cost_variance < planned_cost * 0.1
    ):

        health = "YELLOW"

    else:

        health = "GREEN"

    budget = (
        planned_cost
        if planned_cost > 0
        else None
    )

    # Maps the internal cost row provenance to the label the EVM
    # engine/UI use for "where did the budget number come from".
    budget_source = {
        "schedule_import": "schedule_import",
        "manual": "project_costs",
        None: "project_costs",
    }[cost_source]

    if not budget:

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id
            )
            .first()
        )

        if project and project.contract_value:

            budget = project.contract_value

            budget_source = "contract_value"

    evm = compute_evm(
        schedule_data,
        budget,
        actual_cost=actual_cost,
        budget_source=budget_source,
    )

    return {

        "planned_cost": planned_cost,

        "actual_cost": actual_cost,

        "earned_value": earned_value,

        "remaining_cost": remaining_cost,

        "cost_variance": cost_variance,

        "cost_health": health,

        "cost_source": cost_source,

        "evm": evm,

    }
