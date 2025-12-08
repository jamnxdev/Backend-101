import time
import pytest

from proxy import main as proxy_main

@pytest.mark.asyncio
async def test_proxy_delay_increases_latency(aiohttp_client, monkeypatch, upstream_app):
    upstream_server = await aiohttp_client(upstream_app)

    monkeypatch.setattr(proxy_main, "UPSTREAM_BASE_URL", str(upstream_server.make_url("/")))
    monkeypatch.setattr(proxy_main, "PROXY_DELAY_MS", 200)
    monkeypatch.setattr(proxy_main, "PROXY_DROP_RATE", 0.0)

    app = proxy_main.create_app()
    client = await aiohttp_client(app)

    start = time.monotonic()
    resp = await client.get("/api/resource")
    end = time.monotonic()

    assert resp.status == 200
    elapsed_ms = (end - start) * 1000.0

    assert elapsed_ms >= 180

@pytest.mark.asyncio
async def test_proxy_drop_always_503_with_rate_one(aiohttp_client, monkeypatch, upstream_app):
    upstream_server = await aiohttp_client(upstream_app)

    monkeypatch.setattr(proxy_main, "UPSTREAM_BASE_URL", str(upstream_server.make_url("/")))
    monkeypatch.setattr(proxy_main, "PROXY_DELAY_MS", 0)
    monkeypatch.setattr(proxy_main, "PROXY_DROP_RATE", 1.0)

    rng = proxy_main.random.Random(123)
    monkeypatch.setattr(proxy_main, "FAULT_RNG", rng)

    app = proxy_main.create_app()
    client = await aiohttp_client(app)

    resp = await client.get("/api/resource")

    assert resp.status == 503
    data = await resp.json()
    assert data["error"] == "simulated_drop"

    metrics_text = await (await client.get("/metrics")).text()
    assert "requests_dropped_total" in metrics_text
