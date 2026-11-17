
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from routing.pipeline import route_post

router = APIRouter(
    prefix="/api/v1",
    tags=["Routing"],
)


@router.post("/posts/{post_id}/route")
def trigger_routing(
    post_id: str,
    db: Session = Depends(get_db),
):
    try:
        return route_post(db, post_id)

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Routing failed: {str(error)}",
        )
