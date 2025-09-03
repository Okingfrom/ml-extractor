#!/usr/bin/env bash
# Quick integration test script for the deployed site
# - checks site root
# - checks /api/health
# - attempts a login to /api/login using sample credentials

SITE="https://extractorml.uy"
PROXY_LOCAL="http://127.0.0.1:8000"

echo "Checking site root: $SITE/"
curl -I -sS "$SITE/" | sed -n '1,120p'

echo "\nChecking API health via external URL: $SITE/api/health"
curl -sS "$SITE/api/health" || true

echo "\nChecking API health via local proxy: $PROXY_LOCAL/api/health (may fail if proxy is not running)"
curl -sS "$PROXY_LOCAL/api/health" || true

echo "\nAttempting test login (POST) to $SITE/api/auth/login"
# Use a sample/demo credential that matches frontend/test logs. Adjust if you have different test credentials.
curl -sS -X POST "$SITE/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"test@test.com","password":"123456"}' || true

echo "\nDone. If login returns a token (JSON), the webapp login flow is functional."
