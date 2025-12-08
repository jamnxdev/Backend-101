# TraceForge

TraceForge is a small playground for experimenting with HTTP fault injection, trace propagation, and observability. It ships three pieces:
- **Upstream demo server** (`server/main.py`): serves a static page and a JSON API at `/api/resource`, echoing back trace/request IDs.
- **Proxy with fault injection** (`proxy/main.py`): forwards traffic to the upstream server while injecting delays or drops, propagating trace headers, and exposing Prometheus metrics.
- **Async load generator** (`tools/client.py`): fires concurrent requests at the proxy and records per-request outcomes to JSON or CSV.

## Quick start
```bash
python -m venv venv
venv\Scripts\activate         # On Windows; use `source venv/bin/activate` on Unix
pip install -r requirements.txt
```

Create a `.env` file at the repo root for the proxy (see configuration below), then run the components in two terminals:
```bash
# Terminal 1: start upstream server on 8081
python server/main.py

# Terminal 2: start proxy on 8080 (reads .env)
python proxy/main.py
```

Visit `http://127.0.0.1:8080/api/resource` through the proxy or `http://127.0.0.1:8080/static/index.html` for the static page via the upstream.

## Proxy configuration (.env)
The proxy reads its settings from environment variables (e.g., a `.env` file):
```
UPSTREAM_BASE_URL=http://127.0.0.1:8081
PROXY_DELAY_MS=0             # Artificial latency in milliseconds (0 disables)
PROXY_DROP_RATE=0.0          # Fraction in [0,1]; 1.0 always drops with 503
PROXY_MOD_HEADER=            # Optional "Header-Name: value" added to responses
RNG_SEED=123                 # Optional seed for deterministic fault behavior
```

Key behaviors:
- Adds/propagates `X-Trace-Id` and `X-Request-Id` on every request/response.
- Strips hop-by-hop headers before forwarding.
- Fault injection:
  - Delay: sleeps `PROXY_DELAY_MS` before forwarding.
  - Drop: with probability `PROXY_DROP_RATE`, returns `503` and does **not** forward.
- Prometheus metrics at `GET /metrics` (counters for total, forwarded, dropped, delayed; histogram for latency).

## Upstream demo server
- Runs on `127.0.0.1:8081` by default.
- Routes:
  - `GET /` or `/static/index.html`: static HTML.
  - `GET /api/resource`: JSON payload with a timestamp and message.
- Middleware ensures `X-Trace-Id` and `X-Request-Id` are present and logged.

## Load generator (`tools/client.py`)
Fire concurrent requests at the proxy and capture results:
```bash
python tools/client.py --url http://127.0.0.1:8080/api/resource \
  --n 200 --concurrency 20 --retries 2 --retry-backoff-ms 100 \
  --client-trace --output results.json --format json
```
Options:
- `--n`: total requests (default 100)
- `--concurrency`: max in-flight requests (default 10)
- `--retries`: per-request retries on errors/5xx (default 0)
- `--retry-backoff-ms`: initial backoff in ms; doubles per retry (default 100)
- `--client-trace`: generate `X-Trace-Id` client-side; otherwise rely on proxy
- `--output`: path for results (default `results.json`)
- `--format`: `json` or `csv`

Outputs contain per-request status, latency, retries, and trace IDs for later analysis.

## Testing
Run the automated checks:
```bash
pytest
```

What is covered:
- Trace ID generation and propagation.
- Fault injection delay and drop behavior.
- Hop-by-hop header stripping.

## Useful endpoints
- Proxy: `http://127.0.0.1:8080/api/resource`
- Proxy metrics: `http://127.0.0.1:8080/metrics`
- Upstream direct: `http://127.0.0.1:8081/api/resource`
- Static page via proxy: `http://127.0.0.1:8080/static/index.html`

## Troubleshooting
- Ensure `.env` defines `UPSTREAM_BASE_URL`, `PROXY_DELAY_MS`, and `PROXY_DROP_RATE`; `int()`/`float()` parsing errors will surface on startup.
- If every request returns `503`, check `PROXY_DROP_RATE` (set to `0.0` to disable drops).
- Use `RNG_SEED` for reproducible drop/delay patterns during testing.
