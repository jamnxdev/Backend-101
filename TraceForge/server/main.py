import datetime
import json
import time
import uuid
from aiohttp import web
import pathlib
import structlog

BASE_DIR = pathlib.Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

log = structlog.get_logger()

TRACE_HEADER = "X-Trace-Id"
REQUEST_HEADER = "X-Request-Id"

@web.middleware
async def logging_middleware(request: web.BaseRequest, handler):
    start = time.time()

    headers = request.headers

    trace_id = request.headers.get(TRACE_HEADER)

    if not trace_id:
        trace_id = str(uuid.uuid4())

    req_id = request.headers.get(REQUEST_HEADER)

    if not req_id:
        req_id = str(uuid.uuid4())

    xff = request.headers.get("X-Forwarded-For")
    if xff:
        remote_ip = xff.split(",")[0].strip()
    else:
        peername = request.transport.get_extra_info("peername")
        remote_ip = peername[0] if peername else None
        
    try:
        response = await handler(request)
        response.headers["x-trace-id"] = trace_id
        response.headers["x-request-id"] = req_id
    except Exception as e:
        response = web.Response(status=500)
        raise
    finally:
        latency_ms = round((time.time() - start) * 1000)

        headers_json = json.dumps({
            "timestamp": datetime.datetime.now().isoformat(),
            "trace_id": trace_id,
            "request_id": req_id,
            "method": request.method,
            "path": request.path,
            "status": response.status,
            "latency_ms": latency_ms,
            "remote_ip": remote_ip,
        })
        log.info(headers_json)

    return response


async def handle_root(request: web.BaseRequest):
    return web.FileResponse(STATIC_DIR / "index.html")

async def handle_API_RESOURCE(request: web.BaseRequest):
    return web.json_response({
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "This is a API resource message",
    })

app = web.Application(middlewares=[logging_middleware])
app.router.add_static('/static', STATIC_DIR)
app.router.add_get('/', handle_root)
app.router.add_get('/api/resource', handle_API_RESOURCE)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8081)