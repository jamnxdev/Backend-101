import pytest
from aiohttp import web

from proxy.main import TRACE_HEADER, REQUEST_HEADER
from proxy import main as proxy_main

@pytest.mark.asyncio
async def test_proxy_generates_ids_when_missing(aiohttp_client, monkeypatch, upstream_app):
    upstream_server = await aiohttp_client(upstream_app)

    monkeypatch.setattr(proxy_main, "UPSTREAM_BASE_URL", str(upstream_server.make_url("/")))
    monkeypatch.setattr(proxy_main, "PROXY_DELAY_MS", 0)
    monkeypatch.setattr(proxy_main, "PROXY_DROP_RATE", 0.0)

    app = proxy_main.create_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/resource")

    assert resp.status == 200

    trace_id = resp.headers.get(TRACE_HEADER)
    request_id = resp.headers.get(REQUEST_HEADER)

    assert trace_id is not None and trace_id != ""
    assert request_id is not None and request_id != ""

@pytest.mark.asyncio
async def test_proxy_reuses_client_trace_id(aiohttp_client, monkeypatch):
    async def upstream_handler(request):
        return web.json_response({ "trace": request.headers.get(TRACE_HEADER)})

    upstream  = web.Application()
    upstream.router.add_route("*", "/echo", upstream_handler)
    upstream_server = await aiohttp_client(upstream)

    monkeypatch.setattr(proxy_main, "UPSTREAM_BASE_URL", str(upstream_server.make_url("/")))
    monkeypatch.setattr(proxy_main, "PROXY_DELAY_MS", 0)
    monkeypatch.setattr(proxy_main, "PROXY_DROP_RATE", 0.0)

    app = proxy_main.create_app()
    client = await aiohttp_client(app)

    client_trace = "client-trace-123"
    resp = await client.get("/echo", headers={TRACE_HEADER: client_trace})

    assert resp.status == 200

    assert resp.headers[TRACE_HEADER] == client_trace

    data = await resp.json()

    assert data["trace"] == client_trace

    app = proxy_main.create_app()
    client = await aiohttp_client(app)