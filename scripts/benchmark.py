"""Equivalent 40-scenario Chrome + Firefox workloads; startup/report rendering excluded."""
import argparse, concurrent.futures, csv, json, os, platform, statistics, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def run_browser(browser, directory, workers=1):
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / 'cucumber.json'
    wrapper = 'mvnw.cmd' if os.name == 'nt' else './mvnw'
    command = [wrapper, '-B', '-ntp', 'test', '-Dsuite=ui', '-Dcucumber.filter.tags=@regression',
               f'-Dbrowser={browser}', f'-Dworkers={workers}', f'-Dbuild.dir={directory.as_posix()}',
               f'-Dcucumber.plugin=pretty,json:{json_path.as_posix()},io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm']
    with (directory/'maven.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    scenarios = []
    if json_path.exists():
        scenarios = [scenario for feature in json.loads(json_path.read_text(encoding='utf-8')) for scenario in feature.get('elements', []) if scenario.get('type') == 'scenario']
    all_passed = len(scenarios) == 40 and all(step.get('result', {}).get('status') == 'passed' for s in scenarios for step in s.get('steps', []) + s.get('before', []) + s.get('after', []))
    return {'browser': browser, 'exit': result.returncode, 'scenarios': len(scenarios), 'valid': result.returncode == 0 and all_passed}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=3)
    parser.add_argument('--output', default='benchmark-results')
    args = parser.parse_args()
    if args.trials < 3: parser.error('At least three measured trials per mode are required')
    output = ROOT/args.output/time.strftime('%Y%m%d-%H%M%S')
    output.mkdir(parents=True)
    metadata = {'platform':platform.platform(), 'cpu':platform.processor(), 'logical_cpus':os.cpu_count(), 'concurrency':{'sequential':1,'parallel':2}, 'application':'OrangeHRM 5.7', 'workload':'40 scenarios x 2 browsers = 80 executions per trial', 'excluded':'environment startup, dependency warmup and HTML report generation', 'policy':'fresh browser per scenario, unique owned employees, identical @regression tags, one session per browser node'}
    for tool,cmd in [('docker',['docker','info','--format','{{.NCPU}} CPUs; {{.MemTotal}} bytes RAM; {{.ServerVersion}}']),('images',['docker','compose','images','--format','json'])]:
        metadata[tool]=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True).stdout.strip()
    (output/'machine.json').write_text(json.dumps(metadata,indent=2))
    rows=[]
    for trial in range(1,args.trials+1):
        # Alternate order to reduce systematic warming bias.
        for mode in (['sequential','parallel'] if trial%2 else ['parallel','sequential']):
            start=time.perf_counter()
            folder=output/f'{trial}-{mode}'
            if mode=='parallel':
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    results=list(pool.map(lambda browser: run_browser(browser,folder/browser), ['chrome','firefox']))
            else: results=[run_browser(browser,folder/browser) for browser in ['chrome','firefox']]
            row={'trial':trial,'mode':mode,'seconds':round(time.perf_counter()-start,3),'valid':all(r['valid'] for r in results),'details':json.dumps(results)}
            rows.append(row)
            with (output/'raw.csv').open('w',newline='') as file:
                writer=csv.DictWriter(file,fieldnames=list(row)); writer.writeheader(); writer.writerows(rows)
            print(row,flush=True)
    summary={'status':'INVALID: some runs failed; no speedup claim'}
    if all(row['valid'] for row in rows):
        seq=statistics.median(r['seconds'] for r in rows if r['mode']=='sequential')
        par=statistics.median(r['seconds'] for r in rows if r['mode']=='parallel')
        summary={'status':'measured','sequential_median_seconds':seq,'parallel_median_seconds':par,'speedup':seq/par,'runtime_reduction_percent':100*(seq-par)/seq}
    (output/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
    return 0 if all(row['valid'] for row in rows) else 1

if __name__=='__main__': raise SystemExit(main())
