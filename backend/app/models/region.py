from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from app.db.base import Base


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    okato: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    polygon = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)


