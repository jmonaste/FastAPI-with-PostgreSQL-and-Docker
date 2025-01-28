from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException, status
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError


async def add_color(color: _schemas.ColorCreate, db: "Session") -> _schemas.Color:
    color_data = color.model_dump(exclude_unset=True)
    color_model = _models.Color(
        **color_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    try:
        db.add(color_model)
        db.commit()
        db.refresh(color_model)
    except IntegrityError as e:
        db.rollback()
        # Inspeccionar el objeto de excepción para determinar qué restricción falló
        if hasattr(e.orig, 'args') and len(e.orig.args) > 0:
            error_message = e.orig.args[0]
            if 'uq_colors_name' in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Color with this name already exists."
                )
            elif 'uq_colors_hex_code' in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Color with this hex_code already exists."
                )
        # Si no se puede determinar la restricción, lanzar un error genérico
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error."
        )

    return _schemas.Color.model_validate(color_model)

async def get_color(db: "Session", color_id: int) -> _schemas.Color:
    color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not color:
        raise HTTPException(status_code=404, detail="Color not found")
    return _schemas.Color.model_validate(color)

async def update_color(db: Session, color_id: int, color_data: _schemas.ColorCreate) -> _schemas.Color:
    db_color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found.")

    db_color.name = color_data.name
    db_color.hex_code = color_data.hex_code
    db_color.rgb_code = color_data.rgb_code
    db_color.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(db_color)
    except IntegrityError as e:
        db.rollback()
        if hasattr(e.orig, 'args') and len(e.orig.args) > 0:
            error_message = e.orig.args[0]
            if 'uq_colors_name' in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Color with this name already exists."
                )
            elif 'uq_colors_hex_code' in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Color with this hex_code already exists."
                )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integrity error."
        )

    return _schemas.Color.model_validate(db_color)

async def delete_color(db: "Session", color_id: int) -> bool:
    db_color = db.query(_models.Color).filter(_models.Color.id == color_id).first()
    if not db_color:
        raise HTTPException(status_code=404, detail="Color not found")

    db.delete(db_color)
    db.commit()
    return True

async def fetch_all_colors(db: "Session", skip: int = 0, limit: int = 10) -> List[_models.Color]:
    colors = db.query(_models.Color).offset(skip).limit(limit).all()
    return list(map(_schemas.Color.model_validate, colors))

async def get_color_id_by_name_service(db: Session, color_name: str) -> int:
    color = db.query(_models.Color).filter(_models.Color.name == color_name).first()
    if not color:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Color not found")
    return color.id







