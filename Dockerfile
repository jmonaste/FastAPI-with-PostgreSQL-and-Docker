# Usa una imagen base de Python
FROM python:3.11-slim

# Instala las dependencias del sistema para `zbar` y herramientas esenciales
RUN apt-get update && \
    apt-get install -y zbar-tools libzbar0 build-essential && \
    rm -rf /var/lib/apt/lists/*

# Crea y establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expón el puerto que usa la aplicación
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
