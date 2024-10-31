# tests/test_auth.py
import pytest
import uuid
import httpx

# Generar un nombre de usuario único para la prueba
unique_username = f"user_{uuid.uuid4().hex}"

def test_register_login_refresh_logout():
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
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 3. Acceso a Ruta Protegida
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200
        protected_data = response.json()
        assert protected_data["username"] == unique_username
        assert protected_data["is_active"] is True

        # 4. Renovación de Token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 200
        new_tokens = response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        new_access_token = new_tokens["access_token"]
        new_refresh_token = new_tokens["refresh_token"]

        # 5. Verificar que el Refresh Token Antiguo está Revocado
        # Intentar renovar con el refresh_token antiguo debería fallar
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 401  # Unauthorized

        # 6. Acceso con el Nuevo Access Token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        response = client.get("/protected", headers=new_headers)
        assert response.status_code == 200
        protected_data = response.json()
        assert protected_data["username"] == unique_username
        assert protected_data["is_active"] is True

        # 7. Cierre de Sesión
        logout_data = {"refresh_token": new_refresh_token}
        response = client.post("/logout", json=logout_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # 8. Intentar Renovar Token Después del Logout
        response = client.post("/refresh", json={"refresh_token": new_refresh_token})
        assert response.status_code == 401  # Unauthorized

        # 9. Verificar que todos los Refresh Tokens del Usuario Están Revocados
        # Intentar renovar con cualquier refresh_token debería fallar
        response = client.post("/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 401  # Unauthorized

        # 10. Intentar Acceder con el Access Token Después del Logout (si aplica)
        # Dependiendo de cómo manejes los access tokens, esto podría seguir funcionando hasta que expire
        response = client.get("/protected", headers=new_headers)
        assert response.status_code == 200  # Sigue siendo válido hasta que expire
