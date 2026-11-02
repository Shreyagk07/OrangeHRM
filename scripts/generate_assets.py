"""Deterministic source for the coverage catalogue, manual cases, RTM and XLSX.
Run with Python 3; no third-party packages. Never changes execution statuses to Passed.
"""
from pathlib import Path
import csv, json, zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')

cases = []
def case(title, module, steps, expected, technique='Equivalence partitioning', data='Synthetic isolated data; configured local admin', db='Non-database behavior', requirement=None):
    cases.append(dict(title=title,module=module,steps=steps,expected=expected,technique=technique,data=data,db=db,requirement=requirement or {'Auth':'REQ-01','PIM':'REQ-02','Admin':'REQ-05','Leave':'REQ-06'}[module]))

case('Administrator can authenticate','Auth',['When I log in with "ADMIN" and "ADMIN"','Then the dashboard is shown'],'Authenticated administrator reaches Dashboard')
case('Incorrect password is rejected','Auth',['When I log in with "ADMIN" and "WrongSynthetic123!"','Then invalid credentials are reported'],'Invalid credentials; no authenticated session',data='Valid username / invalid password equivalence class')
case('Unknown username is rejected','Auth',['When I log in with "SyntheticMissingUser" and "WrongSynthetic123!"','Then invalid credentials are reported'],'Invalid credentials; unknown account does not authenticate',data='Unknown username / arbitrary password invalid class')
case('Both login fields are mandatory','Auth',['Given I open the login page','When I submit the form','Then 2 required errors are shown'],'Two Required messages; login blocked',data='Both values empty: invalid class')
case('Username is mandatory','Auth',['When I log in with "" and "WrongSynthetic123!"','Then 1 required errors are shown'],'Required on username; no session',data='Empty username / populated password')
case('Password is mandatory','Auth',['When I log in with "ADMIN" and ""','Then 1 required errors are shown'],'Required on password; no session',data='Populated username / empty password')
case('Login password control masks input','Auth',['Given I open the login page','Then the password is masked'],'Password input has type=password',technique='Checklist',data='Inspect password input type')
case('Anonymous users cannot open employee list','Auth',['When I visit "/pim/viewEmployeeList"','Then login is required'],'Redirect to Login; employee list unavailable',requirement='REQ-07',data='Anonymous session: forbidden equivalence class')
case('Logout revokes protected-page access','Auth',['Given I am the local administrator','When I log out','And I visit "/pim/viewEmployeeList"','Then login is required'],'Protected list requires login after logout',requirement='REQ-07')
case('Password reset can be cancelled','Auth',['When I cancel password reset','Then login is required'],'Cancel returns to Login',technique='State transition')

datasets = {
 'minimal': ('Qa','','Synthetic',True), 'middle': ('Qa','Middle','Synthetic',True),
 'first-min': ('A','','Synthetic',True), 'first-max': ('A'*30,'','Synthetic',True),
 'first-over': ('A'*31,'','Synthetic',False), 'first-empty': ('','','Synthetic',False),
 'last-min': ('Qa','','Z',True), 'last-max': ('Qa','','Z'*30,True),
 'last-over': ('Qa','','Z'*31,False), 'last-empty': ('Qa','','',False),
 'middle-max': ('Qa','M'*30,'Synthetic',True), 'middle-over': ('Qa','M'*31,'Synthetic',False)
}
for key, (first,middle,last,valid) in datasets.items():
    field = key.split('-')[0]
    title = {'minimal':'Create an employee without optional middle name','middle':'Create an employee with all name parts'}.get(key, f'{field.title()} name {key.split("-")[-1]} boundary')
    steps = ['Given I am the local administrator','And I open Add Employee',f'When I fill employee dataset "{key}"']
    if valid:
        steps += ['And I save the new employee','Then the employee is persisted exactly']
    else:
        error = 'Required' if key.endswith('empty') else 'Should not exceed 30 characters'
        steps += ['And I submit the form',f'Then validation reports "{error}"','And the employee was not created']
    case(title,'PIM',steps,'Names saved exactly in UI/MySQL' if valid else f'{error}; no employee saved',
         'Boundary value analysis' if '-' in key else 'Equivalence partitioning',
         f'Excel={key}; first length={len(first)}; middle length={len(middle)}; last length={len(last)}; '+('valid class' if valid else 'invalid class'),
         'Persistence-changing' if valid else 'Non-database behavior')

