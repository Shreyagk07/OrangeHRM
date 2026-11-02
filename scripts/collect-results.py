"""Assemble a report from immutable live-run evidence, preserving browser identity.
Historical failures are explicitly labeled separate entries, never relabeled as passes.
"""
import argparse
import collections
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='append', default=[], metavar='RUN_NAME=BROWSER')
    parser.add_argument('--history', action='append', default=[], metavar='RUN_NAME=BROWSER')
    parser.add_argument('--output', required=True, metavar='NEW_RUN_NAME')
    args = parser.parse_args()
    if not args.run:
        parser.error('Provide at least one final --run')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.output):
        parser.error('Output must be a simple new run name')
    destination = ROOT / 'target/runs' / args.output / 'allure-results'
    if destination.exists() and any(destination.iterdir()):
        parser.error('Output already contains evidence; choose a new output name')
    destination.mkdir(parents=True, exist_ok=True)
    summary = []
    identities = set()
    for historical, descriptors in [(False, args.run), (True, args.history)]:
        for descriptor in descriptors:
            parts = descriptor.split('=')
            if len(parts) != 2 or not re.fullmatch(r'[A-Za-z0-9_-]+', parts[0]) or parts[1] not in {'chrome', 'firefox'}:
                parser.error('Use RUN_NAME=chrome or RUN_NAME=firefox')
            name, browser = parts
            source = ROOT / 'target/runs' / name / 'allure-results'
            result_files = sorted(source.glob('*-result.json'))
            if not result_files:
                raise ValueError('No Allure result files in ' + name)
            results = [(file, json.loads(file.read_text(encoding='utf-8'))) for file in result_files]
            status_counts = dict(collections.Counter(result['status'] for _, result in results))
            selected = [(file, result) for file, result in results if not historical or result['status'] in {'failed', 'broken'}]
            selected_uuids = {result['uuid'] for _, result in selected}
            for file in source.iterdir():
                if file.name.endswith('-result.json'):
                    continue
                if file.name.endswith('-container.json'):
                    container = json.loads(file.read_text(encoding='utf-8'))
                    container['children'] = [child for child in container.get('children', []) if child in selected_uuids]
                    if container['children']:
                        (destination / file.name).write_text(json.dumps(container), encoding='utf-8')
                elif file.is_file() and 'attachment' in file.name:
                    shutil.copy2(file, destination / file.name)
            for file, result in selected:
                identity = result.get('fullName', result['name']) + '|' + browser
                if historical:
                    identity = 'historical|' + name + '|' + identity
                    result['name'] = '[Historical: ' + name + '] ' + result['name']
                    parent = 'Historical framework failures'
                else:
                    if identity in identities:
                        raise ValueError('Duplicate final test/browser identity: ' + identity)
                    identities.add(identity)
                    parent = 'Final live verification / ' + browser
                result['historyId'] = hashlib.sha256(identity.encode()).hexdigest()
                result['parameters'] = [p for p in result.get('parameters', []) if p['name'] not in {'browser', 'evidenceRun'}]
                result['parameters'] += [{'name':'browser', 'value':browser}, {'name':'evidenceRun', 'value':name}]
                result['labels'] = [label for label in result.get('labels', []) if label['name'] != 'parentSuite']
                result['labels'].append({'name':'parentSuite', 'value':parent})
                (destination / file.name).write_text(json.dumps(result), encoding='utf-8')
            summary.append({'run':name, 'browser':browser, 'historical':historical, 'actual_status_counts':status_counts, 'included_results':len(selected)})
    (destination / 'environment.properties').write_text('application=OrangeHRM Starter 5.7\nexecution=LIVE - local MySQL and Selenium Grid\nhistoricalFailures=Explicitly labeled; original statuses preserved\n', encoding='utf-8')
    manifest = {'inputs':summary, 'final_entries':len(identities), 'policy':'Raw run folders untouched; browser-specific histories; historical failures separately labeled with original statuses.'}
    (destination.parent / 'collection.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
