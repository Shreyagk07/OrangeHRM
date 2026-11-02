# Sequential versus parallel protocol

Status: **pending — Docker Server unavailable; no measured timings**. There is no raw-results CSV until actual execution. The target 45→15 minutes is not an accomplishment.

Provision once using the pinned application, database and dated Grid images. Export the same credentials/URLs. Warm Maven dependency resolution with test compilation. Do not change the app, machine, browser images or reporting settings between modes. Use a quiet machine with fixed CPU/RAM allocation; record Docker CPU/memory and image metadata in machine.json. If a resource limit makes three trials impractical, report the limitation; do not invent missing runs.

Run `python3 scripts/benchmark.py --trials 3` from the project root. Each trial executes the same 40 tagged scenarios in Chrome and Firefox. Sequential runs the two browser processes one after another; parallel starts both processes together. Each process has one TestNG DataProvider worker. Grid has one slot per browser. No extra TestNG suite/fork parallelism multiplies sessions.

Environment startup, installer work, dependency warmup and HTML rendering are excluded. Maven process startup, fresh browser per scenario, fixture creation/cleanup, screenshots on failures and Allure result writing are included. Modes alternate first position across trials to reduce order bias. The default three trials per mode represent 480 scenario executions total.

Raw CSV rows contain trial, mode, wall-clock seconds, validation flag and per-browser exit/count details. A trial is valid only when both browsers exit successfully and report exactly 40 passing scenarios including hooks. Any failed/incomplete trial invalidates the final speedup report. Preserve failures for investigation rather than dropping slow or failed samples.

For a completely valid run:

* Sequential median = median(sequential trial durations).
* Parallel median = median(parallel trial durations).
* Speedup = sequential median / parallel median.
* Runtime reduction % = 100 × (sequential median − parallel median) / sequential median.

Concurrency is two, so a threefold speedup is not an expected architectural guarantee. Always report hardware, concurrency, workload and actual medians alongside any resume claim.