for length,valid in [(10,True),(11,False)]:
    steps=['Given I am the local administrator','And I open Add Employee','When I fill employee dataset "minimal"',f'And I set employee ID length to {length}']
    steps += ['And I save the new employee','Then the employee is persisted exactly'] if valid else ['And I submit the form','Then validation reports "Should not exceed 10 characters"','And the employee was not created']
    case(f'Employee ID length {length} is '+('accepted' if valid else 'rejected'),'PIM',steps,'ID accepted and persisted' if valid else 'Length error; no record','Boundary value analysis',f'Unique ID length={length}; '+('valid maximum' if valid else 'maximum plus one invalid'),'Persistence-changing' if valid else 'Non-database behavior')
case('Duplicate employee ID is rejected','PIM',['Given I am the local administrator','And a controlled employee exists','When I attempt to reuse its employee ID','Then validation reports "Employee Id already exists"','And only the original employee exists'],'Duplicate validation; original unchanged',data='Existing owned ID: invalid uniqueness class',db='Read-only')
case('Cancel does not create an employee','PIM',['Given I am the local administrator','And I open Add Employee','When I fill employee dataset "minimal"','And I cancel Add Employee','Then the cancelled employee does not exist'],'List displayed; no MySQL row',technique='State transition')
case('Exact employee ID search isolates its row','PIM',['Given I am the local administrator','And a controlled employee exists','When I search for its employee ID','Then only its employee row is shown'],'Exactly one matching row; consistent with MySQL',db='Read-only',requirement='REQ-03')
case('Unknown employee ID returns no results','PIM',['Given I am the local administrator','When I search for a nonexistent employee','Then no records are shown'],'No Records Found',data='Unique absent ID: no-match equivalence class',db='Read-only',requirement='REQ-03')
case('Reset clears employee search','PIM',['Given I am the local administrator','And a controlled employee exists','When I search for its employee ID','And I reset employee search','Then employee search is cleared'],'Employee ID search input cleared',db='Read-only',requirement='REQ-03')
for field,value in [('firstName','UpdatedFirst'),('lastName','UpdatedLast'),('middleName','UpdatedMiddle')]:
    case(f'Update employee {field} and reload','PIM',['Given I am the local administrator','And a controlled employee exists',f'When I change "{field}" to "{value}"','Then the employee is persisted exactly'],'Reloaded UI and MySQL contain updated value; other names unchanged',db='Persistence-changing',requirement='REQ-04')
case('Delete employee through UI removes persistence','PIM',['Given I am the local administrator','And a controlled employee exists','When I delete the controlled employee through the UI','Then the employee is absent from MySQL and search'],'No row in MySQL or search',db='Persistence-changing',requirement='REQ-04')
case('Search administrator by exact username','Admin',['Given I am the local administrator','When I search for the administrator account','Then the administrator account is shown'],'Matching admin account and Admin role visible',db='Read-only')
case('New user form enforces mandatory fields','Admin',['Given I am the local administrator','When I visit "/admin/saveSystemUser"','And I submit the form','Then 5 required errors are shown','And validation reports "Passwords do not match"'],'Role, employee, status, username and password required; confirmation mismatch',data='All required values empty: invalid equivalence class')
for length,error in [(4,'Should be at least 5 characters'),(41,'Should not exceed 40 characters')]:
    case(f'New username length {length} rejected','Admin',['Given I am the local administrator','When I visit "/admin/saveSystemUser"',f'And I enter an administrator username of length {length}',f'Then validation reports "{error}"'],f'{error}; user not saved','Boundary value analysis',f'Username length {length}; outside valid interval [5,40]')
case('Cancel new user returns to user management','Admin',['Given I am the local administrator','When I visit "/admin/saveSystemUser"','And I cancel user creation','Then the system user list is shown'],'System Users list displayed',technique='State transition')
case('Leave search rejects malformed start date','Leave',['Given I am the local administrator','When I visit "/leave/viewLeaveList"','And I enter an invalid leave start date','Then a date validation error is shown'],'Date validation prevents invalid search',data='not-a-date: invalid date format class')
case('Leave search Reset clears employee filter','Leave',['Given I am the local administrator','When I visit "/leave/viewLeaveList"','And I reset leave search','Then leave employee search is cleared'],'Employee filter is empty after Reset',db='Read-only')
assert len(cases)==40, len(cases)

