# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos requirements.txt a la imagen y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY . .

# Define la variable de entorno para que no genere archivos .pyc
ENV PYTHONUNBUFFERED=1

# Expone el puerto 8000 para la aplicación
EXPOSE 8000

# Comando para iniciar Gunicorn con Uvicorn como worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]