import datetime as _dt
import pydantic as _pydantic



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

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    model: Model  # Retornamos el modelo completo en la respuesta
    vehicle_type: str  # Añadimos el tipo derivado del modelo
    created_at: _dt.datetime
    updated_at: _dt.datetime

    class Config:
        from_attributes = True

# endregion