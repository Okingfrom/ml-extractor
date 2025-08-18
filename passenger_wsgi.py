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


def _log(msg: str):
    try:
        sys.stderr.write(msg + "\n")
    except Exception:
        pass


USE_FALLBACK = os.environ.get("USE_FALLBACK", "").lower() in ("1", "true", "yes")

if USE_FALLBACK:
    _log("passenger_wsgi: USE_FALLBACK set; loading app_flask.app")
    from app_flask import app as application
else:
    try:
        _log("passenger_wsgi: trying to load app_improved.app")
        from app_improved import app as application
    except Exception as exc:  # fallback to lightweight app
        _log("passenger_wsgi: failed to load app_improved.app, falling back to app_flask.app")
        _log("passenger_wsgi: import error:\n" + traceback.format_exc())
        from app_flask import app as application
