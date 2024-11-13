from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_current_user
from services.database_service import get_db
from services.dashboard_service import count_vehicles_service, get_vehicles_with_non_final_status_count_service, get_vehicle_registrations_by_date_service

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
    prefix="/api/dashboard",
    tags=["Dashbaord"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)



@router.get(
    "/vehicles/count",
    summary="Obtener el número de vehículos",
    description="Obtiene el número total de vehículos en el sistema.",
)
async def get_vehicle_count(db: Session = Depends(get_db)):
    try:
        count = await count_vehicles_service(db)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado.")


@router.get(
    "/vehicles/non-final-status",
    summary="Obtener vehículos con estados no finales",
    description="Recupera una lista de vehículos cuyo estado no es final.",
)
async def get_vehicles_in_process_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        count = await get_vehicles_with_non_final_status_count_service(db=db)
        return {"count": count}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR
        )



@router.get(
    "/vehicles/registrations-by-date",
    response_model=List[Dict[str, int]],
    summary="Obtener registros de vehículos por fecha",
    description="Devuelve el número de vehículos registrados por fecha.",
)
async def get_vehicle_registrations_by_date(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        registrations = await get_vehicle_registrations_by_date_service(db=db)
        return registrations
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=UNEXPECTED_ERROR
        )