#!/bin/sh
set -e

echo "Ejecutando migraciones Flyway..."

flyway \
  -url="jdbc:postgresql://${POSTGRES_HOST}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}" \
  -user="${POSTGRES_USER}" \
  -password="${POSTGRES_PASSWORD}" \
  -locations="filesystem:/app/database/migrations" \
  migrate

echo "Migraciones verificadas correctamente."
echo "Iniciando Django con Gunicorn..."

exec gunicorn cr.ac.una.alimentaCR.config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}"