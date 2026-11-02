package data;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import java.io.*;
import java.nio.file.*;
import java.util.*;

public final class ExcelData {
    private ExcelData() {}
    public static Map<String, String> row(String id) throws IOException {
        try (InputStream in = Files.newInputStream(Path.of("src/test/resources/testdata/employees.xlsx")); Workbook wb = new XSSFWorkbook(in)) {
            Sheet sheet = wb.getSheet("Employees");
            if (sheet == null || sheet.getRow(0) == null) throw new IllegalArgumentException("Missing Employees sheet/header");
            DataFormatter format = new DataFormatter(Locale.ROOT);
            Map<String, Integer> headers = new LinkedHashMap<>();
            for (Cell cell : sheet.getRow(0)) {
                String key = format.formatCellValue(cell).trim();
                if (key.isBlank() || headers.put(key, cell.getColumnIndex()) != null) throw new IllegalArgumentException("Blank/duplicate header: " + key);
            }
            if (!headers.keySet().containsAll(List.of("id", "firstName", "middleName", "lastName", "valid"))) throw new IllegalArgumentException("Missing required Excel columns");
            Map<String, String> found = null;
            for (int n = 1; n <= sheet.getLastRowNum(); n++) {
                Row row = sheet.getRow(n); if (row == null) continue;
                if (!format.formatCellValue(row.getCell(headers.get("id"), Row.MissingCellPolicy.RETURN_BLANK_AS_NULL)).equals(id)) continue;
                if (found != null) throw new IllegalArgumentException("Duplicate dataset ID: " + id);
                Map<String, String> result = new LinkedHashMap<>();
                headers.forEach((key, index) -> result.put(key, format.formatCellValue(row.getCell(index, Row.MissingCellPolicy.RETURN_BLANK_AS_NULL))));
                if (!Set.of("true", "false").contains(result.get("valid"))) throw new IllegalArgumentException("valid must be true/false: " + id);
                found = Map.copyOf(result);
            }
            if (found == null) throw new IllegalArgumentException("Unknown Excel dataset: " + id);
            return found;
        }
    }
}
