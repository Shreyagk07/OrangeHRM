package tests;

import api.EmployeeApi;
import config.Settings;
import db.EmployeeRepository;
import drivers.DriverFactory;
import io.qameta.allure.Allure;
import io.restassured.RestAssured;
import models.Employee;
import org.testng.Assert;
import org.testng.annotations.*;
import pages.LoginPage;
import java.util.UUID;

public final class EmployeeApiTest {
    @Test(groups={"api", "db"}) public void employeeLifecycleAndAccessControl() throws Exception {
        String id = "A" + UUID.randomUUID().toString().replace("-", "").substring(0,8);
        Integer number = null; EmployeeApi api = null;
        Throwable primary = null;
        try {
            DriverFactory.start(); new LoginPage().admin(); api = new EmployeeApi();
            Employee initial = new Employee("Api", "", "Synthetic", id);
            var created = api.create(initial); EmployeeApi.ok(created); number = created.jsonPath().getInt("data.empNumber");
            Assert.assertEquals(created.jsonPath().getString("data.firstName"), initial.firstName());
            var fetched = api.get(number); EmployeeApi.ok(fetched); Assert.assertEquals(fetched.jsonPath().getString("data.employeeId"), id);
            var searched = api.search(id); EmployeeApi.ok(searched); Assert.assertEquals(searched.jsonPath().getList("data.empNumber").size(), 1); Assert.assertEquals(searched.jsonPath().getInt("data[0].empNumber"), number.intValue());
            Employee updated = new Employee("ApiUpdated", "", "Synthetic", id);
            var changed = api.update(number, updated); EmployeeApi.ok(changed); Assert.assertEquals(changed.jsonPath().getString("data.firstName"), updated.firstName());
            new EmployeeRepository().assertEmployee(updated);
            var invalid = api.create(new Employee("", "", "Synthetic", "X" + id));
            Assert.assertEquals(invalid.statusCode(), 422); Assert.assertNotNull(invalid.jsonPath().get("error"));
            var unauthorized = RestAssured.given().baseUri(Settings.base()).redirects().follow(false).accept("application/json").get("/api/v2/pim/employees");
            Assert.assertEquals(unauthorized.statusCode(), 401, "Internal API must reject an anonymous session");
            Assert.assertNotNull(unauthorized.jsonPath().get("error"));
            Allure.addAttachment("Sanitized API evidence", "text/plain", "POST employee: 200; GET: 200; search: one matching owned ID; PUT personal-details: 200; invalid payload: 422; anonymous: 401. Headers, cookies and credentials omitted.");
        } catch (Exception | AssertionError e) { primary = e; Allure.addAttachment("API failure", "text/plain", e.getClass().getName() + ": integration failed; request headers/cookies withheld"); throw e; }
        finally {
            try {
                if (api != null && number != null) { EmployeeApi.ok(api.delete(number)); new EmployeeRepository().assertAbsent(id); }
            } catch (Exception | AssertionError cleanup) { if (primary != null) primary.addSuppressed(cleanup); else throw cleanup; }
            finally { DriverFactory.stop(); }
        }
    }
}
