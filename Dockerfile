# Usa una imagen base de Python
FROM python:3.11-slim

# Establece variables de entorno para Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Actualiza el sistema y prepara las herramientas necesarias para la compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libtool \
    autoconf \
    pkg-config \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clona y construye la librería zbar desde el repositorio oficial
RUN git clone https://github.com/mchehab/zbar.git /zbar
WORKDIR /zbar
RUN autoreconf -vfi && ./configure && make && make install

# Actualiza el enlace dinámico
RUN ldconfig

# Vuelve al directorio de trabajo para la app
WORKDIR /app

# Copia el archivo requirements.txt y instala las dependencias de Python
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copia todo el código de la app al contenedor
COPY . .

# Expon el puerto de la app
EXPOSE 8000