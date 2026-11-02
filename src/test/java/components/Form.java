package components;

import config.Settings;
import drivers.DriverFactory;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.*;
import java.time.Duration;

public class Form {
    protected WebDriver d() { return DriverFactory.get(); }
    public WebDriverWait waitFor() { return new WebDriverWait(d(), Duration.ofSeconds(Settings.timeout())); }
    public void awaitUrlContains(String path) {
        new WebDriverWait(d(), Duration.ofSeconds(Settings.pageTimeout()))
            .until(ExpectedConditions.urlContains(path));
    }
    public WebElement visible(By by) { return waitFor().until(ExpectedConditions.visibilityOfElementLocated(by)); }
    public void open(String path) {
        d().get(Settings.browserBase() + path);
        new WebDriverWait(d(), Duration.ofSeconds(Settings.pageTimeout()))
            .withMessage("OrangeHRM Vue application did not finish mounting at " + path)
            .until(driver -> Boolean.TRUE.equals(((JavascriptExecutor) driver).executeScript(
                "const app = document.getElementById('app'); return !!app && app.hasAttribute('data-v-app');")));
    }
    public void type(By by, String value) {
        WebElement input = visible(by);
        input.sendKeys(Keys.chord(Keys.CONTROL, "a")); input.sendKeys(Keys.BACK_SPACE);
        if (!value.isEmpty()) input.sendKeys(value);
    }
    public By label(String label) {
        return By.xpath("//div[contains(@class,'oxd-input-group')][.//label[normalize-space()='" + label + "']]//input");
    }
    public void field(String label, String value) { type(label(label), value); }
    public void button(String text) {
        waitFor().until(ExpectedConditions.elementToBeClickable(By.xpath("//button[normalize-space()='" + text + "']"))).click();
    }
    public void submit() { waitFor().until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))).click(); }
    public void text(String expected) { visible(By.xpath("//*[normalize-space()='" + expected + "']")); }
    public void error(String expected) { visible(By.xpath("//*[contains(@class,'oxd-input-field-error-message') and normalize-space()='" + expected + "']")); }
    public void idle() { waitFor().until(ExpectedConditions.invisibilityOfElementLocated(By.cssSelector(".oxd-form-loader"))); }
}
