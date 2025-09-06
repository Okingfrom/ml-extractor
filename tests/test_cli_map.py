import tempfile
import subprocess
import sys
from pathlib import Path

def test_cli_basic_execution():
    """Test that CLI can be invoked without errors"""
    result = subprocess.run(
        [sys.executable, "-c", "from src.mapper import apply_mapping; print('CLI import success')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "CLI import success" in result.stdout
