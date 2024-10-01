# FastAPI-with-PostgreSQL-and-Docker

# Para rrancar el proceso correctamente con el contendor Docker
# debemos asegurarnos de que postgres no esté escuchando en el puerto del ptoyecto
#
# podemos hacer en powersheel o en la consola:
# netstat -ano | findstr :5432
#
# nos devueve el PID de los procesos que están escuchando en este puerto. Buscamos los que
# estén activos en el admin de tareas de windows, y los matamos.
# Arrancamos el contenedor y hacemos en la consola:
# 
# uvicorn main:app --reload
#
# hemos creado un contenedor que escucha en el 5433, para no tener problemas
