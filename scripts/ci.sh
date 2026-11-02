#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
set -a
source .env
set +a
export BASE_URL=http://localhost:8080/web/index.php
export BROWSER_BASE_URL=http://app/web/index.php
export GRID_URL=http://localhost:4444
bash scripts/environment.sh up
bash scripts/environment.sh install
bash scripts/environment.sh ready
status=0
./mvnw -B -ntp test -Dsuite=ui -Dworkers=1 -Dcucumber.filter.tags="${TEST_TAGS:-@smoke}" || status=$?
./mvnw -B -ntp -Papi test -Dsuite=api || status=$?
# Report generation must run after failed tests, while preserving test failure status.
./mvnw -B -ntp allure:report || { report_status=$?; if [[ "$status" == 0 ]]; then status=$report_status; fi; }
exit "$status"
