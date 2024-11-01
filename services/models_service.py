from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException
from datetime import datetime, timezone

async def create_model(
    model: _schemas.ModelCreate, db: "Session"
) -> _schemas.Model:
    # Verificar si la marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with ID {model.brand_id} does not exist.")
    
    # Si la marca existe, continuar con la creación del modelo
    model_obj = _models.Model(
        **model.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
        )
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return _schemas.Model.model_validate(model_obj)

async def get_all_models(db: "Session") -> List[_schemas.Model]:
    models = db.query(_models.Model).all()
    return list(map(_schemas.Model.model_validate, models))

async def get_model(model_id: int, db: "Session") -> _schemas.Model:
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        return _schemas.Model.model_validate(model)
    return None

async def delete_model(model_id: int, db: "Session") -> bool:
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        db.delete(model)
        db.commit()
        return True
    return False

async def update_model(model_id: int, model: _schemas.ModelCreate, db: "Session"):
    existing_model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    
    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Verificar si la marca existe
    if not db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first():
        raise HTTPException(status_code=404, detail="Brand not found")

    for key, value in model.model_dump(exclude_unset=True).items():
        setattr(existing_model, key, value)

    db.commit()
    db.refresh(existing_model)
    return existing_model



