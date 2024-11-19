# routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
import uuid
import models
import schemas
import services
from dependencies import get_db
from utils import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(
    tags=["Authorization"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/register", response_model=schemas.UserOut, summary="Registrar un nuevo usuario")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar un nuevo usuario.
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token, summary="Iniciar sesión")
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
    refresh_token = create_refresh_token(data={"sub": user.username, "jti": str(uuid.uuid4())})

    # Almacenar el Refresh Token en la base de datos
    new_refresh_token = models.RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_refresh_token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.post("/refresh", response_model=schemas.Token, summary="Refrescar el token de acceso")
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
        models.RefreshToken.expires_at > datetime.utcnow(),
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
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_refresh_token)
    db.commit()

    # Crear un nuevo Access Token
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": new_refresh_token_str, "token_type": "bearer"}



@router.post("/logout", status_code=200, summary="Cerrar sesión")
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
        models.RefreshToken.expires_at > datetime.utcnow(),
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


@router.get("/protected", response_model=schemas.UserOut, summary="Endpoint protegido")
def read_protected(current_user: models.User = Depends(get_current_user)):
    """
    Endpoint de ejemplo que requiere autenticación.
    """
    return current_user
