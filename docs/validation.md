# Actual validation ? 29 October 2026

Workspace: `C:\Users\Shreya\OneDrive\Desktop\Orangehrm`. Dates/times use Asia/Kolkata. Final live execution completed with open failures; acceptance is not all green.

## Final selected executions

| Run | Passed | Failed | Skipped | Actual outcome |
| --- | ---: | ---: | ---: | --- |
| regression-chrome-fixed-1029 | 39 | 1 | 0 | All 40 attempted with final navigation code; UI-040 reproduces DEF-001 |
| regression-firefox-fixed-1029 | 38 | 2 | 0 | All 40 attempted; UI-040 reproduces DEF-001; UI-015 failed before browser creation (FW-009) |
| api-final-1029 | 1 | 0 | 0 | Session-authenticated lifecycle, invalid payload 422, anonymous 401, JDBC update and cleanup; Maven elapsed 1:25 |

UI total: **77 passed, 3 failed, 0 skipped across 80 browser executions of 40 logical scenarios**. Including API: **78 passed, 3 failed, 0 skipped across 81 executions**. Allure classifies the three nonpasses as **2 failed + 1 broken**. UI-015's business assertions were not reached in the final Firefox run; it is a failed setup, not a skipped scenario or an application defect. Its focused post-fix run passed, but the full-run failure remains counted.

## Health, authentication and data

Docker Engine 28.5.1 / Compose v2.40.3-desktop.1 / WSL2 are available. Java 17.0.13 and Wrapper/Maven 3.9.9 compiled the 17 Java files. The installed official OrangeHRM 5.7 and MySQL 8.4.3 persistent environment was reused; no reinstallation or unchanged application-image rebuild was performed.

Final `python scripts/readiness.py`: exit 0; installed application, two Grid nodes and configured Mailpit ready. Independent Grid status: ready=true; Chrome UP/idle and Firefox UP/idle. The final authenticated `/api/v2/pim/employees` inventory returned one row, meta.total=1, and zero Q/A framework-ID fixtures. API lifecycle cleanup and JDBC absence assertions passed. No direct application-table writes were used.

The idle browser node was stopped during each browser's final execution to reduce resource pressure; both were restored afterward. No global Docker prune or database-volume deletion occurred.

## Fixes and remaining issues

* [FW-008](framework-issues.md): authentication URL transitions incorrectly used the 20-second field wait. Access logs showed successful Firefox login POST 302 and dashboard GET 200 about 27 seconds apart. URL predicates now use the existing 60-second page budget; field/business conditions and UI-040 remain at 20 seconds. UI-015/UI-016 passed the focused check, followed by the full Firefox and Chrome runs above. No action/scenario retries or relaxed expected values were added.
* Firefox headless-node display/VNC and unconfigured tracing were disabled through switches verified in the pinned image. This reduces unnecessary processes; it did not alone fix login timing.
* **Open DEF-001:** Leave Reset retains SyntheticNoMatch. REQ-06 / TC-040 / UI-040; independently reproduced in both final browser runs. [Reproduction and original evidence](defects/DEF-001.md). Root cause remains unestablished; no application patch or Jira write was made.
* **Open FW-009:** intermittent Firefox session-start timeout in UI-015. Low free host RAM and high Firefox CPU were observed; a complete root cause is not established. No screenshot is available for a failure before a browser handle exists; the stack remains in Allure/raw results. This is separate from OrangeHRM defects.

Earlier framework corrections and evidence: [framework-issues.md](framework-issues.md), including MySQL TCP readiness, Personal Details synchronization, JSON serialization, cleanup diagnostics, Allure browser identity and SMTP provisioning.

## One final Allure report

Generated once from the three selected current runs using `scripts/collect-results.py` and `run-tests.ps1 -Suite report -RunName final-live-1029`. Report generation exited 0. Historical failed attempts remain in their own raw folders and are not relabeled as passes or included as duplicate final cases.

* HTML: `target/runs/final-live-1029/site/allure-maven-plugin/index.html`
* Raw assembled evidence and collection manifest: `target/runs/final-live-1029/allure-results` and `collection.json` in its parent run directory.
* Verified summary: 78 passed, 2 failed, 1 broken, 0 skipped, 81 total; 81 unique browser/test histories; two actual PNG failure attachments.
* Served existing HTML without another generated report copy at **http://127.0.0.1:8765/**. HTTP 200 verified; Windows browser open command completed successfully.

## Cleanup and preserved scope

Removed **238,624,311 bytes (227.6 MiB)** of redundant file content. [Exact paths/bytes](cleanup-2026-10-29.json) and [reference/ownership review](cleanup-2026-10-29.md). This is measured deleted file content, not a net physical free-space or OneDrive allocation measurement; required new execution/report files were subsequently created. Docker recovered bytes: 0; active/shared resources and every volume were retained.

All 40 scenarios, 50 manual cases, 50 RTM mappings, XLSX datasets, configuration, pipelines, documentation and defect evidence remain. Execution log now records the 81 actual selected executions. RTM/UI coverage distinguish browser outcomes; all 50 manual-case execution statuses remain Not Run. `.gitignore` excludes generated outputs and local secret variants while preserving `.env.example`.

## Diagnostic chronology (retained raw evidence)

