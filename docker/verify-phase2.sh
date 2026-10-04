#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose config --quiet
docker compose up -d --build --wait
docker compose exec -T django python manage.py migrate --check
docker compose exec -T django python manage.py makemigrations --check --dry-run
docker compose exec -T django python manage.py seed_store
docker compose exec -T fastapi alembic upgrade head
docker compose exec -T fastapi alembic current
docker compose exec -T fastapi pytest -q -p no:cacheprovider
curl --fail --silent --output /dev/null http://127.0.0.1:8001/docs
curl --fail --silent --output /dev/null http://127.0.0.1:8001/redoc
curl --fail --silent http://127.0.0.1:8001/api/health
printf '\n%s\n' 'Phase 2 verification passed. API docs: http://localhost:8001/docs'
