# Usa una imagen base de Python
FROM python:3.11-slim

# Establece variables de entorno para Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Actualiza el sistema e instala las herramientas de compilación y dependencias necesarias para zbar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libtool \
    autoconf \
    pkg-config \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clona e instala la biblioteca zbar desde el repositorio oficial
RUN git clone https://github.com/mchehab/zbar.git /zbar
WORKDIR /zbar
RUN autoreconf -vfi && ./configure --with-python=auto --with-gtk=auto && make && make install

# Actualiza el enlace dinámico
RUN ldconfig

# Configuración para la app
WORKDIR /app
COPY requirements.txt ./

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación en el contenedor
COPY . .

# Expón el puerto de la app
EXPOSE 8000

# Comando para ejecutar la app usando gunicorn y el worker UvicornWorker
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
