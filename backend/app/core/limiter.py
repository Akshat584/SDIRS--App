import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Define the shared limiter instance
# Disable limiter in test environment
# Added default limit of 100/minute as per security requirements
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=os.getenv("ENVIRONMENT") != "test"
)

