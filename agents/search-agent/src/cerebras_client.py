import os
from cerebras.cloud.sdk import Cerebras, AsyncCerebras

_client = None
_async_client = None

def get_client():
    """
    Returns a singleton Cerebras client instance.
    """
    global _client
    if _client is None:
        if not os.environ.get("CEREBRAS_API_KEY"):
            raise ValueError("CEREBRAS_API_KEY environment variable not set")
        _client = Cerebras()
    return _client

def get_async_client():
    """
    Returns a singleton AsyncCerebras client instance.
    """
    global _async_client
    if _async_client is None:
        if not os.environ.get("CEREBRAS_API_KEY"):
            raise ValueError("CEREBRAS_API_KEY environment variable not set")
        _async_client = AsyncCerebras()
    return _async_client