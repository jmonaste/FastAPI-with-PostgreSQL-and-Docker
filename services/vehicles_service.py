from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional
from services.states_management_service import register_state_history



async def create_vehicle(
    vehicle: _schemas.VehicleCreate, db: "Session", user_id: int
) -> _schemas.Vehicle:
    
     # Obtener el estado inicial desde la base de datos
    initial_state = db.query(_models.State).filter_by(is_initial=True).first()

    if not initial_state:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No initial state configured in the system."
        )

    # Agregar el estado inicial a los datos del vehículo
    vehicle_data = vehicle.model_dump(exclude_unset=True)
    vehicle_data.update({"status_id": initial_state.id})

    # Crear el modelo de vehículo
    vehicle_model = _models.Vehicle(
        **vehicle_data,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(vehicle_model)
    db.commit()
    db.refresh(vehicle_model)

    # Registrar el estado inicial en el historial
    await register_state_history(
        vehicle_id=vehicle_model.id,
        from_state_id=None,  # No hay estado previo ya que es el primer estado
        to_state_id=vehicle_model.status_id,  # Estado inicial
        user_id=user_id,
        db=db,
        comment_id=None
    )

    return _schemas.Vehicle.model_validate(vehicle_model)

async def get_vehicle(db: "Session", vehicle_id: int):
    return db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()

async def get_vehicles(
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

async def update_vehicle(db: "Session", vehicle_id: int, vehicle: _schemas.VehicleCreate):
    db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        return None

    # Verificar si el VIN ya existe en otro vehículo
    if vehicle.vin != db_vehicle.vin:
        existing_vehicle = db.query(_models.Vehicle).filter(
            _models.Vehicle.vin == vehicle.vin
        ).first()
        if existing_vehicle:
            raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists.")

    # Verificar si el modelo existe
    existing_model = db.query(_models.Model).filter(_models.Model.id == vehicle.vehicle_model_id).first()
    if not existing_model:
        raise HTTPException(status_code=404, detail="Vehicle model not found.")

    # Actualizar los campos
    db_vehicle.vehicle_model_id = vehicle.vehicle_model_id
    db_vehicle.vin = vehicle.vin
    db_vehicle.color_id = vehicle.color_id
    db_vehicle.is_urgent = vehicle.is_urgent

    try:
        db.commit()
        db.refresh(db_vehicle)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists.")

    return db_vehicle

async def delete_vehicle(db: "Session", vehicle_id: int):
    db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()

    if not db_vehicle:
        return False
    
    # Borrar el historial de estados asociado al vehículo
    db.query(_models.StateHistory).filter(_models.StateHistory.vehicle_id == vehicle_id).delete()

    # Borrar el vehículo
    db.delete(db_vehicle)
    db.commit()
    return {"detail": "Vehicle successfully deleted"}


