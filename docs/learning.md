# Interview and resume notes

**Interview explanation:** “I built a Java 17 test project around a self-hosted OrangeHRM release. Cucumber describes business scenarios, TestNG supplies execution, and page objects contain browser operations. Each scenario owns a thread-local browser and unique employee data. For employee mutations I compare the UI result with read-only MySQL queries, and I use authenticated internal REST endpoints for controlled setup and cleanup. I keep generated coverage separate from executed evidence. My local machine lacked Docker Server, so I validated what I could without claiming live regression results.”

Why prepared statements: values remain data and cannot alter SQL structure. Why explicit waits: wait for business-relevant UI conditions instead of guessing elapsed time. Why no retries: a failing first attempt is evidence to investigate. Why immutable Excel rows: workbooks are not thread-safe shared test state. Why separate API adapter profile: Cucumber and TestNG reporting together can create duplicate UI entries.

Honest resume wording at this stage:

* Implemented a Java 17 Selenium/Cucumber testing project with 40 UI scenario definitions, 50 manual cases and requirements traceability for OrangeHRM 5.7.
* Added Excel dataset execution, session-authenticated REST Assured integration code, parameterized JDBC checks, Docker/Grid configuration and Jenkins/GitHub Actions pipelines.
* Built repeatable equivalent-workload browser benchmark tooling; live browser/API/JDBC validation recorded in validation.md; performance measurements remain pending.

Only replace “implemented” with “validated/executed” after saving actual evidence. Do not claim twelve defects, 100% regression success, production readiness or a threefold speedup without measurement. Build/dry-run evidence supports framework construction, not OrangeHRM business behavior.
