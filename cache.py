import time


class ResponseCache:

    def __init__(self, ttl=3600):
        """
        ttl = time-to-live in seconds (default 1 hour)
        """
        self.cache = {}
        self.ttl = ttl

    def get(self, key):

        if key not in self.cache:
            return None

        entry = self.cache[key]

        # Check expiration
        if time.time() - entry["time"] > self.ttl:
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key, value):

        self.cache[key] = {
            "value": value,
            "time": time.time()
        }
