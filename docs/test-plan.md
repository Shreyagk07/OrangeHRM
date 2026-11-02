# STLC test plan, scope and risks

**Purpose:** evaluate a synthetic local OrangeHRM 5.7 lab and demonstrate repeatable testing practice. Owner: learner QA engineer; stakeholders: reviewer and application maintainer. No real employee data.

| Phase | Entry / work | Exit / deliverable |
| --- | --- | --- |
| Requirements analysis | Review official tagged source and installer; identify supported screens, constraints, auth and schema | requirements.md, compatibility.md; unresolved runtime assumptions listed |
| Planning | Prioritize authentication, employee persistence and cleanup; allocate local resources | this plan, risks and execution commands |
| Design | EP valid/invalid classes, actual screen boundaries, independently owned prerequisites | 50 manual cases, RTM, 40 UI scenarios, XLSX |
| Environment | Build official binary with PHP/Apache, real MySQL, Grid | Installed login, successful authenticated API request and SELECT reader check |
| Execution | Smoke first; then regression on both browsers; API lifecycle; manual-only cases | Actual statuses, Allure evidence, execution log |
| Defect lifecycle | Reproduce independently, establish expected behavior, attach sanitized evidence | Real defect records; no quota-driven fabrication |
| Closure | Review coverage, cleanup, residual risks and failed tests | Completed summary and acceptance matrix; measured benchmark if possible |

**In scope:** login/logout/access control, employee create/name validation/search/update/delete, user search/form validation/cancel, leave search validation/reset. Manual-only additions cover ESS accounts and entitled leave application/cancellation. **Out of scope:** payroll, third-party SSO, production load, accessibility certification, mobile app and enterprise-only modules. The current 40 scenarios are not comprehensive product coverage.

Entry to live testing requires the official release artifact, configured local administrator, completed installation, SELECT reader grants and browser reachability. Exit target: all critical smoke scenarios pass in Chrome and Firefox, no unresolved critical/high defects, reviewed manual results and owned-fixture cleanup. Any unexecuted/manual-only case remains explicitly Not Run. Framework compile success is not an application exit criterion.

| Risk | Probability / impact | Mitigation |
| --- | --- | --- |
| No Docker Server | High / blocks all integration | Record blocker, validate compile and bindings; execute later on Linux/WSL2 |
| Deprecated CLI installer | Medium / initialization failure | Pin release; preserve logs privately; documented wizard fallback; fail early |
| OXD rendered locator differs from source inference | Medium / false automation failure | Live inspector confirmation required; scoped labels and name selectors |
| Fixture leakage after partial save | Medium / contaminated runs | Unique per-scenario ID; API search cleanup even when save redirect fails; cleanup failures fail passing tests |
| Cross-browser resource contention | Medium / invalid benchmark | Two fixed node slots; same workload/resources; reject failed/incomplete trials |
| Secrets in evidence | Medium / disclosure | Synthetic data, sanitized text, withheld cookies/headers, short retention, inspect before publication |
| Role/Leave configuration absent | High / manual prerequisites missing | State exact owned fixtures; no dependence on public demo or shared sample employees |

**Design classes:** authentication valid/incorrect/unknown/empty; PIM required names 1–30 vs 0/31, optional middle 0–30 vs 31, Add Employee ID 0–10 and unique vs 11/duplicate; Admin username 5–40 vs 4/41; Leave valid configured dates vs malformed/reversed intervals. Optional empty values are valid, not assumed invalid. Database varchar capacities do not determine UI boundaries. See each case's dataset for concrete values. Boundary cases intentionally isolate one field at a time.

Severity expresses impact (Critical/High/Medium/Low); priority expresses repair urgency (P1–P4). The tester does not label a source inconsistency as a discovered application defect without reproduction.
