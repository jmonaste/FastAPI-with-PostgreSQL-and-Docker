from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from dependencies import get_current_user
from services.database_service import get_db
from services.brands_service import create_new_brand_service, get_all_brands_service, get_brand_service, delete_brand_service, update_brand_service


router = APIRouter(
    prefix="/api/brands",
    tags=["Brands"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)

@router.post("", response_model=schemas.Brand, status_code=201, summary="Crear una nueva marca", description="Crea una nueva marca si no existe.")
async def create_brand(
    brand: schemas.BrandCreate,
    db: Session = Depends(get_db)
):
    # Comprobar si la marca ya existe
    existing_brand = db.query(models.Brand).filter(models.Brand.name == brand.name).first()
    
    if existing_brand:
        raise HTTPException(status_code=409, detail="Brand already exists")

    try:
        return await create_new_brand_service(brand=brand, db=db)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Brand already exists")

@router.get("", response_model=List[schemas.Brand], summary="Obtener todas las marcas")
async def get_brands(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return await get_all_brands_service(db=db, skip=skip, limit=limit)

@router.get("/{brand_id}", response_model=schemas.Brand, summary="Obtener una marca por ID")
async def get_brand(
    brand_id: int, 
    db: Session = Depends(get_db)
):
    brand = await get_brand_service(db=db, brand_id=brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand does not exist")

    return brand

@router.delete("/{brand_id}", status_code=204, summary="Eliminar una marca")
async def delete_brand(
    brand_id: int, 
    db: Session = Depends(get_db)
):
    brand = await get_brand_service(db=db, brand_id=brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand does not exist")

    await delete_brand_service(brand_id, db=db)
    
    return {"detail": "Brand successfully deleted"}

@router.put("/{brand_id}", response_model=schemas.Brand, summary="Actualizar una marca")
async def update_brand(
    brand_id: int,
    brand_data: schemas.BrandCreate,
    db: Session = Depends(get_db)
):
    brand = await get_brand_service(db=db, brand_id=brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand does not exist")

    # Verificar si el nuevo nombre ya existe en otra marca
    existing_brand = db.query(models.Brand).filter(
        models.Brand.name == brand_data.name,
        models.Brand.id != brand_id
    ).first()
    if existing_brand:
        raise HTTPException(status_code=409, detail="Brand name already in use")

    return await update_brand_service(
        brand_data=brand_data, brand_id=brand_id, db=db
    )
