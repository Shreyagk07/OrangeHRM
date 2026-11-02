package listeners;

import config.Settings;
import drivers.DriverFactory;

/** Defense in depth for local synthetic evidence; never attach request headers. */
public final class Sanitizer {
    private Sanitizer() {}
    public static String clean(String text) {
        String result = text;
        for (String key : new String[]{"admin.password", "db.password", "mysql.password", "mysql.root.password"}) {
            String secret = Settings.get(key);
            if (!secret.isBlank()) result = result.replace(secret, "[REDACTED]");
        }
        if (DriverFactory.exists()) {
            for (var cookie : DriverFactory.get().manage().getCookies()) {
                if (!cookie.getValue().isEmpty()) result = result.replace(cookie.getValue(), "[REDACTED]");
            }
        }
        return result.replaceAll("(?is)<input[^>]*(?:type=[\"']hidden[\"']|type=[\"']password[\"'])[^>]*>", "[REDACTED INPUT]")
            .replaceAll("(?i)([\\w:.-]*token[\\w:.-]*\\s*=\\s*[\"'])[^\"']*([\"'])", "$1[REDACTED]$2")
            .replaceAll("(?i)((?:password|token|resetCode)\\s*[=:]\\s*)[^&\\s<]+", "$1[REDACTED]");
    }
}
