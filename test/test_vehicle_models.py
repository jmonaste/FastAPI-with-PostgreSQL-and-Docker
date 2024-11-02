# tests/test_vehicle_models.py
import pytest
import uuid
from fastapi import status
from datetime import datetime, timezone
import pytest_asyncio

@pytest.fixture
def unique_model_name():
    """Genera un nombre de modelo único para cada prueba."""
    return f"Test Model {uuid.uuid4().hex}"

@pytest.fixture
def headers(auth_tokens):
    """Prepara los encabezados de autorización para las solicitudes."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}

@pytest_asyncio.fixture
async def brand_and_type_ids(httpx_client, headers):
    """Crea una marca y un tipo de vehículo únicos para las pruebas de modelos y retorna sus IDs."""
    unique_brand = f"Test Brand {uuid.uuid4().hex}"
    brand_data = {"name": unique_brand}
    brand_response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert brand_response.status_code == status.HTTP_201_CREATED
    brand_id = brand_response.json()["id"]

    unique_type = f"Test Vehicle Type {uuid.uuid4().hex}"
    type_data = {"type_name": unique_type}
    type_response = httpx_client.post("/api/vehicle/types", headers=headers, json=type_data)
    assert type_response.status_code == status.HTTP_201_CREATED
    type_id = type_response.json()["id"]

    yield brand_id, type_id

    # Limpieza: Eliminar los modelos, tipo y marca creados
    # Obtener todos los modelos para eliminar los creados durante la prueba
    models_response = httpx_client.get("/api/models?skip=0&limit=100", headers=headers)
    if models_response.status_code == status.HTTP_200_OK:
        models = models_response.json()
        for model in models:
            if model["brand_id"] == brand_id and model["type_id"] == type_id:
                httpx_client.delete(f"/api/models/{model['id']}", headers=headers)

    # Eliminar tipo
    httpx_client.delete(f"/api/vehicle/types/{type_id}", headers=headers)
    # Eliminar marca
    httpx_client.delete(f"/api/brands/{brand_id}", headers=headers)





@pytest.mark.asyncio
async def test_create_model_success(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba la creación exitosa de un modelo de vehículo."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    response = httpx_client.post("/api/models", headers=headers, json=model_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == unique_model_name
    assert data["brand_id"] == brand_id
    assert data["type_id"] == type_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_create_duplicate_model(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba que la creación de un modelo duplicado falle con un error 409."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    
    # Crear el modelo por primera vez
    response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Intentar crear el mismo modelo nuevamente
    response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Model already exists for this brand and type"

@pytest.mark.asyncio
async def test_get_models(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba la obtención de todos los modelos y verifica la existencia de uno específico."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED

    # Obtener todos los modelos
    response = httpx_client.get("/api/models?skip=0&limit=100", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    models = response.json()
    assert any(model["name"] == unique_model_name for model in models), "El modelo creado no está en la lista de modelos."

@pytest.mark.asyncio
async def test_get_model_by_id(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba la obtención de un modelo específico por su ID."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Obtener el modelo por ID
    response = httpx_client.get(f"/api/models/{model_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == model_id
    assert data["name"] == unique_model_name
    assert data["brand_id"] == brand_id
    assert data["type_id"] == type_id
    assert "brand" in data
    assert data["brand"]["id"] == brand_id
    assert data["brand"]["name"] != ""

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_data,expected_status,expected_detail", [
    (
        {"name": "Valid Name", "brand_id": 999999, "type_id": 1},
        status.HTTP_404_NOT_FOUND,
        f"Brand with ID 999999 does not exist."
    ),
    (
        {"name": "Valid Name", "brand_id": 9, "type_id": 999999},
        status.HTTP_404_NOT_FOUND,
        "Vehicle type with ID 999999 does not exist."
    ),
])
async def test_create_model_invalid_first_type(httpx_client, headers, invalid_data, expected_status, expected_detail, brand_and_type_ids):
    """Prueba la creación de un modelo con datos inválidos."""
    # Si se intenta usar brand_id=1 o type_id=1, asegurarse de que no existan
    # Pero para simplificar, directamente usar 999999 para simular inexistencia
    # Ignorar brand_and_type_ids ya que estamos probando datos inválidos

    # Actualizar invalid_data según los casos
    if invalid_data["brand_id"] == 999999 and invalid_data["type_id"] == 999999:
        # Solo verificar el nombre vacío
        pass
    elif invalid_data["brand_id"] == 999999 and invalid_data["type_id"] == 1:
        # brand_id no existe
        pass
    elif invalid_data["brand_id"] == 1 and invalid_data["type_id"] == 999999:
        # type_id no existe
        pass

    response = httpx_client.post("/api/models", headers=headers, json=invalid_data)
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_data,expected_status,expected_detail", [
    (
        {"name": "", "brand_id": 999999, "type_id": 999999},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Name cannot be empty"
    ),
    (
        {"name": "   ", "brand_id": 999999, "type_id": 999999},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Name cannot be empty"
    ),
])
async def test_create_model_invalid_second_type(httpx_client, headers, invalid_data, expected_status, expected_detail, brand_and_type_ids):
    """Prueba la creación de un modelo con datos inválidos."""
    # Si se intenta usar brand_id=1 o type_id=1, asegurarse de que no existan
    # Pero para simplificar, directamente usar 999999 para simular inexistencia
    # Ignorar brand_and_type_ids ya que estamos probando datos inválidos

    # Actualizar invalid_data según los casos
    if invalid_data["brand_id"] == 999999 and invalid_data["type_id"] == 999999:
        # Solo verificar el nombre vacío
        pass
    elif invalid_data["brand_id"] == 999999 and invalid_data["type_id"] == 1:
        # brand_id no existe
        pass
    elif invalid_data["brand_id"] == 1 and invalid_data["type_id"] == 999999:
        # type_id no existe
        pass

    response = httpx_client.post("/api/models", headers=headers, json=invalid_data)
    assert response.status_code == expected_status
    # Obtener los detalles de los errores de validación
    errors = response.json().get("detail", [])
    # Buscar un error específico para el campo 'name'
    name_error = next(
        (error for error in errors if error.get("loc") == ["body", "name"]),
        None
    )
    assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
    assert "Name cannot be empty or blank" in name_error.get("msg", ""), "El mensaje de error para 'name' no es el esperado"

@pytest.mark.asyncio
async def test_update_model_invalid(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba actualizaciones inválidas de un modelo."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Intentar actualizar con un nombre vacío
    invalid_update_data = {
        "name": "",
        "brand_id": brand_id,
        "type_id": type_id
    }
    update_response = httpx_client.put(f"/api/models/{model_id}", headers=headers, json=invalid_update_data)
    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = update_response.json().get("detail", [])
    name_error = next(
        (error for error in errors if error.get("loc") == ["body", "name"]),
        None
    )
    assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
    assert "Name cannot be empty or blank" in name_error.get("msg", ""), "El mensaje de error para 'name' no es el esperado"

    # Intentar actualizar con una marca inexistente
    invalid_update_data = {
        "name": "Updated Name",
        "brand_id": 999999,
        "type_id": type_id
    }
    update_response = httpx_client.put(f"/api/models/{model_id}", headers=headers, json=invalid_update_data)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json()["detail"] == "Brand with ID 999999 does not exist."

    # Intentar actualizar con un tipo inexistente
    invalid_update_data = {
        "name": "Updated Name",
        "brand_id": brand_id,
        "type_id": 999999
    }
    update_response = httpx_client.put(f"/api/models/{model_id}", headers=headers, json=invalid_update_data)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
    assert update_response.json()["detail"] == "Vehicle type with ID 999999 does not exist."

@pytest.mark.asyncio
async def test_update_nonexistent_model(httpx_client, headers):
    """Prueba la actualización de un modelo que no existe."""
    non_existing_model_id = 999999
    update_data = {
        "name": "Nonexistent Model",
        "brand_id": 999999,
        "type_id": 999999
    }
    response = httpx_client.put(f"/api/models/{non_existing_model_id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Model not found"

@pytest.mark.asyncio
async def test_delete_model_success(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba la eliminación exitosa de un modelo existente."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Eliminar el modelo
    delete_response = httpx_client.delete(f"/api/models/{model_id}", headers=headers)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verificar que ya no existe
    get_response = httpx_client.get(f"/api/models/{model_id}", headers=headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_nonexistent_model(httpx_client, headers):
    """Prueba la eliminación de un modelo que no existe."""
    non_existing_model_id = 999999
    response = httpx_client.delete(f"/api/models/{non_existing_model_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Model does not exist"

@pytest.mark.asyncio
async def test_delete_model_without_auth(httpx_client, unique_model_name, brand_and_type_ids, headers):
    """Prueba la eliminación de un modelo sin proporcionar un token de autorización."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    # Crear un modelo con autorización
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Intentar eliminar sin autorización
    response = httpx_client.delete(f"/api/models/{model_id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_delete_model_with_invalid_token(httpx_client, unique_model_name, brand_and_type_ids, headers):
    """Prueba la eliminación de un modelo con un token de autorización inválido."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    # Crear un modelo con autorización
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Intentar eliminar con un token inválido
    invalid_headers = {"Authorization": "Bearer token_invalido"}
    response = httpx_client.delete(f"/api/models/{model_id}", headers=invalid_headers)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_data,expected_status,expected_detail", [
    (
        {"name": "", "brand_id": 999999, "type_id": 999999},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Name cannot be empty"
    ),
    (
        {"name": "   ", "brand_id": 999999, "type_id": 999999},
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Name cannot be empty"
    ),
])
async def test_update_model_with_empty_name(httpx_client, headers, unique_model_name, brand_and_type_ids, invalid_data, expected_status, expected_detail):
    """Prueba la actualización de un modelo con un nombre vacío o solo espacios en blanco."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Intentar actualizar con nombre vacío
    response = httpx_client.put(f"/api/models/{model_id}", headers=headers, json=invalid_data)
    assert response.status_code == expected_status
    errors = response.json().get("detail", [])
    name_error = next(
        (error for error in errors if error.get("loc") == ["body", "name"]),
        None
    )
    assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
    assert "Name cannot be empty or blank" in name_error.get("msg", ""), "El mensaje de error para 'name' no es el esperado"

@pytest.mark.asyncio
async def test_update_model_success(httpx_client, headers, unique_model_name, brand_and_type_ids):
    """Prueba la actualización exitosa de un modelo existente."""
    brand_id, type_id = brand_and_type_ids
    model_data = {
        "name": unique_model_name,
        "brand_id": brand_id,
        "type_id": type_id
    }
    create_response = httpx_client.post("/api/models", headers=headers, json=model_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    model_id = create_response.json()["id"]

    # Crear una nueva marca y tipo para la actualización
    new_brand = f"Updated Brand {uuid.uuid4().hex}"
    new_model_data = {
        "name": new_brand,
        "brand_id": brand_id,
        "type_id": type_id
    }
    new_brand_response = httpx_client.post("/api/brands", headers=headers, json=new_model_data)
    assert new_brand_response.status_code == status.HTTP_201_CREATED
    new_brand_id = new_brand_response.json()["id"]

    new_type = f"Updated Vehicle Type {uuid.uuid4().hex}"
    new_type_data = {"type_name": new_type}
    new_type_response = httpx_client.post("/api/vehicle/types", headers=headers, json=new_type_data)
    assert new_type_response.status_code == status.HTTP_201_CREATED
    new_type_id = new_type_response.json()["id"]

    # Actualizar el modelo
    updated_name = f"{unique_model_name} Updated"
    update_data = {
        "name": updated_name,
        "brand_id": new_brand_id,
        "type_id": new_type_id
    }
    update_response = httpx_client.put(f"/api/models/{model_id}", headers=headers, json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    updated_model = update_response.json()
    assert updated_model["name"] == updated_name
    assert updated_model["brand_id"] == new_brand_id
    assert updated_model["type_id"] == new_type_id
    assert updated_model["id"] == model_id

