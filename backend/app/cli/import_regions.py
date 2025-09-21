"""CLI: импорт полигонов регионов РФ из GeoJSON.

Usage:
    python -m app.cli.import_regions path/to/regions.geojson
"""

import json
import sys
from sqlalchemy import delete, text
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.region import Region


def run(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with Session(engine) as db:
        db.execute(delete(Region))
        for feature in data["features"]:
            props = feature.get("properties", {})
            name = props.get("name") or props.get("NAME") or props.get("region")
            okato = props.get("okato") or props.get("OKATO")
            geom = json.dumps(feature["geometry"])  # GeoJSON string
            db.execute(
                text(
                    """
                    INSERT INTO region (name, okato, polygon)
                    VALUES (:name, :okato, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))
                    """
                ),
                {"name": name, "okato": okato, "geom": geom},
            )
        db.commit()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli.import_regions path/to/regions.geojson")
        sys.exit(1)
    run(sys.argv[1])


