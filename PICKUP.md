# PICKUP.md

Quick pickup instructions — run these on the other PC to continue where you left off.

## 1) Install tools (Linux example)

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
# optional: install GitHub CLI
sudo apt install -y gh
```

## 2) Clone and update repo

```bash
git clone https://github.com/Okingfrom/ml-extractor.git
cd ml-extractor
git fetch --all
git checkout main
git pull origin main
git status --porcelain=2 -b
```

## 3) Create venv and install minimal deps (fallback-safe)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install flask requests werkzeug
# if you want full deps (may fail on old CPUs):
# pip install -r requirements.txt
```

## 4) Prepare `.env` (DO NOT commit)

```bash
cp .env.template .env
# edit .env and set SECRET_KEY and any required values
nano .env
```

## 5) Run locally (fallback recommended)

```bash
# fallback (safe)
python -m flask --app app_flask run --host 127.0.0.1 --port 5000
# or gunicorn
.venv/bin/gunicorn -b 127.0.0.1:8000 app_flask:app

# restored app (only if full deps available)
.venv/bin/gunicorn -b 127.0.0.1:8001 app_improved:app
```

## 6) Check CI / Actions

```bash
gh run list --repo Okingfrom/ml-extractor --limit 10
# view logs for a run (replace <ID>):
gh run view <ID> --repo Okingfrom/ml-extractor --log
# rerun if needed:
gh run rerun <ID> --repo Okingfrom/ml-extractor
```

## 7) Deploy (server or cPanel)

Server (SSH):

```bash
./scripts/deploy_to_server.sh "$HOME/app_ml_extractor" main
# follow logs:
tail -f ~/app_ml_extractor/gunicorn.log
```

cPanel/Passenger: `passenger_wsgi.py` present; `.cpanel.yml` sets `USE_FALLBACK=1` by default.

## 8) If you have local work-in-progress

```bash
git add -A
git commit -m "WIP: notes before switching PC" || true
git push origin HEAD
# or stash
git stash push -m "WIP before switching PC"
```

## Notes

- I moved backup/corrupt files into `backups/archived/` and renamed to `.txt` so CI compile checks don't fail on them.
- Do NOT commit `.env` or `users.db`.
- Wait until GitHub Actions (Compile check) shows success before deploying.

If you want me to monitor the CI and notify you when it turns green, tell me and I'll watch it and report back.
