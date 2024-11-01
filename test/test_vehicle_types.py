# tests/test_vehicle_types.py
import pytest
import uuid
from fastapi import status

@pytest.fixture
def unique_vehicle_type_name():
    """Genera un nombre de tipo de vehículo único para cada prueba."""
    return f"Test Vehicle Type {uuid.uuid4().hex}"

@pytest.fixture
def headers(auth_tokens):
    """Prepara los encabezados de autorización para las solicitudes."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}


@pytest.mark.asyncio
async def test_create_vehicle_type_success(httpx_client, headers, unique_vehicle_type_name):
    """Prueba la creación exitosa de un tipo de vehículo."""
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type_name"] == unique_vehicle_type_name
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_vehicle_type(httpx_client, headers, unique_vehicle_type_name):
    """Prueba que la creación de un tipo de vehículo duplicado falle con un error 409."""
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    
    # Crear el tipo de vehículo por primera vez
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Intentar crear el mismo tipo de vehículo nuevamente
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Vehicle type already exists"


@pytest.mark.asyncio
async def test_get_vehicle_types(httpx_client, headers, unique_vehicle_type_name):
    """Prueba la obtención de tipos de vehículos y verifica la existencia de uno específico."""
    # Crear un tipo de vehículo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    
    # Obtener todos los tipos de vehículos
    response = httpx_client.get("/api/vehicle/types?skip=0&limit=100", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    vehicle_types = response.json()
    assert any(vt["type_name"] == unique_vehicle_type_name for vt in vehicle_types), "El tipo de vehículo creado no está en la lista."


@pytest.mark.asyncio
async def test_get_vehicle_type_by_id(httpx_client, headers, unique_vehicle_type_name):
    """Prueba la obtención de un tipo de vehículo por su ID."""
    # Crear un tipo de vehículo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    vehicle_type_id = create_response.json()["id"]
    
    # Obtener el tipo de vehículo por ID
    response = httpx_client.get(f"/api/vehicle/types/{vehicle_type_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == vehicle_type_id
    assert data["type_name"] == unique_vehicle_type_name


@pytest.mark.asyncio
async def test_update_vehicle_type_success(httpx_client, headers, unique_vehicle_type_name):
    """Prueba la actualización exitosa de un tipo de vehículo existente."""
    # Crear un tipo de vehículo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    vehicle_type_id = create_response.json()["id"]
    
    # Actualizar el tipo de vehículo
    updated_name = f"{unique_vehicle_type_name} Updated"
    update_data = {"type_name": updated_name}
    update_response = httpx_client.put(f"/api/vehicle/types/{vehicle_type_id}", headers=headers, json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    updated_vehicle_type = update_response.json()
    assert updated_vehicle_type["type_name"] == updated_name
    assert updated_vehicle_type["id"] == vehicle_type_id


@pytest.mark.asyncio
@pytest.mark.parametrize("new_name,expected_status,expected_detail", [
    ("", status.HTTP_400_BAD_REQUEST, "Name cannot be empty"),
])
async def test_update_vehicle_type_invalid(httpx_client, headers, unique_vehicle_type_name, new_name, expected_status, expected_detail):
    """Prueba actualizaciones inválidas de un tipo de vehículo."""
    # Crear un tipo de vehículo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    vehicle_type_id = create_response.json()["id"]
    
    # Intentar actualizar con datos inválidos
    update_data = {"type_name": new_name}
    response = httpx_client.put(f"/api/vehicle/types/{vehicle_type_id}", headers=headers, json=update_data)
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


@pytest.mark.asyncio
async def test_update_nonexistent_vehicle_type(httpx_client, headers):
    """Prueba la actualización de un tipo de vehículo que no existe."""
    non_existing_vehicle_type_id = 999999
    update_data = {"type_name": "Nonexistent Vehicle Type"}
    response = httpx_client.put(f"/api/vehicle/types/{non_existing_vehicle_type_id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vehicle type does not exist"


@pytest.mark.asyncio
async def test_delete_vehicle_type_success(httpx_client, headers, unique_vehicle_type_name):
    """Prueba la eliminación exitosa de un tipo de vehículo existente."""
    # Crear un tipo de vehículo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    vehicle_type_id = create_response.json()["id"]
    
    # Eliminar el tipo de vehículo
    delete_response = httpx_client.delete(f"/api/vehicle/types/{vehicle_type_id}", headers=headers)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar que ya no existe
    get_response = httpx_client.get(f"/api/vehicle/types/{vehicle_type_id}", headers=headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_nonexistent_vehicle_type(httpx_client, headers):
    """Prueba la eliminación de un tipo de vehículo que no existe."""
    non_existing_vehicle_type_id = 999999
    response = httpx_client.delete(f"/api/vehicle/types/{non_existing_vehicle_type_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Vehicle type does not exist"


@pytest.mark.asyncio
async def test_delete_vehicle_type_without_auth(httpx_client, unique_vehicle_type_name):
    """Prueba la eliminación de un tipo de vehículo sin proporcionar un token de autorización."""
    # Crear un tipo de vehículo con autorización
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    auth_headers = {"Authorization": f"Bearer {uuid.uuid4().hex}"}
    create_response = httpx_client.post("/api/vehicle/types", headers=auth_headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_401_UNAUTHORIZED or create_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Intentar eliminar sin autorización
    vehicle_type_id = 1  # Suponiendo que este ID no exista o se obtiene de otra manera
    response = httpx_client.delete(f"/api/vehicle/types/{vehicle_type_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_vehicle_type_with_invalid_token(httpx_client, unique_vehicle_type_name):
    """Prueba la eliminación de un tipo de vehículo con un token de autorización inválido."""
    # Crear un tipo de vehículo con un token válido primero
    valid_headers = {"Authorization": f"Bearer {uuid.uuid4().hex}"}
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=valid_headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_401_UNAUTHORIZED or create_response.status_code == status.HTTP_403_FORBIDDEN
    
    # Intentar eliminar con un token inválido
    invalid_headers = {"Authorization": "Bearer token_invalido"}
    vehicle_type_id = 1  # Suponiendo que este ID no exista o se obtiene de otra manera
    response = httpx_client.delete(f"/api/vehicle/types/{vehicle_type_id}", headers=invalid_headers)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_name,expected_status,expected_detail", [
    ("", " ", "\n"),  # Casos con cadenas vacías o solo espacios
])
async def test_create_vehicle_type_invalid(httpx_client, headers, invalid_name, expected_status, expected_detail):
    """Prueba la creación de un tipo de vehículo con un nombre vacío o inválido."""
    vehicle_type_data = {"type_name": invalid_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Name cannot be empty"


@pytest.mark.asyncio
@pytest.mark.parametrize("new_name,expected_status,expected_detail", [
    ("", " ", "\n"),  # Casos con cadenas vacías o solo espacios
])
async def test_update_vehicle_type_invalid(httpx_client, headers, unique_vehicle_type_name, new_name, expected_status, expected_detail):
    """Prueba actualizaciones inválidas de un tipo de vehículo con nombre vacío."""
    # Crear un tipo de vehículo válido primero
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    create_response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    vehicle_type_id = create_response.json()["id"]
    
    # Intentar actualizar con un nombre vacío
    update_data = {"type_name": new_name}
    response = httpx_client.put(f"/api/vehicle/types/{vehicle_type_id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Name cannot be empty"
