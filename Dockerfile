# Usa una imagen base de Python más completa para mayor compatibilidad
FROM python:3.11

# Instala dependencias necesarias para compilar y otras herramientas esenciales
RUN apt-get update && \
    apt-get install -y wget build-essential libzbar0 zbar-tools libzbar-dev && \
    rm -rf /var/lib/apt/lists/*

# Crea el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Exponer el puerto usado por la API
EXPOSE 8000

# Ejecuta la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
