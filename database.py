import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm

#DATABASE_URL = "postgresql://myuser:password@localhost:5433/fastapi_database"
DATABASE_URL = "postgresql://sgmaquser01:K0KDawfcAEKs5ze3eImeLHU6nEOXUXqP@dpg-csdujgbtq21c73a93oa0-a.frankfurt-postgres.render.com:5432/fastapidb_rspb"

engine = _sql.create_engine(DATABASE_URL)

SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative.declarative_base()