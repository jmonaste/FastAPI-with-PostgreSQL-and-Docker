from typing import TYPE_CHECKING
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from routers import brands_router, qr_bar_codes_router, vehicle_models_router, vehicle_states_router, vehicle_types_router, vehicles_router, colors_router, auth_router


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

app = FastAPI()

app.include_router(vehicle_types_router.router)
app.include_router(brands_router.router)
app.include_router(vehicle_models_router.router)
app.include_router(vehicles_router.router)
app.include_router(qr_bar_codes_router.router) 
app.include_router(vehicle_states_router.router)
app.include_router(colors_router.router)
app.include_router(auth_router.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
revoked_tokens = set() # Lista para almacenar tokens revocados

#origins = ['http://localhost:3000','http://192.168.178.23:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (POST, GET, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)








