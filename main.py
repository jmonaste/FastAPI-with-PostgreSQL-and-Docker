from typing import TYPE_CHECKING, List
import fastapi as _fastapi
from fastapi import HTTPException, Depends
import sqlalchemy.orm as _orm
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
import services as _services

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = _fastapi.FastAPI()




# Endpoints para Vehicle Types *********************************************************************************************

@app.post("/api/vehicle-types/", response_model=_schemas.VehicleType)
async def create_vehicle_type(
    vehicle_type: _schemas.VehicleTypeCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    # Comprobar si el tipo de vehículo ya existe
    existing_type = db.query(_models.VehicleType).filter(_models.VehicleType.type_name == vehicle_type.type_name).first()
    
    if existing_type:
        raise HTTPException(status_code=409, detail="Vehicle Type already exist")

    # Llamar a la función de servicio para crear el tipo de vehículo
    return await _services.create_vehicle_type(vehicle_type=vehicle_type, db=db)

@app.get("/api/vehicle-types/", response_model=List[_schemas.VehicleType])
async def get_vehicle_types(
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_all_vehicle_types(db=db)

@app.get("/api/vehicle-types/{vehicle_type_id}/", response_model=_schemas.VehicleType)
async def get_vehicle_type(
    vehicle_type_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    vehicle_type = await _services.get_vehicle_type(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle Type does not exist")

    return vehicle_type

@app.delete("/api/vehicle-types/{vehicle_type_id}/")
async def delete_vehicle_type(
    vehicle_type_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    vehicle_type = await _services.get_vehicle_type(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle Type does not exist")

    await _services.delete_vehicle_type(vehicle_type_id, db=db)
    
    return "Vehicle type successfully deleted"

@app.put("/api/vehicle-types/{vehicle_type_id}/", response_model=_schemas.VehicleType)
async def update_vehicle_type(
    vehicle_type_id: int,
    vehicle_type_data: _schemas.VehicleTypeCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    vehicle_type = await _services.get_vehicle_type(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle Type does not exist")

    return await _services.update_vehicle_type(
        vehicle_type_data=vehicle_type_data, vehicle_type_id=vehicle_type_id, db=db
    )


# Endpoints para Vehicle Types *********************************************************************************************
# Crear una nueva marca (Brand)
@app.post("/api/brands/", response_model=_schemas.Brand)
async def create_brand(
    brand: _schemas.BrandCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    # Comprobar si la marca ya existe
    existing_brand = db.query(_models.Brand).filter(_models.Brand.name == brand.name).first()
    
    if existing_brand:
        raise HTTPException(status_code=409, detail="Brand already exists")

    # Llamar a la función de servicio para crear la marca
    return await _services.create_brand(brand=brand, db=db)

# Obtener todas las marcas (Brands)
@app.get("/api/brands/", response_model=List[_schemas.Brand])
async def get_brands(
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_all_brands(db=db)

# Obtener una marca por ID
@app.get("/api/brands/{brand_id}/", response_model=_schemas.Brand)
async def get_brand(
    brand_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    return brand

# Eliminar una marca por ID
@app.delete("/api/brands/{brand_id}/")
async def delete_brand(
    brand_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    await _services.delete_brand(brand_id, db=db)
    
    return "Brand successfully deleted"

# Actualizar una marca por ID
@app.put("/api/brands/{brand_id}/", response_model=_schemas.Brand)
async def update_brand(
    brand_id: int,
    brand_data: _schemas.BrandCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    return await _services.update_brand(
        brand_data=brand_data, brand_id=brand_id, db=db
    )


# Endpoints para Vehicule Model *********************************************************************************************
# Crear un nuevo modelo de vehículo (Model)
@app.post("/api/models", response_model=_schemas.Model)
async def create_model(
    model: _schemas.ModelCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    # Comprobar si el modelo ya existe
    existing_model = db.query(_models.Model).filter(
        _models.Model.name == model.name, 
        _models.Model.brand_id == model.brand_id
    ).first()
    
    if existing_model:
        raise HTTPException(status_code=409, detail="Model already exists for this brand")

    # Llamar a la función de servicio para crear el modelo
    return await _services.create_model(model=model, db=db)


# Obtener todos los modelos (Models)
@app.get("/api/models", response_model=List[_schemas.Model])
async def get_models(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_all_models(db=db)


# Obtener un modelo por ID
@app.get("/api/models/{model_id}", response_model=_schemas.Model)
async def get_model(
    model_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    return model


# Eliminar un modelo por ID
@app.delete("/api/models/{model_id}")
async def delete_model(
    model_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    await _services.delete_model(model_id, db=db)
    
    return "Model successfully deleted"


# Actualizar un modelo por ID
@app.put("/api/models/{model_id}", response_model=_schemas.Model)
async def update_model(
    model_id: int, model: _schemas.ModelCreate, db: Session = Depends(_services.get_db)
):
    try:
        updated_model = await _services.update_model(model_id, model, db)
        return updated_model
    except HTTPException as e:
        raise e
