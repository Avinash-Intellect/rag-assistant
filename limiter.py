import time


class RateLimiter:

    def __init__(self, max_calls=15, period=60):
        """
        max_calls = allowed calls
        period = seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def allow(self):

        now = time.time()

        # Remove expired calls
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < self.period
        ]

        if len(self.calls) >= self.max_calls:
            return False

        self.calls.append(now)
        return True
