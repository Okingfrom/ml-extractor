README - Deployment (systemd)
=================================

This document explains the minimal steps to run the application under systemd on a Linux host.

Prerequisites
- The repository is deployed at: /home/granaventura/app_ml_extractor (adjust paths where needed).
- A Python virtualenv exists at `/home/granaventura/app_ml_extractor/.venv` with `gunicorn` and `Flask` installed.
- An `.env` file exists at `/home/granaventura/app_ml_extractor/.env` containing at least:
  - SECRET_KEY (keep secret)
  - USE_FALLBACK=1 (recommended on hosts that can't install heavy numeric wheels)

Create the systemd unit
------------------------
Create `/etc/systemd/system/ml-extractor.service` with the following content (use sudo):

```ini
[Unit]
Description=ML Extractor (gunicorn) WSGI service
After=network.target

[Service]
User=granaventura
Group=granaventura
WorkingDirectory=/home/granaventura/app_ml_extractor

# Load environment variables from .env (KEY=VALUE lines only)
EnvironmentFile=/home/granaventura/app_ml_extractor/.env

# Ensure the virtualenv bin is used
Environment=PATH=/home/granaventura/app_ml_extractor/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin

# Gunicorn executable from the venv
ExecStart=/home/granaventura/app_ml_extractor/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 passenger_wsgi:application

Restart=on-failure
RestartSec=5
TimeoutStopSec=30
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

Enable and start the service
----------------------------
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ml-extractor.service
sudo systemctl status ml-extractor.service -l
```

Basic verification
------------------
- Confirm the service is active and systemd owns the process:

```bash
sudo systemctl status ml-extractor.service -l
sudo journalctl -u ml-extractor.service -n 200 --no-pager -o cat
ss -ltnp | grep -E '127.0.0.1:8000|:8000' || true
curl -sS -D - http://127.0.0.1:8000/ | sed -n '1,40p'
```

Troubleshooting
---------------
- Address already in use: stop any manually started gunicorn processes before starting the systemd service:

```bash
# stop systemd unit (if running)
sudo systemctl stop ml-extractor.service
# kill any leftover manual/nohup gunicorn processes
pkill -f '.venv/bin/gunicorn' || true
# then start systemd unit again
sudo systemctl start ml-extractor.service
```

- If `gunicorn` is missing from the venv, activate the venv and install minimal runtime deps (this will not install heavy numeric packages):

```bash
cd /home/granaventura/app_ml_extractor
source .venv/bin/activate
pip install --upgrade pip
pip install gunicorn Flask PyYAML
```

Make deploy scripts systemd-friendly
-----------------------------------
- If your deploy script currently does a `nohup .venv/bin/gunicorn ...` at the end, remove or comment that line and instead restart the systemd unit as the final step. Example change for `scripts/deploy_to_server.sh`:

```bash
# old: nohup .venv/bin/gunicorn -b 127.0.0.1:8000 passenger_wsgi:application &
# new: sudo systemctl restart ml-extractor.service
```

Log rotation (optional)
-----------------------
If you use a file for gunicorn logs, add a logrotate file, e.g. `/etc/logrotate.d/ml-extractor`:

```
/home/granaventura/app_ml_extractor/gunicorn.log {
    weekly
    rotate 6
    copytruncate
    compress
    missingok
    notifempty
}
```

Security & maintenance
----------------------
- Keep `.env` out of version control. Use `chmod 600 .env` to restrict access.
- If you need the full feature set (pandas/numpy/spacy) on a host that previously raised "Illegal instruction", deploy in a compatible VM/container or build wheels on a compatible machine.

Testing note
------------
The service should be tested by accessing the app locally (curl) and via your reverse proxy / cPanel configuration after wiring the proxy to 127.0.0.1:8000. If you set `USE_FALLBACK=1` the fallback Flask UI will be used on hosts where heavy libraries can't be installed.

-- End
