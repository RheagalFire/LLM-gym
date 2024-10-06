from cachetools import TTLCache


class Cache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, maxsize=1024, ttl=3600):
        if not hasattr(self, "initialized"):  # Ensure __init__ is only called once
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
            self.initialized = True

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def get_available_keys(self):
        return self.cache.keys()

    def pop(self, key):
        return self.cache.pop(key)


cache = Cache()

# __all__ = ["cache"]
