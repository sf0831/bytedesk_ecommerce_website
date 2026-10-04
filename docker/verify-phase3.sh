#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose config --quiet
docker compose up -d --build --wait frontend
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run format:check
docker compose exec -T frontend npm run build
docker compose exec -T frontend npm run smoke
printf '%s\n' 'Phase 3 checks passed. Storefront: http://localhost:5173/'
