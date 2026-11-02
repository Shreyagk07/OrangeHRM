package models;

import api.EmployeeApi;
import java.util.*;

/** PicoContainer creates one instance per scenario, shared only with its hooks/steps. */
public final class ScenarioContext {
    public final String id = "Q" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
    public String employeeId = id;
    public Employee expected = new Employee("Qa", "", "Synthetic", id);
    public Integer number;
    public EmployeeApi api;
    public boolean deleted;
}
