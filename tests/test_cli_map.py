import tempfile
import subprocess
import sys
from pathlib import Path

def test_cli_basic_execution():
    """Test that CLI mapper can be imported without errors"""
    result = subprocess.run(
        ["/workspaces/ml-extractor/.venv/bin/python", "-c", "from src.mapper import apply_mapping; print('CLI import success')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "CLI import success" in result.stdout
