# Title: Prepare repo for cPanel deployment (.cpanel.yml + ignore users.db)

## Summary

This PR prepares the repository for deployment to cPanel by adding a checked-in `.cpanel.yml` at the top level and ensuring local-only artifacts (like `users.db`) are ignored.

## What this PR includes

- `.cpanel.yml` with steps to create a virtualenv, install `requirements.txt`, create necessary folders, and run the app with `gunicorn`.
- `.gitignore` updated to include `users.db`.
- `users.db` removed from git tracking (left intact locally).

## Pre-deploy checklist

- [ ] Verify `.cpanel.yml` commands match the target environment (Python 3 path, $PORT variable availability).
- [ ] Configure environment variables in cPanel (SECRET_KEY, any API keys, DB_URL if using external DB).
- [ ] Make sure `requirements.txt` contains `gunicorn` and other production deps.
- [ ] Confirm uploads/backups directories are writable in the cPanel file system.

## How to test locally

1. Create and activate a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the app with gunicorn locally:

```bash
gunicorn -b 0.0.0.0:8000 app_improved:app
```

3. Open <http://127.0.0.1:8000> and test login (use test accounts created earlier) and upload flow.

## Notes

- The branch is `deploy-cpanel-prepare_20250818_174112` and is ready for PR creation.
- I removed `users.db` from source control to avoid leaking local test data; the file remains locally.

Prepared-by: automation
