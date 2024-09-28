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




# Eliminar, no sirven estos servicios para nada
async def create_contact(
    contact: _schemas.CreateContact, db: "Session"
) -> _schemas.Contact:
    contact = _models.Contact(**contact.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return _schemas.Contact.from_orm(contact)

async def get_all_contacts(db: "Session") -> List[_schemas.Contact]:
    contacts = db.query(_models.Contact).all()
    return list(map(_schemas.Contact.from_orm, contacts))

async def get_contact(contact_id: int, db: "Session"):
    contact = db.query(_models.Contact).filter(_models.Contact.id == contact_id).first()
    return contact

async def delete_contact(contact: _models.Contact, db: "Session"):
    db.delete(contact)
    db.commit()

async def update_contact(
    contact_data: _schemas.CreateContact, contact: _models.Contact, db: "Session"
) -> _schemas.Contact:
    contact.first_name = contact_data.first_name
    contact.last_name = contact_data.last_name
    contact.email = contact_data.email
    contact.phone_number = contact_data.phone_number

    db.commit()
    db.refresh(contact)

    return _schemas.Contact.from_orm(contact)





# Brand Functions
async def create_brand(
    brand: _schemas.BrandCreate, db: "Session"
) -> _schemas.Brand:
    brand_model = _models.Brand(**brand.dict())
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
    model_obj = _models.Model(**model.dict())
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
async def create_vehicle(
    vehicle: _schemas.VehicleCreate, db: "Session"
) -> _schemas.Vehicle:
    vehicle_model = _models.Vehicle(**vehicle.dict())
    db.add(vehicle_model)
    db.commit()
    db.refresh(vehicle_model)
    return _schemas.Vehicle.from_orm(vehicle_model)

async def get_all_vehicles(db: "Session") -> List[_schemas.Vehicle]:
    vehicles = db.query(_models.Vehicle).all()
    return list(map(_schemas.Vehicle.from_orm, vehicles))

async def get_vehicle(vehicle_id: int, db: "Session") -> _schemas.Vehicle:
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if vehicle:
        return _schemas.Vehicle.from_orm(vehicle)
    return None

async def delete_vehicle(vehicle_id: int, db: "Session") -> bool:
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if vehicle:
        db.delete(vehicle)
        db.commit()
        return True
    return False

async def update_vehicle(
    vehicle_data: _schemas.VehicleBase, vehicle_id: int, db: "Session"
) -> _schemas.Vehicle:
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if vehicle:
        vehicle.model_id = vehicle_data.model_id
        vehicle.vehicle_type_id = vehicle_data.vehicle_type_id

        db.commit()
        db.refresh(vehicle)
        return _schemas.Vehicle.from_orm(vehicle)
    return None
