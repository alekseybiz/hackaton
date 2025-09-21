from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.stats import DailyRegionStats, HourlyRegionStats


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(
    region_id: Optional[int] = None,
    from_: Optional[datetime] = Query(default=None, alias="from"),
    to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    q = select(
        func.coalesce(func.sum(DailyRegionStats.flights_cnt), 0).label("flights_cnt"),
        func.coalesce(func.sum(DailyRegionStats.total_duration_sec), 0).label("total_duration_sec"),
        func.coalesce(func.avg(DailyRegionStats.avg_duration_sec), 0).label("avg_duration_sec"),
    )
    if region_id is not None:
        q = q.where(DailyRegionStats.region_id == region_id)
    if from_ is not None:
        q = q.where(DailyRegionStats.date >= from_.date())
    if to is not None:
        q = q.where(DailyRegionStats.date <= to.date())

    row = db.execute(q).one()
    return {
        "flights_cnt": int(row.flights_cnt or 0),
        "total_duration_sec": int(row.total_duration_sec or 0),
        "avg_duration_sec": float(row.avg_duration_sec or 0.0),
    }


@router.get("/time-series")
def time_series(
    region_id: Optional[int] = None,
    interval: str = Query("day", pattern="^(day|hour)$"),
    from_: Optional[datetime] = Query(default=None, alias="from"),
    to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    if interval == "day":
        q = select(
            DailyRegionStats.date.label("ts"),
            DailyRegionStats.flights_cnt,
        )
        if region_id is not None:
            q = q.where(DailyRegionStats.region_id == region_id)
        if from_ is not None:
            q = q.where(DailyRegionStats.date >= from_.date())
        if to is not None:
            q = q.where(DailyRegionStats.date <= to.date())
        q = q.order_by(DailyRegionStats.date)
        rows = db.execute(q).all()
        return [
            {"ts": r.ts.isoformat(), "flights_cnt": int(r.flights_cnt)}
            for r in rows
        ]
    else:
        q = select(
            HourlyRegionStats.hour_ts.label("ts"),
            HourlyRegionStats.flights_cnt,
        )
        if region_id is not None:
            q = q.where(HourlyRegionStats.region_id == region_id)
        if from_ is not None:
            q = q.where(HourlyRegionStats.hour_ts >= from_)
        if to is not None:
            q = q.where(HourlyRegionStats.hour_ts <= to)
        q = q.order_by(HourlyRegionStats.hour_ts)
        rows = db.execute(q).all()
        return [
            {"ts": r.ts.isoformat(), "flights_cnt": int(r.flights_cnt)}
            for r in rows
        ]


