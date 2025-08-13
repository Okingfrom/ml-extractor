#!/usr/bin/env python3
"""
Script de prueba automatizada para el ML Extractor con IA
Demuestra el funcionamiento del sistema end-to-end
"""

import requests
import json
import os

# Configuración
BASE_URL = "http://localhost:5002"
TEMPLATE_FILE = "uploads/Publicar-08-10-22_41_20.xlsx"
CONTENT_FILE = "uploads/test_products.csv"

def test_ml_extractor_ai():
    """Prueba completa del sistema ML Extractor con IA"""
    
    print("🧪 INICIANDO PRUEBA DEL ML EXTRACTOR CON IA")
    print("=" * 60)
    
    # Datos del formulario
    form_data = {
        'selected_fields': ['title', 'price', 'description', 'stock'],
        'ai_provider': 'groq',
        'ai_fields': ['title', 'description', 'peso', 'color'],
        'condicion': 'new',
        'moneda': 'ARS'
    }
    
    # Archivos
    files = {}
    
    try:
        # Abrir archivos
        with open(TEMPLATE_FILE, 'rb') as template_f, open(CONTENT_FILE, 'rb') as content_f:
            files = {
                'template_file': ('template.xlsx', template_f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                'content_file': ('products.csv', content_f, 'text/csv')
            }
            
            print(f"📄 Template: {TEMPLATE_FILE}")
            print(f"📋 Productos: {CONTENT_FILE}")
            print(f"🤖 IA Provider: {form_data['ai_provider'].upper()}")
            print(f"🧠 Campos IA: {', '.join(form_data['ai_fields'])}")
            print()
            print("🚀 Enviando petición al servidor...")
            
            # Enviar petición
            response = requests.post(
                f"{BASE_URL}/process",
                data=form_data,
                files=files,
                timeout=60
            )
            
            print(f"📡 Respuesta del servidor: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ PROCESAMIENTO EXITOSO!")
                
                # Buscar información en la respuesta HTML
                response_text = response.text
                
                if "archivo generado exitosamente" in response_text.lower():
                    print("✅ Archivo generado correctamente")
                
                if "debug log" in response_text.lower():
                    print("✅ Debug logs disponibles")
                
                if "productos procesados" in response_text.lower():
                    print("✅ Productos procesados")
                
                # Buscar enlace de descarga
                if "download" in response_text:
                    print("✅ Enlace de descarga disponible")
                
                print()
                print("🎉 PRUEBA COMPLETADA EXITOSAMENTE!")
                print("💡 Ve a la interfaz web para ver los logs detallados")
                
            else:
                print(f"❌ Error en el procesamiento: {response.status_code}")
                print(response.text[:500])
                
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_ml_extractor_ai()
