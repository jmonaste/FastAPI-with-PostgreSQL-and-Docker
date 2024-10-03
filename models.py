import datetime as _dt
import sqlalchemy as _sql
from sqlalchemy.orm import relationship
import database as _database
from sqlalchemy import func 



class Brand(_database.Base):
    __tablename__ = 'brands'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, unique=True, index=True)
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    models = relationship("Model", back_populates="brand")

class Model(_database.Base):
    __tablename__ = 'models'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    brand_id = _sql.Column(_sql.Integer, _sql.ForeignKey('brands.id'))
    type_id = _sql.Column(_sql.Integer, _sql.ForeignKey('vehicle_types.id'))  # Relación con VehicleType
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())

    brand = relationship('Brand', back_populates='models')
    vehicle_type = relationship('VehicleType', back_populates='models')
    vehicles = relationship('Vehicle', back_populates='model')

class VehicleType(_database.Base):
    __tablename__ = 'vehicle_types'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    type_name = _sql.Column(_sql.String, unique=True, index=True)
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    models = relationship('Model', back_populates='vehicle_type')

class Vehicle(_database.Base):
    __tablename__ = 'vehicles'

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    vehicle_model_id = _sql.Column(_sql.Integer, _sql.ForeignKey('models.id'))
    type_id = _sql.Column(_sql.Integer, _sql.ForeignKey('vehicle_types.id'))
    vin = _sql.Column(_sql.String, unique=True, nullable=False, index=True)  # Código identificador del vehículo
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())

    model = relationship('Model', back_populates='vehicles')
    
    # El tipo de vehículo se infiere del modelo
    @property
    def vehicle_type(self):
        return self.model.vehicle_type.type_name  # El tipo se deriva del modelo


