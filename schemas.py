import datetime as _dt
import pydantic as _pydantic
from enum import Enum
from typing import Optional

class _BaseContact(_pydantic.BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str

class Contact(_BaseContact):
    id: int
    date_created: _dt.datetime

    class Config:
        from_attributes = True
        
class CreateContact(_BaseContact):
    pass




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




class ModelBase(_pydantic.BaseModel):
    name: str
    brand_id: int

class ModelCreate(ModelBase):
    pass

class Model(ModelBase):
    id: int
    brand: Brand
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True






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


class VinCodeSourceEnum(str, Enum):
    qr = 'qr'
    bar_code = 'bar_code'


class VehicleBase(_pydantic.BaseModel):
    vehicle_model_id: int
    vehicle_type_id: int
    is_urgency: bool
    vin_code_source: VinCodeSourceEnum
    is_damaged: bool
    is_only_wash: bool
    status: Optional[int]

class VehicleCreate(VehicleBase):
    plate: Optional[str] = None

class Vehicle(VehicleBase):
    id: int
    vehicle_model: Model
    vehicle_type: VehicleType
    created_at: _dt.datetime
    updated_at: _dt.datetime
    plate: Optional[str] = None

    class Config:
        from_attributes = True