# Requirements catalogue

These are testable lab requirements derived from the tagged implementation, not an invented product specification.

| ID | Requirement | Source / acceptance |
| --- | --- | --- |
| REQ-01 | Valid administrator authenticates; invalid/empty credentials are rejected; password masked | Login.vue / ValidateController; correct screen and error behavior |
| REQ-02 | Admin creates employee with required first/last names, optional middle, unique ID; screen lengths enforced | SaveEmployee.vue; UI plus exact MySQL name/ID values |
| REQ-03 | Employee ID search isolates matches; no match and Reset handled | Employee.vue; owned matching row or no records |
| REQ-04 | Employee name edits survive reload; deletion removes employee from search and persistence | EmployeePersonalDetails.vue, EmployeeAPI deletion; JDBC |
| REQ-05 | Admin can find user accounts; Add User requires valid role, employee, status, username and passwords | SaveSystemUser.vue / SystemUser.vue; constraints and cancel behavior |
| REQ-06 | Leave filtering validates dates and resets filters; entitled leave has controlled workflow | LeaveList.vue / LeaveApply.vue; mutation workflows manual-only |
| REQ-07 | Anonymous/logged-out access blocked; ESS cannot perform privileged unrelated operations | AuthenticationSubscriber and role configuration; ESS manual-only |
| REQ-08 | Framework isolates sessions/data, reads Excel safely, captures evidence and preserves failures | DriverFactory, hooks, ExcelData, suite configuration; utility tests and execution review |

API lifecycle and JDBC integration support REQ-02/03/04/07. REQ-08 is covered by utility checks and framework review, not by inflating the manual case count. Detailed UI/manual mappings are in rtm.csv and ui-coverage.csv.
