from backend_pool import Backend, BackendPool

def test_round_robin_selection():
    pool = BackendPool([
        Backend("localhost", 8001),
        Backend("localhost", 8002),
        Backend("localhost", 8003),
    ])

    assert pool.get_next_backend().port == 8001
    assert pool.get_next_backend().port == 8002
    assert pool.get_next_backend().port == 8003
    assert pool.get_next_backend().port == 8001

def test_skip_unhealthy_backend():
    b1 = Backend("localhost", 8001) 
    b2 = Backend("localhost", 8002) 
    b1.healthy = False

    pool = BackendPool([b1, b2])
    assert pool.get_next_backend().port == 8002

def test_no_healthy_backend():
    b1 = Backend("localhost", 8001)
    b1.healthy = False

    pool = BackendPool([b1])
    assert pool.get_next_backend() is None