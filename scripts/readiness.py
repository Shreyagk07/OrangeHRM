"""Bounded infrastructure readiness. Tests authenticate separately and verify JDBC grants."""
import json, os, time, urllib.request, urllib.error
from application_client import LocalApplication

def await_url(url, check, seconds=180):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                body = response.read().decode()
                if check(body):
                    return
        except (OSError, ValueError) as exc:
            last = type(exc).__name__
        time.sleep(2)  # Infrastructure polling, never browser synchronization.
    raise SystemExit(f'Readiness failed: {url}; last error type={last}')

if __name__ == '__main__':
    # Host reachability differs from browser reachability on the Compose network.
    await_url('http://localhost:8080/web/index.php/auth/login', lambda body: 'auth-login' in body)
    await_url('http://localhost:4444/status', lambda body: json.loads(body)['value']['ready'] and len(json.loads(body)['value'].get('nodes', [])) >= 2)
    await_url('http://localhost:8025/', lambda body: 'Mailpit' in body)
    mail = LocalApplication().api('/api/v2/admin/email-configuration')['data']
    if mail.get('smtpHost') != 'mailpit' or mail.get('smtpPort') != 1025:
        raise SystemExit('Local SMTP prerequisite missing; run python scripts/configure-mail.py')
    print('Installed application, two Grid nodes, and configured local Mailpit are ready.')
