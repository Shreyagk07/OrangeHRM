package steps;

import api.EmployeeApi;
import components.Form;
import config.Settings;
import data.ExcelData;
import db.EmployeeRepository;
import drivers.DriverFactory;
import io.cucumber.java.en.*;
import models.*;
import pages.*;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.testng.Assert;

public final class RegressionSteps {
    private final ScenarioContext c;
    private final EmployeePage employee = new EmployeePage();
    private final LoginPage login = new LoginPage();
    private final Form form = new Form();
    private final EmployeeRepository db = new EmployeeRepository();
    public RegressionSteps(ScenarioContext context) { c = context; }
    @Given("I am the local administrator") public void admin() { login.admin(); c.api = new EmployeeApi(); }
    @Given("I open the login page") public void loginPage() { form.open("/auth/login"); form.visible(By.name("username")); }
    @When("I log in with {string} and {string}") public void credentials(String username, String password) {
        login.login(username.equals("ADMIN") ? Settings.required("admin.username") : username, password.equals("ADMIN") ? Settings.required("admin.password") : password);
    }
    @Then("the dashboard is shown") public void dashboard() { form.awaitUrlContains("/dashboard/"); form.text("Dashboard"); }
    @Then("invalid credentials are reported") public void invalidCredentials() { form.text("Invalid credentials"); Assert.assertTrue(DriverFactory.get().getCurrentUrl().contains("/auth/login")); }
    @When("I submit the form") public void submit() { form.submit(); }
    @Then("{int} required errors are shown") public void required(int count) {
        form.error("Required");
        form.waitFor().until(d -> d.findElements(By.cssSelector(".oxd-input-field-error-message")).stream().filter(e -> e.getText().equals("Required")).count() == count);
    }
    @Then("the password is masked") public void masked() { Assert.assertEquals(form.visible(By.name("password")).getDomAttribute("type"), "password"); }
    @When("I visit {string}") public void visit(String path) { form.open(path); form.idle(); }
    @Then("login is required") public void loginRequired() { form.awaitUrlContains("/auth/login"); form.visible(By.name("username")); }
    @When("I log out") public void logout() { login.logout(); c.api = null; }
    @When("I cancel password reset") public void cancelReset() { form.open("/auth/requestPasswordResetCode"); form.button("Cancel"); }
    @Given("I open Add Employee") public void add() { employee.add(); employee.field("Employee Id", c.employeeId); }
    @When("I fill employee dataset {string}") public void dataset(String id) throws Exception {
        var data = ExcelData.row(id);
        c.expected = new Employee(data.get("firstName"), data.get("middleName"), data.get("lastName"), c.employeeId);
        employee.names(c.expected.firstName(), c.expected.middleName(), c.expected.lastName());
    }
    @When("I set employee ID length to {int}") public void idLength(int length) {
        c.employeeId = c.id + "X".repeat(length - c.id.length());
        c.expected = new Employee(c.expected.firstName(), c.expected.middleName(), c.expected.lastName(), c.employeeId);
        employee.field("Employee Id", c.employeeId);
    }
    @When("I save the new employee") public void save() { c.number = employee.saveCreated(); }
    @Then("the employee is persisted exactly") public void persisted() throws Exception {
        db.assertEmployee(c.expected);
        employee.awaitNames(c.expected);
        Assert.assertEquals(employee.value("firstName"), c.expected.firstName());
        Assert.assertEquals(employee.value("lastName"), c.expected.lastName());
        Assert.assertEquals(employee.value("middleName"), c.expected.middleName());
    }
    @Then("validation reports {string}") public void validation(String message) { form.error(message); }
    @Then("the employee was not created") public void absent() throws Exception { db.assertAbsent(c.employeeId); Assert.assertTrue(DriverFactory.get().getCurrentUrl().contains("/pim/addEmployee")); }
    @Given("a controlled employee exists") public void fixture() {
        var result = c.api.create(c.expected); EmployeeApi.ok(result); c.number = result.jsonPath().getInt("data.empNumber");
        Assert.assertEquals(result.jsonPath().getString("data.employeeId"), c.employeeId);
    }
    @When("I attempt to reuse its employee ID") public void duplicate() {
        employee.add(); employee.names("Duplicate", "", "Synthetic"); employee.field("Employee Id", c.employeeId); employee.submit();
    }
    @Then("only the original employee exists") public void original() throws Exception { db.assertEmployee(c.expected); }
    @When("I cancel Add Employee") public void cancelAdd() { employee.button("Cancel"); form.waitFor().until(ExpectedConditions.urlContains("/viewEmployeeList")); }
    @Then("the cancelled employee does not exist") public void cancelled() throws Exception { db.assertAbsent(c.employeeId); }
    @When("I search for its employee ID") public void search() { employee.search(c.employeeId); }
    @Then("only its employee row is shown") public void row() throws Exception {
        employee.row(c.employeeId); Assert.assertEquals(DriverFactory.get().findElements(By.cssSelector(".oxd-table-body .oxd-table-row")).size(), 1); db.assertEmployee(c.expected);
    }
    @When("I search for a nonexistent employee") public void noMatch() { employee.search(c.id); }
    @Then("no records are shown") public void noRecords() { form.text("No Records Found"); }
    @When("I reset employee search") public void reset() { form.button("Reset"); form.waitFor().until(d -> form.visible(form.label("Employee Id")).getDomProperty("value").isEmpty()); }
    @Then("employee search is cleared") public void searchCleared() { Assert.assertEquals(form.visible(form.label("Employee Id")).getDomProperty("value"), ""); }
    @When("I change {string} to {string}") public void update(String field, String value) {
        employee.personal(c.number); employee.awaitNames(c.expected); employee.type(By.name(field), value);
        c.expected = new Employee(field.equals("firstName") ? value : c.expected.firstName(), field.equals("middleName") ? value : c.expected.middleName(), field.equals("lastName") ? value : c.expected.lastName(), c.employeeId);
        employee.savePersonal(); employee.personal(c.number);
    }
    @When("I delete the controlled employee through the UI") public void delete() { employee.deleteRow(c.employeeId); }
    @Then("the employee is absent from MySQL and search") public void deleted() throws Exception { db.assertAbsent(c.employeeId); employee.search(c.employeeId); noRecords(); c.deleted = true; }
    @When("I search for the administrator account") public void searchAdmin() { form.open("/admin/viewSystemUsers"); form.idle(); form.field("Username", Settings.required("admin.username")); form.submit(); form.idle(); }
    @Then("the administrator account is shown") public void adminShown() { form.text(Settings.required("admin.username")); form.text("Admin"); }
    @When("I enter an administrator username of length {int}") public void userLength(int length) { form.field("Username", "Q".repeat(length)); form.submit(); }
    @When("I cancel user creation") public void cancelUser() { form.button("Cancel"); }
    @Then("the system user list is shown") public void users() { form.waitFor().until(ExpectedConditions.urlContains("/admin/viewSystemUsers")); form.text("System Users"); }
    @When("I enter an invalid leave start date") public void badDate() { form.field("From Date", "not-a-date"); form.submit(); }
    @Then("a date validation error is shown") public void dateError() {
        form.visible(By.xpath("//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='From Date']]//*[contains(@class,'oxd-input-field-error-message')]"));
        Assert.assertTrue(DriverFactory.get().getCurrentUrl().contains("/leave/viewLeaveList"));
    }
    @When("I reset leave search") public void resetLeave() { form.field("Employee Name", "SyntheticNoMatch"); form.button("Reset"); }
    @Then("leave employee search is cleared") public void leaveClear() {
        var observed = new java.util.concurrent.atomic.AtomicReference<>("<not observed>");
        try {
            form.waitFor().until(driver -> {
                observed.set(driver.findElement(form.label("Employee Name")).getDomProperty("value"));
                return observed.get().isEmpty();
            });
        } catch (TimeoutException timeout) {
            Assert.fail("Leave Reset must clear Employee Name; actual value remained '" + observed.get() + "' (UI-040 / REQ-06)", timeout);
        }
        Assert.assertEquals(observed.get(), "", "Leave Reset must clear Employee Name");
    }
}
