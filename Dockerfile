
FROM flyway/flyway:13.3.0 AS flyway

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/main/python

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY --from=flyway /flyway /flyway

ENV PATH="/flyway:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Permitir ejecutar el script de arranque
RUN chmod +x /app/scripts/start.sh

EXPOSE 8000

# Ejecutar Flyway antes de Gunicorn
CMD ["/bin/sh", "/app/scripts/start.sh"]
