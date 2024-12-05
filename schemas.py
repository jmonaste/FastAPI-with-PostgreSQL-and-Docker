import datetime as _dt
import pydantic as _pydantic
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
import re


# region User definition

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

# endregion

# region Brand definition

class BrandBase(_pydantic.BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime
    
    model_config = ConfigDict(from_attributes=True)

# endregion

# region Model definition

class ModelBase(_pydantic.BaseModel):
    name: str = Field(..., description="Nombre del modelo de vehículo")
    brand_id: int = Field(..., description="ID de la marca asociada")
    type_id: int  = Field(..., description="ID del tipo de vehículo asociado")

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or blank')
        return v.strip()

    @field_validator('brand_id', 'type_id')
    def ids_must_be_positive(cls, v, field):
        if not isinstance(v, int) or v <= 0:
            raise ValueError(f"{field.name} must be a positive integer")
        return v

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    brand: Brand
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

# endregion

# region VehicleType definition

class VehicleTypeBase(_pydantic.BaseModel):
    type_name: str

class VehicleTypeCreate(VehicleTypeBase):
    pass

class VehicleType(VehicleTypeBase):
    id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

# endregion

# region Color definition

class ColorBase(BaseModel):
    name: str = Field(..., description="Nombre del color")
    hex_code: str = Field(..., description="Código hexadecimal del color (Ej: '#FF0000')")
    rgb_code: Optional[str] = Field(None, description="Código RGB del color (Ej: '255,0,0')")

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        """
        Valida que el campo 'name' no esté vacío ni contenga solo espacios en blanco.
        """
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or blank')
        return v.strip()

    @field_validator('hex_code')
    def hex_code_must_be_valid(cls, v):
        """
        Valida que el campo 'hex_code' siga el formato '#RRGGBB'.
        """
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('hex_code must be in the format #RRGGBB')
        return v.upper()

    @field_validator('rgb_code')
    def rgb_code_must_be_valid(cls, v):
        """
        Valida que el campo 'rgb_code' siga el formato 'R,G,B' donde R, G, B están entre 0 y 255.
        """
        if v is None:
            return v
        parts = v.split(',')
        if len(parts) != 3:
            raise ValueError('rgb_code must have three components separated by commas')
        try:
            rgb = [int(part) for part in parts]
        except ValueError:
            raise ValueError('rgb_code must contain integers')
        if any(not (0 <= num <= 255) for num in rgb):
            raise ValueError('Each component in rgb_code must be between 0 and 255')
        return v

class ColorCreate(ColorBase):
    pass

class Color(ColorBase):
    id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

# endregion

# region StateComment definition

class StateCommentBase(BaseModel):
    comment: str

class StateCommentRead(StateCommentBase):
    id: int
    state_id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

class StateCommentCreate(StateCommentBase):
    state_id: int  # ID del estado al que pertenece el comentario

class StateCommentUpdate(StateCommentBase):
    pass

class StateComment(StateCommentBase):
    pass

    model_config = ConfigDict(from_attributes=True)

# endregion

# region State definition

class StateBase(BaseModel):
    code: str
    name: str
    description: str
    is_initial: bool = False
    is_final: bool = False
    order: Optional[int]
    active: bool = True
    icon: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    comments: Optional[str] = None

class StateCreate(StateBase):
    pass

class StateUpdate(StateBase):
    pass

class State(StateBase):
    id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

class StateChangeRequest(BaseModel):
    new_state_id: int
    comment_id: Optional[int] = None
    
# endregion

# region Vehicle definition

class VehicleExistsResponse(BaseModel):
    id: int
    created: bool = False

    
class VehicleUpdate(BaseModel):
    vehicle_model_id: int
    vin: str = Field(..., min_length=17, max_length=17, description="Vehicle Identification Number")
    color_id: int
    is_urgent: bool = False

    urgency_delivery_date: Optional[_dt.datetime] = None  # Fecha de entrega de urgencia
    urgency_delivery_time: Optional[_dt.time] = None      # Hora de entrega de urgencia
    urgency_reason: Optional[str] = None              # Motivo de la urgencia
    observations: Optional[str] = None                # Observaciones (texto)

    @field_validator('vin')
    def vin_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("VIN cannot be empty or null.")
        return v

class VehicleBase(_pydantic.BaseModel):
    vehicle_model_id: int
    vin: str
    color_id: int
    is_urgent: bool

    urgency_delivery_date: Optional[_dt.datetime] = None  # Fecha de entrega de urgencia
    urgency_delivery_time: Optional[_dt.time] = None      # Hora de entrega de urgencia
    urgency_reason: Optional[str] = None              # Motivo de la urgencia
    observations: Optional[str] = None                # Observaciones (texto)

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Reemplazo de Config

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    status_id: int
    model: Model  # Retornamos el modelo completo en la respuesta
    color: Color
    status: State
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

# endregion

# region Transition definition

class TransitionBase(BaseModel):
    from_state_id: int
    to_state_id: int
    condition: Optional[str] = None
    action: Optional[str] = None
    active: bool = True

class TransitionCreate(TransitionBase):
    pass

class TransitionUpdate(TransitionBase):
    pass

class Transition(TransitionBase):
    id: int
    from_state: State
    to_state: State
    created_at: _dt.datetime
    updated_at: _dt.datetime

    model_config = ConfigDict(from_attributes=True)

# endregion

# region StateHistory definition

class StateComment(BaseModel):
    id: int
    state_id: int
    comment_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class StateHistoryBase(BaseModel):
    vehicle_id: int
    from_state_id: Optional[int] = None
    to_state_id: int
    user_id: int
    #comment_id: Optional[int] = None
    comment: Optional[StateComment] = None


class StateHistoryCreate(StateHistoryBase):
    pass

class StateHistoryUpdate(StateHistoryBase):
    pass

class StateHistory(StateHistoryBase):
    id: int
    timestamp: _dt.datetime

    model_config = ConfigDict(from_attributes=True)
        
# endregion




# region imagen en base64 definition
class ImageBase64Request(BaseModel):
    image: str
# endregion

