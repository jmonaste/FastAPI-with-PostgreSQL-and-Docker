# tests/test_vehicle_type.py
import pytest
import uuid
from fastapi import status

@pytest.fixture
def unique_brand_name():
    """Genera un nombre de marca único para cada prueba."""
    return f"Test Brand {uuid.uuid4().hex}"

@pytest.fixture
def headers(auth_tokens):
    """Prepara los encabezados de autorización para las solicitudes."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}






@pytest.mark.asyncio
async def test_create_brand_success(httpx_client, headers, unique_brand_name):
    """Prueba la creación exitosa de una marca."""
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == unique_brand_name
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_brand(httpx_client, headers, unique_brand_name):
    """Prueba que la creación de una marca duplicada falle con un error 409."""
    brand_data = {"name": unique_brand_name}
    # Crear la marca por primera vez
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Intentar crear la misma marca nuevamente
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Brand already exists"

@pytest.mark.asyncio
async def test_get_brands(httpx_client, headers, unique_brand_name):
    """Prueba la obtención de marcas y verifica la existencia de una marca específica."""
    # Crear una marca
    brand_data = {"name": unique_brand_name}
    create_response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert create_response.status_code == status.HTTP_201_CREATED

    # Obtener todas las marcas
    response = httpx_client.get("/api/brands?skip=0&limit=100", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    brands = response.json()
    assert any(brand["name"] == unique_brand_name for brand in brands), "La marca creada no está en la lista de marcas."

@pytest.mark.asyncio
async def test_update_brand_success(httpx_client, headers, unique_brand_name):
    """Prueba la actualización exitosa de una marca existente."""
    # Crear una marca
    brand_data = {"name": unique_brand_name}
    create_response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    brand_id = create_response.json()["id"]

    # Actualizar la marca
    updated_name = f"{unique_brand_name} Updated"
    update_data = {"name": updated_name}
    update_response = httpx_client.put(f"/api/brands/{brand_id}", headers=headers, json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    updated_brand = update_response.json()
    assert updated_brand["name"] == updated_name
    assert updated_brand["id"] == brand_id

@pytest.mark.asyncio
@pytest.mark.parametrize("new_name,expected_status,expected_detail", [
    ("", status.HTTP_400_BAD_REQUEST, "Name cannot be empty"),
])
async def test_update_brand_invalid(httpx_client, headers, unique_brand_name, new_name, expected_status, expected_detail):
    """Prueba actualizaciones inválidas de una marca."""
    # Crear una marca
    brand_data = {"name": unique_brand_name}
    create_response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    brand_id = create_response.json()["id"]

    # Intentar actualizar con datos inválidos
    update_data = {"name": new_name}
    response = httpx_client.put(f"/api/brands/{brand_id}", headers=headers, json=update_data)
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail

@pytest.mark.asyncio
async def test_update_nonexistent_brand(httpx_client, headers):
    """Prueba la actualización de una marca que no existe."""
    non_existing_brand_id = 999999
    update_data = {"name": "Nonexistent Brand"}
    response = httpx_client.put(f"/api/brands/{non_existing_brand_id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Brand does not exist"

@pytest.mark.asyncio
async def test_update_brand_without_auth(httpx_client, unique_brand_name):
    """Prueba la actualización de una marca sin proporcionar un token de autorización."""
    # Crear una marca con autorización
    brand_data = {"name": unique_brand_name}
    auth_headers = {"Authorization": f"Bearer {uuid.uuid4().hex}"}
    create_response = httpx_client.post("/api/brands", headers=auth_headers, json=brand_data)
    assert create_response.status_code == status.HTTP_401_UNAUTHORIZED or create_response.status_code == status.HTTP_403_FORBIDDEN

    # Intentar actualizar sin autorización
    brand_id = 1  # Suponiendo que este ID no exista o se obtiene de otra manera
    update_data = {"name": "Updated Name"}
    response = httpx_client.put(f"/api/brands/{brand_id}", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_update_brand_with_invalid_token(httpx_client, unique_brand_name):
    """Prueba la actualización de una marca con un token de autorización inválido."""
    # Crear una marca con un token válido primero
    valid_headers = {"Authorization": f"Bearer {uuid.uuid4().hex}"}
    brand_data = {"name": unique_brand_name}
    create_response = httpx_client.post("/api/brands", headers=valid_headers, json=brand_data)
    assert create_response.status_code == status.HTTP_401_UNAUTHORIZED or create_response.status_code == status.HTTP_403_FORBIDDEN

    # Intentar actualizar con un token inválido
    invalid_headers = {"Authorization": "Bearer token_invalido"}
    brand_id = 1  # Suponiendo que este ID no exista o se obtiene de otra manera
    update_data = {"name": "Updated Name"}
    response = httpx_client.put(f"/api/brands/{brand_id}", headers=invalid_headers, json=update_data)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
