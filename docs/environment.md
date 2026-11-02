# Local environment and initialization

| Service | Host URL / port | Container address |
| --- | --- | --- |
| OrangeHRM | http://localhost:8080 | http://app |
| Login | http://localhost:8080/web/index.php/auth/login | http://app/web/index.php/auth/login |
| MySQL | localhost:3307 | mysql:3306 |
| Grid | http://localhost:4444/ui | hub:4444 |
| Optional Jenkins | http://localhost:8081 | jenkins:8080 |
| Local Mailpit viewer / SMTP sink | http://localhost:8025 | mailpit:1025 (SMTP, no host publication) |

Only loopback ports are published. Browsers use the Compose `app` hostname, while the Java process uses localhost. Session cookie values are copied into an in-memory REST Assured request; no cookie files or credential attachments are produced.

Mailpit is part of the standard lab because the reset form is only available after email configuration. The setup script configures that prerequisite through the supported email API; it does not send a message. Mailpit has no external relay configured. The application entry wizard does not set SMTP by itself.

The MySQL service starts without an application database. First installation creates `orangehrm` through the official installer, then `orangehrm_app` with the installer's runtime permissions. The separate `qa_reader` user gets SELECT only on the employee key, identifier and name columns. Schema migrations and business fixtures are not run with this reader.

`scripts/environment.sh install` creates a temporary installer YAML with mode 0600 inside the app container, invokes the official installer and deletes that YAML in a finally block. App configuration remains in the app volume because OrangeHRM needs its database credentials. Do not archive that volume or `.env`.

The source ZIP is not used as an application binary. `docker/Dockerfile` checks the release ZIP hash before extracting the complete shipped distribution. Debian apt package patch revisions and transitive container digests are not fully locked; dated version tags and the application hash provide a reproducible baseline, not a bit-for-bit supply-chain build.

If choosing the web-wizard alternative, create the reader afterwards through an administrator MySQL client. Use a properly quoted generated secret in place of the placeholder (never commit it):

```sql
CREATE USER 'qa_reader'@'%' IDENTIFIED BY '<reader password from .env>';
GRANT SELECT (emp_number, employee_id, emp_firstname, emp_middle_name, emp_lastname)
ON orangehrm.hs_hr_employee TO 'qa_reader'@'%';
SHOW GRANTS FOR 'qa_reader'@'%';
```

This is infrastructure account provisioning, not application-table mutation. The Java reader also calls `Connection.setReadOnly(true)`; database grants provide the actual restriction.

Readiness waits are bounded: MySQL health requires a responsive server; the app health requires an HTTP login response; `readiness.py` additionally checks the rendered login component and two registered Grid nodes. Integration tests establish authentication and real SELECT access. A healthy HTTP service alone is not proof of a completed installation.

Reset is explicitly destructive and restricted by the Compose project name: `bash scripts/environment.sh reset --delete-local-data`. It removes all three named volumes, including optional Jenkins data. `down` preserves data. For CI use an isolated machine/job and allow no unrelated stack to reuse the same ports/project. Installation failure should fail the job before tests; report generation after failed **tests** occurs in `ci.sh`, and final cleanup occurs in each CI definition.
