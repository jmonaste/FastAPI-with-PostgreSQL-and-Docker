# tests/test_vehicles.py
import pytest
import uuid
from fastapi import status
import pytest_asyncio
from constants.exceptions import (
    VEHICLE_MODEL_NOT_FOUND,
    COLOR_NOT_FOUND,
    INITIAL_STATE_NOT_FOUND,
    VIN_ALREADY_EXISTS,
    INVALID_VIN,
    VEHICLE_NOT_FOUND
)

@pytest.fixture
def headers(auth_tokens):
    """Prepara los encabezados de autorización para las solicitudes."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}

@pytest.fixture
def unique_vehicle_model_name():
    """Genera un nombre de modelo de vehículo único para cada prueba."""
    return f"Test Model {uuid.uuid4().hex[:8].upper()}"

@pytest.fixture
def unique_vehicle_vin():
    """Genera un VIN de vehículo único para cada prueba."""
    return f"VIN{uuid.uuid4().hex[:10].upper()}"

@pytest.fixture
def unique_color_name():
    """Genera un nombre de color único para cada prueba."""
    return f"Test Color {uuid.uuid4().hex[:8].upper()}"

@pytest.fixture
def unique_vehicle_type_name():
    """Genera un nombre de tipo de vhiculo único para cada prueba."""
    return f"Test Vehicle Type {uuid.uuid4().hex}"

@pytest.fixture
def unique_brand_name():
    """Genera un nombre de marca único para cada prueba."""
    return f"Test Brand {uuid.uuid4().hex}"







@pytest.mark.asyncio
async def test_create_vehicle_success(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba la creación exitosa de un vehículo con datos válidos."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF1010",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle
    
    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_create_vehicle_missing_fields_vehicle_model_id(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_color_name, 
    tracked_colors):
    """Prueba que la creación de un vehículo sin el campo 'vehicle_model_id' falle."""
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF0097",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    # Intentar crear un vehículo sin 'vehicle_model_id'
    vehicle_data = {
        # "vehicle_model_id": 1,  # Campo omitido
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": False
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
    errors = response.json().get("detail", [])
    vehicle_model_error = next(
        (error for error in errors if error.get("loc") == ["body", "vehicle_model_id"]),
        None
    )
    assert vehicle_model_error is not None, "No se encontró un error de validación para el campo 'vehicle_model_id'"
    assert vehicle_model_error.get("msg") == "Field required", "El mensaje de error para 'vehicle_model_id' no es el esperado"

    tracked_colors.append(color_id)

@pytest.mark.asyncio
async def test_create_vehicle_missing_fields_color_id(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba que la creación de un vehículo sin el campo 'color_id' falle."""
    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Intentar crear un vehículo sin 'color_id'
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        # "color_id": 1,  # Campo omitido
        "is_urgent": False
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
    errors = response.json().get("detail", [])
    color_error = next(
        (error for error in errors if error.get("loc") == ["body", "color_id"]),
        None
    )
    assert color_error is not None, "No se encontró un error de validación para el campo 'color_id'"
    assert color_error.get("msg") == "Field required", "El mensaje de error para 'color_id' no es el esperado"

    # Limpieza
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_create_vehicle_missing_fields_vin(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba que la creación de un vehículo sin el campo 'vin' falle."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF8383",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    # Intentar crear un vehículo sin 'vin'
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        # "vin": "AAA123",  # Campo omitido
        "color_id": color_id,
        "is_urgent": True
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
    errors = response.json().get("detail", [])
    vin_error = next(
        (error for error in errors if error.get("loc") == ["body", "vin"]),
        None
    )
    assert vin_error is not None, "No se encontró un error de validación para el campo 'vin'"
    assert vin_error.get("msg") == "Field required", "El mensaje de error para 'vin' no es el esperado"

    # Limpieza
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_create_vehicle_invalid_is_urgent(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba que la creación de un vehículo con 'is_urgent' inválido falle."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF1099",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    # Intentar crear un vehículo con 'is_urgent' inválido
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": 90  # Debe ser booleano
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
    errors = response.json().get("detail", [])
    is_urgent_error = next(
        (error for error in errors if error.get("loc") == ["body", "is_urgent"]),
        None
    )
    assert is_urgent_error is not None, "No se encontró un error de validación para el campo 'is_urgent'"
    assert "Input should be a valid boolean, unable to interpret input" in is_urgent_error.get("msg", ""), "El mensaje de error para 'is_urgent' no es el esperado"

    # Limpieza
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_create_vehicle_nonexistent_vehicle_model_id(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    tracked_vehicles, 
    tracked_colors, 
    unique_color_name
    ):
    """Prueba que la creación de un vehículo con 'vehicle_model_id' inexistente falle."""
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF0098",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    tracked_colors.append(color_id)
    
    # Intentar crear un vehículo con 'vehicle_model_id' inexistente
    nonexistent_vehicle_model_id = 999999
    vehicle_data = {
        "vehicle_model_id": nonexistent_vehicle_model_id,
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": False
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
    errors = response.json().get("detail", [])
    assert errors is not None, "No se encontró un error de validación para el campo 'vehicle_model_id'"
    assert errors ==  VEHICLE_MODEL_NOT_FOUND, "El mensaje de error para 'vehicle_model_id' no es el esperado"

@pytest.mark.asyncio
async def test_create_vehicle_nonexistent_color_id(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_vehicle_types,
    tracked_vehicle_models,
    ):
    """Prueba que la creación de un vehículo con 'color_id' inexistente falle."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Intentar crear un vehículo con 'color_id' inexistente
    nonexistent_color_id = 999999
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": f'{unique_vehicle_vin}ABC123',
        "color_id": nonexistent_color_id,
        "is_urgent": False
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
    assert response.json()["detail"] == COLOR_NOT_FOUND

    # Limpieza
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_create_vehicle_duplicate_vin(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba que la creación de un vehículo con un VIN duplicado falle."""
    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF4599",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle


    # Intentar crear otro vehículo con el mismo VIN
    duplicate_vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,  # VIN duplicado
        "color_id": color_id,
        "is_urgent": False
    }
    response = httpx_client.post("/api/vehicles", headers=headers, json=duplicate_vehicle_data)
    assert response.status_code == status.HTTP_409_CONFLICT, f"Respuesta: {response.text}"
    assert response.json()["detail"] == VIN_ALREADY_EXISTS

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_all_vehicles(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba la recuperación exitosa de todos los vehículos."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF5469",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    # Crear algunos vehículos
    vehicles = [
        {"vehicle_model_id": vehicle_model_data["id"], "vin": f"VINTEST{uuid.uuid4().hex[:10].upper()}", "color_id": color_id, "is_urgent": True},
        {"vehicle_model_id": vehicle_model_data["id"], "vin": f"VINTEST{uuid.uuid4().hex[:10].upper()}", "color_id": color_id, "is_urgent": False},
    ]
    for vehicle in vehicles:
        response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_vehicle = response.json()
        tracked_vehicles.append(created_vehicle["id"])

    # Parámetros de consulta
    params = {
        "skip": 0,   # Índice inicial de los resultados
        "limit": 100  # Máximo número de resultados a recuperar
    }
        
    # Recuperar todos los vehículos
    response = httpx_client.get("/api/vehicles", headers=headers, params=params)
    assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
    data = response.json()
    assert isinstance(data, list), "La respuesta debe ser una lista"
    for vehicle in vehicles:
        assert any(v["vin"] == vehicle["vin"] for v in data), f"No se encontró el vehículo con VIN {vehicle['vin']} en la respuesta"

    # Limpieza
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_vehicle_by_id_success(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba la recuperación exitosa de un vehículo por su ID."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF6666",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle
    
    # Recuperar el vehículo por ID
    response = httpx_client.get(f"/api/vehicles/{created_vehicle["id"]}", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
    data = response.json()
    assert data["id"] == created_vehicle["id"], "El ID del vehículo recuperado no coincide"
    assert data["vin"] == vehicle_data["vin"], "El VIN del vehículo recuperado no coincide"
    assert data["is_urgent"] == vehicle_data["is_urgent"], "El campo 'is_urgent' del vehículo recuperado no coincide"
    assert "model" in data, "El campo 'model' no está presente en la respuesta"

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_vehicle_by_id_not_found(httpx_client, headers):
    """Prueba que la recuperación de un vehículo inexistente falle."""
    non_existing_vehicle_id = 999999
    response = httpx_client.get(f"/api/vehicles/{non_existing_vehicle_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
    assert response.json()["detail"] == VEHICLE_NOT_FOUND

@pytest.mark.asyncio
async def test_update_vehicle_success(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba la actualización exitosa de un vehículo existente."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF6666",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle
    
    # Actualizar el vehículo
    updated_data = {
        "vehicle_model_id": vehicle_data["vehicle_model_id"],
        "vin": "BBB456",
        "color_id": color_id,
        "is_urgent": True
    }
    update_response = httpx_client.put(f"/api/vehicles/{created_vehicle["id"]}", headers=headers, json=updated_data)
    assert update_response.status_code == status.HTTP_200_OK, f"Respuesta: {update_response.text}"
    updated_vehicle = update_response.json()
    assert updated_vehicle["id"] == created_vehicle["id"], "El ID del vehículo actualizado no coincide"
    assert updated_vehicle["vin"] == updated_data["vin"], "El VIN del vehículo actualizado no coincide"
    assert updated_vehicle["is_urgent"] == updated_data["is_urgent"], "El campo 'is_urgent' del vehículo actualizado no coincide"

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
@pytest.mark.parametrize("new_vin,expected_status,expected_detail, color_hexcode", [
    ("", status.HTTP_400_BAD_REQUEST, INVALID_VIN, "#FF0088"),
    ("   ", status.HTTP_400_BAD_REQUEST, INVALID_VIN, "#FF0077"),
])
async def test_update_vehicle_invalid(
    httpx_client, 
    headers, 
    new_vin,
    expected_status,
    expected_detail,
    color_hexcode,
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba que la actualización de un vehículo con datos inválidos falle."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": color_hexcode,
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle
    
    # Intentar actualizar con datos inválidos
    updated_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": new_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    response = httpx_client.put(f"/api/vehicles/{created_vehicle["id"]}", headers=headers, json=updated_data)
    assert response.status_code == expected_status, f"Respuesta: {response.text}"
    assert response.json()["detail"] == expected_detail

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_update_nonexistent_vehicle(httpx_client, headers):
    """Prueba la actualización de un vehículo que no existe."""
    non_existing_vehicle_id = 999999
    update_data = {
        "vehicle_model_id": 1,
        "vin": "CCC789",
        "color_id": 1,
        "is_urgent": True
    }
    response = httpx_client.put(f"/api/vehicles/{non_existing_vehicle_id}", headers=headers, json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == VEHICLE_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_vehicle_success(
    httpx_client, 
    headers, 
    unique_vehicle_vin, 
    unique_vehicle_model_name, 
    unique_color_name, 
    unique_vehicle_type_name, 
    unique_brand_name,
    tracked_brands,
    tracked_colors,
    tracked_vehicle_types,
    tracked_vehicle_models,
    tracked_vehicles
    ):
    """Prueba la eliminación exitosa de un vehículo existente."""

    # Crea un tipo de vehiculo
    vehicle_type_data = {"type_name": unique_vehicle_type_name}
    response = httpx_client.post("/api/vehicle/types", headers=headers, json=vehicle_type_data)
    assert response.status_code == status.HTTP_201_CREATED
    vehicle_type_data = response.json()
    assert vehicle_type_data["type_name"] == unique_vehicle_type_name
    assert "id" in vehicle_type_data

    # Crea una marca de vehiculo
    brand_data = {"name": unique_brand_name}
    response = httpx_client.post("/api/brands", headers=headers, json=brand_data)
    assert response.status_code == status.HTTP_201_CREATED
    brand_data = response.json()
    assert brand_data["name"] == unique_brand_name
    assert "id" in brand_data

    # Crear un modelo de vehículo
    vehicle_model_data = {
        "name": unique_vehicle_model_name,
        "brand_id": brand_data["id"],
        "type_id": vehicle_type_data["id"]
    }
    response = httpx_client.post("/api/models", headers=headers, json=vehicle_model_data)
    assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
    vehicle_model_data = response.json()
    
    # Crear un color
    color_data = {
            "name": unique_color_name,
            "hex_code": "#FF6464",
            "rgb_code": "255,0,0"
        }
    create_color_response = httpx_client.post("/api/colors", headers=headers, json=color_data)
    assert create_color_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_color_response.text}"
    color = create_color_response.json()
    color_id = color["id"]
    
    
    # Crear un vehículo
    vehicle_data = {
        "vehicle_model_id": vehicle_model_data["id"],
        "vin": unique_vehicle_vin,
        "color_id": color_id,
        "is_urgent": True
    }
    create_vehicle_response = httpx_client.post("/api/vehicles", headers=headers, json=vehicle_data)
    assert create_vehicle_response.status_code == status.HTTP_201_CREATED, f"Respuesta: {create_vehicle_response.text}"
    created_vehicle = create_vehicle_response.json()
    assert created_vehicle["vehicle_model_id"] == vehicle_data["vehicle_model_id"]
    assert created_vehicle["vin"] == vehicle_data["vin"]
    assert created_vehicle["color_id"] == vehicle_data["color_id"]
    assert created_vehicle["is_urgent"] == vehicle_data["is_urgent"]
    assert "id" in created_vehicle
    assert "status_id" in created_vehicle
    assert "model" in created_vehicle
    assert "created_at" in created_vehicle
    assert "updated_at" in created_vehicle
    
    # Eliminar el vehículo
    delete_response = httpx_client.delete(f"/api/vehicles/{created_vehicle["id"]}", headers=headers)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT, f"Respuesta: {delete_response.text}"
    
    # Verificar que el vehículo ya no exista
    get_response = httpx_client.get(f"/api/vehicles/{created_vehicle["id"]}", headers=headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {get_response.text}"
    assert get_response.json()["detail"] == VEHICLE_NOT_FOUND

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_delete_vehicle_not_found(httpx_client, headers):
    """Prueba que la eliminación de un vehículo inexistente falle."""
    non_existing_vehicle_id = 999999
    response = httpx_client.delete(f"/api/vehicles/{non_existing_vehicle_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
    assert response.json()["detail"] == VEHICLE_NOT_FOUND




