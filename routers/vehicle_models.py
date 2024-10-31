from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/models",
    tags=["Models"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)



@router.post(
    "/",
    response_model=schemas.Model,
    status_code=201,
    summary="Crear un nuevo modelo",
    description="Crea un nuevo modelo si no existe para la marca especificada."
)
async def create_model(
    model: schemas.ModelCreate,
    db: Session = Depends(services.get_db)
):
    # Comprobar si el modelo ya existe
    existing_model = db.query(models.Model).filter(
        models.Model.name == model.name, 
        models.Model.brand_id == model.brand_id
    ).first()
    
    if existing_model:
        raise HTTPException(status_code=409, detail="Model already exists for this brand")

    # Llamar a la función de servicio para crear el modelo
    return await services.create_model(model=model, db=db)


@router.get(
    "/",
    response_model=List[schemas.Model],
    summary="Obtener todos los modelos",
    description="Recupera una lista de todos los modelos disponibles."
)
async def getmodels(
    db: Session = Depends(services.get_db)              
):
    return await services.get_allmodels(db=db)


@router.get(
    "/{model_id}",
    response_model=schemas.Model,
    summary="Obtener un modelo por ID",
    description="Recupera un modelo específico utilizando su ID."
)
async def get_model(
    model_id: int, 
    db: Session = Depends(services.get_db)
):
    model = await services.get_model(db=db, model_id=model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model does not exist")

    return model


@router.delete(
    "/{model_id}",
    status_code=204,
    summary="Eliminar un modelo",
    description="Elimina un modelo existente."
)
async def delete_model(
    model_id: int, 
    db: Session = Depends(services.get_db)
):
    model = await services.get_model(db=db, model_id=model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model does not exist")

    await services.delete_model(model_id, db=db)
    
    return {"detail": "Model successfully deleted"}



@router.put(
    "/{model_id}",
    response_model=schemas.Model,
    summary="Actualizar un modelo",
    description="Actualiza la información de un modelo existente."
)
async def update_model(
    model_id: int, 
    model: schemas.ModelCreate, 
    db: Session = Depends(services.get_db)
):
    try:
        updated_model = await services.update_model(model_id, model, db)
        return updated_model
    except HTTPException as e:
        raise e

