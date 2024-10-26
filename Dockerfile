FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libzbar0

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

CMD ["gunicorn", "main:app"]