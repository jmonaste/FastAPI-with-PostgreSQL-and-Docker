# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from main import app
from dependencies import get_db
from models import Base, Brand
import uuid
import httpx
from fastapi import status
import pytest
import uuid
from fastapi import status
from datetime import datetime, timezone
import pytest_asyncio


# Usando SQLite en memoria para pruebas rápidas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Crear las tablas antes de las pruebas
Base.metadata.create_all(bind=engine)




@pytest.fixture(scope="function")
def db():
    """
    Crea una nueva sesión de base de datos para una prueba.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db):
    """
    Crea un nuevo TestClient con una dependencia de base de datos sobreescrita.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def httpx_client():
    """
    Fixture que proporciona una instancia de httpx.Client con alcance de sesión.
    """
    base_url = "http://127.0.0.1:8000"  # Reemplaza con tu base URL real
    client = httpx.Client(base_url=base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def unique_username():
    """Genera un nombre de usuario único para las pruebas."""
    return f"user_{uuid.uuid4().hex}"

@pytest.fixture(scope="session")
def auth_tokens(unique_username):
    """
    Fixture que maneja el registro y el inicio de sesión de un usuario,
    y devuelve los tokens de acceso y actualización.
    """
    base_url = "http://127.0.0.1:8000"  # URL de tu servicio en ejecución

    with httpx.Client(base_url=base_url) as client:
        # 1. Registro de Usuario
        register_data = {
            "username": unique_username,
            "password": "1234"
        }
        response = client.post("/register", json=register_data)
        assert response.status_code == 200, f"Contenido de la respuesta: {response.content}"
        assert response.json()["username"] == unique_username
        assert response.json()["is_active"] is True
        user_id = response.json()["id"]

        # 2. Inicio de Sesión
        login_data = {
            "grant_type": "password",
            "username": unique_username,
            "password": "1234"
        }
        response = client.post("/login", data=login_data)
        assert response.status_code == 200, f"Contenido de la respuesta: {response.content}"
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        yield {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }

