from app.services.ai.ollama_client import generate


def _fallback_summary(dashboard_data):
    """
    Deterministic dashboard summary.

    Contract:
    - accepts dict
    - accepts Pydantic/BaseModel objects
    - preserves existing dashboard KPI values
    """

    # --------------------------------------------------------
    # Normalize input contract
    # --------------------------------------------------------

    if hasattr(dashboard_data, "model_dump"):
        data = dashboard_data.model_dump()

    elif isinstance(dashboard_data, dict):
        data = dashboard_data

    elif hasattr(dashboard_data, "dict"):
        data = dashboard_data.dict()

    else:
        raise TypeError(
            "dashboard_data must be a dict or Pydantic model"
        )

    # --------------------------------------------------------
    # Extract dashboard fields
    # --------------------------------------------------------

    project_status = data.get(
        "project_status",
        "UNKNOWN"
    )

    progress = data.get(
        "progress",
        {}
    ) or {}

    schedule = data.get(
        "schedule",
        {}
    ) or {}

    cost = data.get(
        "cost",
        {}
    ) or {}

    planned = progress.get(
        "planned_progress",
        progress.get("planned", 0)
    )

    actual = progress.get(
        "actual_progress",
        progress.get("actual", 0)
    )

    variance = progress.get(
        "variance",
        0
    )

    schedule_health = schedule.get(
        "health",
        "UNKNOWN"
    )

    cost_health = cost.get(
        "cost_health",
        cost.get("health", "UNKNOWN")
    )

    critical_count = schedule.get(
        "critical_activities",
        0
    )

    return (
        f"????? ????? {project_status} ???. "
        f"?????? ????????? {planned}% ? "
        f"?????? ????? {actual}% ???? ? "
        f"?????? ?????? {variance}% ???. "
        f"????? ?????? {schedule_health} ? "
        f"????? ????? {cost_health} ??????? ??????. "
        f"{critical_count} ?????? ?????? ??????? ??? ???. "
        f"???? ? ????? ?????? Recovery ???? ????? "
        f"?????????? ?????? ????? ???."
    )


def _compact_dashboard(dashboard_data):
    """
    Normalize DashboardResponse / Pydantic models / dicts
    into a compact plain-dict payload for AI processing.
    """

    # --------------------------------------------------------
    # Pydantic -> dict
    # --------------------------------------------------------

    if hasattr(dashboard_data, "model_dump"):
        dashboard_data = dashboard_data.model_dump()

    elif hasattr(dashboard_data, "dict"):
        dashboard_data = dashboard_data.dict()

    # --------------------------------------------------------
    # Defensive normalization
    # --------------------------------------------------------

    if not isinstance(dashboard_data, dict):
        dashboard_data = {}

    progress = dashboard_data.get(
        "progress",
        {}
    )

    schedule = dashboard_data.get(
        "schedule",
        {}
    )

    cost = dashboard_data.get(
        "cost",
        {}
    )

    alerts = dashboard_data.get(
        "alerts",
        []
    )

    recovery = dashboard_data.get(
        "recovery",
        {}
    )

    # --------------------------------------------------------
    # Nested Pydantic compatibility
    # --------------------------------------------------------

    if hasattr(progress, "model_dump"):
        progress = progress.model_dump()

    elif hasattr(progress, "dict"):
        progress = progress.dict()

    if hasattr(schedule, "model_dump"):
        schedule = schedule.model_dump()

    elif hasattr(schedule, "dict"):
        schedule = schedule.dict()

    if hasattr(cost, "model_dump"):
        cost = cost.model_dump()

    elif hasattr(cost, "dict"):
        cost = cost.dict()

    if hasattr(recovery, "model_dump"):
        recovery = recovery.model_dump()

    elif hasattr(recovery, "dict"):
        recovery = recovery.dict()

    # --------------------------------------------------------
    # COMPACT CONTRACT
    # --------------------------------------------------------

    return {
        "project_status": dashboard_data.get(
            "project_status"
        ),

        "progress": {
            "planned": progress.get(
                "planned_progress",
                progress.get("planned", 0)
            ),
            "actual": progress.get(
                "actual_progress",
                progress.get("actual", 0)
            ),
            "variance": progress.get(
                "variance",
                0
            ),
        },

        "schedule": {
            "health": schedule.get(
                "health",
                "UNKNOWN"
            ),
            "delay_index": schedule.get(
                "delay_index",
                0
            ),
            "critical_activities": schedule.get(
                "critical_activities",
                0
            ),
        },

        "cost": {
            "health": cost.get(
                "cost_health",
                cost.get("health", "UNKNOWN")
            ),
            "planned": cost.get(
                "planned_cost",
                cost.get("planned", 0)
            ),
            "actual": cost.get(
                "actual_cost",
                cost.get("actual", 0)
            ),
            "earned_value": cost.get(
                "earned_value",
                0
            ),
            "variance": cost.get(
                "cost_variance",
                cost.get("variance", 0)
            ),
        },

        "alerts": [
            (
                a.model_dump()
                if hasattr(a, "model_dump")
                else a.dict()
                if hasattr(a, "dict")
                else a
            )
            for a in alerts
        ],

        "recovery": {
            "required": recovery.get(
                "required",
                False
            ),
            "priority": recovery.get(
                "priority",
                "NORMAL"
            ),
        },
    }
def generate_project_summary(
    dashboard_data: dict,
    use_ai: bool = True
) -> str:

    fallback = _fallback_summary(
        dashboard_data
    )

    if not use_ai:
        return fallback

    compact = _compact_dashboard(
        dashboard_data
    )

    prompt = f"""
You are an EPC Project Control Manager.

Analyze this compact project dashboard:

{compact}

Write a concise management summary in formal English.

Rules:
- Maximum 4 sentences.
- Mention project status.
- Mention progress variance.
- Mention schedule health.
- Mention cost health.
- Mention critical activities if applicable.
- Give one clear management priority.
- Do not repeat raw JSON.
- Do not create a recovery plan.
- Do not explain your reasoning.
"""

    try:

        result = generate(
            prompt,
            timeout=12,
            num_predict=50,
            temperature=0.1,
        )

        if result and result.strip():
            return result.strip()

    except Exception:
        pass

    return fallback



