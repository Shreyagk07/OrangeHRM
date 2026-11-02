"""Recover specifically named Qa/Synthetic fixtures after an interrupted failed run.
Dry-run by default. Uses real session + CSRF authentication and supported internal APIs.
"""
import argparse
import http.cookiejar
import json
import os
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

class LoginToken(HTMLParser):
    token = None
    def handle_starttag(self, tag, attrs):
        if tag == 'auth-login':
            attributes = dict(attrs)
            if ':token' in attributes:
                self.token = json.loads(attributes[':token'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('employee_ids', nargs='+')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if any(not re.fullmatch(r'Q[0-9a-f]{8}X{0,2}', value) for value in args.employee_ids):
        parser.error('Only explicitly named framework-owned Q-prefixed fixture IDs are accepted')
    env = dict(os.environ)
    file = Path(__file__).resolve().parents[1] / '.env'
    if file.exists():
        for line in file.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                key, value = line.split('=', 1)
                env.setdefault(key, value.strip().strip('"').strip("'"))
    base = env['BASE_URL'].rstrip('/')
    if urllib.parse.urlparse(base).hostname not in {'localhost', '127.0.0.1'}:
        raise ValueError('Cleanup requires the local host application')
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    with opener.open(base + '/auth/login', timeout=60) as response:
        token = LoginToken()
        token.feed(response.read().decode())
    if not token.token:
        raise ValueError('Official login CSRF token was not present in auth-login props')
    login = urllib.parse.urlencode({'username': env['ADMIN_USERNAME'], 'password': env['ADMIN_PASSWORD'], '_token': token.token}).encode()
    with opener.open(urllib.request.Request(base + '/auth/validate', data=login), timeout=60) as response:
        response.read()
    def api(path, method='GET', payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(base + path, data=data, method=method,
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        with opener.open(request, timeout=60) as response:
            if response.status != 200 or 'application/json' not in response.headers.get('Content-Type', ''):
                raise ValueError('Authenticated API JSON response required')
            return json.load(response)
    for employee_id in args.employee_ids:
        query = urllib.parse.urlencode({'employeeId' if len(employee_id) <= 10 else 'nameOrId': employee_id})
        records = api('/api/v2/pim/employees?' + query)['data']
        matches = [row for row in records if row['employeeId'] == employee_id]
        if not matches:
            print(employee_id + ': already absent')
            continue
        if len(matches) != 1 or any(matches[0].get(key, '') != value for key, value in {'firstName':'Qa', 'lastName':'Synthetic', 'middleName':''}.items()):
            raise ValueError('Refusing to remove fixture with unexpected business values: ' + employee_id)
        number = matches[0]['empNumber']
        if not args.execute:
            print(employee_id + ': DRY RUN; would delete owned employee ' + str(number))
            continue
        deleted = api('/api/v2/pim/employees', 'DELETE', {'ids': [number]})
        if number not in deleted['data']:
            raise ValueError('Deletion response did not confirm owned employee')
        if any(row['employeeId'] == employee_id for row in api('/api/v2/pim/employees?' + query)['data']):
            raise ValueError('Owned fixture still found after deletion')
        print(employee_id + ': deleted through application API and verified absent')

if __name__ == '__main__':
    main()
