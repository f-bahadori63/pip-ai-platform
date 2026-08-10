from sqlalchemy.orm import Session

from app.models.cost.cost import ProjectCost


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


    if not costs:

        return {
            "cost_health": "UNKNOWN",
            "message": "No cost data available"
        }


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


    cost_variance = (
        earned_value - actual_cost
    )


    remaining_cost = (
        planned_cost - actual_cost
    )


    if cost_variance < 0:

        health = "RED"

    elif cost_variance < planned_cost * 0.1:

        health = "YELLOW"

    else:

        health = "GREEN"



    return {

        "planned_cost": planned_cost,

        "actual_cost": actual_cost,

        "earned_value": earned_value,

        "remaining_cost": remaining_cost,

        "cost_variance": cost_variance,

        "cost_health": health

    }