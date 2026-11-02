package config;

import java.io.*;
import java.net.URI;
import java.util.*;

/** System properties > environment > committed defaults. Secrets have no defaults. */
public final class Settings {
    private static final Properties DEFAULTS = new Properties();
    static {
        try (var in = Settings.class.getResourceAsStream("/config/default.properties")) {
            if (in == null) throw new IllegalStateException("Missing default.properties");
            DEFAULTS.load(in);
        } catch (IOException e) { throw new UncheckedIOException(e); }
    }
    private Settings() {}
    public static String get(String key) {
        return System.getProperty(key, System.getenv().getOrDefault(key.toUpperCase(Locale.ROOT).replace('.', '_'), DEFAULTS.getProperty(key, "")));
    }
    public static String required(String key) {
        String value = get(key);
        if (value.isBlank()) throw new IllegalStateException("Set " + key.toUpperCase(Locale.ROOT).replace('.', '_'));
        return value;
    }
    public static String base() {
        String value = required("base.url").replaceAll("/$", "");
        URI uri = URI.create(value);
        String host = uri.getHost();
        if (!(Set.of("localhost", "127.0.0.1", "app", "host.docker.internal").contains(host)))
            throw new IllegalArgumentException("Mutation suites require the local application; disallowed host: " + host);
        return value;
    }
    public static int timeout() { return Integer.parseInt(get("timeout")); }
    public static int pageTimeout() { return Integer.parseInt(get("page.timeout")); }
    public static String browserBase() {
        String value = get("browser.base.url");
        if (value.isBlank()) return base();
        if (!Set.of("localhost", "127.0.0.1", "app", "host.docker.internal").contains(URI.create(value).getHost())) throw new IllegalArgumentException("Browser must target local application");
        return value.replaceAll("/$", "");
    }
}