| Run | Actual result |
| --- | --- |
| smoke-initial | 0 passed / 1 failed; UI read raced Personal Details loading |
| smoke-sync-fix | 0 passed / 1 failed; business checks passed, cleanup lacked JSON serializer |
| smoke-json-fix | 1 passed / 0 failed / 0 skipped; real UI/JDBC/API cleanup |
| api-initial | 1 passed / 0 failed / 0 skipped |
| utility-final | 1 passed / 0 failed / 0 skipped; earlier XLSX utility check, not rerun for navigation-only changes |
| regression-chrome-1 | Interrupted: 14 passed / 5 failed-broken; 21 not executed |
| regression-firefox-1 | Earlier full baseline: 39 passed / 1 failed / 0 skipped (DEF-001) |
| chrome-affected-final | 3 passed / 1 failed / 0 skipped; UI-010/011/013 passed, UI-040 reproduced DEF-001 |
| regression-chrome-final | Earlier full: 36 passed / 4 failed / 0 skipped; DEF-001 plus three intermittent execution failures |
| chrome-diagnosis-1029 | UI-012/029/033: 3 passed / 0 failed / 0 skipped, unchanged-code diagnostic |
| regression-chrome-1029 | First fresh full after cleanup: 39 passed / 1 failed / 0 skipped (DEF-001) |
| regression-firefox-1029 | Interrupted: 14 passed / 2 startup failures; 24 not executed |
| firefox-session-check-1029 | Interrupted: one completed login failure; other case incomplete |
| firefox-headless-check-1029 | 0 passed / 2 login-navigation failures / 0 skipped |
| firefox-navigation-check-1029 | 2 passed / 0 failed / 0 skipped after FW-008 correction |

Stopped processes were selected by exact owned Maven build-directory arguments; unrelated processes were not terminated. The dry-run report and duplicate report-check assembly were removed as documented cleanup. Their earlier generation does not establish live business passes.

CI/Jenkins jobs, manual execution, Jira import and equivalent-workload benchmark trials remain unexecuted. Ordinary suite elapsed time is not a speedup measurement. See [copy-ready future commands](next-run.md), [Windows setup](windows-runbook.md), and [acceptance](acceptance.md).

## Original build/preparation checks (historical)

* Official OrangeHRM `v5.7` release metadata, source archive and installable artifact downloaded. Artifact size 22,085,736 bytes; SHA-256 recorded in compatibility.md and Dockerfile. Relevant source files inspected before implementation.
* Pinned Maven Wrapper 3.3.2 generated for Maven 3.9.9. The first unquoted PowerShell invocation incorrectly split a dotted argument; the corrected explicitly pinned and quoted invocation succeeded.
* `mvn -B -ntp test -Dsuite=unit` using workspace-local Temurin 17.0.13+11 / Maven 3.9.9: **BUILD SUCCESS**, 1 test, 0 failures/errors/skips. The POI reader checked workbook boundary/blank cells and missing dataset handling. Java compilation initially covered 15 files.
* `mvnw.cmd -B -ntp -Papi test-compile -DskipTests`: **BUILD SUCCESS**, all **17** source files compiled after adding evidence sanitization/reporting classes.
* `mvnw.cmd -B -ntp test -Dsuite=ui -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@regression -Dbuild.dir=target/dryrun -Dcucumber.plugin=pretty,json:target/dryrun/cucumber.json,io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm`: **BUILD SUCCESS**, 40 discovered/bound scenarios, no undefined steps. Browser hooks and business steps are **not executed in dry-run**.
* `mvnw.cmd -B -ntp -Dbuild.dir=target/dryrun allure:report`: **BUILD SUCCESS**, Allure Report 2.32.0 generated at `target/dryrun/site/allure-maven-plugin`. It contains **40 dry-run results**, not 40 live business passes. `environment.properties` explicitly labels it DRY RUN / application not started.
* `docker compose --env-file .env.example config --quiet`: exit 0 outside sandbox, where Docker could read its plugin configuration. This validates Compose configuration only.
* Python compilation for all four scripts: exit 0. Git Bash syntax check of environment.sh and ci.sh: exit 0.
* `python scripts/jira_import.py`: dry-run, count 0, no network writes.
* Catalogue checks: 50 manual rows, 14 fields each, all Not Run; 40 unique UI IDs; 50 RTM mappings; 12 XLSX dataset rows.

Nonfatal library messages during the utility test: SLF4J has no bound logger; POI/Log4j uses its fallback logger. These did not affect assertions or the build. No retries were used.

## Original blocker before the live continuation

`docker version` showed Client 28.5.1 but no server; the outside-sandbox check reported the `dockerDesktopLinuxEngine` named pipe missing. Java and Maven were initially absent on PATH, so ignored workspace-local tools were downloaded for build validation. The Adoptium redirect returned HTTP 403; a pinned official GitHub Temurin artifact succeeded.

At the end of the original build-only session, application integration had not executed. That historical limitation is superseded by the live table above. Jenkins/GitHub Actions jobs, manual execution, Jira issue creation and performance trials remain unexecuted; no speedup is claimed.

## Reproduce build checks on this Windows workspace

```powershell
$env:JAVA_HOME = Join-Path (Get-Location) '.tools\jdk-17.0.13+11'
.\mvnw.cmd -B -ntp test '-Dsuite=unit'
.\mvnw.cmd -B -ntp -Papi test-compile '-DskipTests'
.\mvnw.cmd -B -ntp test '-Dsuite=ui' '-Dcucumber.execution.dry-run=true' '-Dcucumber.filter.tags=@regression' '-Dbuild.dir=target/dryrun'
```

`.tools`, `.allure`, `vendor` and `target` are ignored local artifacts; a fresh clone needs Java 17 installed, but Maven itself bootstraps through the committed wrapper. For current native Windows execution use [next-run.md](next-run.md).
