import datetime as _dt
import sqlalchemy as _sql
from sqlalchemy.orm import relationship
import database as _database
from sqlalchemy import func 
from enum import Enum

class Brands(_database.Base):
    __tablename__ = 'brands'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, unique=True, index=True)
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    models = relationship("Model", back_populates="brand")

class Models(_database.Base):
    __tablename__ = 'models'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    brand_id = _sql.Column(_sql.Integer, _sql.ForeignKey('brands.id'))
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    brand = relationship('Brand', back_populates='models')
    vehicles = relationship('Vehicle', back_populates='model')

class VehicleTypes(_database.Base):
    __tablename__ = 'vehicle_types'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    type_name = _sql.Column(_sql.String, unique=True, index=True)
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    vehicles = relationship("Vehicle", back_populates="vehicle_type")





