"""
Passenger WSGI entrypoint for cPanel/Passenger deployments.

Behavior:
- If environment variable USE_FALLBACK is truthy (1/true/yes), load `app_flask.app`.
- Otherwise, try to import `app_improved.app`. If that fails (missing deps / import
  error) the module will fall back to importing `app_flask.app`.

Passenger expects a WSGI callable named `application` in this module.
"""
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv


def _log(msg: str):
    try:
        sys.stderr.write(msg + "\n")
    except Exception:
        pass

# Load .env if present so USE_FALLBACK set in .env is respected by Passenger
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    try:
        load_dotenv(dotenv_path=str(env_path))
        _log(f"passenger_wsgi: loaded environment from {env_path}")
    except Exception:
        _log("passenger_wsgi: could not load .env file")

USE_IMPROVED = os.environ.get("USE_IMPROVED", "").lower() in ("1", "true", "yes")

if USE_IMPROVED:
    # Try improved app first when explicitly requested.
    try:
        _log("passenger_wsgi: USE_IMPROVED set; attempting to load app_improved.app")
        from app_improved import app as application
    except Exception:
        _log("passenger_wsgi: failed to load app_improved.app; will try app_simple next")
        _log("passenger_wsgi: import error:\n" + traceback.format_exc())
        try:
            _log("passenger_wsgi: attempting to load app_simple.app as fallback")
            from app_simple import app as application
        except Exception:
            _log("passenger_wsgi: failed to load app_simple.app; falling back to inline minimal app")
            _log("passenger_wsgi: import error:\n" + traceback.format_exc())
            try:
                from flask import Flask, Response
                _fallback_app = Flask(__name__)

                @_fallback_app.route('/')
                def _fallback_index():
                    html = '<html><head><title>ML Bulk Mapper (Fallback)</title></head>'
                    html += '<body><h1>ML Bulk Mapper - Fallback</h1>'
                    html += '<p>The improved app failed to start; showing fallback UI. Check error logs.</p>'
                    html += '</body></html>'
                    return Response(html, mimetype='text/html')

                application = _fallback_app
            except Exception:
                def application(environ, start_response):
                    start_response('200 OK', [('Content-Type', 'text/plain')])
                    return [b'ML Bulk Mapper fallback: improved app unavailable']
else:
    # Default to the minimal, dependency-light simple UI (app_simple)
    try:
        _log("passenger_wsgi: loading app_simple.app as primary application")
        from app_simple import app as application
    except Exception:
        _log("passenger_wsgi: failed to load app_simple.app, will try improved if requested")
        _log("passenger_wsgi: import error:\n" + traceback.format_exc())

        if USE_IMPROVED:
            try:
                _log("passenger_wsgi: USE_IMPROVED set; attempting to load app_improved.app")
                from app_improved import app as application
            except Exception:
                _log("passenger_wsgi: failed to load app_improved.app; falling back to inline minimal app")
                _log("passenger_wsgi: import error:\n" + traceback.format_exc())
                try:
                    from flask import Flask, Response
                    _fallback_app = Flask(__name__)

                    @_fallback_app.route('/')
                    def _fallback_index():
                        html = '<html><head><title>ML Bulk Mapper (Fallback)</title></head>'
                        html += '<body><h1>ML Bulk Mapper - Fallback</h1>'
                        html += '<p>The improved app failed to start; showing fallback UI. Check error logs.</p>'
                        html += '</body></html>'
                        return Response(html, mimetype='text/html')

                    application = _fallback_app
                except Exception:
                    def application(environ, start_response):
                        start_response('200 OK', [('Content-Type', 'text/plain')])
                        return [b'ML Bulk Mapper fallback: improved app unavailable']
        else:
            # Last resort: minimal inline fallback to avoid 500 errors
            try:
                from flask import Flask, Response
                _fallback_app = Flask(__name__)

                @_fallback_app.route('/')
                def _fallback_index():
                    html = '<html><head><title>ML Bulk Mapper (Fallback)</title></head>'
                    html += '<body><h1>ML Bulk Mapper - Fallback</h1>'
                    html += '<p>The primary app is unavailable. Please contact the administrator or enable USE_IMPROVED to try the improved UI.</p>'
                    html += '</body></html>'
                    return Response(html, mimetype='text/html')

                application = _fallback_app
            except Exception:
                def application(environ, start_response):
                    start_response('200 OK', [('Content-Type', 'text/plain')])
                    return [b'ML Bulk Mapper fallback: primary app unavailable']
