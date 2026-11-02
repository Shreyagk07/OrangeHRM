"""Configure only the isolated lab's local SMTP sink; do not send a test email."""
from application_client import LocalApplication

if __name__ == '__main__':
    app = LocalApplication()
    endpoint = '/api/v2/admin/email-configuration'
    current = app.api(endpoint)['data']
    if current.get('sentAs') and current.get('smtpHost') != 'mailpit':
        raise SystemExit('Existing non-lab mail configuration preserved; use an isolated lab.')
    expected = {'mailType':'smtp', 'sentAs':'qa@example.invalid', 'smtpHost':'mailpit',
        'smtpPort':1025, 'smtpUsername':'', 'smtpPassword':'', 'smtpAuthType':'none', 'smtpSecurityType':'none'}
    app.api(endpoint, 'PUT', expected)
    saved = app.api(endpoint)['data']
    for key, value in expected.items():
        if key in {'smtpPassword', 'smtpUsername'}:
            continue  # Password is deliberately not returned; no auth is used by the local sink.
        if saved.get(key) != value:
            raise AssertionError('Email configuration was not persisted: ' + key)
    print('Verified local mail configuration: mailpit:1025; no test email sent.')
