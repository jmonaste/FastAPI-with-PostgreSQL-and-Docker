from typing import TYPE_CHECKING, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import database as _database
import models as _models
import schemas as _schemas
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import joinedload
import datetime as _dt
from typing import Optional

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# region Brand Functions
async def create_brand(
    brand: _schemas.BrandCreate, db: "Session"
) -> _schemas.Brand:
    brand_model = _models.Brand(
        **brand.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    db.add(brand_model)
    db.commit()
    db.refresh(brand_model)
    return _schemas.Brand.from_orm(brand_model)

async def get_all_brands(db: "Session") -> List[_schemas.Brand]:
    brands = db.query(_models.Brand).all()
    return list(map(_schemas.Brand.from_orm, brands))

async def get_brand(brand_id: int, db: "Session") -> _schemas.Brand:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        return _schemas.Brand.from_orm(brand)
    return None

async def delete_brand(brand_id: int, db: "Session") -> bool:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        db.delete(brand)
        db.commit()
        return True
    return False

async def update_brand(
    brand_data: _schemas.BrandBase, brand_id: int, db: "Session"
) -> _schemas.Brand:
    brand = db.query(_models.Brand).filter(_models.Brand.id == brand_id).first()
    if brand:
        brand.name = brand_data.name

        db.commit()
        db.refresh(brand)
        return _schemas.Brand.from_orm(brand)
    return None

# endregion

# region Model Functions
async def create_model(
    model: _schemas.ModelCreate, db: "Session"
) -> _schemas.Model:
    # Verificar si la marca existe
    brand = db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand with ID {model.brand_id} does not exist.")
    
    # Si la marca existe, continuar con la creación del modelo
    model_obj = _models.Model(
        **model.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    db.add(model_obj)
    db.commit()
    db.refresh(model_obj)
    return _schemas.Model.from_orm(model_obj)

async def get_all_models(db: "Session") -> List[_schemas.Model]:
    models = db.query(_models.Model).all()
    return list(map(_schemas.Model.from_orm, models))

async def get_model(model_id: int, db: "Session") -> _schemas.Model:
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        return _schemas.Model.from_orm(model)
    return None

async def delete_model(model_id: int, db: "Session") -> bool:
    model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    if model:
        db.delete(model)
        db.commit()
        return True
    return False

async def update_model(model_id: int, model: _schemas.ModelCreate, db: "Session"):
    existing_model = db.query(_models.Model).filter(_models.Model.id == model_id).first()
    
    if not existing_model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Verificar si la marca existe
    if not db.query(_models.Brand).filter(_models.Brand.id == model.brand_id).first():
        raise HTTPException(status_code=404, detail="Brand not found")

    for key, value in model.dict(exclude_unset=True).items():
        setattr(existing_model, key, value)

    db.commit()
    db.refresh(existing_model)
    return existing_model

# endregion

# region VehicleType Functions
async def create_vehicle_type(
    vehicle_type: _schemas.VehicleTypeCreate, db: "Session"
) -> _schemas.VehicleType:
    vehicle_type_model = _models.VehicleType(
        **vehicle_type.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
        )
    
    db.add(vehicle_type_model)
    db.commit()
    db.refresh(vehicle_type_model)
    return _schemas.VehicleType.from_orm(vehicle_type_model)

async def get_all_vehicle_types(db: "Session") -> List[_schemas.VehicleType]:
    vehicle_types = db.query(_models.VehicleType).all()
    return list(map(_schemas.VehicleType.from_orm, vehicle_types))

async def get_vehicle_type(vehicle_type_id: int, db: "Session") -> _schemas.VehicleType:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        return _schemas.VehicleType.from_orm(vehicle_type)
    return None

async def delete_vehicle_type(vehicle_type_id: int, db: "Session") -> bool:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        db.delete(vehicle_type)
        db.commit()
        return True
    return False

async def update_vehicle_type(
    vehicle_type_data: _schemas.VehicleTypeBase, vehicle_type_id: int, db: "Session"
) -> _schemas.VehicleType:
    vehicle_type = db.query(_models.VehicleType).filter(_models.VehicleType.id == vehicle_type_id).first()
    if vehicle_type:
        vehicle_type.type_name = vehicle_type_data.type_name

        db.commit()
        db.refresh(vehicle_type)
        return _schemas.VehicleType.from_orm(vehicle_type)
    return None

# endregion

# region Vehicle Functions



# Create Vehicle
async def create_vehicle(
    vehicle: _schemas.VehicleCreate, db: "Session", user_id: int
) -> _schemas.Vehicle:
    
     # Obtener el estado inicial desde la base de datos
    initial_state = db.query(_models.State).filter_by(is_initial=True).first()

    if not initial_state:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No initial state configured in the system."
        )

    # Agregar el estado inicial a los datos del vehículo
    vehicle_data = vehicle.dict(exclude_unset=True)
    vehicle_data.update({"status_id": initial_state.id})

    # Crear el modelo de vehículo
    vehicle_model = _models.Vehicle(
        **vehicle_data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(vehicle_model)
    db.commit()
    db.refresh(vehicle_model)

    # Registrar el estado inicial en el historial
    await register_state_history(
        vehicle_id=vehicle_model.id,
        from_state_id=None,  # No hay estado previo ya que es el primer estado
        to_state_id=vehicle_model.status_id,  # Estado inicial
        user_id=user_id,
        db=db,
        comments="Creación del vehículo con estado inicial"
    )

    return _schemas.Vehicle.from_orm(vehicle_model)

# Get Vehicle by ID
def get_vehicle(db: "Session", vehicle_id: int):
    return db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()

# Get All Vehicles with Pagination
async def get_vehicles(db: "Session", skip: int = 0, limit: int = 10) -> List[_schemas.Vehicle]:
    # Consulta con SQLAlchemy cargando las relaciones con joinedload
    vehicles = (
        db.query(_models.Vehicle)
        .options(
            joinedload(_models.Vehicle.model).joinedload(_models.Model.vehicle_type)  # Cargamos model y vehicle_type
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Convierte los objetos del modelo ORM a esquemas Pydantic
    return list(map(_schemas.Vehicle.from_orm, vehicles))


# Get Vehicles Not in Final State with Pagination
async def get_vehicles_not_in_final_state(db: "Session", skip: int = 0, limit: int = 30) -> List[_schemas.Vehicle]:
    # Consulta con SQLAlchemy para obtener vehículos que no están en un estado final
    vehicles = (
        db.query(_models.Vehicle)
        .join(_models.State, _models.Vehicle.status_id == _models.State.id)  # Join con la tabla de estados
        .filter(_models.State.is_final == False)  # Filtrar por estados no finales
        .options(
            joinedload(_models.Vehicle.model).joinedload(_models.Model.vehicle_type)  # Cargar model y vehicle_type
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convertir los objetos del modelo ORM a esquemas Pydantic
    return list(map(_schemas.Vehicle.from_orm, vehicles))




# Update Vehicle
def update_vehicle(db: "Session", vehicle_id: int, vehicle: _schemas.VehicleCreate):
    db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        return None
    db_vehicle.model_id = vehicle.model_id
    db_vehicle.vehicle_type_id = vehicle.vehicle_type_id
    db_vehicle.vin = vehicle.vin
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

# Delete Vehicle
def delete_vehicle(db: "Session", vehicle_id: int):
    db_vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()

    if not db_vehicle:
        return False
    
    # Borrar el historial de estados asociado al vehículo
    db.query(_models.StateHistory).filter(_models.StateHistory.vehicle_id == vehicle_id).delete()

    # Borrar el vehículo
    db.delete(db_vehicle)
    db.commit()
    return True

# endregion

# region State Management Functions

async def register_state_history(
    vehicle_id: int, 
    from_state_id: int, 
    to_state_id: int, 
    user_id: int, 
    db: "Session",
    comments: str = ""
):
    state_history_entry = _models.StateHistory(
        vehicle_id=vehicle_id,
        from_state_id=from_state_id,
        to_state_id=to_state_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        comments=comments
    )

    db.add(state_history_entry)
    db.commit()
    db.refresh(state_history_entry)

async def get_allowed_transitions_for_vehicle(vehicle_id: int, db: Session) -> List[_schemas.Transition]:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("El vehículo no existe.")

    # Obtener las transiciones permitidas desde el estado actual del vehículo
    allowed_transitions = db.query(_models.Transition).filter(
        _models.Transition.from_state_id == vehicle.status_id
    ).all()

    return [_schemas.Transition.from_orm(transition) for transition in allowed_transitions]

async def get_all_states(db: Session) -> List[_schemas.State]:
    states = db.query(_models.State).all()
    return [ _schemas.State.from_orm(state) for state in states ]

async def get_vehicle_state_history(vehicle_id: int, db: Session) -> List[_schemas.StateHistory]:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("El vehículo no existe.")

    # Obtener el historial de estados del vehículo
    state_history = db.query(_models.StateHistory).filter(
        _models.StateHistory.vehicle_id == vehicle_id
    ).order_by(_models.StateHistory.timestamp).all()

    return [_schemas.StateHistory.from_orm(entry) for entry in state_history]

async def get_vehicle_current_state(db: Session, vehicle_id: int) -> _schemas.State:
    # Obtener el vehículo de la base de datos
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="El vehículo no existe.")

    # Obtener el estado actual del vehículo
    state = db.query(_models.State).filter(_models.State.id == vehicle.status_id).first()
    if not state:
        raise HTTPException(status_code=500, detail="El estado del vehículo no está configurado.")

    return _schemas.State.from_orm(state)

async def change_vehicle_state(
    vehicle_id: int,
    new_state_id: int,
    user_id: int,
    db: Session,
    comments: Optional[str] = None
) -> _schemas.StateHistory:
    # Obtener el vehículo
    vehicle = db.query(_models.Vehicle).filter(_models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("El vehículo no existe.")

    # Obtener el nuevo estado
    new_state = db.query(_models.State).filter(_models.State.id == new_state_id).first()
    if not new_state:
        raise ValueError("El nuevo estado no existe.")

    # Verificar si la transición es válida
    valid_transition = db.query(_models.Transition).filter(
        _models.Transition.from_state_id == vehicle.status_id,
        _models.Transition.to_state_id == new_state_id
    ).first()

    if not valid_transition:
        raise ValueError("La transición al nuevo estado no es válida.")

    # Actualizar el estado del vehículo
    vehicle.status_id = new_state_id
    vehicle.updated_at = _dt.datetime.utcnow()
    db.commit()
    db.refresh(vehicle)

    # Crear una nueva entrada en el historial de estados
    state_history_entry = _models.StateHistory(
        vehicle_id=vehicle_id,
        from_state_id=valid_transition.from_state_id,
        to_state_id=valid_transition.to_state_id,
        user_id=user_id,
        timestamp=_dt.datetime.utcnow(),
        comments=comments
    )
    db.add(state_history_entry)
    db.commit()
    db.refresh(state_history_entry)

    return _schemas.StateHistory.from_orm(state_history_entry)

async def get_state_comments(state_id: int, db: Session) -> List[_schemas.StateCommentRead]:
    """
    Obtiene los comentarios predefinidos para un estado específico.
    """
    # Verificar si el estado existe
    state = db.query(_models.State).filter(_models.State.id == state_id).first()
    if not state:
        raise ValueError("Estado no encontrado.")
    
    # Obtener los comentarios asociados al estado
    comments = db.query(_models.StateComment).filter(_models.StateComment.state_id == state_id).all()
    
    return [_schemas.StateCommentRead.from_orm(comment) for comment in comments]

# endregion

