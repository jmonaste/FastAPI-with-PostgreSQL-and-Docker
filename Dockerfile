# Usa una imagen de Python como base
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instala libzbar y otras dependencias necesarias para pyzbar
RUN sudo apt-get update && apt-get install libzbar0 -y && pip install pyzbar

# Copia el archivo requirements.txt a /app y lo instala
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip3 install -r requirements.txt



# Copia el código de la aplicación a /app
COPY . .

# Expone el puerto de la aplicación (Render asignará un puerto automáticamente)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
