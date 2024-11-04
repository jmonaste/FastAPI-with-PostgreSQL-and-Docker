from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional
from services.exceptions import StateNotFoundException, StateCommentsNotFoundException
from constants.exceptions import STATE_NOT_FOUND, STATE_COMMENT_NOT_FOUND





async def register_state_history_service(
    vehicle_id: int, 
    from_state_id: int, 
    to_state_id: int, 
    user_id: int, 
    db: "Session",
    comment_id: int
):
    state_history_entry = _models.StateHistory(
        vehicle_id=vehicle_id,
        from_state_id=from_state_id,
        to_state_id=to_state_id,
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
        comment_id=comment_id
    )

    db.add(state_history_entry)
    db.commit()
    db.refresh(state_history_entry)

async def get_allowed_transitions_for_vehicle_service(vehicle_id: int, db: Session) -> List[_schemas.Transition]:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    # Obtener las transiciones permitidas desde el estado actual del vehículo
    allowed_transitions = db.query(_models.Transition).filter(
        _models.Transition.from_state_id == vehicle.status_id
    ).all()

    return [_schemas.Transition.model_validate(transition) for transition in allowed_transitions]

async def get_all_states_service(db: Session) -> List[_schemas.State]:
    states = db.query(_models.State).all()
    return [ _schemas.State.model_validate(state) for state in states ]

async def get_vehicle_state_history_service(vehicle_id: int, db: Session) -> List[_schemas.StateHistory]:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("El vehículo no existe.")

    # Obtener el historial de estados del vehículo
    state_history = db.query(_models.StateHistory).filter(
        _models.StateHistory.vehicle_id == vehicle_id
    ).order_by(_models.StateHistory.timestamp).all()

    return [_schemas.StateHistory.model_validate(entry) for entry in state_history]

async def get_vehicle_current_state_service(db: Session, vehicle_id: int) -> _schemas.State:
    # Obtener el vehículo de la base de datos
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="El vehículo no existe.")

    # Obtener el estado actual del vehículo
    state = db.query(_models.State).filter(_models.State.id == vehicle.status_id).first()
    if not state:
        raise HTTPException(status_code=500, detail="El estado del vehículo no está configurado.")

    return _schemas.State.model_validate(state)

async def change_vehicle_state_service(
    vehicle_id: int,
    new_state_id: int,
    user_id: int,
    db: Session,
    comment_id: Optional[int] = None
) -> _schemas.StateHistory:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("El vehículo no existe.")

    # Obtener el nuevo estado
    new_state = db.query(_models.State).filter(_models.State.id == new_state_id).first()
    if not new_state:
        raise ValueError("El nuevo estado no existe.")

    # Verificar si la transición es válida
    valid_transition = db.query(_models.Transition).filter(
        _models.Transition.from_state_id == vehicle.status_id,
        _models.Transition.to_state_id == new_state_id
    ).first()

    if not valid_transition:
        raise ValueError("La transición al nuevo estado no es válida.")

    # Si se proporciona un comment_id, validar que existe y está asociado al nuevo estado
    if comment_id is not None:
        comment = db.query(_models.StateComment).filter(
            _models.StateComment.id == comment_id,
            _models.StateComment.state_id == new_state_id
        ).first()
        if not comment:
            raise ValueError("El comentario proporcionado no es válido para el estado seleccionado.")
    else:
        comment = None

    # Actualizar el estado del vehículo
    vehicle.status_id = new_state_id
    vehicle.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(vehicle)

    # Crear una nueva entrada en el historial de estados
    state_history_entry = _models.StateHistory(
        vehicle_id=vehicle_id,
        from_state_id=valid_transition.from_state_id,
        to_state_id=valid_transition.to_state_id,
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
        comment_id=comment.id if comment else None
    )
    db.add(state_history_entry)
    db.commit()
    db.refresh(state_history_entry)

    return _schemas.StateHistory.model_validate(state_history_entry)

async def get_state_comments_service(state_id: int, db: Session) -> List[_schemas.StateCommentRead]:
    """
    Obtiene los comentarios predefinidos para un estado específico.
    """
    # Verificar si el estado existe
    state = db.query(_models.State).filter(_models.State.id == state_id).first()
    if not state:
        raise StateNotFoundException(STATE_NOT_FOUND)
    
    # Obtener los comentarios asociados al estado
    comments = db.query(_models.StateComment).filter(_models.StateComment.state_id == state_id).all()
    
    if not comments:
        raise StateCommentsNotFoundException(STATE_COMMENT_NOT_FOUND)
    
    return [_schemas.StateCommentRead.model_validate(comment) for comment in comments]




