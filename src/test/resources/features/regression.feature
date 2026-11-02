Feature: Local OrangeHRM 5.7 regression

  @UI-001 @regression @auth @smoke
  Scenario: UI-001 Administrator can authenticate
    When I log in with "ADMIN" and "ADMIN"
    Then the dashboard is shown

  @UI-002 @regression @auth
  Scenario: UI-002 Incorrect password is rejected
    When I log in with "ADMIN" and "WrongSynthetic123!"
    Then invalid credentials are reported

  @UI-003 @regression @auth
  Scenario: UI-003 Unknown username is rejected
    When I log in with "SyntheticMissingUser" and "WrongSynthetic123!"
    Then invalid credentials are reported

  @UI-004 @regression @auth
  Scenario: UI-004 Both login fields are mandatory
    Given I open the login page
    When I submit the form
    Then 2 required errors are shown

  @UI-005 @regression @auth
  Scenario: UI-005 Username is mandatory
    When I log in with "" and "WrongSynthetic123!"
    Then 1 required errors are shown

  @UI-006 @regression @auth
  Scenario: UI-006 Password is mandatory
    When I log in with "ADMIN" and ""
    Then 1 required errors are shown

  @UI-007 @regression @auth
  Scenario: UI-007 Login password control masks input
    Given I open the login page
    Then the password is masked

  @UI-008 @regression @auth @smoke
  Scenario: UI-008 Anonymous users cannot open employee list
    When I visit "/pim/viewEmployeeList"
    Then login is required

  @UI-009 @regression @auth
  Scenario: UI-009 Logout revokes protected-page access
    Given I am the local administrator
    When I log out
    And I visit "/pim/viewEmployeeList"
    Then login is required

  @UI-010 @regression @auth
  Scenario: UI-010 Password reset can be cancelled
    When I cancel password reset
    Then login is required

  @UI-011 @regression @pim @smoke @db
  Scenario: UI-011 Create an employee without optional middle name
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "minimal"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-012 @regression @pim @db
  Scenario: UI-012 Create an employee with all name parts
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "middle"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-013 @regression @pim @db
  Scenario: UI-013 First name min boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "first-min"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-014 @regression @pim @db
  Scenario: UI-014 First name max boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "first-max"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-015 @regression @pim
  Scenario: UI-015 First name over boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "first-over"
    And I submit the form
    Then validation reports "Should not exceed 30 characters"
    And the employee was not created

  @UI-016 @regression @pim
  Scenario: UI-016 First name empty boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "first-empty"
    And I submit the form
    Then validation reports "Required"
    And the employee was not created

  @UI-017 @regression @pim @db
  Scenario: UI-017 Last name min boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "last-min"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-018 @regression @pim @db
  Scenario: UI-018 Last name max boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "last-max"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-019 @regression @pim
  Scenario: UI-019 Last name over boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "last-over"
    And I submit the form
    Then validation reports "Should not exceed 30 characters"
    And the employee was not created

  @UI-020 @regression @pim
  Scenario: UI-020 Last name empty boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "last-empty"
    And I submit the form
    Then validation reports "Required"
    And the employee was not created

  @UI-021 @regression @pim @db
  Scenario: UI-021 Middle name max boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "middle-max"
    And I save the new employee
    Then the employee is persisted exactly

  @UI-022 @regression @pim
  Scenario: UI-022 Middle name over boundary
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "middle-over"
    And I submit the form
    Then validation reports "Should not exceed 30 characters"
    And the employee was not created

  @UI-023 @regression @pim @db
  Scenario: UI-023 Employee ID length 10 is accepted
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "minimal"
    And I set employee ID length to 10
    And I save the new employee
    Then the employee is persisted exactly

  @UI-024 @regression @pim
  Scenario: UI-024 Employee ID length 11 is rejected
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "minimal"
    And I set employee ID length to 11
    And I submit the form
    Then validation reports "Should not exceed 10 characters"
    And the employee was not created

  @UI-025 @regression @pim
  Scenario: UI-025 Duplicate employee ID is rejected
    Given I am the local administrator
    And a controlled employee exists
    When I attempt to reuse its employee ID
    Then validation reports "Employee Id already exists"
    And only the original employee exists

  @UI-026 @regression @pim
  Scenario: UI-026 Cancel does not create an employee
    Given I am the local administrator
    And I open Add Employee
    When I fill employee dataset "minimal"
    And I cancel Add Employee
    Then the cancelled employee does not exist

  @UI-027 @regression @pim
  Scenario: UI-027 Exact employee ID search isolates its row
    Given I am the local administrator
    And a controlled employee exists
    When I search for its employee ID
    Then only its employee row is shown

  @UI-028 @regression @pim
  Scenario: UI-028 Unknown employee ID returns no results
    Given I am the local administrator
    When I search for a nonexistent employee
    Then no records are shown

  @UI-029 @regression @pim
  Scenario: UI-029 Reset clears employee search
    Given I am the local administrator
    And a controlled employee exists
    When I search for its employee ID
    And I reset employee search
    Then employee search is cleared

  @UI-030 @regression @pim @smoke @db
  Scenario: UI-030 Update employee firstName and reload
    Given I am the local administrator
    And a controlled employee exists
    When I change "firstName" to "UpdatedFirst"
    Then the employee is persisted exactly

  @UI-031 @regression @pim @db
  Scenario: UI-031 Update employee lastName and reload
    Given I am the local administrator
    And a controlled employee exists
    When I change "lastName" to "UpdatedLast"
    Then the employee is persisted exactly

  @UI-032 @regression @pim @db
  Scenario: UI-032 Update employee middleName and reload
    Given I am the local administrator
    And a controlled employee exists
    When I change "middleName" to "UpdatedMiddle"
    Then the employee is persisted exactly

  @UI-033 @regression @pim @smoke @db
  Scenario: UI-033 Delete employee through UI removes persistence
    Given I am the local administrator
    And a controlled employee exists
    When I delete the controlled employee through the UI
    Then the employee is absent from MySQL and search

  @UI-034 @regression @admin
  Scenario: UI-034 Search administrator by exact username
    Given I am the local administrator
    When I search for the administrator account
    Then the administrator account is shown

  @UI-035 @regression @admin
  Scenario: UI-035 New user form enforces mandatory fields
    Given I am the local administrator
    When I visit "/admin/saveSystemUser"
    And I submit the form
    Then 5 required errors are shown
    And validation reports "Passwords do not match"

  @UI-036 @regression @admin
  Scenario: UI-036 New username length 4 rejected
    Given I am the local administrator
    When I visit "/admin/saveSystemUser"
    And I enter an administrator username of length 4
    Then validation reports "Should be at least 5 characters"

  @UI-037 @regression @admin
  Scenario: UI-037 New username length 41 rejected
    Given I am the local administrator
    When I visit "/admin/saveSystemUser"
    And I enter an administrator username of length 41
    Then validation reports "Should not exceed 40 characters"

  @UI-038 @regression @admin
  Scenario: UI-038 Cancel new user returns to user management
    Given I am the local administrator
    When I visit "/admin/saveSystemUser"
    And I cancel user creation
    Then the system user list is shown

  @UI-039 @regression @leave
  Scenario: UI-039 Leave search rejects malformed start date
    Given I am the local administrator
    When I visit "/leave/viewLeaveList"
    And I enter an invalid leave start date
    Then a date validation error is shown

  @UI-040 @regression @leave
  Scenario: UI-040 Leave search Reset clears employee filter
    Given I am the local administrator
    When I visit "/leave/viewLeaveList"
    And I reset leave search
    Then leave employee search is cleared
