# Acceptance matrix ? 29 October 2026

Live execution and reporting completed with open failures. **Exit criteria are not met:** DEF-001 remains reproducible and FW-009 caused a Firefox setup failure. Expected values and UI-040's assertion remain active; no test retries or skipped scenarios were introduced.

| Deliverable | Actual execution / verification | Remaining |
| --- | --- | --- |
| Installed official OrangeHRM 5.7 / MySQL | Persistent installed environment reused; authenticated API/JDBC passed; final readiness exit 0 | None for installation |
| Docker / Grid / Mailpit | Engine 28.5.1, Compose v2.40.3, WSL2; both browser nodes UP/idle; configured mail sink ready | FW-009 startup instability can recur |
| Java / Maven Wrapper | Java 17.0.13, Maven 3.9.9; 17 source files compiled for final runs | None for compilation |
| Real UI smoke / data lifecycle | smoke-json-fix passed; final Chrome UI-011/UI-033 passed with JDBC and cleanup | None for these slices |
| Full Chrome, final code | 40 attempted: **39 passed, 1 failed, 0 skipped** | UI-040 / DEF-001 |
| Full Firefox, final code | 40 attempted: **38 passed, 2 failed, 0 skipped** | UI-040 / DEF-001; UI-015 startup / FW-009 |
| API authentication / JDBC | api-final-1029: **1 passed, 0 failed, 0 skipped**; lifecycle, invalid 422, anonymous 401, DB update/deletion | None for this integration check |
| Excel datasets | XLSX preserved; earlier utility-final **1 passed**; final UI datasets executed | No new utility test needed for navigation-only fix |
| Final Allure / evidence | **81 entries: 78 passed, 2 failed, 1 broken**; 81 unique browser histories; 2 actual failure PNGs; HTTP 200 and browser opened | Startup failure has no browser screenshot |
| Cleanup | **238,624,311 bytes** redundant file content removed; no volume/global Docker prune; sources/datasets/evidence preserved | Physical net free-space change not measured |
| 50 manual cases / RTM | 50 cases and 50 mappings preserved; automated outcomes and 81 execution-log rows recorded separately | All manual statuses remain Not Run |
| Application defects | One actual defect, DEF-001; reproduction/evidence retained; CSV ready | Open; no application patch or Jira write |
| Jenkins / GitHub Actions | Pipelines preserved; prior syntax/configuration checks | Jobs not executed |
| Benchmark | Tooling/protocol preserved | Trials unexecuted; no speedup claim |

Final report: `target/runs/final-live-1029/site/allure-maven-plugin/index.html`, served at **http://127.0.0.1:8765/**. Report generation succeeded; this does not change the failed test counts. Final authenticated employee inventory: one administrator row, zero framework-ID fixtures.

See [validation and chronology](validation.md), [framework findings](framework-issues.md), [DEF-001](defects/DEF-001.md), [cleanup manifest](cleanup-2026-10-29.json), and [exact next-run commands](next-run.md).
