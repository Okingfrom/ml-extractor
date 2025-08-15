#!/usr/bin/env python3
"""
Aplicación Flask mejorada para mapeo de productos a Mercado Libre
Mantiene la estructura exacta de ML y permite mapeo selectivo
CON INTELIGENCIA ARTIFICIAL para autocompletar datos faltantes
"""

from flask import Flask, request, render_template_string, send_file, redirect, url_for, jsonify
import openpyxl
from openpyxl.cell import MergedCell
import csv
import docx
import PyPDF2
import yaml
import os
import tempfile
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# 🔧 FUNCIÓN HELPER PARA MANEJO SEGURO DE CELDAS
def safe_get_cell_value(sheet, row, col):
    """Obtiene el valor de una celda manejando MergedCell de forma segura"""
    try:
        cell = sheet.cell(row=row, column=col)
        if isinstance(cell, MergedCell):
            # Buscar el valor en la celda principal del rango fusionado
            for merged_range in sheet.merged_cells.ranges:
                if cell.coordinate in merged_range:
                    top_left = sheet.cell(merged_range.min_row, merged_range.min_col)
                    return top_left.value
            return None
        else:
            return cell.value
    except Exception as e:
        print(f"⚠️ Error accediendo celda ({row},{col}): {e}")
        return None

def safe_set_cell_value(sheet, row, col, value):
    """Establece el valor de una celda manejando MergedCell de forma segura"""
    try:
        cell = sheet.cell(row=row, column=col)
        if isinstance(cell, MergedCell):
            # Para celdas fusionadas, escribir en la celda principal
            for merged_range in sheet.merged_cells.ranges:
                if cell.coordinate in merged_range:
                    top_left = sheet.cell(merged_range.min_row, merged_range.min_col)
                    top_left.value = value
                    return True
            # Si no encontramos el rango, intentar escribir directamente
            safe_set_cell_value(sheet, row, col, value)
            return True
        else:
            cell.value = value
            return True
    except Exception as e:
        print(f"⚠️ Error escribiendo celda ({row},{col}): {e}")
        return False
