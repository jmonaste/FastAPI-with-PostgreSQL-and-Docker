from typing import TYPE_CHECKING, List
import fastapi as _fastapi
import sqlalchemy.orm as _orm
from sqlalchemy.orm import Session
import models as _models
import schemas as _schemas
import services as _services
from fastapi import File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from pyzbar.pyzbar import decode
from PIL import Image
import io
import imghdr



if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Para manejar HEIC
try:
    import pyheif
except ImportError:
    pyheif = None


app = _fastapi.FastAPI()


# region Endpoints para Vehicle Types *********************************************************************************************

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
# endregion

# region Endpoints para Vehicle Types *********************************************************************************************

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

@app.get("/api/brands/", response_model=List[_schemas.Brand])
async def get_brands(
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_all_brands(db=db)

@app.get("/api/brands/{brand_id}/", response_model=_schemas.Brand)
async def get_brand(
    brand_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    return brand

@app.delete("/api/brands/{brand_id}/")
async def delete_brand(
    brand_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    await _services.delete_brand(brand_id, db=db)
    
    return "Brand successfully deleted"

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
# endregion

# region Endpoints para Vehicule Model *********************************************************************************************

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

@app.get("/api/models", response_model=List[_schemas.Model])
async def get_models(db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_all_models(db=db)

@app.get("/api/models/{model_id}", response_model=_schemas.Model)
async def get_model(
    model_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    return model

@app.delete("/api/models/{model_id}")
async def delete_model(
    model_id: int, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    await _services.delete_model(model_id, db=db)
    
    return "Model successfully deleted"

@app.put("/api/models/{model_id}", response_model=_schemas.Model)
async def update_model(
    model_id: int, model: _schemas.ModelCreate, db: Session = Depends(_services.get_db)
):
    try:
        updated_model = await _services.update_model(model_id, model, db)
        return updated_model
    except HTTPException as e:
        raise e

# endregion

# region Endpoints para Vehicule ***************************************************************************************************

@app.post("/api/vehicles", response_model=_schemas.Vehicle)
async def create_vehicle(
    vehicle: _schemas.VehicleCreate,
    db: Session = Depends(_services.get_db),
):
    # Verificar si el vehículo ya existe en la base de datos utilizando el VIN
    existing_vehicle = db.query(_models.Vehicle).filter(
        _models.Vehicle.vin == vehicle.vin  # 'vin' es el número de identificación único del vehículo
    ).first()

    if existing_vehicle:
        raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists")

    # Verificar si el modelo de vehículo existe en la tabla models
    existing_model = db.query(_models.Model).filter(
        _models.Model.id == vehicle.vehicle_model_id  # Verificar que el vehicle_model_id es válido
    ).first()

    if not existing_model:
        raise HTTPException(status_code=404, detail="Vehicle model not found")

    # Crear el vehículo si todas las verificaciones son correctas
    return await _services.create_vehicle(vehicle=vehicle, db=db)





# Get Vehicle by ID
@app.get("/vehicles/{vehicle_id}", response_model=_schemas.Vehicle)
def read_vehicle(vehicle_id: int, db: Session = Depends(_services.get_db)):
    db_vehicle = _services.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

# Get All Vehicles
@app.get("/api/vehicles", response_model=List[_schemas.Vehicle])
async def get_vehicles(skip: int = 0, limit: int = 10, db: Session = Depends(_services.get_db)):
    vehicles = await _services.get_vehicles(db=db, skip=skip, limit=limit)
    return vehicles


# Update Vehicle
@app.put("/vehicles/{vehicle_id}", response_model=_schemas.Vehicle)
def update_vehicle(vehicle_id: int, vehicle: _schemas.VehicleCreate, db: Session = Depends(_services.get_db)):
    db_vehicle = _services.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

# Delete Vehicle
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(_services.get_db)):
    success = _services.delete_vehicle(db=db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"ok": True}
# endregion






# region Endpoint para recibir imagenes qr y barcode

# Verificar los tipos de imagen permitidos
allowed_extensions = {"image/jpeg", "image/jpg", "image/png", "image/heic"}

@app.post("/scan")
async def scan_qr_barcode(file: UploadFile = File(...)):
    # Verificar el tipo de archivo
    if file.content_type not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await file.read()

    # Manejo de imágenes HEIC
    if file.content_type == "image/heic":
        if pyheif is None:
            raise HTTPException(status_code=500, detail="HEIC format not supported. Install pyheif library.")
        
        heif_file = pyheif.read_heif(io.BytesIO(contents))
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.stride)
    else:
        # Si no es HEIC, intentar abrir como imagen regular con PIL
        image = Image.open(io.BytesIO(contents))

    # Decodificar el código QR o de barras usando pyzbar
    decoded_objects = decode(image)
    
    if not decoded_objects:
        return JSONResponse(content={"error": "No QR or Barcode detected"}, status_code=400)
    
    # Procesar los códigos detectados
    result_data = []
    for obj in decoded_objects:
        code_type = "QR Code" if obj.type == "QRCODE" else "Barcode"
        result_data.append({
            "type": code_type,
            "data": obj.data.decode("utf-8")
        })

    # Devolver la lista de códigos detectados junto con su tipo
    return {"detected_codes": result_data}

# endregion










