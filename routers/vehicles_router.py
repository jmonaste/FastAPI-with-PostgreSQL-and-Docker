from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_current_user
from services.database_service import get_db
from services.vehicles_service import create_vehicle_service, get_vehicles_service, update_vehicle_service, delete_vehicle_service, get_vehicle_by_id_service

from services.exceptions import (
    VehicleNotFound,
    VehicleModelNotFound,
    VINAlreadyExists,
    InvalidVIN,
    ColorNotFound,
    InitialStateNotFound
)
from constants.exceptions import (
    VEHICLE_MODEL_NOT_FOUND,
    VIN_ALREADY_EXISTS,
    VEHICLE_NOT_FOUND,
    INVALID_VIN,
    UNEXPECTED_ERROR
)





router = APIRouter(
    prefix="/api/vehicles",
    tags=["Vehicles"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)


@router.post(
    "",
    response_model=schemas.Vehicle,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo vehículo",
    description="Crea un nuevo vehículo si no existe.",
)
async def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        new_vehicle = await create_vehicle_service(vehicle=vehicle, db=db, user_id=current_user.id)
        return new_vehicle
    except VehicleModelNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ColorNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InitialStateNotFound as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=VIN_ALREADY_EXISTS)
    except Exception as e:
        # Manejo de errores inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado.")
    

@router.get(
    "/{vehicle_id}",
    response_model=schemas.Vehicle,
    summary="Obtener vehículo por ID",
    description="Recupera un vehículo utilizando su ID.",
)
async def read_vehicle(
    vehicle_id: int, 
    db: Session = Depends(get_db)
):
    db_vehicle = await get_vehicle_by_id_service(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail=VEHICLE_NOT_FOUND)
    return db_vehicle


@router.get(
    "",
    response_model=List[schemas.Vehicle],
    summary="Obtener lista de vehículos",
    description="Recupera una lista de vehículos con filtros opcionales.",
)
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    in_progress: bool = None,
    vin: str = None,
    db: Session = Depends(get_db)
):
    vehicles = await get_vehicles_service(db=db, skip=skip, limit=limit, in_progress=in_progress, vin=vin)
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
    db: Session = Depends(get_db)
):
    """
    Endpoint to update an existing vehicle. Validates input and delegates the update to the service.
    """
    try:
        updated_vehicle = await update_vehicle_service(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
        return updated_vehicle
    except VehicleNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except VehicleModelNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except VINAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidVIN as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=VIN_ALREADY_EXISTS)
    except Exception:
        # Handle unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=UNEXPECTED_ERROR)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehículo",
    description="Elimina un vehículo por su ID.",
)
async def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(get_db)
):
    success = await delete_vehicle_service(db=db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"detail": "Vehicle successfully deleted"}


