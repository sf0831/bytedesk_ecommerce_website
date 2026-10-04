#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose config --quiet
docker compose up -d --build --wait
docker compose exec -T django python manage.py migrate --check
docker compose exec -T django python manage.py makemigrations --check --dry-run
docker compose exec -T django python manage.py seed_store
docker compose exec -T django python manage.py seed_store
docker compose exec -T django python manage.py check
docker compose exec -T django python manage.py test store --noinput
docker compose exec -T fastapi alembic current
docker compose exec -T fastapi ruff check app tests
docker compose exec -T fastapi ruff format --check app tests
docker compose exec -T fastapi pytest -q -p no:cacheprovider
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run format:check
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
docker compose exec -T frontend npm run smoke
docker compose ps
printf '%s\n' 'ByteDesk automated verification passed. Browser interaction and responsive checks are documented separately.'
