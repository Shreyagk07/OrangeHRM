package listeners;

import io.qameta.allure.Allure;
import io.restassured.filter.*;
import io.restassured.response.Response;
import io.restassured.specification.*;
import java.net.URI;
import java.util.*;

/** Allowlisted response fields; no Authorization, Set-Cookie, Cookie or CSRF values. */
public final class ApiEvidence implements Filter {
    @Override public Response filter(FilterableRequestSpecification request, FilterableResponseSpecification responseSpec, FilterContext context) {
        Response response = context.next(request, responseSpec);
        try {
            Map<String, Object> safe = new LinkedHashMap<>();
            safe.put("request", request.getMethod() + " " + URI.create(request.getURI()).getPath());
            safe.put("status", response.statusCode());
            if (response.contentType().contains("json")) {
                for (String key : List.of("data.empNumber", "data.employeeId", "data.firstName", "data.middleName", "data.lastName", "meta.total", "error.status", "error.message")) {
                    Object value = response.jsonPath().get(key);
                    if (value != null) safe.put(key, value);
                }
            }
            Allure.addAttachment("Sanitized API request/response", "text/plain", Sanitizer.clean(safe.toString()));
        } catch (Exception e) {
            // Reporting cannot replace the real response or conceal its assertion failure.
            System.err.println("API evidence unavailable: " + e.getClass().getSimpleName());
        }
        return response;
    }
}
