from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_current_user
from services.database_service import get_db
from services.vehicle_types_service import create_vehicle_type_service, get_all_vehicle_types_service, get_vehicle_type_service, update_vehicle_type_service, delete_vehicle_type_service


router = APIRouter(
    prefix="/api/vehicle/types",
    tags=["Vehicle Types"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)


@router.post("", response_model=schemas.VehicleType, status_code=201, summary="Crear un nuevo tipo de vehículo", description="Crea un nuevo tipo de vehículo si no existe.")
async def create_vehicle_type(
    vehicle_type: schemas.VehicleTypeCreate,
    db: Session = Depends(get_db)
):
    # Comprobar si el tipo de vehículo ya existe
    existing_type = db.query(models.VehicleType).filter(models.VehicleType.type_name == vehicle_type.type_name).first()
    
    if existing_type:
        raise HTTPException(status_code=409, detail="Vehicle type already exists")
    
    try:
        return await create_vehicle_type_service(vehicle_type=vehicle_type, db=db)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Vehicle type already exists")

@router.get("", response_model=List[schemas.VehicleType], summary="Obtener todos los tipos de vehículos")
async def get_vehicle_types(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    vehicle_types = await get_all_vehicle_types_service(db=db, skip=skip, limit=limit)
    return vehicle_types

@router.get("/{vehicle_type_id}", response_model=schemas.VehicleType, summary="Obtener un tipo de vehículo por ID")
async def get_vehicle_type(
    vehicle_type_id: int, 
    db: Session = Depends(get_db)
):
    vehicle_type = await get_vehicle_type_service(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise HTTPException(status_code=404, detail="Vehicle type does not exist")

    return vehicle_type

@router.delete("/{vehicle_type_id}", status_code=204, summary="Eliminar un tipo de vehículo")
async def delete_vehicle_type(
    vehicle_type_id: int, 
    db: Session = Depends(get_db)
):
    vehicle_type = await get_vehicle_type_service(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise HTTPException(status_code=404, detail="Vehicle type does not exist")

    await delete_vehicle_type_service(vehicle_type_id, db=db)
    
    return {"detail": "Vehicle type successfully deleted"}

@router.put("/{vehicle_type_id}", response_model=schemas.VehicleType, summary="Actualizar un tipo de vehículo")
async def update_vehicle_type(
    vehicle_type_id: int,
    vehicle_type_data: schemas.VehicleTypeCreate,
    db: Session = Depends(get_db)
):
    # Verificar si el nuevo nombre ya existe en otro registro
    existing_type = db.query(models.VehicleType).filter(
        models.VehicleType.type_name == vehicle_type_data.type_name,
        models.VehicleType.id != vehicle_type_id
    ).first()
    if existing_type:
        raise HTTPException(status_code=409, detail="Vehicle type already exists")
    
    vehicle_type = await get_vehicle_type_service(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise HTTPException(status_code=404, detail="Vehicle type does not exist")

    return await update_vehicle_type_service(
        vehicle_type_data=vehicle_type_data, vehicle_type_id=vehicle_type_id, db=db
    )