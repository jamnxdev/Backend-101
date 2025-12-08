# tests/conftest.py
import sys
from pathlib import Path

# This points to the TraceForge directory (one level above tests/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Ensure project root is on sys.path so `import proxy` works
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from aiohttp import web

@pytest.fixture
async def upstream_app():
    async def handler(request):
        return web.json_response({ "ok" : True})

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handler)

    return app
