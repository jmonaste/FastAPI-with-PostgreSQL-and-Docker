# Usa una imagen base de Python más completa para mayor compatibilidad
FROM python:3.11

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libzbar0

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
