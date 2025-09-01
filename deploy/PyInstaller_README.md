PyInstaller build notes

Purpose
- Build a single-file executable for the simple backend (`simple_backend.py`) using PyInstaller.

Requirements
- Build on the target OS (Linux build produces Linux binary). For Ubuntu:
  sudo apt update && sudo apt install -y python3 python3-venv python3-pip build-essential

Steps (on build machine)
1) Clone the repo and create a venv
   git clone https://github.com/Okingfrom/ml-extractor.git
   cd ml-extractor
   python3 -m venv .venv
   source .venv/bin/activate

2) Install project deps (ensure uvicorn is present)
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyinstaller uvicorn

3) Run the build script
   bash scripts/build_pyinstaller.sh

4) Result
   The generated binary will be at `dist-pyinstaller/ml_extractor`. Copy that to your server or distribute it.

Notes & caveats
- The simple backend (`simple_backend.py`) intentionally avoids heavy SQLAlchemy deps so the binary is smaller.
- Static frontend files are added to the bundle via `--add-data`; adjust that line if your frontend build path differs.
- If you need to bundle the full backend (`backend/main.py`) instead, ensure all dependencies (SQLAlchemy, decouple, etc.) are present in the venv before building.
- Building on a different OS than the target usually fails (PyInstaller is not cross-compile friendly). Build on the target OS.
- Test the generated binary in a clean environment before distribution.
