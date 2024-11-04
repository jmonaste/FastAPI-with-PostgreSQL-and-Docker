# routers/vehicle_states.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import models
import schemas
import services
from dependencies import get_current_user
from services.database_service import get_db
from services.states_management_service import (
get_allowed_transitions_for_vehicle_service, 
get_all_states_service, 
get_vehicle_state_history_service, 
get_vehicle_current_state_service, 
change_vehicle_state_service, 
get_state_comments_service)

from services.exceptions import (
    StateNotFoundException,
    StateCommentsNotFoundException
)
from constants.exceptions import (
    STATE_COMMENT_NOT_FOUND,
    STATE_NOT_FOUND,
    INITIAL_STATE_NOT_FOUND
)




router = APIRouter(
    prefix="/api",
    tags=["Vehicle States"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)

@router.get(
    "/vehicles/{vehicle_id}/allowed_transitions",
    response_model=List[schemas.Transition],
    summary="Obtener transiciones permitidas",
    description="Devuelve una lista de transiciones de estado permitidas para un vehículo específico.",
)
async def get_allowed_transitions(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    return await get_allowed_transitions_for_vehicle_service(vehicle_id=vehicle_id, db=db)

@router.get(
    "/states",
    response_model=List[schemas.State],
    summary="Obtener todos los estados",
    description="Devuelve una lista de todos los estados disponibles para los vehículos.",
)
async def get_all_states(
    db: Session = Depends(get_db),
):
    return await get_all_states_service(db=db)

@router.get(
    "/vehicles/{vehicle_id}/state_history",
    response_model=List[schemas.StateHistory],
    summary="Obtener historial de estados del vehículo",
    description="Devuelve el historial de cambios de estado para un vehículo específico.",
)
async def get_vehicle_state_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    state_history = await get_vehicle_state_history_service(vehicle_id=vehicle_id, db=db)
    if not state_history:
        raise HTTPException(status_code=404, detail="Vehicle state history not found.")
    return state_history

@router.get(
    "/vehicles/{vehicle_id}/state",
    response_model=schemas.State,
    summary="Obtener estado actual del vehículo",
    description="Devuelve el estado actual de un vehículo específico.",
)
async def get_vehicle_current_state(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    state = await get_vehicle_current_state_service(db=db, vehicle_id=vehicle_id)
    if not state:
        raise HTTPException(status_code=404, detail="Vehicle state not found.")
    return state

@router.put(
    "/vehicles/{vehicle_id}/state",
    response_model=schemas.StateHistory,
    summary="Cambiar estado del vehículo",
    description="Cambia el estado de un vehículo específico.",
)
async def change_vehicle_state(
    vehicle_id: int,
    state_change: schemas.StateChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        state_history_entry = await change_vehicle_state_service(
            vehicle_id=vehicle_id,
            new_state_id=state_change.new_state_id,
            user_id=current_user.id,
            db=db,
            comment_id=state_change.comment_id,
        )
        return state_history_entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar el estado del vehículo.",
        )

@router.get(
    "/states/{state_id}/comments",
    response_model=List[schemas.StateCommentRead],
    summary="Obtener comentarios de un estado",
    description="Obtiene los comentarios predefinidos para un estado específico.",
)
async def get_state_comments(
    state_id: int,
    db: Session = Depends(get_db),
):

    try:
        comments = await get_state_comments_service(state_id=state_id, db=db)
        return comments
    except StateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except StateCommentsNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Manejo de errores inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado.")