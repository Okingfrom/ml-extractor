"""
Passenger WSGI entrypoint for cPanel/Passenger deployments.
Updated to use the new simple_backend FastAPI application.
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def _log(msg: str):
    try:
        sys.stderr.write(f"[passenger_wsgi] {msg}\n")
        sys.stderr.flush()
    except Exception:
        pass

try:
    _log("Loading simple_backend FastAPI application...")

    # Set production environment
    os.environ.setdefault('PRODUCTION', '1')

    from simple_backend import app as fastapi_app
    _log("Successfully imported FastAPI app from simple_backend")

    # Passenger expects a WSGI callable named `application`.
    # FastAPI is an ASGI app; convert it to WSGI using `asgi2wsgi.AsgiToWsgi`.
    try:
        from asgi2wsgi import AsgiToWsgi
        application = AsgiToWsgi(fastapi_app)
        _log("Using AsgiToWsgi adapter (asgi2wsgi)")
    except ImportError:
        _log("asgi2wsgi not installed; falling back to Flask app for Passenger WSGI")
        # Try to load Flask fallback app instead of raising so Passenger can still serve something.
        try:
            from app_flask import app as application
            _log("Loaded Flask fallback app as Passenger WSGI application")
        except Exception as e_fallback:
            _log(f"Failed to load Flask fallback: {e_fallback}")
            # Re-raise original ImportError to surface installation issue
            raise

except Exception as e:
    _log(f"Error loading simple_backend FastAPI app: {e}")
    _log("Attempting fallback to Flask app (app_flask.py)")
    try:
        from app_flask import app as application
        _log("Successfully loaded Flask fallback app")
    except Exception as e2:
        _log(f"Error loading Flask fallback: {e2}")
        raise Exception("Could not load any application")
