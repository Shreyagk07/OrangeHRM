package api;

import config.Settings;
import drivers.DriverFactory;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import models.Employee;
import java.util.*;

/** Application-internal JSON endpoints, authenticated with a real browser session. */
public final class EmployeeApi {
    private final Map<String, String> cookies = new HashMap<>();
    public EmployeeApi() { DriverFactory.get().manage().getCookies().forEach(c -> cookies.put(c.getName(), c.getValue())); }
    private RequestSpecification request() {
        return RestAssured.given().baseUri(Settings.base()).cookies(cookies).contentType("application/json").accept("application/json").filter(new listeners.ApiEvidence());
    }
    public Response create(Employee employee) { return request().body(employee).post("/api/v2/pim/employees"); }
    public Response get(int number) { return request().get("/api/v2/pim/employees/" + number); }
    public Response search(String id) { return request().queryParam(id.length() <= 10 ? "employeeId" : "nameOrId", id).get("/api/v2/pim/employees"); }
    public Response update(int number, Employee e) { return request().body(e).put("/api/v2/pim/employees/" + number + "/personal-details"); }
    public Response delete(int number) { return request().body(Map.of("ids", List.of(number))).delete("/api/v2/pim/employees"); }
    public static void ok(Response response) {
        org.testng.Assert.assertEquals(response.statusCode(), 200, "OrangeHRM API failed; content type=" + response.contentType());
        org.testng.Assert.assertTrue(response.contentType().contains("json"), "Expected JSON, possibly redirected to login");
    }
}
