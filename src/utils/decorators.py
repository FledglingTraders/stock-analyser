import functools
import time

from src.settings.shared import logger


def retry(times: int = 3, delay: float = 2.0):
    """Retry decorator that retries a function call if an exception occurs."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    logger.error(f"Attempt {attempt}/{times} failed: {error}")
                    if attempt < times:
                        time.sleep(delay)  # Wait before retrying
                    else:
                        logger.error("Max retries reached. Raising exception.")
                        raise  # Raise the last exception if all attempts fail
        return wrapper
    return decorator


def time_execution(func):
    """Decorator to measure execution time of a function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timer
        result = func(*args, **kwargs)
        end_time = time.time()  # End timer
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.6f} seconds")
        return result
    return wrapper