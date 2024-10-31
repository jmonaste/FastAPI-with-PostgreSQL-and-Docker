import datetime as _dt
import pydantic as _pydantic
from pydantic import BaseModel
from typing import Optional, List



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
    
    class Config:
        from_attributes = True


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
    
    class Config:
        from_attributes = True

# endregion

# region Model definition

class ModelBase(_pydantic.BaseModel):
    name: str
    brand_id: int
    type_id: int  # El tipo de vehículo se define a nivel de modelo

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    brand: Brand
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True

# endregion

# region Vehicle definition

class VehicleBase(_pydantic.BaseModel):
    vehicle_model_id: int
    vin: str
    color_id: int
    is_urgent: bool
    
    class Config:
        arbitrary_types_allowed = True  # Permite tipos arbitrarios

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    status_id: int
    model: Model  # Retornamos el modelo completo en la respuesta
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True


class StateChangeRequest(BaseModel):
    new_state_id: int
    comments: Optional[str] = None
    
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
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

# endregion

# region StateHistory definition

class StateHistoryBase(BaseModel):
    vehicle_id: int
    from_state_id: Optional[int] = None
    to_state_id: int
    user_id: int
    comments: Optional[str] = None

class StateHistoryCreate(StateHistoryBase):
    pass

class StateHistoryUpdate(StateHistoryBase):
    pass

class StateHistory(StateHistoryBase):
    id: int
    timestamp: _dt.datetime

    class Config:
        from_attributes = True
        
# endregion

# region StateComment definition

class StateCommentBase(_pydantic.BaseModel):
    comment: str

class StateCommentCreate(StateCommentBase):
    state_id: int  # ID del estado al que pertenece el comentario

class StateCommentRead(StateCommentBase):
    id: int
    state_id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

class StateCommentUpdate(StateCommentBase):
    pass

# endregion

# region Color definition

class ColorBase(BaseModel):
    name: str
    hex_code: str
    rgb_code: Optional[str] = None

class ColorCreate(ColorBase):
    pass

class Color(ColorBase):
    id: int
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

# endregion


