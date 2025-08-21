#!/bin/bash

# Force restart ML Extractor service with clear cache

echo "🔧 Stopping ML Extractor service..."
sudo systemctl stop ml-extractor.service

echo "🔄 Killing any remaining gunicorn processes..."
sudo pkill -f gunicorn

echo "📁 Updating files..."
cp "/home/granaventura/Desktop/ML EXTRACTOR/passenger_wsgi.py" "/home/granaventura/app_ml_extractor/passenger_wsgi.py"
cp "/home/granaventura/Desktop/ML EXTRACTOR/app_improved.py" "/home/granaventura/app_ml_extractor/app_improved.py"
cp "/home/granaventura/Desktop/ML EXTRACTOR/auth_system.py" "/home/granaventura/app_ml_extractor/auth_system.py"

echo "🔧 Setting environment..."
echo "USE_IMPROVED=1" > /home/granaventura/app_ml_extractor/.env

echo "🚀 Starting ML Extractor service..."
sudo systemctl start ml-extractor.service

echo "⏳ Waiting for service to start..."
sleep 3

echo "✅ Service status:"
sudo systemctl status ml-extractor.service --no-pager -l

echo "🌐 Testing service..."
curl -s -I http://127.0.0.1:8000

echo "✅ ML Extractor restarted successfully!"
