"""Re-export app from top-level backend/main.py for backward compatibility."""
from main import app, lifespan

__all__ = ["app", "lifespan"]
