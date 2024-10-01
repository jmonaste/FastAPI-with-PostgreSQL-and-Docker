import datetime as _dt
import pydantic as _pydantic
from enum import Enum
from typing import Optional







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

class VehicleStatus(Enum):
    INIT = 1
    WASHED_ONLY = 2
    WASHED_AND_FINISHED = 3


