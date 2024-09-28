import datetime as _dt
import sqlalchemy as _sql
from sqlalchemy.orm import relationship
import database as _database
from sqlalchemy import func 


class Contact(_database.Base):
    __tablename__ = "contacts"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    first_name = _sql.Column(_sql.String, index=True)
    last_name = _sql.Column(_sql.String, index=True)
    email = _sql.Column(_sql.String, index=True, unique=True)
    phone_number = _sql.Column(_sql.String, index=True, unique=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

class Brand(_database.Base):
    __tablename__ = 'brands'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, unique=True, index=True)
    models = relationship("Model", back_populates="brand")

class Model(_database.Base):
    __tablename__ = 'models'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    brand_id = _sql.Column(_sql.Integer, _sql.ForeignKey('brands.id'))
    brand = relationship('Brand', back_populates='models')
    vehicles = relationship('Vehicle', back_populates='model')

class VehicleType(_database.Base):
    __tablename__ = 'vehicle_types'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    type_name = _sql.Column(_sql.String, unique=True, index=True)
    created_at = _sql.Column(_sql.DateTime, server_default=func.now())
    updated_at = _sql.Column(_sql.DateTime, server_default=func.now(), onupdate=func.now())
    vehicles = relationship("Vehicle", back_populates="vehicle_type")

class Vehicle(_database.Base):
    __tablename__ = 'vehicles'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    model_id = _sql.Column(_sql.Integer, _sql.ForeignKey('models.id'))
    vehicle_type_id = _sql.Column(_sql.Integer, _sql.ForeignKey('vehicle_types.id'))

    model = relationship('Model', back_populates='vehicles')
    vehicle_type = relationship('VehicleType', back_populates='vehicles')


