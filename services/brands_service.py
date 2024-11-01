from typing import List
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
from datetime import datetime, timezone
from fastapi import HTTPException, status




async def create_new_brand_service(
    brand: _schemas.BrandCreate, db: "Session"
) -> _schemas.Brand:
    brand_model = _models.Brand(
        **brand.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
        )
    db.add(brand_model)
    db.commit()
    db.refresh(brand_model)
    return _schemas.Brand.model_validate(brand_model)

async def get_all_brands_service(db: "Session", skip: int = 0, limit: int = 10) -> List[_schemas.Brand]:
    brands = db.query(_models.Brand).offset(skip).limit(limit).all()
    return list(map(_schemas.Brand.model_validate, brands))

async def get_brand_service(brand_id: int, db: "Session") -> _schemas.Brand:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        return _schemas.Brand.model_validate(brand)
    return None

async def delete_brand_service(brand_id: int, db: "Session") -> bool:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        db.delete(brand)
        db.commit()
        return True
    return False



async def update_brand_service(
    brand_data: _schemas.BrandCreate,  # Asegúrate de que estás utilizando el esquema correcto
    brand_id: int,
    db: "Session"
) -> _schemas.Brand:
    # Validación adicional para asegurarse de que el nombre no esté vacío después de eliminar espacios
    if not brand_data.name or not brand_data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    # Verificar si la marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand does not exist")
    
    # Verificar si el nuevo nombre ya existe en otra marca
    existing_brand = db.query(_models.Brand).filter(
        _models.Brand.name == brand_data.name.strip(),
        _models.Brand.id != brand_id
    ).first()
    if existing_brand:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Brand name already in use")
    
    # Actualizar el nombre de la marca
    brand.name = brand_data.name.strip()
    db.commit()
    db.refresh(brand)
    
    return _schemas.Brand.model_validate(brand)

