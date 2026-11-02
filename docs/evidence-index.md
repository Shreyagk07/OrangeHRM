# Evidence index

| Evidence | Location | Meaning |
| --- | --- | --- |
| Compatibility and source contracts | compatibility.md | Pinned release, source links, schema/route/constraint decisions |
| Plan and risks | test-plan.md | STLC phases, scope, entry/exit conditions |
| Requirements | requirements.md | REQ-01 through REQ-08 |
| Manual design | manual-cases.csv / manual-cases.md | Exactly 50 cases, initially Not Run |
| UI catalogue | ui-coverage.csv / ui-coverage.md | Exactly UI-001 through UI-040; database classification |
| Traceability | rtm.csv / rtm.md | Requirement ↔ manual ↔ UI IDs; manual-only gaps explicit |
| Execution template | execution-log.csv | 81 selected live UI/API executions recorded |
| Actual defects | defects.csv | DEF-001: reproduced Leave Reset defect; prepared for Jira import, not submitted |
| Framework validation | validation.md | Commands and actual local outcomes, no inferred business passes |
| Live reports | ../target/runs/<run-name>/allure-results and ../target/runs/<run-name>/site/allure-maven-plugin | Final current report: target/runs/final-live-1029/site/allure-maven-plugin; 81 real entries; historical diagnostics retained separately |
| Performance | ../benchmark-results | Pending; raw trials and summary created by benchmark.py |
| Closure | test-summary-template.md / acceptance.md | Fill actual results; distinguish implemented, executed, verified and blocked |

Never map a generated scenario or dry-run pass to an executed manual case. When tests run, add run IDs/evidence to the execution log and RTM intentionally; generation scripts reset design documents to Not Run.

Cleanup inventory and exact removed-file byte counts: [29 October cleanup](cleanup-2026-10-29.md). Historical raw failures remain separate from the final full-run report.

Final counts and report verification are in [validation.md](validation.md); copy-ready future commands are in [next-run.md](next-run.md). Manual execution remains Not Run.
