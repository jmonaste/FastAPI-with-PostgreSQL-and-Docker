from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/vehicles",
    tags=["Vehicles"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)




@router.post(
    "/",
    response_model=schemas.Vehicle,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo vehículo",
    description="Crea un nuevo vehículo si no existe.",
)
async def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(services.get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Verificar si el modelo de vehículo existe
    existing_model = db.query(models.Model).filter(models.Model.id == vehicle.vehicle_model_id).first()
    if not existing_model:
        raise HTTPException(status_code=404, detail="Vehicle model not found.")

    try:
        # Crear el vehículo
        new_vehicle = await services.create_vehicle(vehicle=vehicle, db=db, user_id=current_user.id)
        return new_vehicle
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists.")
    

@router.get(
    "/{vehicle_id}",
    response_model=schemas.Vehicle,
    summary="Obtener vehículo por ID",
    description="Recupera un vehículo utilizando su ID.",
)
async def read_vehicle(
    vehicle_id: int, 
    db: Session = Depends(services.get_db)
):
    db_vehicle = await services.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle


@router.get(
    "/",
    response_model=List[schemas.Vehicle],
    summary="Obtener lista de vehículos",
    description="Recupera una lista de vehículos con filtros opcionales.",
)
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    in_progress: bool = None,
    vin: str = None,
    db: Session = Depends(services.get_db)
):
    vehicles = await services.get_vehicles(db=db, skip=skip, limit=limit, in_progress=in_progress, vin=vin)
    return vehicles


@router.put(
    "/{vehicle_id}",
    response_model=schemas.Vehicle,
    summary="Actualizar un vehículo",
    description="Actualiza los detalles de un vehículo específico.",
)
async def update_vehicle(
    vehicle_id: int, 
    vehicle: schemas.VehicleCreate, 
    db: Session = Depends(services.get_db)
):
    db_vehicle = await services.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehículo",
    description="Elimina un vehículo por su ID.",
)
async def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(services.get_db)
):
    success = await services.delete_vehicle(db=db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"detail": "Vehicle successfully deleted"}


