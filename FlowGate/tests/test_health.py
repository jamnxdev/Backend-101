import time
from backend_pool import Backend
from health import HealthManager

def test_backend_marked_unhealthy_after_threshold():
    backend = Backend("localhost", 8001)
    health = HealthManager(failure_threshold=2, cooldown=1)

    health.record_failure(backend)
    assert backend.healthy

    health.record_failure(backend)
    assert not backend.healthy

def test_backend_recovers_after_cooldown():
    backend = Backend("localhost", 8001)
    health = HealthManager(failure_threshold=1, cooldown=0.1)

    health.record_failure(backend)
    time.sleep(0.2)

    assert health.can_try_recover(backend)

