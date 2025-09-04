"""
Delegate WSGI entrypoint for Passenger.

This file keeps the Passenger entrypoint tiny and delegates the real loading
and ASGI/WSGI adaptation to `passenger_wsgi_new.py`. If that import fails,
it will attempt a minimal fallback to a Flask app defined in `app_flask.py`.
"""
import os
import sys

# Ensure repository root is on sys.path so imports in passenger_wsgi_new work
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Delegate to the robust loader if present
    from passenger_wsgi_new import application
except Exception:
    # Try to import our all-in-one FastAPI ASGI app and adapt to WSGI
    try:
        # Ensure extractorml package is on path
        REPO_DIR = os.path.dirname(__file__)
        EXTRACTORML_PATH = os.path.join(REPO_DIR, 'extractorml')
        if EXTRACTORML_PATH not in sys.path:
            sys.path.insert(0, EXTRACTORML_PATH)
        # Import ASGI app
        from backend.main import app as asgi_app
        # Adapt ASGI to WSGI using asgiref
        from asgiref.wsgi import AsgiToWsgi
        application = AsgiToWsgi(asgi_app)
    except Exception:
        # Fallback to a simple Flask app if available
        try:
            from app_flask import app as application
        except Exception:
            # Re-raise to let Passenger show the original error
            raise
