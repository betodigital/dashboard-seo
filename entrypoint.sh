#!/bin/sh
set -e

echo "==> Aguardando PostgreSQL..."
while ! python -c "
import psycopg2, os
psycopg2.connect(
    dbname=os.getenv('DB_NAME','django_app'),
    user=os.getenv('DB_USER','postgres'),
    password=os.getenv('DB_PASSWORD',''),
    host=os.getenv('DB_HOST','db'),
    port=os.getenv('DB_PORT','5432'),
)" 2>/dev/null; do
  sleep 1
done
echo "==> PostgreSQL pronto."

echo "==> Rodando migrações..."
python manage.py migrate --noinput

echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "==> Iniciando Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
