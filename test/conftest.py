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

@pytest_asyncio.fixture
def tracked_brands(httpx_client, auth_tokens):
    """
    Fixture para rastrear y limpiar las marcas creadas durante las pruebas.

    Args:
        httpx_client: Cliente HTTP para realizar solicitudes a la API.
        headers: Encabezados de autorización para las solicitudes.

    Yields:
        Una lista para almacenar los IDs de las marcas creadas.
    """
    created_brand_ids = []
    yield created_brand_ids
    # Teardown: Eliminar todas las marcas rastreadas
    for brand_id in created_brand_ids:
        response = httpx_client.delete(
            f"/api/brands/{brand_id}", 
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]:
            # Opcional: Loggear o manejar errores inesperados
            print(f"Error al eliminar la marca con ID {brand_id}: {response.text}")

@pytest.fixture
def tracked_colors(httpx_client, auth_tokens):
    """
    Fixture para rastrear y limpiar los colores creados durante las pruebas.

    Args:
        httpx_client: Cliente HTTP para realizar solicitudes a la API.
        auth_tokens: Tokens de autenticación para los encabezados de autorización.

    Yields:
        Una lista para almacenar los IDs de los colores creados.
    """
    created_color_ids = []
    yield created_color_ids
    # Teardown: Eliminar todos los colores rastreados
    for color_id in created_color_ids:
        response = httpx_client.delete(
            f"/api/colors/{color_id}",
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]:
            # Opcional: Loggear o manejar errores inesperados
            print(f"Error al eliminar el color con ID {color_id}: {response.text}")

@pytest_asyncio.fixture
def tracked_vehicle_types(httpx_client, auth_tokens):
    created_vehicle_types_ids = []
    yield created_vehicle_types_ids
    # Teardown: Eliminar todas las marcas rastreadas
    for vehicle_type_id in created_vehicle_types_ids:
        response = httpx_client.delete(
            f"/api/vehicle/types/{vehicle_type_id}", 
            headers={"Authorization": f"Bearer {auth_tokens['access_token']}"}
        )
        if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]:
            print(f"Error al eliminar el tipo de vhiculo con ID {vehicle_type_id}: {response.text}")

@pytest.fixture
def tracked_vehicle_models(httpx_client, auth_tokens):
    """
    Fixture para rastrear y limpiar los modelos de vehículos creados durante las pruebas.

    Args:
        httpx_client: Cliente HTTP para realizar solicitudes a la API.
        headers: Encabezados de autorización para las solicitudes.

    Yields:
        Una lista para almacenar los IDs de los modelos de vehículos creados.
    """
    created_model_ids = []
    yield created_model_ids
    # Teardown: Eliminar todos los modelos de vehículos rastreados
    for model_id in created_model_ids:
        response = httpx_client.delete(f"/api/models/{model_id}", headers={"Authorization": f"Bearer {auth_tokens['access_token']}"})
        if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]:
            print(f"Error al eliminar el modelo de vehículo con ID {model_id}: {response.text}")

@pytest.fixture
def tracked_vehicles(httpx_client, auth_tokens, tracked_vehicle_models, tracked_colors):
    """
    Fixture para rastrear y limpiar los vehículos creados durante las pruebas.

    Args:
        httpx_client: Cliente HTTP para realizar solicitudes a la API.
        headers: Encabezados de autorización para las solicitudes.

    Yields:
        Una lista para almacenar los IDs de los vehículos creados.
    """
    created_vehicle_ids = []
    yield created_vehicle_ids
    # Teardown: Eliminar todos los vehículos rastreados
    for vehicle_id in created_vehicle_ids:
        response = httpx_client.delete(f"/api/vehicles/{vehicle_id}", headers={"Authorization": f"Bearer {auth_tokens['access_token']}"})
        if response.status_code not in [status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND]:
            # Opcional: Loggear o manejar errores inesperados
            print(f"Error al eliminar el vehículo con ID {vehicle_id}: {response.text}")


