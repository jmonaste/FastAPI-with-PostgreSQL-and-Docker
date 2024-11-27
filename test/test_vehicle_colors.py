# tests/test_colors.py

import pytest
from fastapi import status

class TestColorsAPI:
    """
    Suite de pruebas para los endpoints de Colors.
    """

    def test_create_color_success(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba la creación exitosa de un color con datos válidos.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Red",
            "hex_code": "#FF0000",
            "rgb_code": "255,0,0"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        data = response.json()
        assert data["name"] == color_data["name"]
        assert data["hex_code"] == color_data["hex_code"]
        assert data["rgb_code"] == color_data["rgb_code"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Registrar el color creado para limpieza
        tracked_colors.append(data["id"])

    def test_create_color_missing_fields_name(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color sin el campo 'name' falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            # "name": "Blue",  # Campo 'name' omitido
            "hex_code": "#0000FF",
            "rgb_code": "0,0,255"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        name_error = next(
            (error for error in errors if error.get("loc") == ["body", "name"]),
            None
        )
        assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
        assert name_error.get("msg") == "Field required", "El mensaje de error para 'name' no es el esperado"

    def test_create_color_missing_fields_hex_code(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color sin el campo 'hex_code' falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Blue",
            # "hex_code": "#0000FF",  # Campo 'hex_code' omitido
            "rgb_code": "0,0,255"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        hex_error = next(
            (error for error in errors if error.get("loc") == ["body", "hex_code"]),
            None
        )
        assert hex_error is not None, "No se encontró un error de validación para el campo 'hex_code'"
        assert hex_error.get("msg") == "Field required", "El mensaje de error para 'hex_code' no es el esperado"

    def test_create_color_empty_name(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un nombre vacío o solo espacios falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "   ",  # Solo espacios en blanco
            "hex_code": "#FFFFFF",
            "rgb_code": "255,255,255"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        name_error = next(
            (error for error in errors if error.get("loc") == ["body", "name"]),
            None
        )
        assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
        assert "Name cannot be empty or blank" in name_error.get("msg", ""), "El mensaje de error para 'name' no es el esperado"

    def test_create_color_invalid_hex_code_missing_hash(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un hex_code sin '#' falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Blue",
            "hex_code": "0000FF",  # Falta el '#'
            "rgb_code": "0,0,255"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        hex_error = next(
            (error for error in errors if error.get("loc") == ["body", "hex_code"]),
            None
        )
        assert hex_error is not None, "No se encontró un error de validación para el campo 'hex_code'"
        assert "Value error, hex_code must be in the format #RRGGBB" in hex_error.get("msg", ""), "El mensaje de error para 'hex_code' no es el esperado"

    def test_create_color_invalid_hex_code_wrong_length(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un hex_code de longitud incorrecta falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Blue",
            "hex_code": "#FFF",  # Demasiado corto
            "rgb_code": "0,0,255"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        hex_error = next(
            (error for error in errors if error.get("loc") == ["body", "hex_code"]),
            None
        )
        assert hex_error is not None, "No se encontró un error de validación para el campo 'hex_code'"
        assert "Value error, hex_code must be in the format #RRGGBB" in hex_error.get("msg", ""), "El mensaje de error para 'hex_code' no es el esperado"

    def test_create_color_invalid_rgb_code_out_of_range(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un rgb_code fuera de rango falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Cyan",
            "hex_code": "#00FFFF",
            "rgb_code": "256,0,0"  # 256 es inválido
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        rgb_error = next(
            (error for error in errors if error.get("loc") == ["body", "rgb_code"]),
            None
        )
        assert rgb_error is not None, "No se encontró un error de validación para el campo 'rgb_code'"
        assert "Value error, Each component in rgb_code must be between 0 and 255" in rgb_error.get("msg", ""), "El mensaje de error para 'rgb_code' no es el esperado"

    def test_create_color_invalid_rgb_code_format(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un rgb_code con formato inválido falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Cyan",
            "hex_code": "#00FFFF",
            "rgb_code": "255-0-0"  # Formato incorrecto
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        rgb_error = next(
            (error for error in errors if error.get("loc") == ["body", "rgb_code"]),
            None
        )
        assert rgb_error is not None, "No se encontró un error de validación para el campo 'rgb_code'"
        assert "Value error, rgb_code must have three components separated by commas" in rgb_error.get("msg", ""), "El mensaje de error para 'rgb_code' no es el esperado"

    def test_create_color_invalid_hex_code_non_hex(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un hex_code con caracteres no hexadecimales falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "InvalidColor",
            "hex_code": "#ZZZZZZ",  # No es hexadecimal
            "rgb_code": "0,0,0"
        }
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])
        hex_error = next(
            (error for error in errors if error.get("loc") == ["body", "hex_code"]),
            None
        )
        assert hex_error is not None, "No se encontró un error de validación para el campo 'hex_code'"
        assert "Value error, hex_code must be in the format #RRGGBB" in hex_error.get("msg", ""), "El mensaje de error para 'hex_code' no es el esperado"

    def test_create_color_duplicate_name(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un nombre duplicado falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Purple",
            "hex_code": "#111180",
            "rgb_code": "128,0,128"
        }
        # Crear el primer color
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        tracked_colors.append(created_color["id"])

        # Intentar crear un color con el mismo nombre
        duplicate_color = {
            "name": "Purple",
            "hex_code": "#DA70D6",
            "rgb_code": "218,112,214"
        }
        response = httpx_client.post("/api/colors", json=duplicate_color, headers=headers)
        
        # Esperar un error 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color with this name already exists.", "Mensaje de error inesperado"

    def test_create_color_duplicate_hex_code(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un hex_code duplicado falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Blue",
            "hex_code": "#0000F1",
            "rgb_code": "0,0,255"
        }
        # Crear el primer color
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        tracked_colors.append(created_color["id"])

        # Intentar crear un color con el mismo hex_code
        duplicate_color = {
            "name": "Sky Blue",
            "hex_code": "#0000F1",  # Hex code duplicado
            "rgb_code": "135,206,235"
        }
        response = httpx_client.post("/api/colors", json=duplicate_color, headers=headers)
        
        # Esperar un error 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color with this hex_code already exists.", "Mensaje de error inesperado"

    def test_create_color_duplicate_name_and_hex_code(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la creación de un color con un nombre y hex_code duplicados falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        color_data = {
            "name": "Yellow",
            "hex_code": "#FFFF01",
            "rgb_code": "255,255,0"
        }
        # Crear el primer color
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        tracked_colors.append(created_color["id"])

        # Intentar crear un color con el mismo name y hex_code
        duplicate_color = {
            "name": "Yellow",
            "hex_code": "#FFFF01",
            "rgb_code": "255,255,0"
        }
        response = httpx_client.post("/api/colors", json=duplicate_color, headers=headers)
        
        # Esperar un error 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT, f"Respuesta: {response.text}"
        # Puedes elegir qué detalle verificar, ya que puede ser de 'name' o 'hex_code'
        assert response.json()["detail"] in [
            "Color with this name already exists.",
            "Color with this hex_code already exists."
        ], "Mensaje de error inesperado"

    def test_get_all_colors_after_creations(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la lista de colores incluye los colores creados.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear algunos colores
        colors = [
            {"name": "Navy", "hex_code": "#000081", "rgb_code": "0,0,129"},
            {"name": "Lime", "hex_code": "#00FF01", "rgb_code": "0,255,1"},
            {"name": "Maroon", "hex_code": "#800001", "rgb_code": "128,0,1"},
        ]
        for color in colors:
            response = httpx_client.post("/api/colors", json=color, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
            data = response.json()
            tracked_colors.append(data["id"])

        # Recuperar todos los colores
        response = httpx_client.get("/api/colors", headers=headers)
        assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
        data = response.json()
        assert isinstance(data, list), "La respuesta debe ser una lista"
        for color in colors:
            assert any(c["name"] == color["name"] for c in data), f"No se encontró el color {color['name']} en la respuesta"

    def test_get_color_by_id_success(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba la recuperación exitosa de un color por su ID.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear un color válido
        color_data = {"name": "Orange", "hex_code": "#FFA501", "rgb_code": "255,165,1"}
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        color_id = created_color["id"]
        tracked_colors.append(color_id)

        # Recuperar el color por ID
        response = httpx_client.get(f"/api/colors/{color_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
        data = response.json()
        assert data["id"] == color_id, "El ID del color recuperado no coincide"
        assert data["name"] == color_data["name"], "El nombre del color recuperado no coincide"
        assert data["hex_code"] == color_data["hex_code"], "El hex_code del color recuperado no coincide"

    def test_get_color_by_id_not_found(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la recuperación de un color inexistente falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        response = httpx_client.get("/api/colors/9999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color not found"

    def test_update_color_success(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba la actualización exitosa de un color existente.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear un color válido
        color_data = {"name": "Cyan", "hex_code": "#00FFFF", "rgb_code": "0,255,255"}
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        color_id = created_color["id"]
        tracked_colors.append(color_id)

        # Actualizar el color
        updated_data = {"name": "Dark Cyan", "hex_code": "#008B8B", "rgb_code": "0,139,139"}
        response = httpx_client.put(f"/api/colors/{color_id}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
        data = response.json()
        assert data["id"] == color_id, "El ID del color actualizado no coincide"
        assert data["name"] == updated_data["name"], "El nombre del color actualizado no coincide"
        assert data["hex_code"] == updated_data["hex_code"], "El hex_code del color actualizado no coincide"
        assert data["rgb_code"] == updated_data["rgb_code"], "El rgb_code del color actualizado no coincide"

    def test_update_color_not_found(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la actualización de un color inexistente falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        updated_data = {"name": "Magenta", "hex_code": "#FF00FF", "rgb_code": "255,0,255"}
        response = httpx_client.put("/api/colors/9999", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color not found."

    def test_update_color_invalid_data(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la actualización de un color con datos inválidos falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear un color válido
        color_data = {"name": "Brown", "hex_code": "#A5200A", "rgb_code": "165,42,42"}
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        color_id = created_color["id"]
        tracked_colors.append(color_id)

        # Intentar actualizar con un nombre vacío y hex_code inválido
        updated_data = {"name": "   ", "hex_code": "A52111", "rgb_code": "165,42,42"}  # Falta el '#'
        response = httpx_client.put(f"/api/colors/{color_id}", json=updated_data, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Respuesta: {response.text}"
        errors = response.json().get("detail", [])

        # Verificar error para 'name'
        name_error = next(
            (error for error in errors if error.get("loc") == ["body", "name"]),
            None
        )
        assert name_error is not None, "No se encontró un error de validación para el campo 'name'"
        assert "Name cannot be empty or blank" in name_error.get("msg", ""), "El mensaje de error para 'name' no es el esperado"

        # Verificar error para 'hex_code'
        hex_error = next(
            (error for error in errors if error.get("loc") == ["body", "hex_code"]),
            None
        )
        assert hex_error is not None, "No se encontró un error de validación para el campo 'hex_code'"
        assert "Value error, hex_code must be in the format #RRGGBB" in hex_error.get("msg", ""), "El mensaje de error para 'hex_code' no es el esperado"

    def test_update_color_with_duplicate_name(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la actualización de un color con un nombre duplicado falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear dos colores distintos
        color1 = {"name": "Teal", "hex_code": "#008080", "rgb_code": "0,128,128"}
        color2 = {"name": "Olive", "hex_code": "#808990", "rgb_code": "128,128,0"}

        response1 = httpx_client.post("/api/colors", json=color1, headers=headers)
        assert response1.status_code == status.HTTP_201_CREATED, f"Respuesta: {response1.text}"
        color1_id = response1.json()["id"]
        tracked_colors.append(color1_id)

        response2 = httpx_client.post("/api/colors", json=color2, headers=headers)
        assert response2.status_code == status.HTTP_201_CREATED, f"Respuesta: {response2.text}"
        color2_id = response2.json()["id"]
        tracked_colors.append(color2_id)

        # Intentar actualizar color2 con el nombre de color1
        updated_data = {"name": "Teal", "hex_code": "#556B2F", "rgb_code": "85,107,47"}
        response = httpx_client.put(f"/api/colors/{color2_id}", json=updated_data, headers=headers)
        
        # Esperar un error 409 Conflict
        assert response.status_code == status.HTTP_409_CONFLICT, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color with this name already exists.", "Mensaje de error inesperado"

    def test_get_all_colors_after_creations(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la lista de colores incluye los colores creados.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear algunos colores
        colors = [
            {"name": "Navy", "hex_code": "#000081", "rgb_code": "0,0,129"},
            {"name": "Lime", "hex_code": "#00FF01", "rgb_code": "0,255,1"},
            {"name": "Maroon", "hex_code": "#800001", "rgb_code": "128,0,1"},
        ]
        for color in colors:
            response = httpx_client.post("/api/colors", json=color, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
            data = response.json()
            tracked_colors.append(data["id"])

        # Recuperar todos los colores
        response = httpx_client.get("/api/colors", headers=headers)
        assert response.status_code == status.HTTP_200_OK, f"Respuesta: {response.text}"
        data = response.json()
        assert isinstance(data, list), "La respuesta debe ser una lista"
        for color in colors:
            assert any(c["name"] == color["name"] for c in data), f"No se encontró el color {color['name']} en la respuesta"

    def test_delete_color_success(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba la eliminación exitosa de un color existente.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        # Crear un color válido
        color_data = {"name": "Silver", "hex_code": "#C0C0C1", "rgb_code": "192,192,193"}
        response = httpx_client.post("/api/colors", json=color_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED, f"Respuesta: {response.text}"
        created_color = response.json()
        color_id = created_color["id"]

        # Eliminar el color
        response = httpx_client.delete(f"/api/colors/{color_id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT, f"Respuesta: {response.text}"

        # Verificar que el color ya no exista
        response = httpx_client.get(f"/api/colors/{color_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color not found"

    def test_delete_color_not_found(self, httpx_client, auth_tokens, tracked_colors):
        """
        Prueba que la eliminación de un color inexistente falle.
        """
        headers = {"Authorization": f"Bearer {auth_tokens['access_token']}"}
        response = httpx_client.delete("/api/colors/9999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND, f"Respuesta: {response.text}"
        assert response.json()["detail"] == "Color not found"
