# Framework issues found during live execution

These are automation/environment findings, kept separate from discovered OrangeHRM application defects.

| ID | Observed issue | Fix | Evidence / validation |
| --- | --- | --- | --- |
| FW-001 | MySQL `mysqladmin ping -h localhost` could mark the socket-only temporary initialization server healthy before application TCP access was ready | Health check now executes authenticated `SELECT 1` over TCP, with initialization start period | Initial database logs showed temporary server port 0; replacement MySQL container passed the corrected check; installation completed |
| FW-002 | UI-011 read empty Personal Details values immediately after the redirect, while MySQL already held the correct employee | Wait explicitly for the expected first/middle/last input values before assertions and before editing an existing employee | `smoke-initial`: assertion failure plus screenshot of loading spinner. `smoke-sync-fix`: business assertions passed. `smoke-json-fix`: full scenario including cleanup passed |
| FW-003 | REST Assured DELETE cleanup failed with “no JSON serializer found in classpath” | Added explicit pinned Gson 2.11.0 dependency | `smoke-sync-fix` sanitized stack trace identifies serialization failure; `smoke-json-fix` and `api-initial` passed with real JSON writes and deletion |
| FW-004 | Cleanup diagnostics recorded only an exception class; a cleanup-only failure also missed UI screenshot capture | Attach sanitized cleanup stack traces and capture available UI evidence before quitting on cleanup-only failures | Real cleanup stack captured in `smoke-sync-fix`; expanded screenshot branch implemented, not artificially fault-injected |
| FW-005 | Live Allure Cucumber results lacked browser parameters and shared history identity; dynamic hook metadata was not retained by the adapter | Preserve raw run folders and add explicit browser identity while assembling the combined report with collect-results.py | A partial real matrix produced 13 entries and 13 unique browser-specific histories; original statuses unchanged |
| FW-006 | UI-010 expected the reset form's Cancel button although the fresh installation had no email configuration; the controller correctly displayed its email warning instead | Add pinned local Mailpit and configure the verified email API as a lab prerequisite, without sending mail; readiness checks require that configuration | Local SMTP configuration saved and read back; Firefox UI-010 passed after provisioning. Chrome UI-010 passed in chrome-affected-final |
| FW-007 | During concurrent execution, some PIM navigations returned raw server component tags before Vue mounted; the next field wait timed out | Navigation now waits for the observed `#app[data-v-app]` bootstrap marker under a separate 60-second page-load budget. Field/business waits stay at 20 seconds. No refresh, action retry or assertion change | Raw HTML and screenshots preserved from Chrome UI-011/UI-013; Chrome UI-010/UI-011/UI-013 passed in chrome-affected-final. Host snapshot also showed high browser CPU use and about 690 MiB free Windows RAM, so final matrix will run sequentially |

The initial concurrent Chrome run later encountered a failed browser shutdown and Grid session-creation timeouts. That partial diagnostic run was explicitly stopped by matching only its Maven command line (`regression-chrome-1`) and stopping only the project's Chrome node. Firefox and the application/database were left running. The remaining Chrome cases are not counted as executed from that interrupted run; the final current-code Chrome run subsequently completed 39 passed, 1 failed (DEF-001), 0 skipped. No test retry policy was added.

The two leaked owned fixtures from the failed cleanup attempts (`Q09cacfdb`, `Q57ce8923`) were independently located, checked for exact Qa/Synthetic business values, deleted through the supported authenticated application API, and verified absent. The recovery command was:

```powershell
python scripts/cleanup-employees.py Q09cacfdb Q57ce8923
python scripts/cleanup-employees.py Q09cacfdb Q57ce8923 --execute
```

The first command previews; the second performs only those named deletions. It refuses unrelated IDs or unexpected names. No direct application-table writes were used.

The official CLI installer emitted two bundled Doctrine PHP deprecation warnings but completed successfully. These warnings alone have not been classified as a reproducible application defect.

## 29 October continuation

The completed `regression-chrome-final` run had 36 passed, 4 failed, 0 skipped: UI-040 confirmed DEF-001; UI-012 renderer disconnect, UI-029 WebDriver HTTP timeout, and UI-033 result-visibility timeout remain intermittent execution findings. UI-033 screenshot/source already show No Records Found; no product defect is established from that timeout. An unchanged-code focused run `chrome-diagnosis-1029` passed UI-012/UI-029/UI-033 (3/0/0). This is diagnostic evidence, not a retry policy or proof that the environment issue is fixed. The original failures and attachments remain intact. A new complete sequential Chrome run is recorded separately.

## FW-008 ? authentication navigation used the field budget

Firefox recovery checks reached the populated login form but timed out waiting for `/dashboard/` under the 20-second field timeout. Apache access logs independently showed successful Firefox POST `/auth/validate` (302) and GET `/dashboard/index` (200), approximately 27 seconds apart. An independent Python session-authenticated email-configuration read also succeeded. These observations do not establish an OrangeHRM authentication defect.

`Form.awaitUrlContains` now applies the existing `page.timeout=60` to authentication/navigation URL transitions. The expected URL predicates are unchanged. Field/business waits remain 20 seconds; UI-040's empty-value assertion remains active. No action or scenario retries were added. Post-fix `firefox-navigation-check-1029` passed UI-015/UI-016: 2 passed, 0 failed, 0 skipped. Full regression results are recorded in validation.md.

The preceding new-session failures occurred with low host free RAM and high Firefox CPU. Only the affected run processes/nodes were recovered. Firefox's unused Xvfb/VNC stack and unconfigured telemetry export were disabled through switches verified in the pinned image startup scripts; this is resource reduction, not proof of a complete hardware/startup root cause. The initial lightweight-node check still failed login navigation and is retained (`firefox-headless-check-1029`: 0 passed, 2 failed, 0 skipped). A preceding interrupted recovery check completed one failing login case; its other case was not completed. Do not relabel these as product defects or passes.

## FW-009 ? open Firefox session-start instability

The complete `regression-firefox-fixed-1029` run attempted all 40 scenarios: 38 passed, UI-040 failed with DEF-001, and UI-015 failed in `DriverFactory.start` with `SessionNotCreatedException` / client request timeout. Its application assertions were not reached. The remaining scenarios continued and passed. A preceding focused post-navigation-fix run passed UI-015/UI-016; that does not erase the full-run startup failure.

This is an unresolved Grid/browser/environment finding, not an OrangeHRM application defect. Low Windows free RAM (about 541?619 MiB in sampled readings) and high Firefox CPU were observed; a complete root cause is not established. Disabling unused headless-node desktop processes did not alone resolve login timing. No scenario retry, skipped test or browser-version substitution was added. A startup failure has no screenshot when no WebDriver session was obtained; its stack is preserved. Avoid simultaneous browser execution on this host. Keep Windows awake; investigate host resource/sleep/network changes if startup stalls recur.

Final verification: `regression-chrome-fixed-1029` 39/1/0; `regression-firefox-fixed-1029` 38/2/0; `api-final-1029` 1/0/0. Full counts include FW-009 as a failed setup and DEF-001 as active business failures. Final report verification and browser opening are recorded in validation.md.
