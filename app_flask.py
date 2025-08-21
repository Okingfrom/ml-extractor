#!/usr/bin/env python3
"""
ML Extractor - Fallback Flask Application
Versión ligera para servidores con limitaciones de dependencias
"""

from flask import Flask, request, render_template_string, jsonify, send_file
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-2025')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear directorio de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Template HTML básico
FALLBACK_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Extractor - Fallback Mode</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .alert { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .alert-info { background-color: #d1ecf1; border-color: #bee5eb; color: #0c5460; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="file"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background-color: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ML Extractor - Fallback Mode</h1>
        <div class="alert alert-info">
            <strong>Modo de compatibilidad activo:</strong> Funcionalidad básica disponible.
            Para características avanzadas, use la nueva aplicación React + FastAPI.
        </div>
    </div>
    
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label for="file">Subir archivo para procesar:</label>
            <input type="file" name="file" id="file" accept=".xlsx,.xls,.csv,.pdf,.docx,.txt" required>
        </div>
        
        <button type="submit" class="btn">Procesar Archivo</button>
    </form>
    
    {% if message %}
    <div class="alert alert-info">
        {{ message }}
    </div>
    {% endif %}
    
    <div style="margin-top: 40px; text-align: center; color: #666;">
        <p>🚀 <strong>¿Busca la funcionalidad completa?</strong></p>
        <p>La nueva aplicación React + FastAPI ofrece:</p>
        <ul style="text-align: left; display: inline-block;">
            <li>Interfaz moderna y responsiva</li>
            <li>Procesamiento IA avanzado</li>
            <li>Mapeo inteligente de campos</li>
            <li>Autenticación y perfiles de usuario</li>
            <li>Analytics y dashboard</li>
        </ul>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """Página principal del fallback"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(FALLBACK_TEMPLATE, message="No se seleccionó ningún archivo")
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(FALLBACK_TEMPLATE, message="No se seleccionó ningún archivo")
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)
            
            return render_template_string(FALLBACK_TEMPLATE, 
                message=f"Archivo '{filename}' recibido correctamente. En modo fallback, el procesamiento avanzado no está disponible. Use la aplicación React + FastAPI para funcionalidad completa.")
    
    return render_template_string(FALLBACK_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "mode": "fallback",
        "message": "ML Extractor fallback mode is running"
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "mode": "fallback",
        "features": {
            "file_upload": True,
            "advanced_processing": False,
            "ai_enhancement": False,
            "user_authentication": False
        },
        "recommendation": "Use React + FastAPI application for full functionality"
    })

if __name__ == '__main__':
    print("🚀 ML Extractor Fallback Mode")
    print("📱 Running at: http://localhost:5000")
    print("🔧 For full functionality, use the React + FastAPI application")
    app.run(debug=True, host='0.0.0.0', port=5000)
