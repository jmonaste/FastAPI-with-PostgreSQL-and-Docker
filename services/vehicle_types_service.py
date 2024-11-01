from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from datetime import datetime, timezone
from fastapi import HTTPException



async def create_vehicle_type_service(
    vehicle_type: _schemas.VehicleTypeCreate, db: "Session"
) -> _schemas.VehicleType:
    
    # Validar que el nombre no esté vacío o solo contenga espacios en blanco
    if not vehicle_type.type_name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    

    vehicle_type_model = _models.VehicleType(
        **vehicle_type.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
        )
    
    db.add(vehicle_type_model)
    db.commit()
    db.refresh(vehicle_type_model)
    return _schemas.VehicleType.model_validate(vehicle_type_model)

async def get_all_vehicle_types_service(db: "Session", skip: int = 0, limit: int = 10) -> List[_schemas.VehicleType]:
    vehicle_types = db.query(_models.VehicleType).offset(skip).limit(limit).all()
    return list(map(_schemas.VehicleType.model_validate, vehicle_types))


async def get_vehicle_type_service(vehicle_type_id: int, db: "Session") -> _schemas.VehicleType:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        return _schemas.VehicleType.model_validate(vehicle_type)
    return None

async def delete_vehicle_type_service(vehicle_type_id: int, db: "Session") -> bool:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        db.delete(vehicle_type)
        db.commit()
        return True
    return False

async def update_vehicle_type_service(
    vehicle_type_data: _schemas.VehicleTypeBase, vehicle_type_id: int, db: "Session"
) -> _schemas.VehicleType:
    
    # Validar que el nuevo nombre no esté vacío o solo contenga espacios en blanco
    if not vehicle_type_data.type_name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        vehicle_type.type_name = vehicle_type_data.type_name
        db.commit()
        db.refresh(vehicle_type)
        return _schemas.VehicleType.model_validate(vehicle_type)
    return None


