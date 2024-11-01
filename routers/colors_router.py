# routers/colors.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import schemas
from services.colors_service import get_color, add_color, update_color, delete_color, fetch_all_colors
from dependencies import get_current_user
from services.database_service import get_db

router = APIRouter(
    prefix="/api/colors",
    tags=["Colors"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)

@router.post(
    "",
    response_model=schemas.Color,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo color",
    description="Crea un nuevo color en la base de datos.",
)
async def create_color(
    color: schemas.ColorCreate,
    db: Session = Depends(get_db),
):
    new_color = await add_color(color=color, db=db)
    return new_color


@router.get(
    "/{color_id}",
    response_model=schemas.Color,
    summary="Obtener un color",
    description="Obtiene un color específico por su ID.",
)
async def read_color(
    color_id: int,
    db: Session = Depends(get_db),
):
    color = await get_color(db=db, color_id=color_id)
    if color is None:
        raise HTTPException(status_code=404, detail="Color not found.")
    return color


@router.put(
    "/{color_id}",
    response_model=schemas.Color,
    summary="Actualizar un color",
    description="Actualiza los datos de un color existente.",
)
async def modify_color(
    color_id: int,
    color: schemas.ColorCreate,
    db: Session = Depends(get_db),
):
    updated_color = await update_color(db=db, color_id=color_id, color_data=color)
    if updated_color is None:
        raise HTTPException(status_code=404, detail="Color not found.")
    return updated_color


@router.delete(
    "/{color_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un color",
    description="Elimina un color existente de la base de datos.",
)
async def remove_color(
    color_id: int,
    db: Session = Depends(get_db),
):
    success = await delete_color(db=db, color_id=color_id)
    if not success:
        raise HTTPException(status_code=404, detail="Color not found.")
    return {"detail": "Color successfully deleted."}


@router.get(
    "",
    response_model=List[schemas.Color],
    summary="Obtener todos los colores",
    description="Devuelve una lista de todos los colores disponibles.",
)
async def get_all_colors(
    db: Session = Depends(get_db),
):
    try:
        colors = await fetch_all_colors(db=db)  # Llama a la función de servicio renombrada
        return colors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los colores."
        ) from e
