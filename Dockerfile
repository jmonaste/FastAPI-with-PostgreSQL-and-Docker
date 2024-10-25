# Usa una imagen de Python como base
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instala libzbar y otras dependencias necesarias para pyzbar
RUN apt-get update && apt-get install -y \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Reinstala pyzbar para asegurar compatibilidad
RUN pip3 install pyzbar


# Copia el archivo requirements.txt a /app y lo instala
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt



# Copia el código de la aplicación a /app
COPY . .

# Expone el puerto de la aplicación (Render asignará un puerto automáticamente)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
