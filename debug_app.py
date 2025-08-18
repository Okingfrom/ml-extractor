#!/usr/bin/env python3
"""
Debug script para encontrar el problema en app_improved.py
"""
import sys
import traceback

print("🔍 Iniciando diagnóstico de app_improved.py...")

try:
    print("📦 1. Importando módulo...")
    import app_improved
    print("✅ Importación exitosa")
    
    print("📱 2. Verificando app Flask...")
    app = app_improved.app
    print(f"✅ App Flask: {type(app)}")
    
    print("🚀 3. Intentando ejecutar app...")
    app.run(debug=True, host='localhost', port=5003)
    
except KeyboardInterrupt:
    print("⚠️ Interrumpido por usuario (Ctrl+C)")
except Exception as e:
    print(f"❌ ERROR ENCONTRADO: {e}")
    print("📋 Traceback completo:")
    traceback.print_exc()
    print("\n🔧 Analizando el error...")
    
    # Análisis del error
    error_str = str(e)
    if "Address already in use" in error_str:
        print("💡 CAUSA: Puerto 5003 ya está en uso")
        print("🛠️ SOLUCIÓN: Cambiar puerto o matar proceso existente")
    elif "Permission denied" in error_str:
        print("💡 CAUSA: Permisos insuficientes")
        print("🛠️ SOLUCIÓN: Verificar permisos del puerto")
    elif "Import" in error_str:
        print("💡 CAUSA: Error de importación")
        print("🛠️ SOLUCIÓN: Verificar dependencias")
    else:
        print("💡 CAUSA: Error desconocido - revisar traceback arriba")
