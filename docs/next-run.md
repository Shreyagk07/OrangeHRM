# Next run on this Windows workspace

Open PowerShell in `C:\Users\Shreya\OneDrive\Desktop\Orangehrm`. Docker Desktop must show its engine running. The existing database and application are installed: reuse `.env` and the persistent volumes. These commands reuse the images, use fresh evidence directories and run one browser node at a time. Keep Windows awake.

```powershell
$stamp = Get-Date -Format yyyyMMdd-HHmmss
docker compose up -d mysql app hub chrome firefox mailpit
python scripts/readiness.py
docker compose stop firefox
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser chrome -Tags '@regression' -RunName "chrome-$stamp"
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite api -Browser chrome -RunName "api-$stamp"
docker compose stop chrome
docker compose up -d --no-deps firefox
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser firefox -Tags '@regression' -RunName "firefox-$stamp"
docker compose up -d --no-deps chrome
python scripts/readiness.py
python scripts/collect-results.py --run "chrome-${stamp}=chrome" --run "firefox-${stamp}=firefox" --run "api-${stamp}=chrome" --output "report-$stamp"
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite report -RunName "report-$stamp"
powershell -ExecutionPolicy Bypass -File .\scripts\serve-report.ps1 -RunName "report-$stamp"
```

Review each Maven result. UI-040 remains active and causes a nonzero test exit while DEF-001 is open; report generation still follows. A Firefox startup failure is a separate failed setup (FW-009). Preserve its evidence and diagnose it; no retries are configured. Collect only completed runs; interrupted results do not establish a complete 40-case regression.

The last command serves the existing report at `http://127.0.0.1:8765/`. Open that URL in a browser, or run `Start-Process http://127.0.0.1:8765/` in a second PowerShell window. Ctrl+C stops the report server. If an earlier report server still occupies that port, stop that server or add `-Port 8766` (another free port) to the last command and open the matching URL. Reports live under `target/runs/report-<stamp>/site/allure-maven-plugin`; raw results remain in their source run directories.

Application: `http://localhost:8080/web/index.php/auth/login`. Use `ADMIN_USERNAME` and `ADMIN_PASSWORD` from your local `.env`; this installation uses username `qaadmin`. Grid: `http://localhost:4444/ui`. Local mail viewer: `http://localhost:8025/`.

To rerun a specific affected scenario, choose a fresh run name, for example:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-tests.ps1 -Suite ui -Browser firefox -Tags '@UI-015' -RunName "firefox-015-$stamp"
```

Run the full relevant suite after a framework change. Preserve DEF-001's assertion and screenshots. The [Windows runbook](windows-runbook.md) covers the exact Docker Desktop start steps and initial provisioning if needed.
