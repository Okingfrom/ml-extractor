Suggested cleanup before commit:

Move to backups/legacy/ (these files are large or duplicates or development servers):
- backend/dev_server.py
- backend/dev_server_backup.py
- backend/dev_server_fixed.py
- app_improved.py
- app_improved.py.corrupt_backup
- app.py and app.py.bak
- backend/dev_server_* variants and other legacy dev copies

Keep these active entrypoints:
- backend/main.py  (canonical full-featured FastAPI)
- simple_backend.py (lightweight fallback compatible with cPanel simple setups)
- passenger_wsgi.py (now attempts Flask fallback if asgi2wsgi not available)

Other notes:
- requirements.txt: pin versions appropriate for target Python (recommend Python 3.8 or 3.11 on server)
- Add a small `.gitignore` entry for local `data/` and `logs/` if not present.

Suggested git commit message:
"chore: tidy entrypoints, harden passenger_wsgi fallback, add deployment notes"
