# config/config.py

import os

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Additional configs can be added here, e.g.:
# VOTE_EXPIRATION_SECONDS = 86400  # if vote expiration is required
