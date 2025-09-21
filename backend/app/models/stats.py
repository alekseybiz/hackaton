from sqlalchemy import Integer, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DailyRegionStats(Base):
    __tablename__ = "daily_region_stats"

    date: Mapped[Date] = mapped_column(Date, primary_key=True)
    region_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flights_cnt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class HourlyRegionStats(Base):
    __tablename__ = "hourly_region_stats"

    hour_ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), primary_key=True)
    region_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flights_cnt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


