package drivers;

import config.Settings;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.*;
import org.openqa.selenium.firefox.*;
import org.openqa.selenium.remote.RemoteWebDriver;
import java.net.*;

public final class DriverFactory {
    private static final ThreadLocal<WebDriver> DRIVER = new ThreadLocal<>();
    private DriverFactory() {}
    public static WebDriver get() {
        WebDriver driver = DRIVER.get();
        if (driver == null) throw new IllegalStateException("No driver on this scenario thread");
        return driver;
    }
    public static void start() throws MalformedURLException {
        if (DRIVER.get() != null) throw new IllegalStateException("Driver already exists");
        String browser = Settings.get("browser");
        boolean headless = Boolean.parseBoolean(Settings.get("headless"));
        String grid = Settings.get("grid.url");
        WebDriver driver;
        if (browser.equals("chrome")) {
            ChromeOptions options = new ChromeOptions();
            if (headless) options.addArguments("--headless=new");
            options.addArguments("--window-size=1440,1000");
            driver = grid.isBlank() ? new ChromeDriver(options) : new RemoteWebDriver(URI.create(grid).toURL(), options);
        } else if (browser.equals("firefox")) {
            FirefoxOptions options = new FirefoxOptions();
            if (headless) options.addArguments("-headless");
            driver = grid.isBlank() ? new FirefoxDriver(options) : new RemoteWebDriver(URI.create(grid).toURL(), options);
        } else throw new IllegalArgumentException("browser must be chrome or firefox");
        DRIVER.set(driver);
        driver.manage().timeouts().implicitlyWait(java.time.Duration.ZERO);
        driver.manage().timeouts().pageLoadTimeout(java.time.Duration.ofSeconds(Settings.pageTimeout()));
    }
    public static boolean exists() { return DRIVER.get() != null; }
    public static void stop() {
        try { if (DRIVER.get() != null) DRIVER.get().quit(); }
        finally { DRIVER.remove(); }
    }
}