feature=['Feature: Local OrangeHRM 5.7 regression','']
catalog=[]
for n,c in enumerate(cases,1):
    uid=f'UI-{n:03}'
    tags=f'@{uid} @regression @{c["module"].lower()}'
    if n in (1,8,11,30,33): tags+=' @smoke'
    if c['db']=='Persistence-changing': tags+=' @db'
    feature += ['  '+tags,f'  Scenario: {uid} {c["title"]}']+['    '+s for s in c['steps']]+['']
    catalog.append({'UI ID':uid,'Manual ID':f'TC-{n:03}','Requirement':c['requirement'],'Title':c['title'],'Module':c['module'],'Database classification':c['db'],'JDBC rationale':'Compare owned hs_hr_employee names/ID after mutation, then assert absent after cleanup' if c['db']=='Persistence-changing' else ('Search/lookup; fixtures checked where relevant' if c['db']=='Read-only' else 'Client validation/navigation/authentication; no employee mutation; absence checked for invalid adds'),'Status':'Not Run'})
write('src/test/resources/features/regression.feature','\n'.join(feature))

# Extra manual cases deliberately cover flows beyond the current automated scope.
extras=[
 ('Admin','Create enabled ESS account','Owned employee exists with no login; Admin session','Unique 5-character username; strong password; ESS; Enabled','1. Open Admin > Add user. 2. Select ESS, owned employee and Enabled. 3. Enter unique username and matching strong passwords. 4. Save. 5. Log in as new account. 6. Delete user and employee using Admin.','Account appears; ESS login works; Admin management unavailable','Boundary value analysis','REQ-05'),
 ('Admin','Accept 40-character username','Owned employee without login; Admin session','Unique 40-character username; ESS; Enabled; strong matching passwords','1. Open Add user. 2. Populate all required fields using the dataset. 3. Save. 4. Search exact username. 5. Delete owned account and employee.','40-character username saved and retrieved exactly','Boundary value analysis','REQ-05'),
 ('Admin','Disabled account cannot authenticate','Owned disabled ESS user and employee; Admin session','Disabled ESS credentials; valid password','1. Log out. 2. Attempt disabled account login. 3. Observe result. 4. Clean up using Admin.','Login rejected; no employee data disclosed','Equivalence partitioning','REQ-07'),
 ('Admin','Reject mismatched password confirmation','Admin session; owned employee','Password=LocalQaChange123!; confirmation=DifferentQa123!','1. Open Add user. 2. Complete all fields. 3. Enter different confirmation. 4. Save. 5. Correct confirmation and inspect error clearance. 6. Cancel; delete fixture.','Passwords do not match; account not created before correction','Equivalence partitioning','REQ-05'),
 ('PIM','Optional middle name accepts length zero','Admin session','First=A; middle empty; last=Z; unique ID','1. Open Add Employee. 2. Enter data. 3. Save. 4. Reload Personal Details. 5. Verify empty middle name. 6. Delete employee.','Empty middle name remains empty after reload','Boundary value analysis','REQ-02'),
 ('Leave','Apply one full workday of entitled leave','Owned ESS employee with work week, leave period and 2 days entitlement; no overlaps','Future working date; full day; configured leave type','1. Log in as owned ESS. 2. Open Leave > Apply. 3. Select entitled type and same future working date for From/To. 4. Apply. 5. Inspect My Leave. 6. Cancel request and remove owned prerequisites as Admin.','Pending request for one day; balance reflects request under configured workflow','Equivalence partitioning','REQ-06'),
 ('Leave','Reject reversed leave date interval','Owned ESS with entitlement and work week','From=future workday+2; To=future workday','1. Open Apply Leave. 2. Select entitled type. 3. Enter reversed dates. 4. Apply. 5. Inspect validation and My Leave. 6. Remove owned prerequisites.','End-date validation; no request created','Equivalence partitioning','REQ-06'),
 ('Leave','Reject missing leave type','Owned ESS with at least one entitled type','Leave type unselected; valid future working dates','1. Open Apply. 2. Enter valid dates, leave type blank. 3. Apply. 4. Inspect Required. 5. Remove owned prerequisites.','Required type error; no request created','Equivalence partitioning','REQ-06'),
 ('Leave','Cancel owned pending request','Owned ESS with independently created pending request','One synthetic pending leave request','1. Log in as ESS. 2. Open My Leave. 3. Locate owned request by dates/type. 4. Cancel. 5. Refresh and inspect status/balance. 6. Remove owned prerequisites.','Status becomes Cancelled; balance restored according to configuration','State transition','REQ-06'),
 ('Leave','ESS cannot approve another employee request','Two owned ESS employees; one owned pending request','ESS account without supervisor or admin role','1. Log in as unrelated ESS. 2. Inspect available Leave actions. 3. Attempt protected admin leave-list route. 4. Confirm no approval occurs. 5. Clean up as Admin.','No authorization to approve unrelated employee leave; request remains pending','Equivalence partitioning','REQ-07')
]

