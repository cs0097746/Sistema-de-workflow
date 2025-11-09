#!/usr/bin/env bash


# Script simples para esperar o Postgres, aplicar migrações, coletar static e iniciar Gunicorn
# Usa as variáveis do .env


# função para checar se o banco está pronto
wait_for_db() {
  echo "Waiting for postgres..."
  until python - <<'PY'
import os, sys, psycopg2
from psycopg2 import OperationalError

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        connect_timeout=3
    )
    conn.close()
    print("Postgres is available")
except Exception as e:
    print("Postgres not available yet:", e)
    sys.exit(1)
PY
  do
    echo "Database not ready, retrying..."
    sleep 2
  done
}



# Tenta várias vezes
n=0
until wait_for_db; do
    n=$((n+1))
    if [ "$n" -ge 12 ]; then
        echo "Banco não ficou disponível após várias tentativas. Saindo."
        exit 1
    fi
    sleep 2
done


# Configurar variáveis opcionais
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-workflow.settings}


# Aplicar migrações e popular dados (se desejar)
python manage.py migrate --noinput


# Se você quiser rodar o comando custom para popular dados só na primeira vez,
# comente a linha abaixo quando não for necessária
python manage.py popular_dados


# Coletar arquivos estáticos
python manage.py collectstatic --noinput


# Start Gunicorn
# Em desenvolvimento pode preferir: python manage.py runserver 0.0.0.0:8000


exec gunicorn workflow.wsgi:application \
--bind 0.0.0.0:8000 \
--workers ${GUNICORN_WORKERS:-3} \
--log-level ${GUNICORN_LOG_LEVEL:-info}
