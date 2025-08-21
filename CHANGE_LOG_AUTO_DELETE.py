#!/usr/bin/env python3
"""
AUTO-DELETING CHANGE LOG
========================
Created: August 21, 2025
Auto-delete: September 21, 2025 (30 days)

This file tracks changes made to the ml-extractor project during the Flask to React+FastAPI transition.
This file will automatically delete itself when no longer needed or after one month.

IMPORTANT: This file is set to self-destruct after 30 days or when changes are no longer relevant.
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Auto-delete configuration
CREATION_DATE = datetime(2025, 8, 21)
AUTO_DELETE_DATE = CREATION_DATE + timedelta(days=30)  # September 21, 2025

def check_auto_delete():
    """Check if this file should auto-delete itself"""
    current_date = datetime.now()
    if current_date >= AUTO_DELETE_DATE:
        print(f"[AUTO-DELETE] Change log expired on {AUTO_DELETE_DATE.strftime('%Y-%m-%d')}")
        try:
            os.remove(__file__)
            print(f"[AUTO-DELETE] Successfully deleted {__file__}")
        except Exception as e:
            print(f"[AUTO-DELETE] Failed to delete {__file__}: {e}")
        return True
    else:
        days_remaining = (AUTO_DELETE_DATE - current_date).days
        print(f"[AUTO-DELETE] {days_remaining} days remaining until auto-delete")
        return False

# Check for auto-delete on import/execution
if __name__ == "__main__":
    if check_auto_delete():
        sys.exit(0)

# CHANGE LOG ENTRIES
# ==================

CHANGES_LOG = {
    "2025-08-21": {
        "timestamp": "2025-08-21 16:30:00",
        "action": "package.json_modifications",
        "description": "Updated frontend/package.json during Flask to React+FastAPI transition",
        "files_affected": ["frontend/package.json"],
        "changes": {
            "package.json": {
                "before_state": "Basic React configuration",
                "after_state": "Enhanced with Tailwind CSS, custom PORT, and complete dependencies",
                "key_modifications": [
                    "Added PORT=3001 to start script",
                    "Added @tailwindcss/forms and @tailwindcss/typography dependencies", 
                    "Added complete dev dependencies (autoprefixer, postcss, tailwindcss)",
                    "Added proxy configuration pointing to http://localhost:8000",
                    "Added lint and format scripts",
                    "Updated package name to 'ml-extractor-frontend'",
                    "Added description field"
                ],
                "final_content": {
                    "name": "ml-extractor-frontend",
                    "version": "1.0.0",
                    "private": True,
                    "description": "ML Extractor Frontend - React + Tailwind CSS",
                    "scripts": {
                        "start": "set PORT=3001 && react-scripts start",
                        "build": "react-scripts build",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject",
                        "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
                        "lint:fix": "eslint src --ext .js,.jsx,.ts,.tsx --fix",
                        "format": "prettier --write 'src/**/*.{js,jsx,ts,tsx,json,css,md}'"
                    },
                    "dependencies": [
                        "@tailwindcss/forms@^0.5.10",
                        "@tailwindcss/typography@^0.5.16",
                        "@testing-library/jest-dom@^5.17.0",
                        "@testing-library/react@^13.4.0", 
                        "@testing-library/user-event@^14.5.2",
                        "axios@^1.6.0",
                        "clsx@^2.0.0",
                        "lucide-react@^0.290.0",
                        "react@^18.2.0",
                        "react-dom@^18.2.0",
                        "react-dropzone@^14.2.3",
                        "react-hot-toast@^2.4.1",
                        "react-router-dom@^6.8.0",
                        "react-scripts@5.0.1",
                        "web-vitals@^2.1.4"
                    ],
                    "devDependencies": [
                        "@types/react@^18.2.42",
                        "@types/react-dom@^18.2.17",
                        "autoprefixer@^10.4.16",
                        "eslint@^8.55.0",
                        "postcss@^8.4.32",
                        "prettier@^3.1.0",
                        "tailwindcss@^3.3.6"
                    ],
                    "proxy": "http://localhost:8000"
                }
            }
        },
        "context": "Final phase of Flask to React+FastAPI transition",
        "impact": "Enables full React frontend functionality with Tailwind CSS and proper development environment",
        "next_steps": "Frontend-backend integration testing"
    }
}

# Recovery information
RECOVERY_INFO = {
    "purpose": "Track manual changes during architecture transition",
    "backup_location": "Changes are tracked in this file only",
    "rollback_instructions": "Use git history or recreate package.json with basic React template",
    "related_files": [
        "frontend/package.json",
        "frontend/tailwind.config.js", 
        "frontend/postcss.config.js",
        "backend/dev_server.py"
    ]
}

def print_change_summary():
    """Print a summary of all tracked changes"""
    print("=" * 60)
    print("ML-EXTRACTOR CHANGE LOG SUMMARY")
    print("=" * 60)
    print(f"Created: {CREATION_DATE.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Auto-delete: {AUTO_DELETE_DATE.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for date, change in CHANGES_LOG.items():
        print(f"DATE: {date}")
        print(f"ACTION: {change['action']}")
        print(f"DESCRIPTION: {change['description']}")
        print(f"FILES: {', '.join(change['files_affected'])}")
        print(f"IMPACT: {change['impact']}")
        print("-" * 40)

def get_package_json_backup():
    """Return the current package.json content as backup"""
    return CHANGES_LOG["2025-08-21"]["changes"]["package.json"]["final_content"]

if __name__ == "__main__":
    print_change_summary()
    print(f"\nDays until auto-delete: {(AUTO_DELETE_DATE - datetime.now()).days}")
    print("\nTo manually delete this file when no longer needed:")
    print(f"rm {__file__}")
