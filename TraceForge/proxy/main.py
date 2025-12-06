import os
from urllib.parse import urljoin
import uuid
from aiohttp import ClientSession, web
from aiohttp.tracing import TraceRequestHeadersSentParams
from multidict import CIMultiDict
import structlog
from dotenv import load_dotenv
load_dotenv()

log = structlog.get_logger()

UPSTREAM_BASE_URL = os.getenv("UPSTREAM_BASE_URL")
LISTEN_PORT = 8080

TRACE_HEADER = "X-Trace-Id"
REQUEST_HEADER = "X-Request-Id"

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade"
}

def strip_hop_by_hop_headers(headers: CIMultiDict):
    new_headers = CIMultiDict(headers)

    for h in list(new_headers.keys()):
        if h.lower() in HOP_BY_HOP_HEADERS:
            del new_headers[h]

    connection = headers.get("connection")
    if connection:
        tokens = [h.strip() for h in connection.split(",") if h.strip()]

        for token in tokens:
            for key in list(new_headers.keys()):
                if key.lower() == token.lower():
                    del new_headers[key]

    return new_headers

@web.middleware
async def trace_request_middleware(request:web.BaseRequest, handler):
    trace_id = request.headers.get(TRACE_HEADER)

    if not trace_id:
        trace_id = uuid.uuid4().hex

    request_id = request.headers.get(REQUEST_HEADER)

    if not request_id:
        request_id = uuid.uuid4().hex

    request["trace_id"] = trace_id
    request["request_id"] = request_id

    log.info("Incoming request %s %s trace_id=%s request_id=%s", request.method, request.rel_url, trace_id, request_id)

    response = await handler(request)

    response.headers.setdefault(TRACE_HEADER, trace_id)
    response.headers.setdefault(REQUEST_HEADER, request_id)

    return response

async def handle_proxy(request: web.BaseRequest):
    upstream_url = urljoin(UPSTREAM_BASE_URL, str(request.rel_url))

    trace_id = request["trace_id"]
    request_id = request["request_id"]

    body = await request.read()

    headers = strip_hop_by_hop_headers(request.headers)

    headers.pop("Host", None)

    headers[TRACE_HEADER] = trace_id
    headers[REQUEST_HEADER] = request_id

    log.info("Forwarding %s %s to %s trace_id=%s request_id=%s", request.method, request.rel_url, upstream_url, trace_id, request_id)

    async with ClientSession() as session:
        async with session.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            data=body,
            allow_redirects=False,
        ) as upstream_resp:

            resp_body = await upstream_resp.read()
            resp_headers = strip_hop_by_hop_headers(upstream_resp.headers)

            resp_headers.setdefault(TRACE_HEADER, trace_id)
            resp_headers.setdefault(REQUEST_HEADER, request_id)

            log.info("Upstream response %s for %s trace_id=%s request_id=%s", upstream_resp.status, request.rel_url, trace_id, request_id)

            return web.Response(
                status=upstream_resp.status,
                headers=resp_headers,
                body=resp_body
            )

def create_app():
    app = web.Application(middlewares=[trace_request_middleware])
    app.router.add_route("*", "/{tail:.*}", handle_proxy)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="127.0.0.1", port=LISTEN_PORT)