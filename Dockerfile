# Usa una imagen base de Python
FROM python:3.11-slim

# Configura variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependencias del sistema para pyzbar y bibliotecas necesarias para zbar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libzbar0 \
    libzbar-dev \
    libgl1 \
    libxrender1 \
    libfontconfig1 \
    libsm6 \
    libxext6 \
    libice6 \
    libgtk2.0-dev \
    zbar-tools \
    freeglut3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea el directorio de trabajo y copia el archivo de requerimientos
WORKDIR /app
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY . .

# Expone el puerto 8000 para FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
