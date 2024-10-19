from typing import TYPE_CHECKING, List
from fastapi import HTTPException, Depends, status, File, UploadFile
from sqlalchemy.orm import Session
from schemas import UserCreate, UserRead
from utils import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies import get_db, get_current_user
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from dependencies import get_current_user
from pyzbar.pyzbar import decode
from PIL import Image
from models import User
import fastapi as _fastapi
import sqlalchemy.orm as _orm
import models as _models
import schemas as _schemas
import services as _services
import io
import imghdr

if TYPE_CHECKING:
    from sqlalchemy.orm import Session



app = _fastapi.FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
revoked_tokens = set() # Lista para almacenar tokens revocados


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (POST, GET, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)


# region Endpoints para Usuarios y Login *********************************************************************************************

@app.post("/users/", response_model=UserRead)
async def create_user(
    user: UserCreate, 
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    if token in revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token ya ha sido revocado."
        )
    
    # Revocar el token actual
    revoked_tokens.add(token)
    return {"message": "Sesión cerrada correctamente. Token revocado."}

# endregion

# region Endpoints para Vehicle Types *********************************************************************************************

@app.post("/api/vehicle-types/", response_model=_schemas.VehicleType)
async def create_vehicle_type(
    vehicle_type: _schemas.VehicleTypeCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),  # Añadido para autenticación
):
    # Comprobar si el tipo de vehículo ya existe
    existing_type = db.query(_models.VehicleType).filter(_models.VehicleType.type_name == vehicle_type.type_name).first()
    
    if existing_type:
        raise HTTPException(status_code=409, detail="El tipo de vehículo ya existe")

    # Llamar a la función de servicio para crear el tipo de vehículo
    return await _services.create_vehicle_type(vehicle_type=vehicle_type, db=db)

