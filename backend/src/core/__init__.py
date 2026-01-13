"""Core module initialization."""

from .config import settings
from .database import get_session, async_engine, sync_engine

# Providing 'engine' as an alias for async_engine to prevent other import errors
engine = async_engine