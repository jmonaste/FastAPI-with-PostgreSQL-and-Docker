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
    VEHICLE_NOT_FOUND,
    STATE_NOT_FOUND,
    STATE_COMMENT_NOT_FOUND
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
def unique_color_hexcode():
    """Genera un código hexadecimal de color único para cada prueba."""
    # Obtiene un entero de 128 bits desde UUID, aplica una máscara para obtener los 24 bits inferiores
    # y lo formatea como un código hexadecimal de 6 dígitos precedido por '#'.
    return f"#{uuid.uuid4().int & 0xFFFFFF:06X}"

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
            "hex_code": "#FF0099",
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
async def test_get_allowed_transitions_success(
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
    """Prueba obtener transiciones permitidas para un vehículo existente."""
    
    # Crear un vehículo usando la misma forma que en test_create_vehicle_success
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
            "hex_code": "#FF0099",
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
    
    # Obtener las transiciones permitidas
    allowed_transitions_response = httpx_client.get(f"/api/vehicles/{created_vehicle['id']}/allowed_transitions", headers=headers)
    assert allowed_transitions_response.status_code == status.HTTP_200_OK, f"Respuesta: {allowed_transitions_response.text}"
    allowed_transitions = allowed_transitions_response.json()
    
    # Aserciones sobre las transiciones permitidas
    assert isinstance(allowed_transitions, list), "Las transiciones permitidas deben ser una lista."
    for transition in allowed_transitions:
        assert "from_state_id" in transition
        assert "to_state_id" in transition

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_allowed_transitions_vehicle_not_found(
    httpx_client, 
    headers
):
    """Prueba obtener transiciones permitidas para un vehículo que no existe."""
    
    non_existent_vehicle_id = 999999  # Asume que este ID no existe
    
    allowed_transitions_response = httpx_client.get(f"/api/vehicles/{non_existent_vehicle_id}/allowed_transitions", headers=headers)
    assert allowed_transitions_response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {allowed_transitions_response.text}"
    assert allowed_transitions_response.json()["detail"] == VEHICLE_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_states_success(
    httpx_client, 
    headers
):
    """Prueba obtener todos los estados de vehículos existentes."""
    
    response = httpx_client.get("/api/states", headers=headers)
    assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
    states = response.json()
    
    # Aserciones sobre la lista de estados
    assert isinstance(states, list), "La respuesta debe ser una lista de estados."
    for state in states:
        assert "id" in state
        assert "name" in state

@pytest.mark.asyncio
async def test_get_vehicle_state_history_success(
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
    """Prueba obtener el historial de estados de un vehículo existente."""
    
    # Crear un vehículo usando la misma forma que en test_create_vehicle_success
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
            "hex_code": "#FF0099",
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
    
    # Obtener el historial de estados
    state_history_response = httpx_client.get(f"/api/vehicles/{created_vehicle['id']}/state_history", headers=headers)
    assert state_history_response.status_code == status.HTTP_200_OK, f"Respuesta: {state_history_response.text}"
    state_history = state_history_response.json()
    
    # Aserciones sobre el historial de estados
    assert isinstance(state_history, list), "El historial de estados debe ser una lista."
    for entry in state_history:
        assert "vehicle_id" in entry
        assert "from_state_id" in entry
        assert "to_state_id" in entry
        assert "user_id" in entry
        assert "timestamp" in entry
        # 'comment_id' puede ser opcional
    
    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_vehicle_current_state_success(
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
    """Prueba obtener el estado actual de un vehículo existente."""
    
    # Crear un vehículo usando la misma forma que en test_create_vehicle_success
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
            "hex_code": "#FF0099",
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
      
    # Obtener el estado actual del vehículo
    current_state_response = httpx_client.get(f"/api/vehicles/{created_vehicle['id']}/state", headers=headers)
    assert current_state_response.status_code == status.HTTP_200_OK, f"Respuesta: {current_state_response.text}"
    current_state = current_state_response.json()
    
    # Aserciones sobre el estado actual
    assert "id" in current_state
    assert "name" in current_state
    assert current_state["id"] == created_vehicle["status_id"]

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_change_vehicle_state_success(
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
    """Prueba cambiar el estado de un vehículo existente con una transición permitida."""
    
    # Crear un vehículo usando la misma forma que en test_create_vehicle_success
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
            "hex_code": "#FF0099",
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
        
    # Cambiar el estado del vehículo
    change_state_data = {
        "new_state_id": 2,
        "comment_id": None  # O proporciona un comment_id válido si es necesario
    }
    change_state_response = httpx_client.put(f"/api/vehicles/{created_vehicle['id']}/state", headers=headers, json=change_state_data)
    assert change_state_response.status_code == status.HTTP_200_OK, f"Respuesta: {change_state_response.text}"
    state_history = change_state_response.json()
    
    # Aserciones sobre el historial de cambio de estado
    assert "vehicle_id" in state_history
    assert "from_state_id" in state_history
    assert "to_state_id" in state_history
    assert "user_id" in state_history
    assert "timestamp" in state_history
    assert state_history["to_state_id"] == 2
    
    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_change_vehicle_state_invalid_transition(
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
    """Prueba cambiar el estado de un vehículo existente con una transición permitida."""
    
    # Crear un vehículo usando la misma forma que en test_create_vehicle_success
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
            "hex_code": "#FF0099",
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
        
    # Cambiar el estado del vehículo
    change_state_data = {
        "new_state_id": 3,
        "comment_id": None  # O proporciona un comment_id válido si es necesario
    }
    change_state_response = httpx_client.put(f"/api/vehicles/{created_vehicle['id']}/state", headers=headers, json=change_state_data)
    assert change_state_response.status_code == status.HTTP_400_BAD_REQUEST, f"Respuesta: {change_state_response.text}"
    assert change_state_response.json()["detail"] == "La transición al nuevo estado no es válida."

    # Limpieza
    tracked_vehicles.append(created_vehicle["id"])
    tracked_vehicle_models.append(vehicle_model_data["id"])
    tracked_vehicle_types.append(vehicle_type_data["id"])
    tracked_colors.append(color_id)
    tracked_brands.append(brand_data["id"])

@pytest.mark.asyncio
async def test_get_state_comments_state_not_found(
    httpx_client, 
    headers
):
    """Prueba obtener comentarios para un estado que no existe."""
    
    non_existent_state_id = 999999  # Asume que este ID no existe
    
    comments_response = httpx_client.get(f"/api/states/{non_existent_state_id}/comments", headers=headers)
    assert comments_response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {comments_response.text}"
    assert comments_response.json()["detail"] == STATE_NOT_FOUND





