def manual_step(step):
    action=step.split(' ',1)[1]
    plain={
      'I am the local administrator':'Open /web/index.php/auth/login, enter configured ADMIN_USERNAME and ADMIN_PASSWORD, click Login, and wait for Dashboard.',
      'I open the login page':'Open /web/index.php/auth/login in a fresh browser.',
      'the dashboard is shown':'Confirm the Dashboard heading and authenticated dashboard URL.',
      'invalid credentials are reported':'Confirm Invalid credentials and that the Login page remains displayed.',
      'I submit the form':'Click the form submit button and wait for validation or navigation.',
      'the password is masked':'Inspect the password field: characters must be masked and HTML type must be password.',
      'login is required':'Confirm redirect to Login; the protected employee content must be unavailable.',
      'I log out':'Use Logout; confirm the Login form appears.',
      'I cancel password reset':'Open /auth/requestPasswordResetCode relative to /web/index.php and click Cancel.',
      'I open Add Employee':'Open PIM > Add Employee; replace Employee Id with a new unique Q-prefixed ID of 9 characters and record it.',
      'I save the new employee':'Click Save, wait for Personal Details, and record empNumber from the URL.',
      'the employee is persisted exactly':'Reload Personal Details; compare all three names and employee ID with input. Use the read-only SELECT documented in architecture.md to confirm exact stored values.',
      'the employee was not created':'Confirm Add Employee remains open and search the unique ID in a separate authenticated session; no row must exist. Verify absence with the read-only SELECT.',
      'a controlled employee exists':'Independently create Qa / empty middle / Synthetic through PIM Add Employee with a new unique Q-prefixed 9-character ID; record ID and empNumber. Use only this owned employee.',
      'I attempt to reuse its employee ID':'Open Add Employee again, enter Duplicate / empty middle / Synthetic and the owned existing ID, then click Save.',
      'only the original employee exists':'Search the owned ID: exactly one original employee must exist; compare original names in MySQL.',
      'I cancel Add Employee':'Click Cancel and confirm return to Employee List.',
      'the cancelled employee does not exist':'Search the recorded unique ID; no employee should exist. Confirm MySQL absence.',
      'I search for its employee ID':'Open PIM > Employee List, enter the owned ID in Employee Id and click Search.',
      'only its employee row is shown':'Confirm exactly one row with the owned ID and names; compare with the read-only database record.',
      'I search for a nonexistent employee':'Search Employee List using a newly generated Q-prefixed 9-character ID that has never been created.',
      'no records are shown':'Confirm No Records Found and no employee rows.',
      'I reset employee search':'Click Reset on Employee List after the filter search.',
      'employee search is cleared':'Confirm Employee Id input is empty.',
      'I delete the controlled employee through the UI':'Search the owned ID, click the row trash icon, and confirm Yes, Delete.',
      'the employee is absent from MySQL and search':'Search the owned ID again and confirm No Records Found; run the read-only SELECT and confirm zero rows.',
      'I search for the administrator account':'Open Admin > User Management > Users, enter ADMIN_USERNAME in Username and click Search.',
      'the administrator account is shown':'Confirm matching username and Admin role in the results.',
      'I cancel user creation':'Click Cancel on Add User.',
      'the system user list is shown':'Confirm System Users heading and /admin/viewSystemUsers URL.',
      'I enter an invalid leave start date':'On Leave List replace From Date with not-a-date and click Search.',
      'a date validation error is shown':'Confirm an inline error on From Date and that no invalid search is accepted.',
      'I reset leave search':'Enter SyntheticNoMatch in Employee Name and click Reset.',
      'leave employee search is cleared':'Confirm Employee Name filter is empty.'
    }
    if action in plain: return plain[action]
    if action.startswith('I fill employee dataset '):
        key=action.split('"')[1]; first,middle,last,_=datasets[key]
        return f'Enter First Name="{first}", Middle Name="{middle}", Last Name="{last}" (Excel row {key}).'
    if action.startswith('I log in with '):
        values=action.split('"'); return f'Enter Username="{values[1]}" and Password="{values[3]}" on Login, substituting ADMIN with the configured credential, then click Login.'
    if action.startswith('I visit '): return 'Navigate to '+action.split('"')[1]+' relative to /web/index.php and wait for the screen.'
    if action.startswith('I change '):
        values=action.split('"'); return f'Open the owned employee Personal Details, replace {values[1]} with {values[3]}, click the first Save button, wait for success and reload.'
    if action.startswith('validation reports '): return 'Confirm inline message '+action.split('"')[1]+'.'
    if 'required errors are shown' in action: return 'Confirm exactly '+action.split()[0]+' inline Required messages.'
    if action.startswith('I set employee ID length to '): return 'Replace Employee Id with a unique ID of exactly '+action.split()[-1]+' characters (record the full ID).'
    if action.startswith('I enter an administrator username of length '): return 'Enter '+'Q'*int(action.split()[-1])+' in Username and click Save; other missing fields may also report errors.'
    raise ValueError('Missing manual instruction: '+action)

