from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException
from datetime import datetime, timezone


async def add_color(color: _schemas.ColorCreate, db: "Session") -> _schemas.Color:
    color_data = color.model_dump(exclude_unset=True)
    color_model = _models.Color(
        **color_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(color_model)
    db.commit()
    db.refresh(color_model)

    return _schemas.Color.model_validate(color_model)

async def get_color(db: "Session", color_id: int) -> _schemas.Color:
    color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color not found")
    return _schemas.Color.model_validate(color)

async def update_color(db: "Session", color_id: int, color_data: _schemas.ColorCreate) -> _schemas.Color:
    db_color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")

    db_color.name = color_data.name
    db_color.hex_code = color_data.hex_code
    db_color.rgb_code = color_data.rgb_code
    db_color.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_color)

    return _schemas.Color.model_validate(db_color)

async def delete_color(db: "Session", color_id: int) -> bool:
    db_color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")

    db.delete(db_color)
    db.commit()
    return True

async def fetch_all_colors(db: "Session") -> List[_models.Color]:
    return db.query(_models.Color).all()

