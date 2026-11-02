# End-to-End QA & Hybrid Test Automation Framework – OrangeHRM

A Java 17 learning project for a self-hosted OrangeHRM Starter 5.7 instance with MySQL. It contains 40 logical Cucumber UI scenarios, 50 manual cases, Excel datasets, REST Assured integration code, JDBC assertions, Grid configuration, CI pipelines and benchmark tooling.

**Execution status:** installed application and final live UI/API/JDBC runs completed. Chrome: 39 passed / 1 failed; Firefox: 38 passed / 2 failed; API: 1 passed. DEF-001 and Firefox startup issue FW-009 remain open. See [actual validation](docs/validation.md), [acceptance](docs/acceptance.md) and [exact next-run commands](docs/next-run.md). Benchmark trials remain unexecuted.

## Start on Windows with WSL2

For this existing Windows workspace, see [the native PowerShell runbook](docs/windows-runbook.md). It uses the installed Docker Desktop engine and the workspace Java 17 installation, preserves `.env`, and stores separate live-run evidence through `scripts/run-tests.ps1`.

Use a Linux distribution in WSL2 with Docker Engine and the Compose plugin installed using the [official Engine instructions](https://docs.docker.com/engine/install/ubuntu/). Docker Desktop is optional and its workplace licensing must be assessed separately. Work from the Linux filesystem for better container build performance. Linux users follow the same commands.

Install a Java 17 JDK, Python 3, Git, curl, unzip and Docker Engine with Compose. Allow roughly 8 GB RAM and 4 CPUs for the application, database and two browser nodes. Maven downloads through the included Wrapper; no paid service is needed. Use a free editor such as VS Code.

```bash
java -version
docker version
docker compose version
python3 --version
cp .env.example .env
# Edit the synthetic local passwords in .env before provisioning.
chmod +x mvnw
bash scripts/environment.sh up
bash scripts/environment.sh install
bash scripts/environment.sh ready
```

`install` is a first-install command, not a database reset. It uses OrangeHRM 5.7's **deprecated official CLI installer**, with generated environment configuration, and creates a column-restricted reader. The container must build before this command. This path is source-inspected but not runtime-validated. Do not repeatedly run it after partial installation: inspect the installer log and reset the disposable lab if needed. Review the release's GPLv3 license before running the installer (the generated configuration accepts it).

The release ZIP is downloaded from the official GitHub release and checked against the measured SHA-256 in the Dockerfile. `app_data` preserves the installed files/configuration; `mysql_data` preserves the database. Replacing the app version requires a deliberate fresh lab or the official upgrade procedure; rebuilding an image does not replace an existing app volume.

If CLI installation fails, use the official web wizard at `http://localhost:8080/installer/index.php`: Fresh Installation → accept license → resolve system checks → database host `mysql`, port `3306`, database `orangehrm`, privileged user `root` with `.env` root password → choose separate application user `orangehrm_app` with `.env` application password → organization Synthetic QA Laboratory, country US, English, UTC → synthetic administrator with `.env` credentials → decline registration → install. The wizard is an alternative for a fresh database; it does not repair a half-installed one. The reader grant still needs creation; use the grant section of `docker/install.php` as documented in [environment notes](docs/environment.md).

## Configuration and execution

Values resolve as **Java system property → environment variable → committed defaults**. Dots become underscores: `admin.username` maps to `ADMIN_USERNAME`. There are no default credentials in Java. `.env` is consumed by Compose, so export it for Maven:

```bash
set -a
source .env
set +a
```

Use passwords without shell expansion characters in `.env`, or quote them as valid Bash assignments. CI generates safe hexadecimal secrets. Avoid passing secrets in command-line arguments. Default URL `BASE_URL=http://localhost:8080/web/index.php` is for the Java process; `BROWSER_BASE_URL` is for the browser. Both are restricted to local lab hosts.

Local browsers (Chrome/Firefox installed on the host, Selenium Manager resolves drivers):

```bash
unset GRID_URL BROWSER_BASE_URL
./mvnw -B test -Dsuite=ui -Dcucumber.filter.tags=@smoke -Dbrowser=chrome
./mvnw -B test -Dsuite=ui -Dcucumber.filter.tags=@UI-011 -Dbrowser=firefox
```

Grid browsers need the Compose service URL, because `localhost` inside a node is the node itself:

```bash
export GRID_URL=http://localhost:4444
export BROWSER_BASE_URL=http://app/web/index.php
./mvnw -B test -Dsuite=ui -Dcucumber.filter.tags=@regression -Dbrowser=chrome -Dworkers=1
./mvnw -B test -Dsuite=ui -Dcucumber.filter.tags=@regression -Dbrowser=firefox -Dworkers=1
./mvnw -B -Papi test -Dsuite=api
```

API tests log in through the browser (including the application's CSRF login form) and transfer session cookies in memory. They then call real internal OrangeHRM JSON endpoints. They require a browser or Grid even though assertions use REST Assured. These are not OAuth/public API tests. See [compatibility](docs/compatibility.md).

JDBC runs inside relevant UI steps, not a separate synthetic SQL insertion suite. Read-only credentials require SELECT on five employee columns only. Fixtures and cleanup use application operations, never SQL writes. `@db` selects persistence-changing UI scenarios:

```bash
./mvnw test -Dcucumber.filter.tags=@db
./mvnw -B test -Dsuite=unit
./mvnw -B -DskipTests test-compile
./mvnw -B test -Dcucumber.execution.dry-run=true -Dcucumber.filter.tags=@regression
```

Dry-run checks Gherkin bindings; it does not exercise a browser or prove application behavior. On native PowerShell use `.\mvnw.cmd` and quote all `'-Dkey=value'` arguments. Set environment variables with `$env:ADMIN_USERNAME='...'`; `.env` is not automatically imported by PowerShell. The setup and CI shell scripts target Linux/WSL2.

## Excel and reports

`employees.xlsx` is a real XLSX file generated by Python's standard ZIP/XML libraries. Apache POI reads header-mapped immutable rows, including blank optional cells and 1/30/31-character name datasets, in the actual employee scenarios. Each call owns and closes its workbook/stream, so threads share no workbook. Regenerate assets with:

```bash
python3 scripts/generate_assets.py
```

Excel suits reusable business datasets; Gherkin Examples suit small tables that explain behavior in the feature itself. This suite has no Scenario Outlines: **40 scenarios, 40 scenario rows, 80 executions for a complete two-browser matrix**. Running both browsers never increases the logical scenario count.

```bash
./mvnw allure:report
./mvnw allure:serve
```

Results: `target/allure-results`; HTML: `target/site/allure-maven-plugin`. Failure hooks capture screenshot, sanitized source, URL, available console evidence and cleanup errors before quitting the browser. Cucumber supplies exception details. The UI classpath has only the Cucumber adapter; use `-Papi` only with `-Dsuite=api` to add the TestNG adapter without duplicate Cucumber entries. Keep synthetic data only; inspect artifacts before sharing.

Native Windows runs through `scripts/run-tests.ps1` store evidence separately under `target/runs/<RunName>`. For a combined browser report, `scripts/collect-results.py` adds browser-specific identities to copies of the real results; it preserves raw folders and original statuses. Historical failures can be included as clearly labeled separate entries. See the Windows runbook for report assembly commands.

## CI, defects and performance

[GitHub Actions](.github/workflows/qa.yml) provisions its own ephemeral Compose stack on a standard Ubuntu runner. It never connects to your laptop. A nightly run is scheduled at 01:00 India time, with manual dispatch available. `QA_ADMIN_PASSWORD` is an optional GitHub Secret; otherwise the job generates an ephemeral secret. Public repositories can use the standard free hosted runner allowance; private repositories are subject to account quotas. Schedules require available runners and can be delayed.

[Jenkinsfile](Jenkinsfile) requires a Linux agent labeled `linux-docker-java17` with Java 17, Python 3, Docker CLI/Engine and Compose. Create the secret-text credential `orangehrm-qa-admin-password`. Use a Pipeline from SCM job, select this Jenkinsfile and run Build with Parameters. The agent uses Java already installed; the pipeline verifies it. The optional controller is started with `docker compose --profile jenkins up -d jenkins`, at port 8081. Attach the Linux agent through Jenkins' node setup; the controller image alone is not a Docker-capable test agent. No commercial reporting plugins are required. Both pipelines archive reports and clean up after failure.

The [defect CSV](docs/defects.csv) contains **one reproduced application defect**, [DEF-001](docs/defects/DEF-001.md), with genuine Chrome/Firefox screenshots. It is prepared for Jira import; nothing has been logged in Jira. Follow [defect management](docs/defect-management.md). Preview the optional importer without credentials:

```bash
python3 scripts/jira_import.py
# Optional only after reviewing actual defect records and configuring JIRA_URL,
# JIRA_PROJECT, JIRA_EMAIL and JIRA_TOKEN:
python3 scripts/jira_import.py docs/defects.csv --execute
```

The benchmark compares sequential Chrome+Firefox against simultaneous Chrome+Firefox, with one scenario worker per browser in both modes. Warm dependency downloads first; keep the same running environment and resources:

```bash
./mvnw -B -DskipTests test-compile
python3 scripts/benchmark.py --trials 3
```

It stores raw trials, per-browser logs/Allure results, machine metadata, medians and formulas under `benchmark-results/`. Startup and HTML rendering are excluded; fresh scenario sessions and result recording are included. A failed/incomplete workload invalidates the comparison. Results are pending. “45 minutes to 15 minutes” is a target, not a measured claim. See [benchmark protocol](docs/benchmark.md).

## Troubleshooting and cleanup

| Symptom | Check |
| --- | --- |
| Docker pipe/daemon unavailable | Start Docker Engine inside WSL2/Linux; confirm `docker version` shows Server. |
| Login route shows installer | Finish installation and check `src/log/installer.log` inside app. |
| Connection refused from Grid | Use `BROWSER_BASE_URL=http://app/web/index.php`; keep host `BASE_URL` on localhost. |
| JDBC access denied | Match `.env` reader password and installed grant; reset stale lab volumes after credential changes. |
| Cucumber undefined steps | Run dry-run and check feature/step compilation. |
| Maven tries Java other than 17 | Set `JAVA_HOME` to a JDK 17 installation. |
| Browser queued | Each node has one slot; keep `workers=1` per browser. |
| Old app after image rebuild | Existing `app_data` wins; use explicit disposable-lab reset. |
| Failed test plus cleanup warning | Preserve original failure; investigate the logged owned employee ID and clean it through PIM. |

```bash
bash scripts/environment.sh down
# Destructive: deletes this lab's DB, installed app and optional Jenkins data.
bash scripts/environment.sh reset --delete-local-data
```

Known limits: source-backed locators and contracts still need live validation; the official noninteractive installer is deprecated; Leave entitlement/application and Admin account mutation cases are manual-only; role-based ESS restrictions are not yet automated beyond anonymous/logout protection. Single-node browser slots limit default concurrency to two across the browser matrix. Do not claim complete product regression or a speedup from the generated catalogue.

Learning: [architecture and scenario walkthrough](docs/architecture.md), [STLC test plan](docs/test-plan.md), [manual cases](docs/manual-cases.md), [RTM](docs/rtm.md), [interview/resume](docs/learning.md), [evidence index](docs/evidence-index.md).
#   O r a n g e H R M  
 