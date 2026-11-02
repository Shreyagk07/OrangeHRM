package db;

import config.Settings;
import models.Employee;
import java.sql.*;
import java.util.Optional;
import org.testng.Assert;

/** SELECT only; credentials must have no mutation grants. */
public final class EmployeeRepository {
    public Optional<Employee> find(String id) throws SQLException {
        try (Connection c = DriverManager.getConnection(Settings.required("db.url"), Settings.required("db.user"), Settings.required("db.password"))) {
            c.setReadOnly(true);
            try (PreparedStatement s = c.prepareStatement("SELECT emp_firstname, emp_middle_name, emp_lastname, employee_id FROM hs_hr_employee WHERE employee_id = ?")) {
                s.setString(1, id); s.setQueryTimeout(10);
                try (ResultSet r = s.executeQuery()) {
                    if (!r.next()) return Optional.empty();
                    Employee result = new Employee(r.getString(1), r.getString(2), r.getString(3), r.getString(4));
                    Assert.assertFalse(r.next(), "Employee ID must identify exactly one record: " + id);
                    return Optional.of(result);
                }
            }
        }
    }
    public void assertEmployee(Employee expected) throws SQLException {
        Assert.assertEquals(find(expected.employeeId()).orElseThrow(() -> new AssertionError("Employee not persisted: " + expected.employeeId())), expected, "UI/API values differ from MySQL");
    }
    public void assertAbsent(String id) throws SQLException { Assert.assertTrue(find(id).isEmpty(), "Employee still persisted: " + id); }
}
