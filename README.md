# Railway cron and worker examples

Two Python standard-library scripts demonstrate different process lifecycles:

- `python check_once.py`: checks TARGET_URL once and exits 0 for HTTP 2xx, otherwise 1.
- `python worker.py`: repeats the check, waiting 60 seconds after each attempt; SIGTERM/SIGINT stops the loop.

TARGET_URL defaults to https://example.com. Use a public HTTP(S) URL without credentials. HTTP redirects are followed. The network-operation timeout is 10 seconds; this is not a hard end-to-end task deadline.

Run locally with Python 3.13, or build the included Dockerfile. No pip packages are required.

On Railway, use two services from this repository:

- cron-check: start command `python check_once.py`, Cron Schedule `0 9 * * *` (09:00 UTC daily), restart policy Never.
- worker-check: start command `python worker.py`, no cron schedule, restart policy On Failure, App Sleep disabled.

Neither service needs a public domain. Add TARGET_URL in each service's Variables tab. Worker logs show results; a failed URL check does not crash the worker. Railway's restart policy applies if the worker process exits with an error.

The worker demonstrates polling, not durable task delivery or alerting. Neither script stores state. Before adding writes, design for safe repeated execution. For queue-backed work, add a queue library and the appropriate broker.

## Validation

Run `python -m unittest discover -s tests -v`. Tests use an HTTP server on localhost; they cover success, HTTP failure, request timeout, repeated worker checks, and termination.

## Railway Infrastructure as Code

Node.js is only needed for the optional infrastructure tooling; the running scripts use Python alone.

Install the tooling with `npm ci`, authenticate with `railway login`, and link a new, empty project using `railway link`. Review `.railway/railway.ts`, then run `npm run check:iac`, `railway config plan`, and `railway config apply`. The file defines two services, including `deploy.cronSchedule` on cron-check. Do not apply this complete project definition to an unrelated populated environment.

The schedule is 09:00 UTC daily. To trigger a manual check in the linked project: `railway cron run --service cron-check --yes`. Inspect recent runs with `railway cron list --service cron-check` and output with `railway logs --service cron-check --latest --lines 20`.

Deployment and template verification results are recorded with the accompanying article.
