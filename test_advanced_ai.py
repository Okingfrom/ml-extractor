#!/usr/bin/env python3
"""
Prueba avanzada del ML Extractor con IA - Datos complejos y precisos
Demuestra el sistema con productos reales y configuración optimizada
"""

import sys
import os
import csv
sys.path.append('/home/keller/ml-extractor')

from ai_enhancer import AIProductEnhancer
import json

def test_complex_products():
    """Prueba con productos complejos y IA optimizada"""
    
    print("🎯 PRUEBA AVANZADA: ML EXTRACTOR CON DATOS COMPLEJOS")
    print("=" * 70)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY no encontrada en variables de entorno")
        print("💡 Crea un archivo .env con: GROQ_API_KEY=tu_api_key_aqui")
        return
    
    # Inicializar AI enhancer con configuración optimizada
    print("🧠 Inicializando IA optimizada...")
    ai_enhancer = AIProductEnhancer(
        provider='groq',
        api_key=api_key
    )
    
    print(f"✅ IA configurada: {ai_enhancer.current_api.upper()}")
    print(f"🔧 Configuración: Mixtral-8x7b, temperatura 0.1, max_tokens 1000")
    print()
    
    # Cargar productos complejos desde CSV
    print("📋 Cargando productos complejos...")
    products_data = []
    
    try:
        with open('/home/keller/ml-extractor/test_products_complex.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            products_data = list(reader)
        
        print(f"✅ {len(products_data)} productos cargados desde CSV")
        print()
        
        # Mostrar productos cargados
        print("📦 PRODUCTOS A PROCESAR:")
        for i, product in enumerate(products_data[:3], 1):  # Solo mostrar los primeros 3
            print(f"   {i}. {product['Nombre del Producto'][:50]}...")
        print(f"   ... y {len(products_data)-3} más")
        print()
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo de productos complejos")
        return
    
    # Procesar productos con IA avanzada
    print("🤖 PROCESANDO CON IA OPTIMIZADA...")
    print("-" * 50)
    
    enhanced_products = []
    successful_ai_calls = 0
    
    for i, product in enumerate(products_data[:5], 1):  # Procesar solo los primeros 5
        print(f"\n🔄 Producto {i}: {product['Nombre del Producto'][:40]}...")
        
        # Mapear a formato ML
        ml_product = {
            'title': product['Nombre del Producto'],
            'price': product['Precio Base'],
            'description': product['Información'],
            'stock': product['Inventario'],
            'category': product['Sector'],
            'material': product.get('Material', ''),
            'dimensions': product.get('Dimensiones', ''),
            'origin': product.get('Origen', '')
        }
        
        # Campos específicos para IA
        ai_fields = [
            'codigo_universal',  # EAN-13
            'marca',            # Marca extraída
            'modelo',           # Modelo inferido  
            'peso',             # Peso estimado
            'color',            # Color principal
            'garantia'          # Garantía estándar
        ]
        
        try:
            print(f"   🧠 Consultando IA para: {', '.join(ai_fields)}")
            
            # Generar datos con IA optimizada
            ai_data = ai_enhancer.generate_missing_data(ml_product, ai_fields)
            
            if ai_data and len(ai_data) > 0:
                ml_product.update(ai_data)
                successful_ai_calls += 1
                
                print(f"   ✅ IA generó {len(ai_data)} campos:")
                for field, value in ai_data.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"      🎯 {field}: {value[:47]}...")
                    else:
                        print(f"      🎯 {field}: {value}")
            else:
                print(f"   ⚠️  IA no generó datos - usando fallback")
            
            enhanced_products.append(ml_product)
            
        except Exception as e:
            print(f"   ❌ Error de IA: {e}")
            enhanced_products.append(ml_product)
    
    print()
    print("🎉 PROCESAMIENTO COMPLETADO!")
    print("=" * 70)
    
    # Estadísticas
    print("📊 ESTADÍSTICAS:")
    print(f"   📦 Productos procesados: {len(enhanced_products)}")
    print(f"   🧠 Llamadas IA exitosas: {successful_ai_calls}/{len(enhanced_products)}")
    print(f"   📈 Tasa de éxito IA: {(successful_ai_calls/len(enhanced_products)*100):.1f}%")
    print()
    
    # Mostrar resultados detallados de los primeros 2 productos
    print("🏆 RESULTADOS DETALLADOS (primeros 2 productos):")
    print("-" * 50)
    
    for i, product in enumerate(enhanced_products[:2], 1):
        print(f"\n📱 PRODUCTO {i}: {product['title'][:30]}...")
        print(f"   💰 Precio: ${product['price']}")
        print(f"   📝 Descripción: {product['description'][:80]}...")
        print(f"   📦 Stock: {product['stock']} | Categoría: {product['category']}")
        
        # Campos generados por IA
        ai_generated = ['codigo_universal', 'marca', 'modelo', 'peso', 'color', 'garantia']
        for field in ai_generated:
            if field in product and product[field]:
                value = str(product[field])
                if len(value) > 40:
                    print(f"   🤖 {field.upper()}: {value[:37]}...")
                else:
                    print(f"   🤖 {field.upper()}: {value}")
    
    # Mostrar debug log completo
    debug_log = ai_enhancer.get_debug_log()
    if debug_log:
        print("\n🔍 DEBUG LOG COMPLETO:")
        print("-" * 30)
        print(debug_log)
    
    print()
    print("✨ PRUEBA AVANZADA COMPLETADA")
    print("💡 La IA puede procesar productos complejos con información detallada!")

if __name__ == "__main__":
    test_complex_products()
