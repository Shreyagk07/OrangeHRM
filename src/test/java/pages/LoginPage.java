package pages;

import components.Form;
import config.Settings;
import org.openqa.selenium.By;

public final class LoginPage extends Form {
    public void login(String username, String password) {
        open("/auth/login"); type(By.name("username"), username); type(By.name("password"), password); submit();
    }
    public void admin() {
        login(Settings.required("admin.username"), Settings.required("admin.password"));
        awaitUrlContains("/dashboard/");
    }
    public void logout() { open("/auth/logout"); visible(By.name("username")); }
}
