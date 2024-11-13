# dashboard_service.py
from sqlalchemy import func, Integer
from sqlalchemy.orm import Session
import models as _models
from typing import List, Dict


async def count_vehicles_service(db: Session) -> int:
    return db.query(_models.Vehicle).count()


async def get_vehicles_with_non_final_status_count_service(db: Session):
    try:
        count = db.query(_models.Vehicle)\
            .join(_models.State, _models.Vehicle.status_id == _models.State.id)\
            .filter(_models.State.is_final == False)\
            .count()
        return count
    except Exception as e:
        # Manejo de excepciones específicas si es necesario
        raise e
    





async def get_vehicle_registrations_by_date_service(db: Session) -> List[Dict[str, int]]:
    try:
        # Definir las expresiones para extraer año y mes
        year = func.extract('year', _models.Vehicle.created_at).cast(Integer).label('year')
        month = func.extract('month', _models.Vehicle.created_at).cast(Integer).label('month')
        
        # Realizar la consulta agrupando por año y mes
        registrations = (
            db.query(
                year,
                month,
                func.count(_models.Vehicle.id).label('count')
            )
            .group_by(year, month)
            .order_by(year, month)
            .all()
        )
        
        # Convertir el resultado en una lista de diccionarios con el formato deseado
        result = [
            {'year': r.year, 'month': r.month, 'value': r.count}
            for r in registrations
        ]
        
        return result
    except Exception as e:
        # Aquí puedes agregar más lógica de manejo de errores si es necesario
        raise e
