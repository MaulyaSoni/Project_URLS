import logging
from collections import OrderedDict
from concurrent.futures import Future
from threading import RLock
from time import monotonic 

class MemoryCacheClass:

    def __init__(self, max_size=10_000):
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size
        self._cache = OrderedDict()
        self._inflight = {}
        self._versions = {}
        self._lock = RLock()

    def get_unlocked(self, key):
        entry = self._cache.get(key)
        if entry is None:
            return False, None

        value, expires_at = entry
        if monotonic() >= expires_at:
            del self._cache[key]
            logging.debug(f"Cache key expired: {key}")
            return False, None

        self._cache.move_to_end(key)
        return True, value

    def get(self, key):
        with self._lock:
            found, value = self.get_unlocked(key)
            if found:
                logging.debug(f"Cache HIT: {key}")
            else:
                logging.debug(f"Cache MISS: {key}")
            return found, value

    def _store_unlocked(self, key, value, ttl):
        if ttl <= 0:
            return

        self._cache[key] = (value, monotonic() + ttl)
        self._cache.move_to_end(key)

        while len(self._cache) > self.max_size:
            evicted_key, _ = self._cache.popitem(last=False)
            logging.info(f"Cache eviction triggered. Removed key: {evicted_key}")

    def set(self, key, value, ttl=600):
        with self._lock:
            if key in self._inflight:
                self._versions[key] = self._versions.get(key, 0) + 1
                logging.warning(f"Version updated during set for key :{key}")

            self._store_unlocked(key, value, ttl)
            logging.debug(f"Key set in cache:{key} -> {ttl})")

    def delete(self, key):
        with self._lock:
            self._cache.pop(key, None)
            if key in self._inflight:
                self._versions[key] = self._versions.get(key, 0) + 1
            logging.debug(f"Key deleted : {key}")

    def get_or_load(self, key, loader, ttl=600, negative_ttl=5):
        found, value = self.get(key)
        if found:
            return value

        with self._lock:
            found, value = self.get_unlocked(key)
            if found:
                return value

            future = self._inflight.get(key)

            if future is None:
                future = Future()
                self._inflight[key] = future
                self._versions[key] = 0
                is_loader = True
                logging.info(f"Executing DB/API loader for key : {key}")
            else:
                is_loader = False
                logging.info(f"Waiting on in-flight request (Single Flight) for key : {key}")

        if not is_loader:
            return future.result()

        try:
            while True:
                with self._lock:
                    version = self._versions[key]

                value = loader()

                with self._lock:
                    current_version = self._versions[key]

                    if current_version != version:
                        logging.warning(f"Version mismatch for key {key}. Overwrite prevented.")
                        found, latest_value = self.get_unlocked(key)
                        if found:
                            value = latest_value
                            future.set_result(value)
                            break
                        continue

                    effective_ttl = negative_ttl if value is None else ttl
                    self._store_unlocked(key, value, effective_ttl)
                    future.set_result(value)
                    break

            return value

        except Exception as exc:
            logging.error(f"Loader execution failed for key {key} :{exc} " , exc_info=True)
            with self._lock:
                future.set_exception(exc)
            raise

        finally:
            with self._lock:
                if self._inflight.get(key) is future:
                    del self._inflight[key]
                self._versions.pop(key, None)