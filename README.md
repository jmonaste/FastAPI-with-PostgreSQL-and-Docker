# FastAPI with PostgreSQL and Docker

Este proyecto es un ejemplo de cómo crear una API con **FastAPI**, **PostgreSQL** y **Docker**. La API gestiona un sistema de vehículos, con soporte para diferentes modelos, y permite realizar operaciones CRUD sobre los registros en una base de datos PostgreSQL. La aplicación se ejecuta dentro de un contenedor Docker, asegurando un entorno reproducible y fácil de desplegar.

## Requisitos

Antes de empezar, asegúrate de tener instalados los siguientes componentes:

- **Docker** y **Docker Compose**
- **Python 3.9+**
- **Postman** (opcional, para pruebas manuales)
  
## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tu_usuario/FastAPI-with-PostgreSQL-and-Docker.git
    cd FastAPI-with-PostgreSQL-and-Docker
    ```

2. Crea un entorno virtual e instala las dependencias de Python:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Configura el archivo `.env` con las variables necesarias para la conexión a la base de datos PostgreSQL y otras configuraciones del entorno.

## Uso de Docker

El proyecto está configurado para ejecutarse en un contenedor Docker, lo cual facilita su despliegue en diferentes entornos. Asegúrate de que no hay ningún proceso de PostgreSQL en ejecución en tu sistema que pueda estar ocupando el puerto predeterminado (5432). Puedes verificarlo con el siguiente comando en PowerShell o en la consola de Windows:

```bash
netstat -ano | findstr :5432
