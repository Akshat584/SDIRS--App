import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger("SDIRS_CircuitBreaker")

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(
        self, 
        name: str, 
        failure_threshold: int = 3, 
        recovery_timeout: int = 60
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    def allow_request(self) -> bool:
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name} transitioned to HALF_OPEN")
                return True
            return False
        return True

    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit {self.name} transitioned to CLOSED")
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit {self.name} transitioned to OPEN (failures: {self.failure_count})")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if not self.allow_request():
            logger.warning(f"Circuit {self.name} is OPEN. Blocking request.")
            return None

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.error(f"Circuit {self.name} call failed: {e}")
            raise e

# Create instances for specific services
usgs_breaker = CircuitBreaker("USGS_Earthquake_API", failure_threshold=3, recovery_timeout=300)
weather_breaker = CircuitBreaker("OpenWeatherMap_API", failure_threshold=3, recovery_timeout=300)
