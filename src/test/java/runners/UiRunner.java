package runners;

import io.cucumber.testng.*;
import org.testng.annotations.DataProvider;

@CucumberOptions(features="src/test/resources/features", glue={"steps", "hooks"},
    plugin={"pretty", "json:target/cucumber.json", "io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm"})
public final class UiRunner extends AbstractTestNGCucumberTests {
    @Override @DataProvider(parallel=true)
    public Object[][] scenarios() { return super.scenarios(); }
}
