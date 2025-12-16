class Backend:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.healthy = True
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None

class BackendPool:
    def __init__(self, backends):
        self.backends = backends
        self.index = 0

    def get_next_backend(self):
        if not self.backends:
            return None
        
        for _ in range(len(self.backends)):
            backend = self.backends[self.index]
            self.index = (self.index + 1) % len(self.backends)

            if backend.healthy:
                return backend
        return None