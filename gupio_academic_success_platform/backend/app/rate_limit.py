import threading
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._hits = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            q = self._hits[key]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True


limiter = InMemoryRateLimiter()
