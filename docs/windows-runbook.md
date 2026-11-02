# Windows execution runbook

Run PowerShell from `C:\Users\Shreya\OneDrive\Desktop\Orangehrm`.

## Start the installed Docker Engine

Docker Desktop and Compose were already installed. The initial blocker was a stopped Desktop backend / WSL2 distribution, not a missing installation. On this machine starting Desktop brought Engine 28.5.1 online.

1. Click **Start**, type **Docker Desktop**, and click **Open**.
2. Wait for the engine status to show running. If a first-run screen appears, review the terms and complete the setup; use Linux containers and the WSL2 engine.
3. In PowerShell, verify both Client and Server are present:

```powershell
docker version
docker compose version
wsl --list --verbose
```

The equivalent launch command is:

```powershell
Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe' -WindowStyle Hidden
```

Do not reset Desktop or unregister its WSL distribution to fix a stopped engine: those actions can destroy existing container data. The `com.docker.service` Windows helper can be stopped while the WSL2 engine works; use `docker version` Server output as the actual check. See [Docker Windows setup](https://docs.docker.com/desktop/setup/install/windows-install/) and [WSL2 backend](https://docs.docker.com/desktop/features/wsl/).

## Provision this repository

An ignored `.env` is created for this local lab; preserve it so installed passwords remain consistent. For a fresh clone only, copy `.env.example` and change dummy passwords before initialization.

```powershell
docker compose up -d --build mysql app hub chrome firefox mailpit
# First installation only, on the fresh lab:
docker compose exec -T app php /opt/qa/install.php
docker compose exec -T app chown -R www-data:www-data /var/www/html/lib/confs /var/www/html/src/cache /var/www/html/src/log
python scripts/configure-mail.py
python scripts/readiness.py
docker compose ps
```

The application is `http://localhost:8080/web/index.php/auth/login`; Grid is `http://localhost:4444/ui`. The install creates the account specified by `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env`. Read those values locally in your editor; never post that file or its passwords in a defect or report. These are local synthetic credentials, not public-demo credentials.

Mailpit is the local SMTP sink at container address `mailpit:1025`, with a loopback-only viewer at `http://localhost:8025`. UI-010 needs email configuration for the reset form to exist. `configure-mail.py` saves and verifies the official email configuration API without sending a test email; the sink has no configured external relay.

## Run and preserve separate evidence

`run-tests.ps1` imports `.env` without printing secrets, uses the existing workspace JDK if JAVA_HOME is unset, selects the real Maven suite/profile, and stores each run under `target/runs/<RunName>`. Use a fresh RunName to preserve failed attempts.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser chrome -Tags '@UI-011' -RunName smoke-chrome
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite api -Browser chrome -RunName api-chrome
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser chrome -Tags '@regression' -RunName regression-chrome
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser firefox -Tags '@regression' -RunName regression-firefox
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite report -RunName regression-chrome
powershell -ExecutionPolicy Bypass -File .\scripts\serve-report.ps1 -RunName regression-chrome
```

UI-011 includes a real JDBC persistence assertion and authenticated API cleanup. The API suite checks authenticated employee lifecycle, invalid payload rejection, anonymous access denial, MySQL persistence and cleanup. No separate invented authentication Maven profile is required: API uses `-Papi -Dsuite=api` internally.

The per-run HTML report is `target/runs/<RunName>/site/allure-maven-plugin/index.html`; `serve-report.ps1` serves that existing report at `http://127.0.0.1:8765/` without generating another copy. Open that URL in your browser, or run `Start-Process http://127.0.0.1:8765/` from a second PowerShell window. Ctrl+C stops the server. If the chosen port is occupied, specify another free port with `-Port` and use that URL. The raw results and screenshots are in that run's `allure-results` directory. Keep historical dry-run output separate from live evidence.

To combine completed runs, use a fresh output name and the exact run names you executed:

```powershell
python scripts/collect-results.py --run regression-chrome=chrome --run regression-firefox=firefox --run api-chrome=chrome --output combined-live
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite report -RunName combined-live
powershell -ExecutionPolicy Bypass -File .\scripts\serve-report.ps1 -RunName combined-live
```

Optional `--history <failed-run-name>=chrome` includes only that run's failed/broken results, explicitly labeled Historical, with failure screenshots preserved. It does not convert them to passes or overwrite the source run. Do not include two final runs of the same logical test/browser: the collector rejects duplicates. Record any targeted reruns separately or select a fresh complete final run.

Navigation has a separate `page.timeout` / `PAGE_TIMEOUT` budget (60 seconds) for document/Vue bootstrap readiness. Individual field and business waits remain `timeout` / `TIMEOUT` (20 seconds). No page refresh or automatic test retry is used. On this 8 GB Windows machine, prefer the sequential browser commands shown above; the initial concurrent attempt exposed resource-related rendering/session failures.

```powershell
# Stop this project while preserving its database and installed configuration:
docker compose down --remove-orphans
```

For a free Engine-only alternative, install a normal Ubuntu WSL2 distribution with `wsl --install -d Ubuntu`, complete its Linux username/password prompts, and follow the official Docker Engine Ubuntu installation instructions linked from README. Do not install a second engine or change Docker contexts while a test run is active. This machine already has a usable Desktop installation, so no Ubuntu installation was needed for the current execution.

## Resource-constrained Firefox execution

The Grid Firefox node is configured for headless tests (`headless=true` in committed defaults); Xvfb, VNC/noVNC and unconfigured tracing are disabled. For a headed Firefox session, use a local browser (`-LocalBrowser` and `HEADLESS=false`), or explicitly restore the node's display settings before recreating it.

On this 8 GB host, stop the idle Chrome node while executing Firefox, then restore it before the two-node readiness check. These commands preserve application/database containers and all volumes:

```powershell
docker compose stop chrome
docker compose up -d --no-deps firefox
# Run Firefox tests with run-tests.ps1 here.
docker compose up -d --no-deps chrome
python scripts/readiness.py
```

Authentication URL transitions use the existing 60-second page budget; field checks and UI-040 still use the existing 20-second business budget. No retry policy is enabled.
