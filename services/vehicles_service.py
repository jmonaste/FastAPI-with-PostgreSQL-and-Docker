from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional, Union
from services.states_management_service import register_state_history_service
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
    COLOR_NOT_FOUND,
    INITIAL_STATE_NOT_FOUND,
    VEHICLE_NOT_FOUND,
    VIN_ALREADY_EXISTS,
    INVALID_VIN
)


async def create_vehicle_service(
    vehicle: _schemas.VehicleCreate, db: Session, user_id: int
) -> _schemas.Vehicle:
    """
    Servicio para crear un nuevo vehículo. Realiza todas las validaciones necesarias
    y maneja la lógica de negocio asociada.
    """

    # Verificar si el modelo de vehículo existe
    existing_model = db.query(_models.Model).filter(_models.Model.id == vehicle.vehicle_model_id).first()
    if not existing_model:
        raise VehicleModelNotFound(VEHICLE_MODEL_NOT_FOUND)

    # Verificar si existe el color en el sistema
    color = db.query(_models.Color).filter(_models.Color.id == vehicle.color_id).first()
    if not color:
        raise ColorNotFound(COLOR_NOT_FOUND)

    # Obtener el estado inicial desde la base de datos
    initial_state = db.query(_models.State).filter_by(is_initial=True).first()
    if not initial_state:
        raise InitialStateNotFound(INITIAL_STATE_NOT_FOUND)

    # Agregar el estado inicial a los datos del vehículo
    vehicle_data = vehicle.model_dump(exclude_unset=True)
    vehicle_data.update({"status_id": initial_state.id})

    # Crear la instancia del vehículo
    vehicle_model = _models.Vehicle(
        **vehicle_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Agregar y confirmar la transacción
    db.add(vehicle_model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise  # Será manejado en el endpoint

    db.refresh(vehicle_model)

    # Registrar el estado inicial en el historial
    await register_state_history_service(
        vehicle_id=vehicle_model.id,
        from_state_id=None,  # No hay estado previo ya que es el primer estado
        to_state_id=vehicle_model.status_id,  # Estado inicial
        user_id=user_id,
        db=db,
        comment_id=None
    )

    return _schemas.Vehicle.model_validate(vehicle_model)

async def get_vehicle_by_id_service(db: Session, vehicle_id: int):
    vehicle = (
        db.query(_models.Vehicle)
        .join(_models.State, _models.Vehicle.status_id == _models.State.id)
        .filter(_models.Vehicle.id == vehicle_id)
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=VEHICLE_NOT_FOUND)
    return _schemas.Vehicle.model_validate(vehicle)

async def get_vehicles_service(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    in_progress: Optional[bool] = None,
    vin: Optional[str] = None
):
    # Iniciamos la consulta con un join al modelo State
    query = db.query(_models.Vehicle).join(_models.State, _models.Vehicle.status_id == _models.State.id)
    
    if in_progress is not None:
        if in_progress:
            # Filtrar vehículos que NO están en un estado final (is_final == False)
            query = query.filter(_models.State.is_final == False)
        else:
            # Filtrar vehículos que están en un estado final (is_final == True)
            query = query.filter(_models.State.is_final == True)
    
    if vin:
        query = query.filter(_models.Vehicle.vin.ilike(f"%{vin}%"))
    
    vehicles = query.offset(skip).limit(limit).all()
    return list(map(_schemas.Vehicle.model_validate, vehicles))

async def update_vehicle_service(db: Session, vehicle_id: int, vehicle: _schemas.VehicleUpdate):
    # Fetch the vehicle to update
    db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        raise VehicleNotFound(VEHICLE_NOT_FOUND)
    
    # Validate VIN is not empty or null
    if vehicle.vin is None or vehicle.vin.strip() == "":
        raise InvalidVIN(INVALID_VIN)
    
    # Check if the VIN is being changed
    if vehicle.vin != db_vehicle.vin:
        existing_vehicle = db.query(_models.Vehicle).filter(
            _models.Vehicle.vin == vehicle.vin
        ).first()
        if existing_vehicle:
            raise VINAlreadyExists(VIN_ALREADY_EXISTS)
    
    # Verify if the vehicle model exists
    existing_model = db.query(_models.Model).filter(_models.Model.id == vehicle.vehicle_model_id).first()
    if not existing_model:
        raise VehicleModelNotFound(VEHICLE_MODEL_NOT_FOUND)
    
    # Update the vehicle fields
    db_vehicle.vehicle_model_id = vehicle.vehicle_model_id
    db_vehicle.vin = vehicle.vin
    db_vehicle.color_id = vehicle.color_id
    db_vehicle.is_urgent = vehicle.is_urgent
    
    try:
        db.commit()
        db.refresh(db_vehicle)
    except IntegrityError:
        db.rollback()
        raise VINAlreadyExists(VIN_ALREADY_EXISTS)
    
    return _schemas.Vehicle.model_validate(db_vehicle)

async def delete_vehicle_service(db: "Session", vehicle_id: int) -> Union[bool, dict]:
    try:
        # Buscar el vehículo por su ID
        db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()

        if not db_vehicle:
            # Si el vehículo no existe, lanzar una excepción HTTP 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=VEHICLE_NOT_FOUND
            )
        
        # Eliminar los registros asociados en StateHistory
        db.query(_models.StateHistory).filter(_models.StateHistory.vehicle_id == vehicle_id).delete()
        
        # Eliminar el vehículo
        db.delete(db_vehicle)
        
        # Confirmar la transacción
        db.commit()
        
        return {"detail": "Vehicle successfully deleted"}
    
    except HTTPException as http_exc:
        # Re-levantar excepciones HTTP para que sean manejadas por el endpoint
        raise http_exc
    
    except Exception as exc:
        # En caso de otros errores, re-levantar una excepción HTTP 500
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the vehicle: {str(exc)}"
        )


