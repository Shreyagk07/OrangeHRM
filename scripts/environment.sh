#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
case "${1:-up}" in
  up)
    docker compose up -d --build mysql app hub chrome firefox mailpit
    ;;
  install)
    # Explicit first-install action: invokes the official deprecated CLI installer.
    docker compose exec -T app php /opt/qa/install.php
    docker compose exec -T app chown -R www-data:www-data /var/www/html/lib/confs /var/www/html/src/cache /var/www/html/src/log
    python3 scripts/configure-mail.py
    ;;
  ready) python3 scripts/readiness.py ;;
  down) docker compose down --remove-orphans ;;
  reset)
    if [[ "${2:-}" != '--delete-local-data' ]]; then echo 'Reset requires --delete-local-data (deletes application, database and Jenkins volumes).'; exit 2; fi
    docker compose --profile jenkins down --volumes --remove-orphans
    ;;
  *) echo 'Use up | install | ready | down | reset --delete-local-data'; exit 2 ;;
esac