from werkzeug.utils import secure_filename
import shutil
from ai_enhancer import AIProductEnhancer, AI_CONFIG

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar AI enhancer con la API key del entorno
ai_enhancer = AIProductEnhancer(
    provider=os.getenv('AI_PROVIDER', 'groq'),
    api_key=os.getenv('GROQ_API_KEY')
)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ML Bulk Mapper Pro</title>
    <style>
        body { 
            font-family: 'Proxima Nova', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
            background: linear-gradient(135deg, #fff159 0%, #ffca28 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #3483fa;
        }
        .ml-logo {
            background: linear-gradient(135deg, #3483fa, #2968c8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        .ai-badge {
            background: linear-gradient(135deg, #00a650, #00c457);
            color: white;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
            margin-left: 8px;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #333;
            font-size: 14px;
        }
        input[type="file"], input[type="text"], input[type="password"], select { 
            width: 100%; 
            padding: 12px 16px; 
            border: 2px solid #e6e6e6;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: #fafafa;
        }
        input[type="file"]:focus, input[type="text"]:focus, input[type="password"]:focus, select:focus {
            border-color: #3483fa;
            outline: none;
            background: white;
            box-shadow: 0 0 8px rgba(52, 131, 250, 0.2);
        }
        button { 
            background: linear-gradient(135deg, #3483fa, #2968c8);
            color: white; 
            padding: 16px 32px; 
            border: none; 
            cursor: pointer;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            width: 100%;
        }
        button:hover { 
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(52, 131, 250, 0.3);
        }
        .success { 
            color: #00a650; 
            background: linear-gradient(135deg, #e8f5e8, #d4f4d4);
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #00a650;
        }
        .error { 
            color: #ff3333; 
            background: linear-gradient(135deg, #ffe6e6, #ffcccc);
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #ff3333;
        }
        .ai-section {
            background: linear-gradient(135deg, #f8fffe, #f0f9ff);
            padding: 24px;
            border-radius: 8px;
            margin: 24px 0;
            border: 2px solid #3483fa;
        }
        .mapping-section {
            background: #fafafa;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border: 1px solid #e6e6e6;
        }
        .manual-config-section {
            background: linear-gradient(135deg, #fff8e1, #fff3c4);
            padding: 24px;
            border-radius: 8px;
            margin: 24px 0;
            border: 2px solid #ff9800;
        }
        .manual-config-section h3 {
            color: #f57c00;
            margin-bottom: 16px;
        }
        .manual-config-section textarea {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            resize: vertical;
        }
        .manual-config-section input[type="radio"] {
            width: auto;
            margin-right: 8px;
            accent-color: #ff9800;
        }
        .manual-config-section label {
            font-weight: 500;
        }
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e6e6e6;
            transition: all 0.2s ease;
        }
        .checkbox-item:hover {
            border-color: #3483fa;
            box-shadow: 0 2px 8px rgba(52, 131, 250, 0.1);
        }
        .checkbox-item input[type="checkbox"] {
            width: auto;
            margin-right: 12px;
            transform: scale(1.1);
            accent-color: #3483fa;
        }
        .required { color: #ff3333; font-weight: 600; }
        .optional { color: #666; }
        .ai-enhanced { color: #00a650; font-weight: 600; }
        .info-text {
            background: linear-gradient(135deg, #e3f2fd, #e1f5fe);
            padding: 18px;
            border-radius: 6px;
            margin: 16px 0;
            border-left: 4px solid #3483fa;
            color: #1565c0;
        }
        .ai-info {
            background: linear-gradient(135deg, #e8f5e8, #f1f8e9);
            padding: 16px;
            border-radius: 6px;
            margin: 12px 0;
            border-left: 4px solid #00a650;
            color: #2e7d32;
        }
        h1 { color: #3483fa; font-weight: 700; margin-bottom: 8px; }
        h3 { color: #333; margin-top: 28px; font-weight: 600; }
        .api-selector {
            background: white;
            padding: 16px;
            border-radius: 6px;
            border: 2px solid #e6e6e6;
            margin: 12px 0;
        }
        .api-option {
            margin: 10px 0;
            padding: 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        .api-option:hover {
            background: #f5f5f5;
        }
        .api-option input[type="radio"] {
            margin-right: 12px;
            accent-color: #3483fa;
        }
        .cost-badge {
            background: #00a650;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: 600;
            margin-left: 6px;
        }
        .quality-stars {
            color: #ffb400;
            margin-left: 6px;
            font-size: 12px;
        }
        .debug-section {
            background: #2d2d2d;
            color: #00ff41;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            border: 2px solid #555;
        }
        .debug-title {
            color: #00ff41;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .creator-signature {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: linear-gradient(135deg, #f5f5f5, #eeeeee);
            border-radius: 6px;
            color: #666;
            font-size: 14px;
        }
        .creator-name {
            color: #3483fa;
            font-weight: 600;
        }
        
        /* 🎬 NUEVA SECCIÓN: LOADING SCREEN CREATIVO */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 90%;
        }
        .loading-logo {
            font-size: 32px;
            background: linear-gradient(135deg, #3483fa, #2968c8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .progress-container {
            background: #f0f0f0;
            border-radius: 25px;
            padding: 4px;
            margin: 20px 0;
        }
        .progress-bar {
            background: linear-gradient(135deg, #3483fa, #00a650);
            border-radius: 20px;
            height: 30px;
            width: 0%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }
        .loading-steps {
            text-align: left;
            margin: 20px 0;
        }
        .loading-step {
            display: flex;
            align-items: center;
            padding: 8px 0;
            color: #666;
            transition: all 0.3s ease;
        }
        .loading-step.active {
            color: #3483fa;
            font-weight: 600;
        }
        .loading-step.completed {
            color: #00a650;
        }
        .loading-step-icon {
            margin-right: 12px;
            font-size: 18px;
        }
        .ml-animation {
            display: inline-block;
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
        small { color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="ml-logo">ML Bulk Mapper Pro <span class="ai-badge">AI POWERED</span></h1>
            <p style="color: #666; margin: 0;">Herramienta profesional para carga masiva en Mercado Libre</p>
        </div>
        
        <div class="info-text">
            <strong>Funcionalidades principales:</strong><br>
            • Mantiene estructura exacta de plantillas ML<br>
            • Autocompletado inteligente con IA<br>
            • Mapeo flexible de datos de productos<br>
            • Generación automática de códigos EAN-13
        </div>
        
        {% if message %}
            <div class="{{ message_type }}">{{ message }}</div>
        {% endif %}
        
        {% if debug_info %}
            <div class="debug-section">
                <div class="debug-title">DEBUG LOG:</div>
                <pre>{{ debug_info }}</pre>
            </div>
        {% endif %}
        
        <form method="post" enctype="multipart/form-data">
            
            <!-- SECCIÓN IA -->
            <div class="ai-section">
                <h3>Configuración de Inteligencia Artificial</h3>
                
                <div class="ai-info">
                    <strong>La IA ayuda a completar automáticamente:</strong> códigos universales, marcas, modelos, descripciones y características técnicas que falten en tus datos.
                </div>
                
                <div class="form-group">
                    <label>Selecciona tu proveedor de IA:</label>
                    <div class="api-selector">
                        <div class="api-option">
                            <input type="radio" name="ai_provider" value="groq" id="groq" checked>
                            <label for="groq">
                                <strong>Groq</strong> <span class="cost-badge">GRATIS</span>
                                <span class="quality-stars">★★★★★</span><br>
                                <small>Rápido y gratuito. Recomendado para empezar.</small>
                            </label>
                        </div>
                        
                        <div class="api-option">
                            <input type="radio" name="ai_provider" value="deepseek" id="deepseek">
                            <label for="deepseek">
                                <strong>DeepSeek</strong> <span class="cost-badge">$0.14/1M</span>
                                <span class="quality-stars">★★★★★</span><br>
                                <small>Muy económico y excelente calidad.</small>
                            </label>
                        </div>
                        
                        <div class="api-option">
                            <input type="radio" name="ai_provider" value="manual" id="manual">
                            <label for="manual">
                                <strong>Modo Manual</strong> <span class="cost-badge">SIN IA</span><br>
                                <small>Valores por defecto sin usar IA.</small>
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="form-group" id="api_key_section">
                    <label for="ai_api_key">API Key (requerida para Groq/DeepSeek):</label>
                    <input type="password" name="ai_api_key" id="ai_api_key" placeholder="Ingresa tu API key aquí">
                    <small>Para Groq: Regístrate gratis en <a href="https://groq.com" target="_blank" style="color: #3483fa;">groq.com</a></small>
                </div>
                
                <div class="form-group">
                    <label>Campos que la IA debe completar automáticamente:</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="codigo_universal" id="ai_codigo" checked>
                            <label for="ai_codigo"><span class="ai-enhanced">Código Universal EAN-13</span></label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="marca" id="ai_marca" checked>
                            <label for="ai_marca"><span class="ai-enhanced">Marca</span> (si no está en datos)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="modelo" id="ai_modelo" checked>
                            <label for="ai_modelo"><span class="ai-enhanced">Modelo</span> (si no está en datos)</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="descripcion" id="ai_desc">
                            <label for="ai_desc"><span class="ai-enhanced">Descripción atractiva</span></label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="peso" id="ai_peso">
                            <label for="ai_peso"><span class="ai-enhanced">Peso estimado</span></label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="ai_fields" value="color" id="ai_color">
                            <label for="ai_color"><span class="ai-enhanced">Color inferido</span></label>
                        </div>
                    </div>
                </div>
            </div>
            
            <h3>Archivos</h3>
            
            <div class="form-group">
                <label for="template">Plantilla de Mercado Libre (.xlsx):</label>
                <input type="file" name="template" accept=".xlsx" required>
                <small>Sube la plantilla oficial descargada de Mercado Libre</small>
            </div>
            
            <div class="form-group">
                <label for="content">Datos de Productos:</label>
                <input type="file" name="content" accept=".xlsx,.xls,.csv,.pdf,.docx,.txt" required>
                <small>Recomendado: Excel o CSV para mejor mapeo</small>
            </div>
            
            <h3>Configuración de Mapeo</h3>
            
            <div class="mapping-section">
                <label>Selecciona los campos que quieres mapear desde tus datos:</label>
                
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="titulo" id="titulo" checked>
                        <label for="titulo"><span class="required">Título</span> (Nombre del producto)</label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="precio" id="precio" checked>
                        <label for="precio"><span class="required">Precio</span></label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="stock" id="stock" checked>
                        <label for="stock"><span class="required">Stock</span></label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="sku" id="sku" checked>
                        <label for="sku"><span class="optional">SKU</span></label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="descripcion" id="descripcion">
                        <label for="descripcion"><span class="optional">Descripción</span> (existente en datos)</label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="marca" id="marca_existing">
                        <label for="marca_existing"><span class="required">Marca</span> (existente en datos)</label>
                    </div>
                    
                    <div class="checkbox-item">
                        <input type="checkbox" name="map_fields" value="modelo" id="modelo_existing">
                        <label for="modelo_existing"><span class="required">Modelo</span> (existente en datos)</label>
                    </div>
                </div>
            </div>
            
            <h3>Valores por Defecto</h3>
            
            <div class="form-group">
                <label for="condicion">Condición del producto:</label>
                <select name="condicion">
                    <option value="Nuevo" selected>Nuevo</option>
                    <option value="Usado">Usado</option>
                    <option value="Reacondicionado">Reacondicionado</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="moneda">Moneda:</label>
                <select name="moneda">
                    <option value="$" selected>$ (Peso Uruguayo)</option>
                    <option value="USD">USD (Dólar)</option>
                </select>
            </div>
            
            <!-- NUEVA SECCIÓN: CONFIGURACIÓN MANUAL MASIVA -->
            <div class="manual-config-section">
                <h3>⚙️ Configuración Manual Masiva</h3>
                <div class="info-text">
                    <strong>Configura valores que se aplicarán a todos los productos o selectivamente por número de fila.</strong><br>
                    💡 <em>Perfecto para tiendas que manejan valores estándar en todos sus productos.</em>
                </div>
                
                <!-- Stock Masivo -->
                <div class="form-group">
                    <label>📦 Stock:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="stock_global">Stock para todos los productos:</label>
                            <input type="number" name="stock_global" id="stock_global" placeholder="ej: 100" min="0">
                            <small>Aplicará a todos los productos detectados</small>
                        </div>
                        <div>
                            <label for="stock_selective">Stock selectivo (Fila#:Cantidad):</label>
                            <textarea name="stock_selective" id="stock_selective" rows="3" placeholder="ej: 8:50, 10:70, 12:25"></textarea>
                            <small>Formato: Fila_Excel:Stock (separados por comas)</small>
                        </div>
                    </div>
                </div>
                
                <!-- Marca y Modelo -->
                <div class="form-group">
                    <label>🏷️ Marca y Modelo:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="marca_global">Marca para todos:</label>
                            <input type="text" name="marca_global" id="marca_global" placeholder="ej: Samsung, Apple, Sony">
                            <small>Se aplicará a todos los productos</small>
                        </div>
                        <div>
                            <label for="modelo_global">Modelo para todos:</label>
                            <input type="text" name="modelo_global" id="modelo_global" placeholder="ej: Pro Max, Standard">
                            <small>Se aplicará a todos los productos</small>
                        </div>
                    </div>
                    <div style="margin-top: 12px;">
                        <label for="marca_modelo_selective">Excepciones selectivas (Fila#:Marca:Modelo):</label>
                        <textarea name="marca_modelo_selective" id="marca_modelo_selective" rows="2" placeholder="ej: 8:iPhone:14 Pro, 10:Samsung:Galaxy S24"></textarea>
                        <small>Formato: Fila_Excel:Marca:Modelo (separados por comas)</small>
                    </div>
                </div>
                
                <!-- Retiro en Persona -->
                <div class="form-group">
                    <label>🏪 Retiro en Persona:</label>
                    <div style="display: flex; gap: 20px; align-items: center;">
                        <label><input type="radio" name="retiro_persona" value="Acepto"> ✅ Acepto (todos los productos)</label>
                        <label><input type="radio" name="retiro_persona" value="No acepto"> ❌ No acepto (todos los productos)</label>
                        <label><input type="radio" name="retiro_persona" value="" checked> Sin configurar</label>
                    </div>
                </div>
                
                <!-- NUEVA SECCIÓN: FORMAS DE ENVÍO -->
                <div class="form-group">
                    <label>🚚 Formas de Envío:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="forma_envio_global">Forma de envío para todos:</label>
                            <select name="forma_envio_global" id="forma_envio_global">
                                <option value="">Sin configurar</option>
                                <option value="Mercado Envíos">🚚 Mercado Envíos</option>
                                <option value="Mercado Envíos + Mercado Envíos Flex">🚚⚡ Mercado Envíos + Mercado Envíos Flex</option>
                                <option value="Acordar con el vendedor">🤝 Acordar con el vendedor</option>
                            </select>
                            <small>Aplica a todos los productos</small>
                        </div>
                        <div>
                            <label for="forma_envio_selective">Excepciones selectivas:</label>
                            <textarea name="forma_envio_selective" id="forma_envio_selective" rows="2" placeholder="ej: 8:Mercado Envíos, 10:Mercado Envíos + Mercado Envíos Flex"></textarea>
                            <small>Formato: Fila_Excel:Forma_Envío</small>
                        </div>
                    </div>
                </div>
                
                <!-- NUEVA SECCIÓN: COSTO DE ENVÍO -->
                <div class="form-group">
                    <label>💰 Costo de Envío:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="costo_envio_global">Costo para todos los productos:</label>
                            <select name="costo_envio_global" id="costo_envio_global">
                                <option value="">Sin configurar</option>
                                <option value="A cargo del comprador">💳 A cargo del comprador</option>
                                <option value="Envío gratis">🆓 Envío gratis</option>
                            </select>
                            <small>Política de costo de envío general</small>
                        </div>
                        <div>
                            <label for="costo_envio_selective">Excepciones por fila:</label>
                            <textarea name="costo_envio_selective" id="costo_envio_selective" rows="2" placeholder="ej: 8:Envío gratis, 10:A cargo del comprador"></textarea>
                            <small>Formato: Fila_Excel:Tipo_Costo</small>
                        </div>
                    </div>
                </div>
                
                <!-- NUEVA SECCIÓN: VARIACIONES POR COLOR -->
                <div class="form-group">
                    <label>🎨 Variaciones por Color:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="color_global">Color base para todos:</label>
                            <select name="color_global" id="color_global">
                                <option value="">Sin configurar</option>
                                <option value="Negro">⚫ Negro</option>
                                <option value="Blanco">⚪ Blanco</option>
                                <option value="Azul">🔵 Azul</option>
                                <option value="Rojo">🔴 Rojo</option>
                                <option value="Verde">🟢 Verde</option>
                                <option value="Amarillo">🟡 Amarillo</option>
                                <option value="Rosa">🩷 Rosa</option>
                                <option value="Gris">⬜ Gris</option>
                                <option value="Marrón">🟤 Marrón</option>
                                <option value="Multicolor">🌈 Multicolor</option>
                                <option value="Transparente">💎 Transparente</option>
                            </select>
                        </div>
                        <div>
                            <label for="color_comercial_global">Nombre comercial del color:</label>
                            <input type="text" name="color_comercial_global" id="color_comercial_global" placeholder="ej: Azul Marino, Rojo Cereza">
                            <small>Nombre específico o comercial del color</small>
                        </div>
                    </div>
                    <div style="margin-top: 12px;">
                        <label for="color_selective">Colores selectivos (Fila#:Color:Nombre_Comercial):</label>
                        <textarea name="color_selective" id="color_selective" rows="2" placeholder="ej: 8:Azul:Azul Marino, 10:Rojo:Rojo Cereza"></textarea>
                        <small>Formato: Fila_Excel:Color_Base:Nombre_Comercial (separados por comas)</small>
                    </div>
                </div>
                
                <!-- Garantía -->
                <div class="form-group">
                    <label>🛡️ Garantía:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="tipo_garantia">Tipo de garantía:</label>
                            <select name="tipo_garantia" id="tipo_garantia">
                                <option value="">Sin configurar</option>
                                <option value="Garantía del vendedor">Garantía del vendedor</option>
                                <option value="Garantía de fábrica">Garantía de fábrica</option>
                                <option value="Sin garantía">Sin garantía</option>
                            </select>
                        </div>
                        <div>
                            <label for="tiempo_garantia">Tiempo garantía:</label>
                            <input type="number" name="tiempo_garantia" id="tiempo_garantia" placeholder="ej: 12" min="0">
                        </div>
                        <div>
                            <label for="unidad_garantia">Unidad de tiempo:</label>
                            <select name="unidad_garantia" id="unidad_garantia">
                                <option value="">Seleccionar</option>
                                <option value="días">Días</option>
                                <option value="meses" selected>Meses</option>
                                <option value="años">Años</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- Códigos Universales -->
                <div class="form-group">
                    <label>🔢 Códigos Universales:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="codigo_universal_masivo">Código base para todos:</label>
                            <input type="text" name="codigo_universal_masivo" id="codigo_universal_masivo" placeholder="ej: PROD, SKU, UPC">
                            <small>Se aplicará como base a todos los productos</small>
                        </div>
                        <div>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" name="codigo_universal_secuencial" id="codigo_universal_secuencial">
                                Agregar numeración secuencial
                            </label>
                            <input type="number" name="codigo_universal_offset" id="codigo_universal_offset" placeholder="Empezar en (ej: 1001)" min="1" style="margin-top: 8px;">
                            <small>Ej: PROD0001, PROD0002, PROD0003...</small>
                        </div>
                    </div>
                    <div style="margin-top: 12px;">
                        <label for="codigo_universal_selective">Códigos específicos (Fila#:Código):</label>
                        <textarea name="codigo_universal_selective" id="codigo_universal_selective" rows="2" placeholder="ej: 8:UPC123456, 10:EAN987654, 12:CODE555"></textarea>
                        <small>Formato: Fila_Excel:Código_Específico (separados por comas)</small>
                    </div>
                </div>
                
                <!-- Catálogo -->
                <div class="form-group">
                    <label>📚 Catálogo:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                        <div>
                            <label for="tiene_catalogo">¿Los productos tienen catálogo?</label>
                            <select name="tiene_catalogo" id="tiene_catalogo">
                                <option value="">Sin configurar</option>
                                <option value="Si">Sí, tienen catálogo</option>
                                <option value="No">No tienen catálogo</option>
                            </select>
                        </div>
                        <div>
                            <label for="numero_catalogo_selective">Números de catálogo selectivos:</label>
                            <textarea name="numero_catalogo_selective" id="numero_catalogo_selective" rows="2" placeholder="ej: 8:CAT001, 10:CAT002, 12:CAT003"></textarea>
                            <small>Formato: Fila_Excel:Código_Catálogo</small>
                        </div>
                    </div>
                </div>
                
                <!-- Descripción Global -->
                <div class="form-group">
                    <label>📝 Descripción Global de la Tienda:</label>
                    <textarea name="descripcion_global" id="descripcion_global" rows="4" placeholder="ej: 🕒 Horario: Lunes a Viernes 9-18h | 📍 Ubicación: Centro de Montevideo | 📞 WhatsApp: 099123456 | ✅ Envíos a todo el país"></textarea>
                    <small>Esta información se agregará al final de cada descripción de producto. Usa emojis para mejor visualización.</small>
                </div>
                
                <!-- Gestión de Fotos - Coming Soon -->
                <div class="form-group" style="background: linear-gradient(135deg, #f5f5f5, #e8e8e8); padding: 16px; border-radius: 6px; border: 2px dashed #ccc;">
                    <label>📸 Gestión Automática de Fotos:</label>
                    <div style="text-align: center; color: #666; padding: 20px;">
                        <h4 style="color: #999;">🚧 COMING SOON 🚧</h4>
                        <p>Próximamente podrás conectar tu cuenta de ML para obtener automáticamente las URLs de las fotos de tus productos.</p>
                        <small>Esta funcionalidad estará disponible en futuras actualizaciones.</small>
                    </div>
                </div>
            </div>
            
            <button type="submit">Procesar y Generar Archivo ML</button>
        </form>
        
        <!-- 🎬 PANTALLA DE CARGA CREATIVA -->
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-container">
                <div class="loading-logo">
                    <span class="ml-animation">🚀</span> ML Bulk Mapper Pro
                </div>
                <div class="progress-container">
                    <div class="progress-bar" id="progressBar">0%</div>
                </div>
                <div class="loading-steps" id="loadingSteps">
                    <div class="loading-step" id="step1">
                        <span class="loading-step-icon">📁</span>
                        <span>Cargando archivos...</span>
                    </div>
                    <div class="loading-step" id="step2">
                        <span class="loading-step-icon">🔍</span>
                        <span>Analizando estructura de datos...</span>
                    </div>
                    <div class="loading-step" id="step3">
                        <span class="loading-step-icon">🧠</span>
                        <span>Procesando con IA...</span>
                    </div>
                    <div class="loading-step" id="step4">
                        <span class="loading-step-icon">🔧</span>
                        <span>Aplicando configuración manual...</span>
                    </div>
                    <div class="loading-step" id="step5">
                        <span class="loading-step-icon">📊</span>
                        <span>Generando archivo ML...</span>
                    </div>
                    <div class="loading-step" id="step6">
                        <span class="loading-step-icon">✅</span>
                        <span>¡Completado!</span>
                    </div>
                </div>
                <p style="color: #666; font-size: 14px; margin-top: 20px;">
                    ⏱️ Este proceso puede tomar entre 10-30 segundos dependiendo del tamaño de tu archivo
                </p>
            </div>
        </div>
        
        <script>
        // 🎬 SISTEMA DE CARGA CREATIVO
        document.querySelector('form').addEventListener('submit', function(e) {
            const templateFile = document.querySelector('input[name="template"]').files[0];
            const contentFile = document.querySelector('input[name="content"]').files[0];
            
            if (!templateFile || !contentFile) {
                e.preventDefault();
                alert('Por favor selecciona ambos archivos antes de continuar.');
                return;
            }
            
            // Mostrar pantalla de carga
            showLoadingScreen();
        });
        
        function showLoadingScreen() {
            const overlay = document.getElementById('loadingOverlay');
            const progressBar = document.getElementById('progressBar');
            const steps = ['step1', 'step2', 'step3', 'step4', 'step5', 'step6'];
            
            overlay.style.display = 'flex';
            
            let currentStep = 0;
            let progress = 0;
            
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15 + 5; // Progreso variable
                
                if (progress > 100) progress = 100;
                
                progressBar.style.width = progress + '%';
                progressBar.textContent = Math.round(progress) + '%';
                
                // Activar pasos
                if (progress > 10 && currentStep < 1) {
                    activateStep(steps[currentStep]);
                    currentStep++;
                }
                if (progress > 25 && currentStep < 2) {
                    completeStep(steps[currentStep - 1]);
                    activateStep(steps[currentStep]);
                    currentStep++;
                }
                if (progress > 45 && currentStep < 3) {
                    completeStep(steps[currentStep - 1]);
                    activateStep(steps[currentStep]);
                    currentStep++;
                }
                if (progress > 65 && currentStep < 4) {
                    completeStep(steps[currentStep - 1]);
                    activateStep(steps[currentStep]);
                    currentStep++;
                }
                if (progress > 85 && currentStep < 5) {
                    completeStep(steps[currentStep - 1]);
                    activateStep(steps[currentStep]);
                    currentStep++;
                }
                if (progress >= 100) {
                    completeStep(steps[currentStep - 1]);
                    activateStep(steps[currentStep]);
                    clearInterval(progressInterval);
                }
            }, 800);
        }
        
        function activateStep(stepId) {
            document.getElementById(stepId).classList.add('active');
        }
        
        function completeStep(stepId) {
            const step = document.getElementById(stepId);
            step.classList.remove('active');
            step.classList.add('completed');
            step.querySelector('.loading-step-icon').textContent = '✅';
        }
        </script>
        
        {% if output_file %}
            <div class="success">
                <strong>¡Archivo generado exitosamente!</strong><br>
                {{ ai_summary if ai_summary else '' }}<br>
                {{ manual_summary if manual_summary else '' }}<br>
                <a href="{{ url_for('download_file', filename=output_file) }}" style="color: #00a650; font-weight: 600;">Descargar archivo para Mercado Libre</a>
            </div>
        {% endif %}
        
        <div class="creator-signature">
            Desarrollado por <span class="creator-name">Joss Mateo</span><br>
            <small>Herramienta profesional para automatización de Mercado Libre</small>
        </div>
    </div>
</body>
</html>
'''

# Función para analizar plantilla ML y extraer estructura
def analyze_ml_template(file_path):
    """Analiza la plantilla de ML y extrae la estructura de categorías"""
    # 🔧 FIX CRÍTICO: Usar data_only=True (compatible con todas las versiones)
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
    except TypeError:
        # Fallback para versiones muy antiguas
        wb = openpyxl.load_workbook(file_path)
    
    # Encontrar hoja de categoría (no Ayuda ni Legales)
    category_sheet = None
    
    # 🎯 BUSCAR HOJA CORRECTA: Evitar hojas de ayuda/legales
    priority_sheets = []
    for sheet_name in wb.sheetnames:
        sheet_name_lower = sheet_name.lower()
        if not any(skip in sheet_name_lower for skip in ['ayuda', 'help', 'legal', 'info', 'extra']):
            priority_sheets.append(sheet_name)
    
    if priority_sheets:
        category_sheet = wb[priority_sheets[0]]  # Usar la primera hoja válida
    else:
        category_sheet = wb.active  # Fallback
    
    if not category_sheet:
        raise ValueError("No se encontró hoja de categoría en la plantilla ML")

    # 🎯 EXTRAER HEADERS DE FILA 3 (estructura correcta ML)
    headers = {}
    for col in range(1, category_sheet.max_column + 1):
        header = safe_get_cell_value(category_sheet, 3, col)  # FILA 3 es donde están los headers
        if header and len(str(header).strip()) > 0:
            headers[col] = str(header)

    return category_sheet, headers
    for sheet_name in wb.sheetnames:
        if sheet_name.lower() not in ['ayuda', 'legales', 'extra info']:
            category_sheet = wb[sheet_name]
            break
    
    if not category_sheet:
        raise ValueError("No se encontró hoja de categoría en la plantilla ML")
    
    # Extraer headers (fila 3) con manejo seguro de MergedCell
    headers = {}
    for col in range(1, category_sheet.max_column + 1):
        header = safe_get_cell_value(category_sheet, 3, col)
        if header and len(str(header).strip()) > 0:
            headers[col] = str(header)
    
    return category_sheet, headers

# Función mejorada para leer datos de productos
def read_product_data(file_path, file_ext):
    """Lee datos de productos desde diferentes formatos con manejo de MergedCell"""
    if file_ext in ['xlsx', 'xls']:
        # 🔧 FIX CRÍTICO: Manejo de MergedCell y data_only=True para fórmulas
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
        except TypeError:
            # Fallback para versiones antiguas de openpyxl
            wb = openpyxl.load_workbook(file_path)
        
        sheet = wb.active
        
        if not sheet:
            return []
        
        # Obtener headers con manejo seguro de MergedCell
        headers = []
        for col in range(1, (sheet.max_column or 0) + 1):
            header_value = safe_get_cell_value(sheet, 1, col)
            if header_value:
                headers.append(str(header_value).lower().strip())
            else:
                headers.append("")
        
        if not headers:
            return []
        
        # Obtener datos (todas las filas) con manejo seguro de MergedCell
        products = []
        for row in range(2, (sheet.max_row or 1) + 1):
            product = {}
            for col in range(1, len(headers) + 1):
                if col <= len(headers):
                    value = safe_get_cell_value(sheet, row, col)
                    
                    if value is not None:
                        # 💰 Para precios, asegurar que sean números válidos
                        if 'precio' in headers[col-1]:
                            try:
                                # Convertir a float y formatear
                                if isinstance(value, str) and value.startswith('='):
                                    # Si todavía hay fórmula, evaluar manualmente o usar valor por defecto
                                    print(f"⚠️  Fórmula detectada en precio: {value}")
                                    product[headers[col-1]] = "0"  # Valor por defecto
                                else:
                                    value = float(value)
                                    product[headers[col-1]] = str(value)
                            except (ValueError, TypeError):
                                product[headers[col-1]] = str(value)
                        else:
                            product[headers[col-1]] = str(value)
            if product:  # Solo agregar si tiene datos
                products.append(product)
        
        return products
    
    elif file_ext == 'csv':
        products = []
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Normalizar keys a lowercase
                product = {k.lower().strip(): v for k, v in row.items() if v}
                if product:
                    products.append(product)
        return products
    
    else:
        # Para PDF, DOCX, TXT - retornar datos básicos
        return [{'content': f'Datos extraídos de {file_path}'}]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Obtener archivos
            template_file = request.files.get('template')
            content_file = request.files.get('content')
            
            if not template_file or not content_file or not template_file.filename or not content_file.filename:
                return render_template_string(HTML_TEMPLATE, 
                                           message="Por favor selecciona ambos archivos", 
                                           message_type="error")
            
            # Obtener configuración IA
            ai_provider = request.form.get('ai_provider', 'manual')
            ai_api_key = request.form.get('ai_api_key', '')
            ai_fields = request.form.getlist('ai_fields')
            
            # Configurar IA
            local_ai_enhancer = AIProductEnhancer(
                provider=ai_provider if ai_provider != 'manual' else 'groq',
                api_key=ai_api_key if ai_api_key else None
            )
            
            # Guardar archivos
            template_filename = secure_filename(template_file.filename)
            content_filename = secure_filename(content_file.filename)
            
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)
            content_path = os.path.join(app.config['UPLOAD_FOLDER'], content_filename)
            
            template_file.save(template_path)
            content_file.save(content_path)
            
            # Analizar plantilla ML
            category_sheet, ml_headers = analyze_ml_template(template_path)
            
            # Leer datos de productos
            content_ext = content_filename.split('.')[-1].lower()
            products = read_product_data(content_path, content_ext)
            
            # Obtener configuración de mapeo
            selected_fields = request.form.getlist('map_fields')
            condicion = request.form.get('condicion', 'Nuevo')
            moneda = request.form.get('moneda', '$')
            
            # 🔧 NUEVA CONFIGURACIÓN MANUAL MASIVA
            manual_config = {
                'stock_global': request.form.get('stock_global'),
                'stock_selective': request.form.get('stock_selective'),
                'marca_global': request.form.get('marca_global'),
                'modelo_global': request.form.get('modelo_global'),
                'marca_modelo_selective': request.form.get('marca_modelo_selective'),
                'retiro_persona': request.form.get('retiro_persona'),
                'tipo_garantia': request.form.get('tipo_garantia'),
                'tiempo_garantia': request.form.get('tiempo_garantia'),
                'unidad_garantia': request.form.get('unidad_garantia'),
                'tiene_catalogo': request.form.get('tiene_catalogo'),
                'numero_catalogo_selective': request.form.get('numero_catalogo_selective'),
                'descripcion_global': request.form.get('descripcion_global'),
                # 🆕 NUEVAS CONFIGURACIONES
                'forma_envio_global': request.form.get('forma_envio_global'),
                'forma_envio_selective': request.form.get('forma_envio_selective'),
                'costo_envio_global': request.form.get('costo_envio_global'),
                'costo_envio_selective': request.form.get('costo_envio_selective'),
                'color_global': request.form.get('color_global'),
                'color_comercial_global': request.form.get('color_comercial_global'),
                'color_selective': request.form.get('color_selective'),
                # 🔢 CÓDIGOS UNIVERSALES
                'codigo_universal_masivo': request.form.get('codigo_universal_masivo'),
                'codigo_universal_secuencial': request.form.get('codigo_universal_secuencial') == 'on',
                'codigo_universal_offset': int(request.form.get('codigo_universal_offset', 1)) if request.form.get('codigo_universal_offset') else 1,
                'codigo_universal_selective': request.form.get('codigo_universal_selective')
            }
            
            # 🧠 PROCESAR CON IA - Enriquecer datos de productos
            ai_summary = ""
            debug_info = []  # 🔍 NUEVO: Log de debug detallado
            
            debug_info.append("🔍 INICIANDO PROCESAMIENTO...")
            debug_info.append(f"📊 Total productos detectados: {len(products)}")
            debug_info.append(f"📋 Campos a mapear: {selected_fields}")
            debug_info.append(f"🧠 IA habilitada: {'Sí' if ai_provider != 'manual' else 'No'}")
            debug_info.append(f"🔧 Configuración manual: {'Activa' if any(manual_config.values()) else 'No configurada'}")
            
            # 🔍 Debug precios ANTES del procesamiento IA
            precios_detectados_input = 0
            for i, product in enumerate(products):
                precio_value = find_product_value(product, 'precio')
                if precio_value:
                    precios_detectados_input += 1
                    debug_info.append(f"💰 INPUT Precio fila {i+2}: {precio_value}")
            debug_info.append(f"💰 Total precios detectados en INPUT: {precios_detectados_input}")
            
            if ai_provider != 'manual' and ai_fields:
                enhanced_products = []
                ai_stats = {'enhanced': 0, 'total': len(products)}
                
                for product in products:
                    # Determinar qué campos faltan
                    missing_fields = []
                    for field in ai_fields:
                        if not find_product_value(product, field):
                            missing_fields.append(field)
                    
                    if missing_fields:
                        # Generar datos faltantes con IA
                        try:
                            ai_data = local_ai_enhancer.generate_missing_data(product, missing_fields)
                            product.update(ai_data)
                            ai_stats['enhanced'] += 1
                            debug_info.append(f"🧠 IA mejoró producto: {missing_fields}")
                        except Exception as e:
                            debug_info.append(f"❌ Error IA para producto {product}: {e}")
                    
                    enhanced_products.append(product)
                
                products = enhanced_products
                ai_summary = f"🧠 IA procesó {ai_stats['enhanced']}/{ai_stats['total']} productos, completando {len(ai_fields)} tipos de campos."
                debug_info.append(ai_summary)
            
            # Crear archivo de salida
            output_filename = f"ML_AI_Output_{template_filename}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Copiar plantilla original como base
            shutil.copy2(template_path, output_path)
            
            # Procesar y llenar datos
            wb_output = openpyxl.load_workbook(output_path)
            
            # 🛠️ PROCESAR CONFIGURACIONES MANUALES SELECTIVAS
            debug_info.append("🔧 PROCESANDO CONFIGURACIONES MANUALES...")
            
            # Configuraciones selectivas por fila
            stock_overrides = {}
            marca_modelo_overrides = {}
            forma_envio_overrides = {}
            costo_envio_overrides = {}
            color_overrides = {}
            
            # Procesar stock selectivo
            if manual_config.get('stock_selective'):
                try:
                    for item in manual_config['stock_selective'].split(','):
                        if ':' in item:
                            row, stock = item.strip().split(':', 1)
                            stock_overrides[int(row)] = stock.strip()
                            debug_info.append(f"📦 Stock selectivo fila {row}: {stock}")
                except Exception as e:
                    debug_info.append(f"⚠️ Error en stock selectivo: {e}")
            
            # Procesar marca/modelo selectivo
            if manual_config.get('marca_modelo_selective'):
                try:
                    for item in manual_config['marca_modelo_selective'].split(','):
                        if ':' in item:
                            parts = item.strip().split(':')
                            if len(parts) >= 3:
                                row, marca, modelo = parts[0], parts[1], ':'.join(parts[2:])
                                marca_modelo_overrides[int(row)] = {'marca': marca.strip(), 'modelo': modelo.strip()}
                                debug_info.append(f"🏷️ Marca/Modelo fila {row}: {marca}/{modelo}")
                except Exception as e:
                    debug_info.append(f"⚠️ Error en marca/modelo selectivo: {e}")
            
            # 🆕 Procesar forma de envío selectiva
            if manual_config.get('forma_envio_selective'):
                try:
                    for item in manual_config['forma_envio_selective'].split(','):
                        if ':' in item:
                            row, forma = item.strip().split(':', 1)
                            forma_envio_overrides[int(row)] = forma.strip()
                            debug_info.append(f"🚚 Forma envío fila {row}: {forma}")
                except Exception as e:
                    debug_info.append(f"⚠️ Error en forma envío selectiva: {e}")
            
            # 🆕 Procesar costo de envío selectivo
            if manual_config.get('costo_envio_selective'):
                try:
                    for item in manual_config['costo_envio_selective'].split(','):
                        if ':' in item:
                            row, costo = item.strip().split(':', 1)
                            costo_envio_overrides[int(row)] = costo.strip()
                            debug_info.append(f"💰 Costo envío fila {row}: {costo}")
                except Exception as e:
                    debug_info.append(f"⚠️ Error en costo envío selectivo: {e}")
            
            # 🆕 Procesar color selectivo
            if manual_config.get('color_selective'):
                try:
                    for item in manual_config['color_selective'].split(','):
                        if ':' in item:
                            parts = item.strip().split(':')
                            if len(parts) >= 3:
                                row, color, nombre_comercial = parts[0], parts[1], ':'.join(parts[2:])
                                color_overrides[int(row)] = {'color': color.strip(), 'nombre_comercial': nombre_comercial.strip()}
                                debug_info.append(f"🎨 Color fila {row}: {color}/{nombre_comercial}")
                except Exception as e:
                    debug_info.append(f"⚠️ Error en color selectivo: {e}")
            
            # Encontrar hoja de categoría
            category_sheet_name = None
            for sheet_name in wb_output.sheetnames:
                if sheet_name.lower() not in ['ayuda', 'legales', 'extra info']:
                    category_sheet_name = sheet_name
                    break
            
            if not category_sheet_name:
                raise ValueError("No se encontró hoja de categoría en la plantilla")
            
            output_sheet = wb_output[category_sheet_name]
            
            # Mapear y llenar datos con debug info
            debug_info = fill_ml_template(output_sheet, ml_headers, products, selected_fields, condicion, moneda, manual_config, debug_info)
            
            wb_output.save(output_path)
            
            success_message = f"¡Archivo generado exitosamente! {len(products)} productos procesados."
            if ai_provider != 'manual':
                success_message += f" Con IA {ai_provider.upper()}."
            
            # Agregar información sobre configuración manual aplicada
            manual_summary = ""
            if manual_config:
                applied_configs = []
                if manual_config.get('stock_global'):
                    applied_configs.append(f"Stock global: {manual_config['stock_global']}")
                if manual_config.get('stock_selective'):
                    applied_configs.append("Stock selectivo aplicado")
                if manual_config.get('marca_global'):
                    applied_configs.append(f"Marca global: {manual_config['marca_global']}")
                if manual_config.get('modelo_global'):
                    applied_configs.append(f"Modelo global: {manual_config['modelo_global']}")
                if manual_config.get('retiro_persona'):
                    applied_configs.append(f"Retiro persona: {manual_config['retiro_persona']}")
                if manual_config.get('tipo_garantia'):
                    applied_configs.append(f"Garantía: {manual_config['tipo_garantia']}")
                if manual_config.get('descripcion_global'):
                    applied_configs.append("Descripción global agregada")
                # 🆕 NUEVAS CONFIGURACIONES
                if manual_config.get('forma_envio_global'):
                    applied_configs.append(f"Forma envío: {manual_config['forma_envio_global']}")
                if manual_config.get('costo_envio_global'):
                    applied_configs.append(f"Costo envío: {manual_config['costo_envio_global']}")
                if manual_config.get('color_global'):
                    applied_configs.append(f"Color: {manual_config['color_global']}")
                
                if applied_configs:
                    manual_summary = f"⚙️ Configuración manual aplicada: {', '.join(applied_configs)}"
            
            # Convertir debug_info a string para mostrar
            debug_info_str = '\n'.join(debug_info) if debug_info else None
            
            return render_template_string(HTML_TEMPLATE, 
                                       message=success_message,
                                       message_type="success",
                                       output_file=output_filename,
                                       ai_summary=ai_summary,
                                       manual_summary=manual_summary,
                                       debug_info=debug_info_str)
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, 
                                       message=f"Error al procesar archivos: {str(e)}", 
                                       message_type="error")
    
    return render_template_string(HTML_TEMPLATE)

def fill_ml_template(sheet, headers, products, selected_fields, condicion, moneda, manual_config=None, debug_info=None):
    """Llena la plantilla ML con datos de productos y configuración manual masiva"""
    
    if debug_info is None:
        debug_info = []
        
    debug_info.append("📋 INICIANDO MAPEO DE DATOS A TEMPLATE ML...")
    debug_info.append(f"📊 Headers ML disponibles: {len(headers)}")
    debug_info.append(f"📦 Productos a mapear: {len(products)}")
    
    # 🔍 Mapeo de campos ML - POSICIONES EXACTAS SEGÚN PLANTILLA ML
    ml_field_mapping = {
        'titulo': ['Título: incluye producto, marca, modelo y destaca sus características principales'],
        'precio': ['Precio'],
        'stock': ['Stock', 'Stock disponible'],
        'sku': ['SKU'],
        'descripcion': ['Descripción'],
        'marca': ['Marca'],
        'modelo': ['Modelo'],
        'condicion': ['Condición'],
        'moneda': ['Moneda'],
        'codigo_universal': ['Código universal de producto'],
        'garantia_tipo': ['Tipo de garantía'],
        'garantia_tiempo': ['Tiempo de garantía'],
        'garantia_unidad': ['Unidad de Tiempo de garantía'],
        'retiro_persona': ['Retiro en persona'],
        'tiene_catalogo': ['Código de catálogo ML'],
        # 🆕 NUEVOS CAMPOS
        'forma_envio': ['Forma de envío'],
        'costo_envio': ['Costo de envío'],
        'color': ['Varía por: Color'],
        'color_comercial': ['Varía por: Nombre comercial del color']
    }
    
    # 🎯 MAPEO FIJO DE COLUMNAS ML (para evitar alteración de template)
    # Basado en la estructura estándar de plantilla ML
    ml_columns_fixed = {
        'titulo': 2,      # Columna B - Título
        'condicion': 4,   # Columna D - Condición  
        'codigo_universal': 5, # Columna E - Código universal
        'color': 6,       # Columna F - Color
        'color_comercial': 7, # Columna G - Nombre comercial color
        'sku': 9,         # Columna I - SKU
        'stock': 10,      # Columna J - Stock
        'precio': 11,     # Columna K - Precio
        'moneda': 12,     # Columna L - Moneda
        'descripcion': 13, # Columna M - Descripción
        # 🚚 CAMPOS DE ENVÍO (FALTABAN!)
        'forma_envio': 15, # Columna O - Forma de envío
        'costo_envio': 16, # Columna P - Costo de envío
        'retiro_persona': 17, # Columna Q - Retiro en persona
        # 🛡️ CAMPOS DE GARANTÍA
        'garantia_tipo': 18, # Columna R - Tipo de garantía
        'garantia_tiempo': 19, # Columna S - Tiempo de garantía
        'garantia_unidad': 20, # Columna T - Unidad de Tiempo de garantía
        # 🏷️ CAMPOS DE PRODUCTO
        'marca': 22,      # Columna V - Marca (posición correcta)
        'modelo': 23,     # Columna W - Modelo (posición correcta)
    }
    
    # 🎯 USAR MAPEO FIJO DE COLUMNAS (no buscar dinámicamente)
    ml_columns = ml_columns_fixed.copy()
    
    debug_info.append("🔒 USANDO MAPEO FIJO DE COLUMNAS ML:")
    for field, col in ml_columns.items():
        debug_info.append(f"  {field} -> Columna {col} ({'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[col-1]})")
    
    debug_info.append(f"✅ Campos ML mapeados: {list(ml_columns.keys())}")
    
    # Contadores para estadísticas
    productos_mapeados = 0
    precios_mapeados = 0
    campos_aplicados = {field: 0 for field in ml_columns.keys()}
    
    # 🛠️ Procesar configuraciones selectivas (acceder desde manual_config)
    stock_overrides = {}
    marca_modelo_overrides = {}
    forma_envio_overrides = {}
    costo_envio_overrides = {}
    color_overrides = {}
    
    if manual_config:
        # Procesar stock selectivo
        if manual_config.get('stock_selective'):
            try:
                for item in manual_config['stock_selective'].split(','):
                    if ':' in item:
                        row, stock = item.strip().split(':', 1)
                        stock_overrides[int(row)] = stock.strip()
            except:
                pass
        
        # Procesar marca/modelo selectivo  
        if manual_config.get('marca_modelo_selective'):
            try:
                for item in manual_config['marca_modelo_selective'].split(','):
                    if ':' in item:
                        parts = item.strip().split(':')
                        if len(parts) >= 3:
                            row, marca, modelo = parts[0], parts[1], ':'.join(parts[2:])
                            marca_modelo_overrides[int(row)] = {'marca': marca.strip(), 'modelo': modelo.strip()}
            except:
                pass
        
        # Procesar forma de envío selectiva
        if manual_config.get('forma_envio_selective'):
            try:
                for item in manual_config['forma_envio_selective'].split(','):
                    if ':' in item:
                        row, forma = item.strip().split(':', 1)
                        forma_envio_overrides[int(row)] = forma.strip()
            except:
                pass
        
        # Procesar costo de envío selectivo
        if manual_config.get('costo_envio_selective'):
            try:
                for item in manual_config['costo_envio_selective'].split(','):
                    if ':' in item:
                        row, costo = item.strip().split(':', 1)
                        costo_envio_overrides[int(row)] = costo.strip()
            except:
                pass
        
        # Procesar color selectivo
        if manual_config.get('color_selective'):
            try:
                for item in manual_config['color_selective'].split(','):
                    if ':' in item:
                        parts = item.strip().split(':')
                        if len(parts) >= 3:
                            row, color, nombre_comercial = parts[0], parts[1], ':'.join(parts[2:])
                            color_overrides[int(row)] = {'color': color.strip(), 'nombre_comercial': nombre_comercial.strip()}
            except:
                pass
    
    # Mapear cada producto
    for i, product in enumerate(products):
        row_num = i + 8  # 🎯 FIX CRÍTICO: Fila en Excel (empezando desde la 8, NO desde la 4)
        producto_mapeado = False
        
        debug_info.append(f"📦 Procesando producto {i+1}/{len(products)} (fila {row_num})")
        
        # Mapear campos básicos
        for field in selected_fields:
            if field in ml_columns:
                col = ml_columns[field]
                value = find_product_value(product, field)
                
                if value:
                    safe_set_cell_value(sheet, row_num, col, value)
                    campos_aplicados[field] += 1
                    producto_mapeado = True
                    
                    # 💰 Debug especial para precios
                    if field == 'precio':
                        precios_mapeados += 1
                        debug_info.append(f"💰 PRECIO MAPEADO fila {row_num}: {value}")
        
        # 🔧 APLICAR CONFIGURACIONES MANUALES GLOBALES Y SELECTIVAS
        
        # Stock
        if manual_config.get('stock_global') and 'stock' in ml_columns:
            if row_num not in stock_overrides:  # No override selectivo
                safe_set_cell_value(sheet, row_num, ml_columns['stock'], manual_config['stock_global'])
                campos_aplicados['stock'] += 1
                producto_mapeado = True
        
        # Stock selectivo
        if row_num in stock_overrides and 'stock' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['stock'], stock_overrides[row_num])
            campos_aplicados['stock'] += 1
            producto_mapeado = True
        
        # Marca y Modelo globales
        if manual_config.get('marca_global') and 'marca' in ml_columns:
            if row_num not in marca_modelo_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['marca'], manual_config['marca_global'])
                campos_aplicados['marca'] += 1
                producto_mapeado = True
                
        if manual_config.get('modelo_global') and 'modelo' in ml_columns:
            if row_num not in marca_modelo_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['modelo'], manual_config['modelo_global'])
                campos_aplicados['modelo'] += 1
                producto_mapeado = True
        
        # Marca/Modelo selectivos
        if row_num in marca_modelo_overrides:
            override = marca_modelo_overrides[row_num]
            if 'marca' in ml_columns:
                safe_set_cell_value(sheet, row_num, ml_columns['marca'], override['marca'])
                campos_aplicados['marca'] += 1
                producto_mapeado = True
            if 'modelo' in ml_columns:
                safe_set_cell_value(sheet, row_num, ml_columns['modelo'], override['modelo'])
                campos_aplicados['modelo'] += 1
                producto_mapeado = True
        
        # 🆕 NUEVAS CONFIGURACIONES
        
        # Forma de envío
        if manual_config.get('forma_envio_global') and 'forma_envio' in ml_columns:
            if row_num not in forma_envio_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['forma_envio'], manual_config['forma_envio_global'])
                campos_aplicados['forma_envio'] += 1
                producto_mapeado = True
        
        if row_num in forma_envio_overrides and 'forma_envio' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['forma_envio'], forma_envio_overrides[row_num])
            campos_aplicados['forma_envio'] += 1
            producto_mapeado = True
        
        # Costo de envío
        if manual_config.get('costo_envio_global') and 'costo_envio' in ml_columns:
            if row_num not in costo_envio_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['costo_envio'], manual_config['costo_envio_global'])
                campos_aplicados['costo_envio'] += 1
                producto_mapeado = True
        
        if row_num in costo_envio_overrides and 'costo_envio' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['costo_envio'], costo_envio_overrides[row_num])
            campos_aplicados['costo_envio'] += 1
            producto_mapeado = True
        
        # Color
        if manual_config.get('color_global') and 'color' in ml_columns:
            if row_num not in color_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['color'], manual_config['color_global'])
                campos_aplicados['color'] += 1
                producto_mapeado = True
        
        if manual_config.get('color_comercial_global') and 'color_comercial' in ml_columns:
            if row_num not in color_overrides:
                safe_set_cell_value(sheet, row_num, ml_columns['color_comercial'], manual_config['color_comercial_global'])
                campos_aplicados['color_comercial'] += 1
                producto_mapeado = True
        
        if row_num in color_overrides:
            override = color_overrides[row_num]
            if 'color' in ml_columns:
                safe_set_cell_value(sheet, row_num, ml_columns['color'], override['color'])
                campos_aplicados['color'] += 1
                producto_mapeado = True
            if 'color_comercial' in ml_columns:
                safe_set_cell_value(sheet, row_num, ml_columns['color_comercial'], override['nombre_comercial'])
                campos_aplicados['color_comercial'] += 1
                producto_mapeado = True
        
        # Retiro en persona
        if manual_config.get('retiro_persona') and 'retiro_persona' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['retiro_persona'], manual_config['retiro_persona'])
            campos_aplicados['retiro_persona'] += 1
            producto_mapeado = True
        
        # Garantía
        if manual_config.get('tipo_garantia') and 'garantia_tipo' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['garantia_tipo'], manual_config['tipo_garantia'])
            campos_aplicados['garantia_tipo'] += 1
            producto_mapeado = True
            
        if manual_config.get('tiempo_garantia') and 'garantia_tiempo' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['garantia_tiempo'], manual_config['tiempo_garantia'])
            campos_aplicados['garantia_tiempo'] += 1
            producto_mapeado = True
            
        if manual_config.get('unidad_garantia') and 'garantia_unidad' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['garantia_unidad'], manual_config['unidad_garantia'])
            campos_aplicados['garantia_unidad'] += 1
            producto_mapeado = True
        
        # Códigos universales masivos
        if manual_config.get('codigo_universal_masivo') and 'codigo_universal' in ml_columns:
            codigo_masivo = manual_config['codigo_universal_masivo']
            # Agregar número secuencial si se especifica
            if manual_config.get('codigo_universal_secuencial', False):
                # Usar el índice actual + offset si se especifica
                offset = manual_config.get('codigo_universal_offset', 1)
                numero_secuencial = row_num - 7 + offset  # 🎯 FIX: Ajustar porque empezamos en fila 8 (no 4)
                codigo_final = f"{codigo_masivo}{numero_secuencial:04d}"  # Formato con 4 dígitos
            else:
                codigo_final = codigo_masivo
            
            safe_set_cell_value(sheet, row_num, ml_columns['codigo_universal'], codigo_final)
            campos_aplicados['codigo_universal'] += 1
            producto_mapeado = True
        
        # Valores por defecto (condición, moneda, envío)
        if 'condicion' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['condicion'], condicion)
            campos_aplicados['condicion'] += 1
            producto_mapeado = True
            
        if 'moneda' in ml_columns:
            safe_set_cell_value(sheet, row_num, ml_columns['moneda'], moneda)
            campos_aplicados['moneda'] += 1
            producto_mapeado = True
        
        # 🚚 VALORES POR DEFECTO PARA ENVÍO (CAMPOS OBLIGATORIOS)
        if 'forma_envio' in ml_columns and not manual_config.get('forma_envio_global'):
            safe_set_cell_value(sheet, row_num, ml_columns['forma_envio'], 'Mercado Envíos')
            campos_aplicados['forma_envio'] += 1
            producto_mapeado = True
            
        if 'costo_envio' in ml_columns and not manual_config.get('costo_envio_global'):
            safe_set_cell_value(sheet, row_num, ml_columns['costo_envio'], 'A cargo del comprador')
            campos_aplicados['costo_envio'] += 1
            producto_mapeado = True
            
        if 'retiro_persona' in ml_columns and not manual_config.get('retiro_persona'):
            safe_set_cell_value(sheet, row_num, ml_columns['retiro_persona'], 'Acepto')
            campos_aplicados['retiro_persona'] += 1
            producto_mapeado = True
        
        # Descripción global
        if manual_config.get('descripcion_global') and 'descripcion' in ml_columns:
            existing_desc = find_product_value(product, 'descripcion') or ""
            combined_desc = f"{existing_desc}\n\n{manual_config['descripcion_global']}" if existing_desc else manual_config['descripcion_global']
            safe_set_cell_value(sheet, row_num, ml_columns['descripcion'], combined_desc)
            campos_aplicados['descripcion'] += 1
            producto_mapeado = True
        
        if producto_mapeado:
            productos_mapeados += 1
    
    # 📊 Generar estadísticas finales
    debug_info.append("📊 ESTADÍSTICAS FINALES DE MAPEO:")
    debug_info.append(f"✅ Productos mapeados: {productos_mapeados}/{len(products)}")
    debug_info.append(f"💰 Precios mapeados: {precios_mapeados}")
    
    for campo, cantidad in campos_aplicados.items():
        if cantidad > 0:
            debug_info.append(f"📋 {campo}: {cantidad} valores aplicados")
    
    return debug_info
    
    # Mapeo de campos
    field_mapping = {
        'titulo': 'Título: incluye producto, marca, modelo y destaca sus características principales',
        'precio': 'Precio',
        'stock': 'Stock',
        'sku': 'SKU',
        'descripcion': 'Descripción',
        'marca': 'Marca',
        'modelo': 'Modelo',
        'codigo_universal': 'Código universal de producto',
        'color': 'Color',
        'peso': 'Peso',
        'retiro_persona': 'Acepto retiro del comprador en domicilio del vendedor',
        'tipo_garantia': 'Tipo de garantía',
        'tiempo_garantia': 'Tiempo de garantía',
        'unidad_garantia': 'Unidad de tiempo de la garantía',
        'catalogo': 'El producto tiene catálogo',
        'numero_catalogo': 'Número de catálogo'
    }
    
    # Encontrar columnas en la plantilla
    column_map = {}
    for col_num, header in headers.items():
        for field, ml_field in field_mapping.items():
            if ml_field in header:
                column_map[field] = col_num
                break
    
    # Procesar configuración selectiva de la configuración manual
    stock_selective_dict = {}
    marca_modelo_selective_dict = {}
    catalogo_selective_dict = {}
    codigo_universal_selective_dict = {}
    
    if manual_config:
        # Procesar stock selectivo
        if manual_config.get('stock_selective'):
            try:
                for item in manual_config['stock_selective'].split(','):
                    if ':' in item:
                        fila, stock = item.strip().split(':')
                        stock_selective_dict[int(fila)] = int(stock)
            except Exception as e:
                print(f"Error procesando stock selectivo: {e}")
        
        # Procesar marca/modelo selectivo
        if manual_config.get('marca_modelo_selective'):
            try:
                for item in manual_config['marca_modelo_selective'].split(','):
                    if ':' in item:
                        parts = item.strip().split(':')
                        if len(parts) >= 3:
                            fila, marca, modelo = parts[0], parts[1], parts[2]
                            marca_modelo_selective_dict[int(fila)] = {'marca': marca, 'modelo': modelo}
            except Exception as e:
                print(f"Error procesando marca/modelo selectivo: {e}")
        
        # Procesar catálogo selectivo
        if manual_config.get('numero_catalogo_selective'):
            try:
                for item in manual_config['numero_catalogo_selective'].split(','):
                    if ':' in item:
                        fila, numero = item.strip().split(':')
                        catalogo_selective_dict[int(fila)] = numero
            except Exception as e:
                print(f"Error procesando catálogo selectivo: {e}")
        
        # Procesar códigos universales selectivos
        if manual_config.get('codigo_universal_selective'):
            try:
                for item in manual_config['codigo_universal_selective'].split(','):
                    if ':' in item:
                        fila, codigo = item.strip().split(':')
                        codigo_universal_selective_dict[int(fila)] = codigo
            except Exception as e:
                print(f"Error procesando código universal selectivo: {e}")
    
    # Llenar datos para cada producto
    start_row = 8  # Comenzar después de las filas de headers e instrucciones
    
    for i, product in enumerate(products):
        row_num = start_row + i
        excel_row = row_num  # Fila real en Excel para configuración selectiva
        
        # Llenar campos seleccionados del archivo de datos
        for field in selected_fields:
            if field in column_map:
                col_num = column_map[field]
                
                # Buscar valor en datos del producto
                value = find_product_value(product, field)
                if value:
                    safe_set_cell_value(sheet, row_num, col_num, value)
        
        # 🔧 APLICAR CONFIGURACIÓN MANUAL MASIVA
        if manual_config:
            
            # Stock: selectivo tiene prioridad sobre global
            if excel_row in stock_selective_dict:
                if 'stock' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['stock'], stock_selective_dict[excel_row])
            elif manual_config.get('stock_global'):
                if 'stock' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['stock'], int(manual_config['stock_global']))
            
            # Marca y Modelo: selectivo tiene prioridad sobre global
            if excel_row in marca_modelo_selective_dict:
                selective_data = marca_modelo_selective_dict[excel_row]
                if 'marca' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['marca'], selective_data['marca'])
                if 'modelo' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['modelo'], selective_data['modelo'])
            else:
                # Aplicar valores globales
                if manual_config.get('marca_global') and 'marca' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['marca'], manual_config['marca_global'])
                if manual_config.get('modelo_global') and 'modelo' in column_map:
                    safe_set_cell_value(sheet, row_num, column_map['modelo'], manual_config['modelo_global'])
            
            # Retiro en persona
            if manual_config.get('retiro_persona') and 'retiro_persona' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['retiro_persona'], manual_config['retiro_persona'])
            
            # Garantía
            if manual_config.get('tipo_garantia') and 'tipo_garantia' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['tipo_garantia'], manual_config['tipo_garantia'])
            if manual_config.get('tiempo_garantia') and 'tiempo_garantia' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['tiempo_garantia'], int(manual_config['tiempo_garantia']))
            if manual_config.get('unidad_garantia') and 'unidad_garantia' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['unidad_garantia'], manual_config['unidad_garantia'])
            
            # Catálogo
            if manual_config.get('tiene_catalogo') and 'catalogo' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['catalogo'], manual_config['tiene_catalogo'])
            
            # Número de catálogo selectivo
            if excel_row in catalogo_selective_dict and 'numero_catalogo' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['numero_catalogo'], catalogo_selective_dict[excel_row])
            
            # Código universal selectivo (sobrescribe el masivo si existe)
            if excel_row in codigo_universal_selective_dict and 'codigo_universal' in column_map:
                safe_set_cell_value(sheet, row_num, column_map['codigo_universal'], codigo_universal_selective_dict[excel_row])
            
            # Descripción global: agregar al final de descripción existente
            if manual_config.get('descripcion_global') and 'descripcion' in column_map:
                existing_desc = safe_get_cell_value(sheet, row_num, column_map['descripcion']) or ""
                if existing_desc:
                    new_desc = f"{existing_desc}\n\n{manual_config['descripcion_global']}"
                else:
                    new_desc = manual_config['descripcion_global']
                safe_set_cell_value(sheet, row_num, column_map['descripcion'], new_desc)
        
        # Llenar valores por defecto estándar
        if 'Condición' in [headers.get(col) for col in headers]:
            for col_num, header in headers.items():
                if 'Condición' in header:
                    safe_set_cell_value(sheet, row_num, col_num, condicion)
                    break
        
        if 'Moneda' in [headers.get(col) for col in headers]:
            for col_num, header in headers.items():
                if 'Moneda' in header:
                    safe_set_cell_value(sheet, row_num, col_num, moneda)
                    break

def find_product_value(product, field):
    """Encuentra el valor correspondiente en los datos del producto"""
    
    # Mapeo flexible de nombres de campos
    field_variations = {
        'titulo': ['titulo', 'title', 'nombre', 'product_name', 'name', 'producto'],
        'precio': ['precio', 'price', 'cost', 'costo'],
        'stock': ['stock', 'cantidad', 'inventory', 'qty'],
        'sku': ['sku', 'codigo', 'code', 'id'],
        'descripcion': ['descripcion', 'description', 'desc'],
        'marca': ['marca', 'brand'],
        'modelo': ['modelo', 'model'],
        'codigo_universal': ['codigo_universal', 'upc', 'ean', 'barcode'],
        'color': ['color', 'colour'],
        'peso': ['peso', 'weight']
    }
    
    if field in field_variations:
        for variation in field_variations[field]:
            for key in product.keys():
                if variation in key.lower():
                    value = product[key]
                    
                    # 🎯 CONVERSIÓN ESPECIAL PARA PRECIOS Y NÚMEROS
                    if field in ['precio', 'stock']:
                        try:
                            # Remover símbolos de moneda y espacios
                            if isinstance(value, str):
                                cleaned_value = value.replace('$', '').replace(',', '').replace(' ', '').strip()
                                return float(cleaned_value)
                            elif isinstance(value, (int, float)):
                                return float(value)
                        except (ValueError, TypeError):
                            return value  # Devolver valor original si no se puede convertir
                    
                    return value
    
    return None

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"Error descargando archivo: {str(e)}", 404

if __name__ == '__main__':
    print("🚀 Iniciando Mercado Libre Bulk Mapper Pro en http://localhost:5003")
    app.run(debug=True, host='localhost', port=5003)
