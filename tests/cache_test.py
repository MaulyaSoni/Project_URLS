from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep
from cache.memory_cache import MemoryCacheClass

def test_cache_hit():
    cache = MemoryCacheClass()

    cache.set("url:abc123", {"url": "https://example.com"})

    found, value = cache.get("url:abc123")

    assert found is True
    assert value["url"] == "https://example.com"


def test_ttl_expiration():
    cache = MemoryCacheClass()

    cache.set("url:abc123", "value", ttl=0.05)

    sleep(0.1)

    found, value = cache.get("url:abc123")

    assert found is False
    assert value is None


def test_negative_caching():
    cache = MemoryCacheClass()
    calls = 0

    def loader():
        nonlocal calls
        calls += 1
        return None

    assert cache.get_or_load(
        "url:missing",
        loader,
        ttl=600,
        negative_ttl=5
    ) is None

    assert cache.get_or_load(
        "url:missing",
        loader,
        ttl=600,
        negative_ttl=5
    ) is None

    assert calls == 1


def test_concurrent_misses_share_one_loader():
    cache = MemoryCacheClass()
    barrier = Barrier(10)
    calls = 0

    def loader():
        nonlocal calls
        calls += 1
        sleep(0.1)
        return {"url": "https://example.com"}

    def request():
        barrier.wait()

        return cache.get_or_load(
            "url:abc123",
            loader,
            ttl=600
        )

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: request(), range(10)))

    assert calls == 1
    assert all(
        result["url"] == "https://example.com"
        for result in results
    )