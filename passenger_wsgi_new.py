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
    from simple_backend import app
    _log("Successfully loaded FastAPI app")
    
    # Passenger expects a WSGI application
    # FastAPI is ASGI, so we need an ASGI-to-WSGI adapter
    try:
        from asgiref.wsgi import WsgiToAsgi
        application = WsgiToAsgi(app)
        _log("Using ASGI-to-WSGI adapter")
    except ImportError:
        _log("asgiref not available, trying direct WSGI mode")
        # Some hosts support ASGI directly
        application = app
        
except Exception as e:
    _log(f"Error loading simple_backend: {e}")
    _log("Falling back to Flask app...")
    try:
        from app_flask import app as application
        _log("Successfully loaded Flask fallback")
    except Exception as e2:
        _log(f"Error loading Flask app: {e2}")
        raise Exception("Could not load any application")
