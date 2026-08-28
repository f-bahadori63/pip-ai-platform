from sqlalchemy.orm import Session

from app.models.cost.cost import ProjectCost
from app.models.project import Project
from app.services.ai.schedule_analyzer import analyze_project_schedule
from app.services.evm_engine import compute_evm


def calculate_cost_kpis(
    db: Session,
    project_id: int
):

    costs = (
        db.query(ProjectCost)
        .filter(
            ProjectCost.project_id == project_id
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

    planned_cost = sum(
        c.planned_cost or 0
        for c in costs
    )

    actual_cost = sum(
        c.actual_cost or 0
        for c in costs
    )

    earned_value = sum(
        c.earned_value or 0
        for c in costs
    )

    if not costs and not schedule_data:

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

    budget_source = "project_costs"

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

        "evm": evm,

    }