manual=[]
for n,c in enumerate(cases,1):
    manual.append({'Test case ID':f'TC-{n:03}','Requirement ID':c['requirement'],'Module':c['module'],'Title':c['title'],'Preconditions':'Initialized local 5.7 English instance; configured Admin; MySQL SELECT reader/client. Fresh browser; own synthetic fixtures only. ADMIN denotes configured credentials, never public-demo values.','Test data':c['data'],'Numbered steps':' '.join(f'{i}. {manual_step(s)}' for i,s in enumerate(c['steps'],1))+f' {len(c["steps"])+1}. Delete any owned employee/user through Admin/PIM; confirm no owned records remain. Do not delete the installation administrator.','Expected result':c['expected'],'Priority':'P1' if n in (1,8,11,30,33) else 'P2','Test type':'Functional / '+('negative' if 'invalid class' in c['data'] or any(k in c['title'].lower() for k in ['reject','mandatory','cannot','incorrect','unknown']) else 'positive'),'Design technique':c['technique'],'Actual result':'','Execution status':'Not Run','Linked defect IDs':''})
manual[9]['Preconditions'] += ' Local Mailpit SMTP baseline configured through scripts/configure-mail.py.'
for n,(module,title,pre,data,steps,expected,tech,req) in enumerate(extras,41):
    manual.append({'Test case ID':f'TC-{n:03}','Requirement ID':req,'Module':module,'Title':title,'Preconditions':pre+'; local 5.7 English instance only','Test data':data,'Numbered steps':steps,'Expected result':expected,'Priority':'P2','Test type':'Functional','Design technique':tech,'Actual result':'','Execution status':'Not Run','Linked defect IDs':''})
assert len(manual)==50

def table(rows):
    headers=list(rows[0]); lines=['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
    return '\n'.join(lines+['| '+' | '.join(str(r[h]).replace('|','/').replace('\n','<br>') for h in headers)+' |' for r in rows])+'\n'
def csv_md(name,rows):
    write(f'docs/{name}.md',table(rows))
    path=ROOT/f'docs/{name}.csv'
    with path.open('w',newline='',encoding='utf-8') as file:
        out=csv.DictWriter(file,fieldnames=list(rows[0])); out.writeheader(); out.writerows(rows)
csv_md('manual-cases',manual)
csv_md('ui-coverage',catalog)
rtm=[{'Requirement ID':c['Requirement ID'],'Manual case':c['Test case ID'],'UI scenario':f'UI-{n:03}' if n<=40 else 'Manual only','Execution status':'Not Run','Evidence':'Pending live execution','Defect IDs':''} for n,c in enumerate(manual,1)]
csv_md('rtm',rtm)

# Minimal standards-compliant XLSX: inline strings preserve blank and boundary cells.
rows=[['id','firstName','middleName','lastName','valid']]+[[key,a,b,c,str(ok).lower()] for key,(a,b,c,ok) in datasets.items()]
sheet='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
for i,row in enumerate(rows,1):
    sheet+=f'<row r="{i}">'+''.join(f'<c r="{chr(65+j)}{i}" t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>' for j,value in enumerate(row))+'</row>'
sheet+='</sheetData></worksheet>'
xlsx=ROOT/'src/test/resources/testdata/employees.xlsx'; xlsx.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(xlsx,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    z.writestr('_rels/.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Employees" sheetId="1" r:id="rId1"/></sheets></workbook>')
    z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
    z.writestr('xl/worksheets/sheet1.xml',sheet)
print('Generated exactly 40 UI scenarios, 50 manual cases, RTM and 12 XLSX datasets.')
