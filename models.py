import datetime as _dt
import sqlalchemy as sa
import sqlalchemy as _sql
from sqlalchemy.orm import relationship
import database as _database
from sqlalchemy import func, Enum, Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Time
import enum
from sqlalchemy.orm import declarative_base
from typing import TYPE_CHECKING




Base = declarative_base()

class UserRole(enum.Enum):
    admin = "admin"
    client = "client"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.client, nullable=False)

    state_histories = relationship("StateHistory", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")    

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(_sql.DateTime(timezone=True), nullable=False)
    
    user = relationship("User", back_populates="refresh_tokens")

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    models = relationship("Model", back_populates="brand")

class Model(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand_id = Column(Integer, _sql.ForeignKey('brands.id'))
    type_id = Column(Integer, _sql.ForeignKey('vehicle_types.id'))  # Relación con VehicleType
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    brand = relationship('Brand', back_populates='models')
    vehicle_type = relationship('VehicleType', back_populates='models')
    vehicles = relationship('Vehicle', back_populates='model')

class VehicleType(Base):
    __tablename__ = 'vehicle_types'
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, unique=True, index=True)
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    models = relationship('Model', back_populates='vehicle_type')

class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    is_initial = Column(_sql.Boolean, default=False)
    is_final = Column(_sql.Boolean, default=False)
    order = Column(Integer)
    active = Column(_sql.Boolean, default=True)
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    icon = Column(String(50))
    color = Column(String(50))
    category = Column(String(50))
    comments = Column(_sql.Text)

    transitions_from = relationship('Transition', back_populates='from_state', foreign_keys='Transition.from_state_id')
    transitions_to = relationship('Transition', back_populates='to_state', foreign_keys='Transition.to_state_id')
    state_comments = relationship('StateComment', back_populates='state', cascade="all, delete-orphan")

class Transition(Base):
    __tablename__ = 'transitions'
    id = Column(Integer, primary_key=True, index=True)
    from_state_id = Column(Integer, _sql.ForeignKey('states.id'), nullable=False)
    to_state_id = Column(Integer, _sql.ForeignKey('states.id'), nullable=False)
    condition = Column(String(255), nullable=True)
    action = Column(String(255), nullable=True)
    active = Column(_sql.Boolean, default=True)
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    from_state = relationship('State', foreign_keys=[from_state_id], back_populates='transitions_from')
    to_state = relationship('State', foreign_keys=[to_state_id], back_populates='transitions_to')

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True, index=True)
    vehicle_model_id = Column(Integer, _sql.ForeignKey('models.id'))
    vin = Column(String, unique=True, nullable=False, index=True)  # Código identificador del vehículo
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_urgent = Column(_sql.Boolean, default=False)  # Por defecto no es urgente
    status_id = Column(Integer, _sql.ForeignKey('states.id'), nullable=False)
    color_id = Column(Integer, _sql.ForeignKey('colors.id'), nullable=True)

    # Nuevos campos añadidos (urgencias)
    urgency_delivery_date = Column(_sql.DateTime(timezone=True), nullable=True)
    urgency_delivery_time = Column(Time, nullable=True)
    urgency_reason = Column(String, nullable=True)
    observations = Column(String, nullable=True)

    status = relationship('State')
    state_history = relationship('StateHistory', back_populates='vehicle', cascade="all, delete-orphan")
    model = relationship('Model', back_populates='vehicles')
    color = relationship("Color", back_populates="vehicles")

    # El tipo de vehículo se infiere del modelo
    @property
    def vehicle_type(self):
        if self.model and self.model.vehicle_type:
            return self.model.vehicle_type.type_name
        return None  # O alguna alternativa predeterminada

class StateHistory(Base):
    __tablename__ = 'state_history'
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, _sql.ForeignKey('vehicles.id'), nullable=False)
    from_state_id = Column(Integer, _sql.ForeignKey('states.id'), nullable=True)  # Puede ser null si es el primer estado
    to_state_id = Column(Integer, _sql.ForeignKey('states.id'), nullable=False)
    user_id = Column(Integer, _sql.ForeignKey('users.id'), nullable=False)  # Usuario que cambió el estado
    timestamp = Column(_sql.DateTime(timezone=True), server_default=func.now(), nullable=False)
    comment_id = Column(Integer, ForeignKey('states_comments.id'), nullable=True) # ALEMBIC

    vehicle = relationship('Vehicle', back_populates='state_history')
    from_state = relationship('State', foreign_keys=[from_state_id])
    to_state = relationship('State', foreign_keys=[to_state_id])
    user = relationship('User', back_populates='state_histories')
    comment = relationship("StateComment", back_populates="state_histories")

class StateComment(Base):
    __tablename__ = 'states_comments'

    id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, sa.ForeignKey('states.id'), nullable=False)
    comment = Column(sa.Text, nullable=False)
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    state = relationship('State', back_populates='state_comments')
    state_histories = relationship('StateHistory', back_populates='comment') # ??

class Color(Base):
    __tablename__ = 'colors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    hex_code = Column(String(7), nullable=False, unique=True)  # Ej: "#FF0000"
    rgb_code = Column(String(20), nullable=True)  # Ej: "255,0,0"
    created_at = Column(_sql.DateTime(timezone=True), server_default=func.now())
    updated_at = Column(_sql.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Definir restricciones de unicidad con nombres explícitos
    __table_args__ = (
        UniqueConstraint('name', name='uq_colors_name'),
        UniqueConstraint('hex_code', name='uq_colors_hex_code'),
    )

    # Relación inversa con Vehicle
    vehicles = relationship("Vehicle", back_populates="color")





