# endpoints/models.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_current_user
from services.database_service import get_db
from services.models_service import (
    create_model_service,
    get_all_models_service,
    get_model_service,
    delete_model_service,
    update_model_service,
    get_model_id_by_name_service
)


router = APIRouter(
    prefix="/api/models",
    tags=["Models"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)

@router.post(
    "",
    response_model=schemas.Model,
    status_code=201,
    summary="Crear un nuevo modelo",
    description="Crea un nuevo modelo si no existe para la marca especificada."
)
async def create_model(
    model: schemas.ModelCreate,
    db: Session = Depends(get_db)
):
    # Validar que el nombre no esté vacío o solo contenga espacios
    if not model.name or not model.name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be empty or blank")
    
    # Validar que brand_id sea un entero positivo
    if not isinstance(model.brand_id, int) or model.brand_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid brand_id")
    
    # Validar que type_id sea un entero positivo
    if not isinstance(model.type_id, int) or model.type_id <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid type_id")
    
    # Comprobar si el modelo ya existe para la marca y tipo especificados
    existing_model = db.query(models.Model).filter(
        models.Model.name == model.name.strip(),
        models.Model.brand_id == model.brand_id,
        models.Model.type_id == model.type_id
    ).first()
    
    if existing_model:
        raise HTTPException(status_code=409, detail="Model already exists for this brand and type")
    
    try:
        # Llamar a la función de servicio para crear el modelo
        return await create_model_service(model=model, db=db)
    except HTTPException as e:
        raise e
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Model already exists for this brand and type")

@router.get(
    "",
    response_model=List[schemas.Model],
    summary="Obtener todos los modelos",
    description="Recupera una lista de todos los modelos disponibles."
)
async def get_models(
    skip: int = 0,
    limit: int = 10,    
    db: Session = Depends(get_db)              
):
    return await get_all_models_service(db=db, skip=skip, limit=limit)

@router.get(
    "/{model_id}",
    response_model=schemas.Model,
    summary="Obtener un modelo por ID",
    description="Recupera un modelo específico utilizando su ID."
)
async def get_model(
    model_id: int, 
    db: Session = Depends(get_db)
):
    # Validar que model_id sea un entero positivo
    if not isinstance(model_id, int) or model_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid model_id")
    
    model = await get_model_service(db=db, model_id=model_id)
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
    db: Session = Depends(get_db)
):
    # Validar que model_id sea un entero positivo
    if not isinstance(model_id, int) or model_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid model_id")
    
    model = await get_model_service(db=db, model_id=model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model does not exist")
    
    # Intentar eliminar el modelo
    try:
        success = await delete_model_service(model_id, db=db)
        if not success:
            raise HTTPException(status_code=404, detail="Model does not exist")
    except HTTPException as e:
        raise e
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete model")
    
    return

@router.put(
    "/{model_id}",
    response_model=schemas.Model,
    summary="Actualizar un modelo",
    description="Actualiza la información de un modelo existente."
)
async def update_model(
    model_id: int, 
    model: schemas.ModelCreate, 
    db: Session = Depends(get_db)
):
    # Validar que model_id sea un entero positivo
    if not isinstance(model_id, int) or model_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid model_id")
    
    # Validar que el nombre no esté vacío o solo contenga espacios
    if not model.name or not model.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty or blank")
    
    # Validar que brand_id sea un entero positivo
    if not isinstance(model.brand_id, int) or model.brand_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid brand_id")
    
    # Validar que type_id sea un entero positivo
    if not isinstance(model.type_id, int) or model.type_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid type_id")
    
    # Llamar a la función de servicio para actualizar el modelo
    try:
        updated_model = await update_model_service(model_id, model, db)
        return updated_model
    except HTTPException as e:
        raise e
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Another model with the same name, brand, and type already exists")

@router.get(
    "/",
    summary="Obtener ID del modelo por nombre",
    description="Obtiene el ID del modelo a partir del nombre del modelo.",
)
async def get_model_id_by_name(name: str = Query(..., description="Nombre del modelo para buscar su ID"), db: Session = Depends(get_db)):
    try:
        model_id = await get_model_id_by_name_service(db, name)
        return {"model_id": model_id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error inesperado.")




