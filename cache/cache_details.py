from cache.memory_cache import MemoryCacheClass

url_cache = MemoryCacheClass(max_size=10_000)

# 600 seconds and 5 rounds 
URL_CACHE_TTL = 600       
NEGATIVE_CACHE_TTL = 5   