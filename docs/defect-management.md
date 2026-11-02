# Defect management

**Discovered application defects: 1.** [DEF-001](defects/DEF-001.md) was independently reproduced in Firefox and Chrome: Leave Reset retains unmatched Employee Name text. `defects.csv` is prepared for Jira import; nothing has been logged in Jira. Framework failures are recorded separately in framework-issues.md. No educational examples or injected faults are mixed into the defect dataset.

Investigate up to twelve real issues if execution exposes them; twelve is a cap for the exercise, not a required count. First exclude bad fixtures, configuration and locator bugs. Reproduce on a fresh independent scenario, compare with release behavior/source, record environment and evidence, then triage. Record root cause only after it is established.

Use the columns in defects.csv. Jira generally supports Summary, Issue Type, Priority, Description and project-specific fields; severity, environment and external ID may require custom mapping. In Jira Cloud Free, open project issue import / CSV import as an authorized project administrator, upload a **reviewed nonempty** CSV, map Summary and Issue Type, then map the remaining fields to supported/custom fields or combine them into Description. Import options depend on project type and permissions. Preview before confirming. Never import credentials, session cookies or real employee data.

The optional `scripts/jira_import.py` defaults to a local dry-run. `--execute` requires JIRA_URL, JIRA_PROJECT, JIRA_EMAIL and JIRA_TOKEN. It uses a standard Bug type, formats the description as Atlassian Document Format, and checks a deterministic external-ID label with enhanced JQL search before creating an issue. Run a single importer at a time: the search-then-create operation is not transactionally idempotent across concurrent processes. A timeout after creation should be reconciled by the label before retrying. No retry loop masks such uncertainty.

Source: [Jira Cloud enhanced search](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/) and [REST v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/). Credentials are read from environment and never printed. Default workflow status is the project's configured initial state; the CSV status is recorded in Description, not forced through an unverified workflow transition.

## Report template

* External ID / Summary:
* Environment / browser / Grid mode / OS:
* Application version / artifact hash:
* Preconditions and owned synthetic fixtures:
* Reproduction steps (numbered):
* Expected result and supporting requirement:
* Actual result:
* Severity / Priority and rationale:
* Evidence references (sanitized screenshot, Allure test UUID, log):
* Requirement / manual / UI test IDs:
* Status / reporter / date:
* Root cause: Unknown until established.
