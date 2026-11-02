package hooks;

import api.EmployeeApi;
import config.Settings;
import db.EmployeeRepository;
import drivers.DriverFactory;
import io.cucumber.java.*;
import models.ScenarioContext;
import org.openqa.selenium.*;
import java.util.*;

public final class ScenarioHooks {
    private final ScenarioContext context;
    public ScenarioHooks(ScenarioContext context) { this.context = context; }
    @Before public void start(Scenario scenario) throws Exception {
        DriverFactory.start();
        scenario.attach("OrangeHRM=5.7; browser=" + Settings.get("browser") + "; mode=" + (Settings.get("grid.url").isBlank() ? "local" : "Grid"), "text/plain", "environment");
    }
    @After public void finish(Scenario scenario) throws Exception {
        Exception cleanupFailure = null;
        try {
            if (scenario.isFailed()) captureFailure(scenario);
            if (context.api != null && !context.deleted) {
                var response = context.api.search(context.employeeId);
                EmployeeApi.ok(response);
                List<Integer> ids = response.jsonPath().getList("data.empNumber", Integer.class);
                for (Integer id : ids) EmployeeApi.ok(context.api.delete(id));
                new EmployeeRepository().assertAbsent(context.employeeId);
            }
        } catch (Exception e) { cleanupFailure = e; cleanupEvidence(scenario, e); if (!scenario.isFailed()) captureFailure(scenario); }
        catch (AssertionError e) { cleanupFailure = new IllegalStateException("Cleanup verification failed for " + context.employeeId, e); cleanupEvidence(scenario, e); if (!scenario.isFailed()) captureFailure(scenario); }
        finally {
            try { DriverFactory.stop(); } catch (Exception e) { if (cleanupFailure == null) cleanupFailure = e; else cleanupFailure.addSuppressed(e); }
        }
        if (cleanupFailure != null) {
            if (!scenario.isFailed()) throw cleanupFailure;
            System.err.println("Cleanup also failed: " + cleanupFailure.getClass().getName());
        }
    }
    private void evidence(Scenario s, String name, Runnable action) {
        try { action.run(); } catch (Exception e) { s.attach(name + " unavailable: " + e.getClass().getSimpleName(), "text/plain", "evidence-warning"); }
    }
    private void captureFailure(Scenario scenario) {
        if (!DriverFactory.exists()) return;
        evidence(scenario, "screenshot", () -> scenario.attach(((TakesScreenshot) DriverFactory.get()).getScreenshotAs(OutputType.BYTES), "image/png", "failure"));
        evidence(scenario, "URL", () -> scenario.attach(listeners.Sanitizer.clean(DriverFactory.get().getCurrentUrl()), "text/plain", "URL"));
        evidence(scenario, "source", () -> scenario.attach(listeners.Sanitizer.clean(DriverFactory.get().getPageSource()), "text/html", "page-source"));
        evidence(scenario, "console", () -> scenario.attach(listeners.Sanitizer.clean(DriverFactory.get().manage().logs().get("browser").getAll().toString()), "text/plain", "console"));
    }
    private void cleanupEvidence(Scenario scenario, Throwable failure) {
        var trace = new java.io.StringWriter();
        failure.printStackTrace(new java.io.PrintWriter(trace));
        evidence(scenario, "cleanup-error", () -> scenario.attach(listeners.Sanitizer.clean(trace.toString()), "text/plain", "cleanup-error"));
    }
}
