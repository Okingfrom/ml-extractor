#!/bin/bash
# Touch tmp/restart.txt to signal Passenger to restart the app
set -euo pipefail
APP_ROOT="$HOME/repositories/ml-extractor"
cd "$APP_ROOT"
mkdir -p tmp
touch tmp/restart.txt
sleep 2
echo "Signaled Passenger restart by touching tmp/restart.txt in $APP_ROOT"
