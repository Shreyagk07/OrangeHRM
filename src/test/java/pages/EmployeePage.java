package pages;

import components.Form;
import models.Employee;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;

public final class EmployeePage extends Form {
    public void add() { open("/pim/addEmployee"); visible(By.name("firstName")); idle(); }
    public void names(String first, String middle, String last) {
        type(By.name("firstName"), first); type(By.name("middleName"), middle); type(By.name("lastName"), last);
    }
    public int saveCreated() {
        submit(); waitFor().until(ExpectedConditions.urlContains("/viewPersonalDetails/empNumber/"));
        return Integer.parseInt(d().getCurrentUrl().replaceAll(".*/empNumber/(\\d+).*", "$1"));
    }
    public void personal(int number) { open("/pim/viewPersonalDetails/empNumber/" + number); visible(By.name("firstName")); idle(); }
    public void awaitNames(Employee expected) {
        waitFor().withMessage("Personal Details did not load the expected first/middle/last names for " + expected.employeeId())
            .until(driver -> expected.firstName().equals(driver.findElement(By.name("firstName")).getDomProperty("value"))
                && expected.middleName().equals(driver.findElement(By.name("middleName")).getDomProperty("value"))
                && expected.lastName().equals(driver.findElement(By.name("lastName")).getDomProperty("value")));
    }
    public void savePersonal() {
        d().findElements(By.cssSelector("button[type='submit']")).get(0).click();
        visible(By.cssSelector(".oxd-toast--success")); idle();
    }
    public void search(String employeeId) {
        open("/pim/viewEmployeeList"); idle(); field("Employee Id", employeeId); submit(); idle();
    }
    public void row(String employeeId) { visible(By.xpath("//div[contains(@class,'oxd-table-row')][.//div[normalize-space()='" + employeeId + "']]")); }
    public void deleteRow(String employeeId) {
        search(employeeId); row(employeeId);
        d().findElement(By.xpath("//div[contains(@class,'oxd-table-row')][.//div[normalize-space()='"+employeeId+"']]//button[.//i[contains(@class,'bi-trash')]]")).click();
        button("Yes, Delete"); visible(By.cssSelector(".oxd-toast--success"));
    }
    public String value(String name) { return visible(By.name(name)).getDomProperty("value"); }
}
