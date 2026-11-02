package tests;
import data.ExcelData;
import org.testng.Assert;
import org.testng.annotations.Test;

public final class ExcelTest {
    @Test public void workbookProvidesBoundaryAndBlankValues() throws Exception {
        Assert.assertEquals(ExcelData.row("first-max").get("firstName").length(), 30);
        Assert.assertEquals(ExcelData.row("first-over").get("firstName").length(), 31);
        Assert.assertEquals(ExcelData.row("first-empty").get("firstName"), "");
        Assert.assertThrows(IllegalArgumentException.class, () -> ExcelData.row("missing"));
    }
}
