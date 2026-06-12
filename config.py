# config.py

# Rate Limit Settings
RATE_LIMIT_REQUESTS = 10        # Max requests per window
                                # (10 for easy local testing, 100 for production)
RATE_LIMIT_WINDOW_SECONDS = 60  # Time window: 1 minute

# IP Block Settings
BLOCK_DURATION_SECONDS = 900    # How long to block an IP: 15 minutes

# Redis Settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Redis Key Prefixes
RATE_LIMIT_KEY_PREFIX = 'rate_limit'  # -> rate_limit:{ip}
BLOCK_KEY_PREFIX = 'blocked'           # -> blocked:{ip}
