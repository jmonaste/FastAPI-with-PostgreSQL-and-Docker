# services.py
from typing import List
from sqlalchemy.orm import Session, joinedload
import models as _models
import schemas as _schemas
from fastapi import HTTPException
from datetime import datetime, timezone

from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas

async def create_model_service(
    model: _schemas.ModelCreate, db: "Session"
) -> _schemas.Model:
    """
    Crea un nuevo modelo de vehículo en la base de datos.

    Args:
        model (schemas.ModelCreate): Datos del modelo a crear.
        db (Session): Sesión de la base de datos.

    Returns:
        schemas.Model: Modelo creado con sus relaciones.
    
    Raises:
        HTTPException: Si la marca o el tipo de vehículo no existen,
                       o si el modelo ya existe para la marca y tipo especificados.
    """
    # Comprobación adicional de que el nombre no venga vacío o solo con espacios
    if not model.name or not model.name.strip():
        raise HTTPException(
            status_code=400,
            detail="Name cannot be empty or blank."
        )
    
    # Verificar si la marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=404,
            detail=f"Brand with ID {model.brand_id} does not exist."
        )
    
    # Verificar si el tipo de vehículo existe
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == model.type_id).first()
    if not vehicle_type:
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle type with ID {model.type_id} does not exist."
        )
    
    # Verificar si el modelo ya existe para la marca y tipo especificados
    existing_model = db.query(_models.Model).filter(
        _models.Model.name == model.name,
        _models.Model.brand_id == model.brand_id,
        _models.Model.type_id == model.type_id
    ).first()
    
    if existing_model:
        raise HTTPException(
            status_code=409,
            detail="Model already exists for this brand and type"
        )
    
    # Crear el modelo
    model_obj = _models.Model(
        name=model.name,
        brand_id=model.brand_id,
        type_id=model.type_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    
    # Cargar relaciones para retornar el modelo completo
    db.refresh(model_obj, attribute_names=["brand", "vehicle_type"])
    
    # Convertir el objeto ORM a un schema de Pydantic utilizando Pydantic v2
    return _schemas.Model.model_validate(model_obj)


async def get_all_models_service(db: "Session") -> List[_schemas.Model]:
    models = db.query(_models.Model).options(
        joinedload(_models.Model.brand),
        joinedload(_models.Model.vehicle_type)
    ).all()
    return list(map(_schemas.Model.model_validate, models))

async def get_model_service(model_id: int, db: "Session") -> _schemas.Model:
    # Validar que model_id sea un entero positivo
    if not isinstance(model_id, int) or model_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid model_id")
    
    model = db.query(_models.Model).options(
        joinedload(_models.Model.brand),
        joinedload(_models.Model.vehicle_type)
    ).filter(_models.Model.id == model_id).first()
    if model:
        return _schemas.Model.model_validate(model)
    return None

async def delete_model_service(model_id: int, db: "Session") -> bool:
    # Validar que model_id sea un entero positivo
    if not isinstance(model_id, int) or model_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid model_id")
    
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        db.delete(model)
        db.commit()
        return True
    return False

async def update_model_service(model_id: int, model: _schemas.ModelCreate, db: "Session"):
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
    
    existing_model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    
    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Verificar si la nueva marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with ID {model.brand_id} does not exist.")
    
    # Verificar si el nuevo tipo de vehículo existe
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == model.type_id).first()
    if not vehicle_type:
        raise HTTPException(status_code=404, detail=f"Vehicle type with ID {model.type_id} does not exist.")
    
    # Verificar si otro modelo con el mismo nombre, marca y tipo ya existe
    duplicate_model = db.query(_models.Model).filter(
        _models.Model.name == model.name.strip(),
        _models.Model.brand_id == model.brand_id,
        _models.Model.type_id == model.type_id,
        _models.Model.id != model_id
    ).first()
    
    if duplicate_model:
        raise HTTPException(status_code=409, detail="Another model with the same name, brand, and type already exists")
    
    # Actualizar el modelo
    existing_model.name = model.name.strip()
    existing_model.brand_id = model.brand_id
    existing_model.type_id = model.type_id
    existing_model.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(existing_model)
    return _schemas.Model.model_validate(existing_model)
