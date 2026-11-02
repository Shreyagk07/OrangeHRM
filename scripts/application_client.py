"""Local setup/recovery client using OrangeHRM's real browser-form session flow."""
import http.cookiejar
import json
import os
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

class _LoginToken(HTMLParser):
    token = None
    def handle_starttag(self, tag, attrs):
        if tag == 'auth-login' and ':token' in dict(attrs):
            self.token = json.loads(dict(attrs)[':token'])

class LocalApplication:
    def __init__(self):
        env = dict(os.environ)
        file = Path(__file__).resolve().parents[1] / '.env'
        if file.exists():
            for line in file.read_text().splitlines():
                if line.strip() and not line.lstrip().startswith('#'):
                    key, value = line.split('=', 1)
                    env.setdefault(key, value.strip().strip('"').strip("'"))
        self.base = env['BASE_URL'].rstrip('/')
        if urllib.parse.urlparse(self.base).hostname not in {'localhost', '127.0.0.1'}:
            raise ValueError('Setup requires the local host application')
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with self.opener.open(self.base + '/auth/login', timeout=60) as response:
            parser = _LoginToken()
            parser.feed(response.read().decode())
        if not parser.token:
            raise ValueError('Official login CSRF token not present')
        data = urllib.parse.urlencode({'username':env['ADMIN_USERNAME'], 'password':env['ADMIN_PASSWORD'], '_token':parser.token}).encode()
        with self.opener.open(urllib.request.Request(self.base + '/auth/validate', data=data), timeout=60) as response:
            response.read()

    def api(self, path, method='GET', payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base + path, data=data, method=method,
            headers={'Accept':'application/json', 'Content-Type':'application/json'})
        with self.opener.open(request, timeout=60) as response:
            if response.status != 200 or 'application/json' not in response.headers.get('Content-Type', ''):
                raise ValueError('Authenticated API JSON response required')
            return json.load(response)
