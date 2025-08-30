#!/usr/bin/env python3
"""
Pre-deployment checker for ML Extractor
Verifies that all files and configurations are ready for cPanel deployment
"""

import os
import sys
import json
import importlib.util
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ Missing {description}: {filepath}")
        return False

def check_python_syntax(filepath):
    """Check if Python file has valid syntax"""
    try:
        spec = importlib.util.spec_from_file_location("module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ Python syntax valid: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Python syntax error in {filepath}: {e}")
        return False

def check_frontend_build():
    """Check if frontend build exists and is complete"""
    build_dir = "frontend/build"
    if not os.path.exists(build_dir):
        print(f"❌ Frontend build not found. Run 'npm run build' in frontend/")
        return False
    
    required_files = [
        "frontend/build/index.html",
        "frontend/build/static",
        "frontend/build/manifest.json"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ Frontend build file: {file}")
        else:
            print(f"❌ Missing frontend build file: {file}")
            all_exist = False
    
    return all_exist

def check_env_files():
    """Check environment configuration files"""
    env_files = [
        "frontend/.env.production",
        "frontend/.env.development"
    ]
    
    all_exist = True
    for file in env_files:
        if os.path.exists(file):
            print(f"✅ Environment file: {file}")
        else:
            print(f"❌ Missing environment file: {file}")
            all_exist = False
    
    return all_exist

def main():
    print("🔍 ML Extractor Pre-Deployment Check\n")
    
    # Check core backend files
    backend_files = [
        ("simple_backend.py", "Main backend application"),
        ("passenger_wsgi.py", "cPanel WSGI entry point"),
        ("requirements_production.txt", "Production requirements"),
        ("config/mapping.yaml", "Mapping configuration")
    ]
    
    backend_ok = True
    for filepath, desc in backend_files:
        if not check_file_exists(filepath, desc):
            backend_ok = False
    
    # Check Python syntax
    python_files = ["simple_backend.py", "passenger_wsgi.py"]
    syntax_ok = True
    for filepath in python_files:
        if os.path.exists(filepath):
            if not check_python_syntax(filepath):
                syntax_ok = False
    
    # Check frontend build
    frontend_ok = check_frontend_build()
    
    # Check environment files
    env_ok = check_env_files()
    
    # Check deployment guide
    guide_ok = check_file_exists("DEPLOY_CPANEL.md", "Deployment guide")
    
    print("\n" + "="*50)
    print("📋 DEPLOYMENT READINESS SUMMARY")
    print("="*50)
    
    if backend_ok:
        print("✅ Backend files: Ready")
    else:
        print("❌ Backend files: Missing files")
    
    if syntax_ok:
        print("✅ Python syntax: Valid")
    else:
        print("❌ Python syntax: Errors found")
    
    if frontend_ok:
        print("✅ Frontend build: Ready")
    else:
        print("❌ Frontend build: Not ready")
    
    if env_ok:
        print("✅ Environment config: Ready")
    else:
        print("❌ Environment config: Missing files")
    
    if guide_ok:
        print("✅ Deployment guide: Available")
    else:
        print("❌ Deployment guide: Missing")
    
    overall_ready = backend_ok and syntax_ok and frontend_ok and env_ok and guide_ok
    
    print("\n" + "="*50)
    if overall_ready:
        print("🚀 READY FOR DEPLOYMENT!")
        print("📖 Follow the instructions in DEPLOY_CPANEL.md")
    else:
        print("⚠️  NOT READY - Fix the issues above first")
    print("="*50)
    
    return 0 if overall_ready else 1

if __name__ == "__main__":
    sys.exit(main())
