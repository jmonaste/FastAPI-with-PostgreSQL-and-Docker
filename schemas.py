import datetime as _dt
import pydantic as _pydantic





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




class VehicleBase(_pydantic.BaseModel):
    vehicle_model_id: int
    vehicle_type_id: int

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    vehicle_model: Model
    vehicle_type: VehicleType

    class Config:
        from_attributes = True