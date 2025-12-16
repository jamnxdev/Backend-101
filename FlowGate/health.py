import time

class HealthManager:
    def __init__(self, failure_threshold, cooldown):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
    
    def record_failure(self, backend):
        backend.failure_count += 1
        backend.last_failure_time = time.time()

        if backend.failure_count >= self.failure_threshold:
            backend.healthy = False

    def record_success(self, backend):
        backend.failure_count = 0
        backend.healthy = True
        backend.last_success_time = time.time()

    def can_try_recover(self, backend):
        if backend.healthy:
            return True

        if backend.last_failure_time is None:
            return False

        return time.time() - backend.last_failure_time >= self.cooldown