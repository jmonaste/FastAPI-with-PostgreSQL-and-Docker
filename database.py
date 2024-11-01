import sqlalchemy as _sql
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Cargar el archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = _sql.create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

metadata = _sql.MetaData()