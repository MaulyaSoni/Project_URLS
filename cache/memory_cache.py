from collections import OrderedDict
from threading import RLock
from time import monotonic
from concurrent.futures import Future

class MemoryCacheClass:

    def __init__(self, max_size=10_000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = RLock()
        self.inflight = {}

    def get(self, key):
        with self.lock:
            entry = self.cache.get(key)

            if entry is None:
                return False, None

            value, expires_at = entry

            if monotonic() >= expires_at:
                del self.cache[key]
                return False, None

            self.cache.move_to_end(key)
            return True, value

    def set(self, key, value, ttl=600):
        if ttl <= 0:
            return

        with self.lock:
            self.cache[key] = (
                value,
                monotonic() + ttl
            )
            self.cache.move_to_end(key)

            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def delete(self, key):
        with self.lock:
            self.cache.pop(key, None)

    def get_or_load(self, key, loader, ttl=600):
        found, value = self.get(key)

        if found:
            return value

        with self.lock:
            found, value = self.get(key)

            if found:
                return value

            future = self.inflight.get(key)

            if future is None:
                future = Future()
                self.inflight[key] = future
                is_loader = True
            else:
                is_loader = False

        if not is_loader:
            return future.result()

        try:
            value = loader()
            eff_ttl = (5 if value is None else ttl) 
            self.set(key, value, eff_ttl )
            future.set_result(value)
            return value

        except Exception as exc:
            future.set_exception(exc)
            raise

        finally:
            with self.lock:
                if self.inflight.get(key) is future:
                    del self.inflight[key]