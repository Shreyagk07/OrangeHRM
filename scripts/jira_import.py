"""Optional Jira Cloud import. Dry-run by default; no credentials needed to preview."""
import argparse, base64, csv, json, os, re, urllib.request
from pathlib import Path

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('csv',nargs='?',default='docs/defects.csv')
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    rows=list(csv.DictReader(Path(args.csv).open(encoding='utf-8',newline='')))
    if not args.execute:
        print(json.dumps({'mode':'DRY RUN; prepared for Jira import','count':len(rows),'summaries':[r['Summary'] for r in rows]},indent=2)); return
    project=os.environ['JIRA_PROJECT']
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*',project): raise ValueError('Invalid project key')
    site=os.environ['JIRA_URL'].rstrip('/')
    if not re.fullmatch(r'https://[a-zA-Z0-9-]+\.atlassian\.net',site): raise ValueError('Expected HTTPS Jira Cloud site')
    auth=base64.b64encode((os.environ['JIRA_EMAIL']+':'+os.environ['JIRA_TOKEN']).encode()).decode()
    def request(path,payload):
        req=urllib.request.Request(site+path,data=json.dumps(payload).encode(),headers={'Authorization':'Basic '+auth,'Content-Type':'application/json','Accept':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=30) as response: return json.load(response)
    for row in rows:
        external=row['External ID']
        if not re.fullmatch(r'DEF-\d{3}',external): raise ValueError('External ID must be DEF-nnn')
        label='orangehrm-qa-'+external.lower()
        found=request('/rest/api/3/search/jql',{'jql':f'project = {project} AND labels = "{label}"','fields':['key'],'maxResults':1})
        if found.get('issues'): print(external+': already exists; skipped'); continue
        description='\n'.join(f'{k}: {v}' for k,v in row.items() if k!='Summary')
        adf={'type':'doc','version':1,'content':[{'type':'paragraph','content':[{'type':'text','text':description}]}]}
        created=request('/rest/api/3/issue',{'fields':{'project':{'key':project},'issuetype':{'name':'Bug'},'summary':row['Summary'],'description':adf,'labels':[label]}})
        print(external+': '+created['key'])
if __name__=='__main__': main()
