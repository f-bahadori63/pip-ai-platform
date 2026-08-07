from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.services.ai.project_control_center import (
    build_project_control_center
)

from app.services.dashboard_service import (
    build_dashboard_response
)

from app.services.dashboard_contract_mapper import (
    map_dashboard_contract
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/project/{project_id}"
)
def project_dashboard(
    project_id: int,
    db: Session = Depends(get_db)
):

    control_data = build_project_control_center(
        db,
        project_id
    )


    dashboard = build_dashboard_response(
        project_id,
        control_data
    )


    return dashboard



@router.get("/executive/{project_id}")
def executive_dashboard(
    project_id: int,
    db: Session = Depends(get_db)
):

    print("STEP 1")

    control_data = build_project_control_center(
        db,
        project_id
    )

    print("STEP 2 CONTROL CENTER DONE")

    dashboard_data = build_dashboard_response(
        project_id,
        control_data
    )

    print("STEP 3 DASHBOARD RESPONSE DONE")

    result = map_dashboard_contract(
        dashboard_data.model_dump()
    )

    print("STEP 4 MAPPING DONE")

    return result