from typing import TYPE_CHECKING, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import database as _database
import models as _models
import schemas as _schemas
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import joinedload
import datetime as _dt
from typing import Optional

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

def _add_tables():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()




