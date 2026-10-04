#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose config --quiet
docker compose up -d --build --wait
docker compose exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker compose exec -T django python manage.py check
docker compose exec -T django python manage.py makemigrations --check --dry-run
docker compose exec -T django python manage.py migrate --check
docker compose exec -T django python manage.py seed_store
docker compose exec -T django python manage.py seed_store
docker compose exec -T django python manage.py test store --verbosity=2
curl --fail --silent --output /dev/null http://127.0.0.1:8000/admin/login/
printf '%s\n' 'Phase 1 verification passed. Admin: http://localhost:8000/admin/'
