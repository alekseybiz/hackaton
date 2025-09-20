from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.region import Region


router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/regions")
def list_regions(db: Session = Depends(get_db)):
    rows = db.execute(select(Region.id, Region.name, Region.okato)).all()
    return [
        {"id": r.id, "name": r.name, "okato": r.okato}
        for r in rows
    ]


