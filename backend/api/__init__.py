"""API routes package

This package intentionally avoids importing submodules at package import time
to prevent heavy import-time side-effects (like SQLAlchemy) when the dev
server uses importlib to load specific modules. Individual routers should
be imported explicitly by the main application.
"""

__all__ = []
