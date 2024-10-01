from typing import TYPE_CHECKING, List
from sqlalchemy.exc import IntegrityError
import database as _database
import models as _models
import schemas as _schemas
from fastapi import HTTPException
from datetime import datetime

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()








# Brand Functions
async def create_brand(
    brand: _schemas.BrandCreate, db: "Session"
) -> _schemas.Brand:
    brand_model = _models.Brand(
        **brand.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    db.add(brand_model)
    db.commit()
    db.refresh(brand_model)
    return _schemas.Brand.from_orm(brand_model)

async def get_all_brands(db: "Session") -> List[_schemas.Brand]:
    brands = db.query(_models.Brand).all()
    return list(map(_schemas.Brand.from_orm, brands))

async def get_brand(brand_id: int, db: "Session") -> _schemas.Brand:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        return _schemas.Brand.from_orm(brand)
    return None

async def delete_brand(brand_id: int, db: "Session") -> bool:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        db.delete(brand)
        db.commit()
        return True
    return False

async def update_brand(
    brand_data: _schemas.BrandBase, brand_id: int, db: "Session"
) -> _schemas.Brand:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        brand.name = brand_data.name

        db.commit()
        db.refresh(brand)
        return _schemas.Brand.from_orm(brand)
    return None


# Model Functions
async def create_model(
    model: _schemas.ModelCreate, db: "Session"
) -> _schemas.Model:
    # Verificar si la marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with ID {model.brand_id} does not exist.")
    
    # Si la marca existe, continuar con la creación del modelo
    model_obj = _models.Model(
        **model.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return _schemas.Model.from_orm(model_obj)

async def get_all_models(db: "Session") -> List[_schemas.Model]:
    models = db.query(_models.Model).all()
    return list(map(_schemas.Model.from_orm, models))

async def get_model(model_id: int, db: "Session") -> _schemas.Model:
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        return _schemas.Model.from_orm(model)
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

    for key, value in model.dict(exclude_unset=True).items():
        setattr(existing_model, key, value)

    db.commit()
    db.refresh(existing_model)
    return existing_model


# VehicleType Functions
async def create_vehicle_type(
    vehicle_type: _schemas.VehicleTypeCreate, db: "Session"
) -> _schemas.VehicleType:
    vehicle_type_model = _models.VehicleType(
        **vehicle_type.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    
    db.add(vehicle_type_model)
    db.commit()
    db.refresh(vehicle_type_model)
    return _schemas.VehicleType.from_orm(vehicle_type_model)

async def get_all_vehicle_types(db: "Session") -> List[_schemas.VehicleType]:
    vehicle_types = db.query(_models.VehicleType).all()
    return list(map(_schemas.VehicleType.from_orm, vehicle_types))

async def get_vehicle_type(vehicle_type_id: int, db: "Session") -> _schemas.VehicleType:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        return _schemas.VehicleType.from_orm(vehicle_type)
    return None

async def delete_vehicle_type(vehicle_type_id: int, db: "Session") -> bool:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        db.delete(vehicle_type)
        db.commit()
        return True
    return False

async def update_vehicle_type(
    vehicle_type_data: _schemas.VehicleTypeBase, vehicle_type_id: int, db: "Session"
) -> _schemas.VehicleType:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        vehicle_type.type_name = vehicle_type_data.type_name

        db.commit()
        db.refresh(vehicle_type)
        return _schemas.VehicleType.from_orm(vehicle_type)
    return None


# Vehicle Functions
