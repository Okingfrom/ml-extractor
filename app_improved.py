#!/usr/bin/env python3
"""
Aplicación Flask mejorada para mapeo de productos a Mercado Libre
Mantiene la estructura exacta de ML y permite mapeo selectivo
CON INTELIGENCIA ARTIFICIAL para autocompletar datos faltantes
"""

from flask import Flask, request, render_template_string, send_file, redirect, url_for, jsonify
import openpyxl
import csv
import docx
import PyPDF2
import yaml
import os
import tempfile
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
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
            
            <button type="submit">Procesar y Generar Archivo ML</button>
        </form>
        
        {% if output_file %}
            <div class="success">
                <strong>¡Archivo generado exitosamente!</strong><br>
                {{ ai_summary if ai_summary else '' }}<br>
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
    wb = openpyxl.load_workbook(file_path)
    
    # Encontrar hoja de categoría (no Ayuda ni Legales)
    category_sheet = None
    for sheet_name in wb.sheetnames:
        if sheet_name.lower() not in ['ayuda', 'legales', 'extra info']:
            category_sheet = wb[sheet_name]
            break
    
    if not category_sheet:
        raise ValueError("No se encontró hoja de categoría en la plantilla ML")
    
    # Extraer headers (fila 3)
    headers = {}
    for col in range(1, category_sheet.max_column + 1):
        header = category_sheet.cell(row=3, column=col).value
        if header and len(str(header).strip()) > 0:
            headers[col] = str(header)
    
    return category_sheet, headers

# Función mejorada para leer datos de productos
def read_product_data(file_path, file_ext):
    """Lee datos de productos desde diferentes formatos"""
    if file_ext in ['xlsx', 'xls']:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        if not sheet:
            return []
        
        # Obtener headers
        headers = []
        for col in range(1, (sheet.max_column or 0) + 1):
            header = sheet.cell(row=1, column=col).value
            if header:
                headers.append(str(header).lower().strip())
        
        if not headers:
            return []
        
        # Obtener datos (todas las filas)
        products = []
        for row in range(2, (sheet.max_row or 1) + 1):
            product = {}
            for col in range(1, len(headers) + 1):
                if col <= len(headers):
                    value = sheet.cell(row=row, column=col).value
                    if value is not None:
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
            
            # 🧠 PROCESAR CON IA - Enriquecer datos de productos
            ai_summary = ""
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
                        except Exception as e:
                            print(f"Error IA para producto {product}: {e}")
                    
                    enhanced_products.append(product)
                
                products = enhanced_products
                ai_summary = f"🧠 IA procesó {ai_stats['enhanced']}/{ai_stats['total']} productos, completando {len(ai_fields)} tipos de campos."
            
            # Crear archivo de salida
            output_filename = f"ML_AI_Output_{template_filename}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Copiar plantilla original como base
            shutil.copy2(template_path, output_path)
            
            # Procesar y llenar datos
            wb_output = openpyxl.load_workbook(output_path)
            
            # Encontrar hoja de categoría
            category_sheet_name = None
            for sheet_name in wb_output.sheetnames:
                if sheet_name.lower() not in ['ayuda', 'legales', 'extra info']:
                    category_sheet_name = sheet_name
                    break
            
            if not category_sheet_name:
                raise ValueError("No se encontró hoja de categoría en la plantilla")
            
            output_sheet = wb_output[category_sheet_name]
            
            # Mapear y llenar datos
            fill_ml_template(output_sheet, ml_headers, products, selected_fields, condicion, moneda)
            
            wb_output.save(output_path)
            
            success_message = f"¡Archivo generado exitosamente! {len(products)} productos procesados."
            if ai_provider != 'manual':
                success_message += f" Con IA {ai_provider.upper()}."
            
            # Agregar debug info si está disponible
            debug_info = local_ai_enhancer.get_debug_log() if ai_provider != 'manual' else None
            
            return render_template_string(HTML_TEMPLATE, 
                                       message=success_message,
                                       message_type="success",
                                       output_file=output_filename,
                                       ai_summary=ai_summary,
                                       debug_info=debug_info)
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, 
                                       message=f"Error al procesar archivos: {str(e)}", 
                                       message_type="error")
    
    return render_template_string(HTML_TEMPLATE)

def fill_ml_template(sheet, headers, products, selected_fields, condicion, moneda):
    """Llena la plantilla ML con datos de productos"""
    
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
        'peso': 'Peso'
    }
    
    # Encontrar columnas en la plantilla
    column_map = {}
    for col_num, header in headers.items():
        for field, ml_field in field_mapping.items():
            if ml_field in header:
                column_map[field] = col_num
                break
    
    # Llenar datos para cada producto
    start_row = 8  # Comenzar después de las filas de headers e instrucciones
    
    for i, product in enumerate(products):
        row_num = start_row + i
        
        # Llenar campos seleccionados
        for field in selected_fields:
            if field in column_map:
                col_num = column_map[field]
                
                # Buscar valor en datos del producto
                value = find_product_value(product, field)
                if value:
                    sheet.cell(row=row_num, column=col_num, value=value)
        
        # Llenar valores por defecto
        if 'Condición' in [headers.get(col) for col in headers]:
            for col_num, header in headers.items():
                if 'Condición' in header:
                    sheet.cell(row=row_num, column=col_num, value=condicion)
                    break
        
        if 'Moneda' in [headers.get(col) for col in headers]:
            for col_num, header in headers.items():
                if 'Moneda' in header:
                    sheet.cell(row=row_num, column=col_num, value=moneda)
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
                    return product[key]
    
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
