from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
import services
from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/api/models",
    tags=["Models"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not Found"}},
)