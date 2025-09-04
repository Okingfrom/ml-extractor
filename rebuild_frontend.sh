#!/bin/bash
# Script para rebuildar frontend con puerto correcto

cd ~/repositories/ml-extractor/frontend

# Crear archivo .env con la configuración correcta
echo "REACT_APP_API_BASE_URL=http://localhost:8000" > .env

# Rebuildar el frontend
npm run build

# Copiar al servidor
cp -r dist/* ~/extractorml.uy/frontend/dist/

echo "Frontend rebuilt for port 8000!"
