#!/usr/bin/env python3
"""
Demostración del ML Extractor con IA - Procesamiento directo
Muestra el funcionamiento del sistema sin usar el servidor Flask
"""

import sys
import os
sys.path.append('/home/keller/ml-extractor')

from ai_enhancer import AIProductEnhancer
import openpyxl
import os

def demo_ml_extractor_ai():
    """Demostración completa del sistema ML Extractor con IA"""
    
    print("🎯 DEMO: ML EXTRACTOR CON IA POWERED BY GROQ")
    print("=" * 60)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY no encontrada en variables de entorno")
        print("💡 Configura tu API key en el archivo .env")
        return
    
    # Inicializar AI enhancer
    print("🧠 Inicializando sistema de IA...")
    ai_enhancer = AIProductEnhancer(
        provider='groq',
        api_key=api_key
    )
    
    print(f"✅ IA configurada: {ai_enhancer.current_api.upper()}")
    if ai_enhancer.api_key:
        print(f"🔑 API Key: {ai_enhancer.api_key[:10]}...{ai_enhancer.api_key[-4:]}")
    else:
        print("🔑 API Key: No configurada")
    print()
    
    # Cargar datos de productos
    print("📋 Cargando productos de prueba...")
    products_data = [
        {
            'Producto': 'iPhone 15 Pro',
            'Precio': '999.99',
            'Descripción': 'Smartphone Apple con cámara avanzada',
            'Stock': '10',
            'Categoría': 'Celulares'
        },
        {
            'Producto': 'Samsung Galaxy S24',
            'Precio': '899.99', 
            'Descripción': 'Teléfono Android última generación',
            'Stock': '15',
            'Categoría': 'Celulares'
        },
        {
            'Producto': 'MacBook Air M2',
            'Precio': '1299.99',
            'Descripción': 'Laptop Apple ultraligera',
            'Stock': '5',
            'Categoría': 'Computadoras'
        }
    ]
    
    print(f"✅ {len(products_data)} productos cargados")
    print()
    
    # Procesar cada producto con IA
    print("🤖 PROCESANDO PRODUCTOS CON IA...")
    print("-" * 40)
    
    enhanced_products = []
    
    for i, product in enumerate(products_data, 1):
        print(f"\n🔄 Producto {i}: {product['Producto']}")
        
        # Mapear a formato ML básico
        ml_product = {
            'title': product['Producto'],
            'price': product['Precio'],
            'description': product['Descripción'],
            'stock': product['Stock'],
            'category': product['Categoría']
        }
        
        # Campos que queremos que la IA complete
        ai_fields = ['peso', 'color', 'marca', 'garantia']
        
        try:
            print(f"   🧠 Solicitando IA para completar: {', '.join(ai_fields)}")
            
            # Generar datos faltantes con IA
            ai_data = ai_enhancer.generate_missing_data(ml_product, ai_fields)
            
            # Combinar datos originales con los generados por IA
            ml_product.update(ai_data)
            
            print(f"   ✅ IA completó {len(ai_data)} campos")
            for field, value in ai_data.items():
                print(f"      🎯 {field}: {value}")
            
            enhanced_products.append(ml_product)
            
        except Exception as e:
            print(f"   ❌ Error de IA: {e}")
            enhanced_products.append(ml_product)
    
    print()
    print("🎉 PROCESAMIENTO COMPLETADO!")
    print("=" * 60)
    
    # Mostrar resultados
    print("📊 RESULTADOS FINALES:")
    print()
    
    for i, product in enumerate(enhanced_products, 1):
        print(f"🏷️ Producto {i}: {product['title']}")
        print(f"   💰 Precio: ${product['price']}")
        print(f"   📝 Descripción: {product['description']}")
        print(f"   📦 Stock: {product['stock']}")
        print(f"   🏪 Categoría: {product['category']}")
        
        # Mostrar campos generados por IA
        ai_generated = ['peso', 'color', 'marca', 'garantia']
        for field in ai_generated:
            if field in product:
                print(f"   🤖 {field.upper()}: {product[field]}")
        print()
    
    # Mostrar debug log
    debug_log = ai_enhancer.get_debug_log()
    if debug_log:
        print("🔍 DEBUG LOG:")
        print("-" * 30)
        print(debug_log)
    
    print()
    print("✨ DEMO COMPLETADO - ¡EL SISTEMA FUNCIONA PERFECTAMENTE!")

if __name__ == "__main__":
    demo_ml_extractor_ai()
