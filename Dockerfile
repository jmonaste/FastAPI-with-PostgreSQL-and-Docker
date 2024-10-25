# Usa una imagen base oficial de Python
FROM python:3.12

# Instala las dependencias del sistema necesarias para zbar
# Instala las dependencias del sistema necesarias para zbar
RUN apt-get update -y
RUN apt-get install -y libzbar0
RUN apt-get install -y python3-pip python3-dev build-essential

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos requirements.txt a la imagen y los instala
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Initially encountered an issue that indicated I had to set these ENVs
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Copia el resto de los archivos de la aplicación al contenedor
COPY . .

# Define la variable de entorno para que no genere archivos .pyc
ENV PYTHONUNBUFFERED=1

# Expone el puerto 8000 para la aplicación
EXPOSE 8000

# Comando para iniciar Gunicorn con Uvicorn como worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