@app.get("/api/vehicle-types/", response_model=List[_schemas.VehicleType])
async def get_vehicle_types(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle_types = await _services.get_all_vehicle_types(db=db)
    
    # Convertir los campos de datetime a cadenas
    vehicle_types_serialized = [
        {
            "type_name": vt.type_name,
            "id": vt.id,
            "created_at": vt.created_at.isoformat() if isinstance(vt.created_at, datetime) else vt.created_at,
            "updated_at": vt.updated_at.isoformat() if isinstance(vt.updated_at, datetime) else vt.updated_at,
        }
        for vt in vehicle_types
    ]
    
    return JSONResponse(
        content=vehicle_types_serialized,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/api/vehicle-types/{vehicle_type_id}/", response_model=_schemas.VehicleType)
async def get_vehicle_type(
    vehicle_type_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle_type = await _services.get_vehicle_type(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle Type does not exist")

    return vehicle_type

@app.delete("/api/vehicle-types/{vehicle_type_id}/")
async def delete_vehicle_type(
    vehicle_type_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    vehicle_type = await _services.get_vehicle_type(db=db, vehicle_type_id=vehicle_type_id)
    if vehicle_type is None:
        raise _fastapi.HTTPException(status_code=404, detail="Vehicle Type does not exist")

    return await _services.update_vehicle_type(
        vehicle_type_data=vehicle_type_data, vehicle_type_id=vehicle_type_id, db=db
    )
# endregion

# region Endpoints para Vehicle Brands *********************************************************************************************

@app.post("/api/brands/", response_model=_schemas.Brand)
async def create_brand(
    brand: _schemas.BrandCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    # Comprobar si la marca ya existe
    existing_brand = db.query(_models.Brand).filter(_models.Brand.name == brand.name).first()
    
    if existing_brand:
        raise HTTPException(status_code=409, detail="Brand already exists")

    # Llamar a la función de servicio para crear la marca
    return await _services.create_brand(brand=brand, db=db)

@app.get("/api/brands/", response_model=List[_schemas.Brand])
async def get_brands(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    return await _services.get_all_brands(db=db)

@app.get("/api/brands/{brand_id}/", response_model=_schemas.Brand)
async def get_brand(
    brand_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    return brand

@app.delete("/api/brands/{brand_id}/")
async def delete_brand(
    brand_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    brand = await _services.get_brand(db=db, brand_id=brand_id)
    if brand is None:
        raise _fastapi.HTTPException(status_code=404, detail="Brand does not exist")

    return await _services.update_brand(
        brand_data=brand_data, brand_id=brand_id, db=db
    )
# endregion

# region Endpoints para Vehicle Model *********************************************************************************************

@app.post("/api/models", response_model=_schemas.Model)
async def create_model(
    model: _schemas.ModelCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
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
async def get_models(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),                 
):
    return await _services.get_all_models(db=db)

@app.get("/api/models/{model_id}", response_model=_schemas.Model)
async def get_model(
    model_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    return model

@app.delete("/api/models/{model_id}")
async def delete_model(
    model_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    await _services.delete_model(model_id, db=db)
    
    return "Model successfully deleted"

@app.put("/api/models/{model_id}", response_model=_schemas.Model)
async def update_model(
    model_id: int, 
    model: _schemas.ModelCreate, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_model = await _services.update_model(model_id, model, db)
        return updated_model
    except HTTPException as e:
        raise e

# endregion

# region Endpoints para Vehicle ***************************************************************************************************

@app.post("/api/vehicles", response_model=_schemas.Vehicle)
async def create_vehicle(
    vehicle: _schemas.VehicleCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        existing_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.vin == vehicle.vin).first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cannot check if this VIN already exists."
        )

    if existing_vehicle:
        raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists.")

    # Verificar si el modelo de vehículo existe en la tabla models
    existing_model = db.query(_models.Model).filter(_models.Model.id == vehicle.vehicle_model_id).first()

    if not existing_model:
        raise HTTPException(status_code=404, detail="Vehicle model not found.")

    try:
        # Crear el vehículo si todas las verificaciones son correctas
        return await _services.create_vehicle(vehicle=vehicle, db=db, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating the vehicle."
        )

@app.get("/api/vehicles/{vehicle_id}", response_model=_schemas.Vehicle)
def read_vehicle(
    vehicle_id: int, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    db_vehicle = _services.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.get("/api/vehicles", response_model=List[_schemas.Vehicle])
async def get_vehicles(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    vehicles = await _services.get_vehicles(db=db, skip=skip, limit=limit)
    return vehicles

@app.put("/api/vehicles/{vehicle_id}", response_model=_schemas.Vehicle)
def update_vehicle(
    vehicle_id: int, 
    vehicle: _schemas.VehicleCreate, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    db_vehicle = _services.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    success = _services.delete_vehicle(db=db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"ok": True}

# endregion



# region Endpoint para recibir imagenes qr y barcode

# Verificar los tipos de imagen permitidos
allowed_extensions = {"image/jpeg", "image/jpg", "image/png", "image/heic"}

@app.post("/scan")
async def scan_qr_barcode(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),  # Añadido para autenticación
):
    print(f"File content type: {file.content_type}")
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


# region Endpoint para la gestión de estados permitidos

## Consultar Transiciones Permitidas --> OK
## Cambiar Estado del Vehículo
## Obtener Histórico de Estados
## Obtener Todos los Estados --> OK
## Consultar Estado Actual del Vehículo --> OK

@app.get("/api/vehicles/{vehicle_id}/allowed_transitions", response_model=List[_schemas.Transition])
async def get_allowed_transitions(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    try:
        return await _services.get_allowed_transitions_for_vehicle(vehicle_id=vehicle_id, db=db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error al obtener las transiciones permitidas.")


@app.get("/api/states/", response_model=List[_schemas.State])
async def get_all_states(
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    try:
        return await _services.get_all_states(db=db)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Ocurrió un error al obtener los estados.")


# Endpoint para consultar el estado actual del vehículo
@app.get("/api/vehicles/{vehicle_id}/current_state", response_model=_schemas.State)
async def get_vehicle_current_state(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    try:
        return await _services.get_vehicle_current_state(db=db, vehicle_id=vehicle_id)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Ocurrió un error al obtener el estado del vehículo.")


# endregion














