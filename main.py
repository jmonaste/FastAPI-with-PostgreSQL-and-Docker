import os
import pyzbar
from pyzbar.pyzbar import decode
from PIL import Image
from typing import TYPE_CHECKING, List
from fastapi import HTTPException, Depends, status, File, UploadFile, FastAPI, Query
from sqlalchemy.orm import Session
from schemas import UserCreate, UserRead
from utils import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS
from dependencies import get_db, get_current_user
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from models import User
import fastapi as _fastapi
import sqlalchemy.orm as _orm
import models as _models
import schemas as _schemas
import services as _services
import uuid
import io
import datetime as _dt
import imghdr
from jose import JWTError, jwt
from typing import Optional
import models, schemas
from sqlalchemy.exc import IntegrityError
from database import engine, Base
from utils import authenticate_user, create_access_token, create_refresh_token,get_current_user, get_db
from schemas import Token, TokenRefresh
from routers import vehicle_types, brands


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = FastAPI()
app.include_router(vehicle_types.router)
app.include_router(brands.router)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
revoked_tokens = set() # Lista para almacenar tokens revocados

#origins = ['http://localhost:3000','http://192.168.178.23:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (POST, GET, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)


# region Endpoints para Usuarios y Login *********************************************************************************************

# Ruta para crear un nuevo usuario (registro)
@app.post("/register", response_model=schemas.UserOut, tags=["Authorization"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token, tags=["Authorization"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint de login que devuelve Access y Refresh Tokens.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username, "jti": str(uuid.uuid4())})  # Añadir jti para identificar el token

    # Almacenar el Refresh Token en la base de datos
    new_refresh_token = models.RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_refresh_token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/refresh", response_model=schemas.Token, tags=["Authorization"])
def refresh_token(token_refresh: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """
    Endpoint para renovar el Access Token utilizando un Refresh Token válido.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el Refresh Token
        payload = jwt.decode(token_refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")  # JWT ID
        if username is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Obtener el usuario desde la base de datos
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    # Verificar si el Refresh Token está en la base de datos y no está revocado
    stored_refresh_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token_refresh.refresh_token,
        models.RefreshToken.is_revoked == False,
        models.RefreshToken.expires_at > datetime.utcnow()
    ).first()
    if stored_refresh_token is None:
        raise credentials_exception

    # Revocar el Refresh Token actual
    stored_refresh_token.is_revoked = True
    db.commit()

    # Crear un nuevo Refresh Token
    new_refresh_token_str = create_refresh_token(data={"sub": user.username, "jti": str(uuid.uuid4())})
    new_refresh_token = models.RefreshToken(
        token=new_refresh_token_str,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_refresh_token)
    db.commit()

    # Crear un nuevo Access Token
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": new_refresh_token_str, "token_type": "bearer"}

# Ruta protegida de ejemplo
@app.get("/protected", response_model=schemas.UserOut, tags=["Authorization"])
def read_protected(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/logout", status_code=200, tags=["Authorization"])
def logout(token_refresh: schemas.TokenRefresh, db: Session = Depends(get_db)):
    """
    Endpoint para cerrar sesión revocando el Refresh Token proporcionado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificar el Refresh Token
        payload = jwt.decode(token_refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Obtener el usuario desde la base de datos
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    # Buscar el Refresh Token en la base de datos
    stored_refresh_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token_refresh.refresh_token,
        models.RefreshToken.is_revoked == False,
        models.RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if stored_refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not found or already revoked",
        )

    # Revocar el Refresh Token
    stored_refresh_token.is_revoked = True
    db.commit()

    return {"message": "Logged out successfully"}

# endregion





# region Endpoints para VehicleModel *********************************************************************************************

@app.post("/api/models", response_model=_schemas.Model, tags=["Models"])
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

@app.get("/api/models", response_model=List[_schemas.Model], tags=["Models"])
async def get_models(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),                 
):
    return await _services.get_all_models(db=db)

@app.get("/api/models/{model_id}", response_model=_schemas.Model, tags=["Models"])
async def get_model(
    model_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    return model

@app.delete("/api/models/{model_id}", tags=["Models"])
async def delete_model(
    model_id: int, 
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    model = await _services.get_model(db=db, model_id=model_id)
    if model is None:
        raise _fastapi.HTTPException(status_code=404, detail="Model does not exist")

    await _services.delete_model(model_id, db=db)
    
    return {"detail": "Model successfully deleted"}

@app.put("/api/models/{model_id}", response_model=_schemas.Model, tags=["Models"])
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

@app.post("/api/vehicles", response_model=_schemas.Vehicle, tags=["Vehicles"])
async def create_vehicle(
    vehicle: _schemas.VehicleCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    # Verificar si el modelo de vehículo existe
    existing_model = db.query(models.Model).filter(models.Model.id == vehicle.vehicle_model_id).first()
    if not existing_model:
        raise HTTPException(status_code=404, detail="Vehicle model not found.")

    try:
        # Crear el vehículo
        new_vehicle = await _services.create_vehicle(vehicle=vehicle, db=db, user_id=current_user.id)
        return new_vehicle
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A vehicle with this VIN already exists.")
    

@app.get("/api/vehicles/{vehicle_id}", response_model=_schemas.Vehicle, tags=["Vehicles"])
async def read_vehicle(
    vehicle_id: int, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    db_vehicle = await _services.get_vehicle(db, vehicle_id=vehicle_id)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.get("/api/vehicles", response_model=List[_schemas.Vehicle], tags=["Vehicles"])
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    in_progress: bool = None,
    vin: str = None,
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    vehicles = await _services.get_vehicles(db=db, skip=skip, limit=limit, in_progress=in_progress, vin=vin)
    return vehicles

@app.put("/api/vehicles/{vehicle_id}", response_model=_schemas.Vehicle, tags=["Vehicles"])
async def update_vehicle(
    vehicle_id: int, 
    vehicle: _schemas.VehicleCreate, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    db_vehicle = await _services.update_vehicle(db=db, vehicle_id=vehicle_id, vehicle=vehicle)
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.delete("/api/vehicles/{vehicle_id}", tags=["Vehicles"])
async def delete_vehicle(
    vehicle_id: int, 
    db: Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    success = await _services.delete_vehicle(db=db, vehicle_id=vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"detail": "Vehicle successfully deleted"}


# endregion

# region Endpoints para recibir imagenes qr y barcode

# Verificar los tipos de imagen permitidos
allowed_extensions = {"image/jpeg", "image/jpg", "image/png", "image/heic"}

@app.post("/scan", tags=["QR & Barcodes"])
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
        raise HTTPException(status_code=500, detail="HEIC format not supported. Install pyheif library.")
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

# region Endpoints para la gestión de estados permitidos

@app.get("/api/vehicles/{vehicle_id}/allowed_transitions", response_model=List[_schemas.Transition], tags=["Vehicle States"])
async def get_allowed_transitions(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    return await _services.get_allowed_transitions_for_vehicle(vehicle_id=vehicle_id, db=db)

@app.get("/api/states", response_model=List[_schemas.State], tags=["Vehicle States"], summary="Obtener todos los estados", description="Devuelve una lista de todos los estados disponibles para los vehículos")
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

@app.get("/api/vehicles/{vehicle_id}/state_history", response_model=List[_schemas.StateHistory], tags=["Vehicle States"])
async def get_vehicle_state_history(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    try:
        state_history = await _services.get_vehicle_state_history(vehicle_id=vehicle_id, db=db)
        return state_history
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el historial de estados del vehículo.")

@app.get("/api/vehicles/{vehicle_id}/state", response_model=_schemas.State, tags=["Vehicle States"])
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

@app.put("/api/vehicles/{vehicle_id}/state", response_model=_schemas.StateHistory, tags=["Vehicle States"])
async def change_vehicle_state(
    vehicle_id: int,
    state_change: _schemas.StateChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        state_history_entry = await _services.change_vehicle_state(
            vehicle_id=vehicle_id,
            new_state_id=state_change.new_state_id,
            user_id=get_current_user().id,
            db=db,
            comments=state_change.comments,
        )
        return state_history_entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar el estado del vehículo."
        )

@app.get("/api/states/{state_id}/comments", response_model=List[_schemas.StateCommentRead], tags=["Vehicle States"])
async def get_state_comments(
    state_id: int,
    db: Session = Depends(get_db),
    current_user: _models.User = Depends(get_current_user),
):
    """
    Obtiene los comentarios predefinidos para un estado específico.
    """
    try:
        comments = await _services.get_state_comments(state_id=state_id, db=db)
        return comments
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ocurrió un error al obtener los comentarios del estado.")

# endregion

# region Endpoints para Color *****************************************************************************************************

@app.post("/api/colors", response_model=_schemas.Color)
async def create_color(
    color: _schemas.ColorCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await _services.add_color(color=color, db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating the color."
        )

@app.get("/api/colors/{color_id}", response_model=_schemas.Color)
def read_color(
    color_id: int,
    db: _orm.Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    color = _services.get_color(db=db, color_id=color_id)
    if color is None:
        raise HTTPException(status_code=404, detail="Color not found")
    return color

@app.put("/api/colors/{color_id}", response_model=_schemas.Color)
def modify_color(
    color_id: int,
    color: _schemas.ColorCreate,
    db: _orm.Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_color = _services.update_color(db=db, color_id=color_id, color_data=color)
        return updated_color
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while updating the color."
        )

@app.delete("/api/colors/{color_id}")
def remove_color(
    color_id: int,
    db: _orm.Session = Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        success = _services.delete_color(db=db, color_id=color_id)
        if not success:
            raise HTTPException(status_code=404, detail="Color not found")
        return {"ok": True}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while deleting the color."
        )

@app.get("/api/colors", response_model=List[_schemas.Color])
async def get_all_colors(
    db: _orm.Session = _fastapi.Depends(_services.get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        colors = await _services.get_all_colors(db=db)
        return colors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while fetching colors."
        )

# endregion













