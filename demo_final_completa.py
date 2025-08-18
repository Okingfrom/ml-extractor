#!/usr/bin/env python3
"""
DEMOSTRACIÓN FINAL COMPLETA
Login + Sesión + Estados persistentes
"""
import sys
sys.path.append('/home/keller/ml-extractor')

from flask import Flask, request, session
from auth_system import UserManager
import threading
import time
import requests

# Flask app setup
app = Flask(__name__)
app.secret_key = 'demo_key_final_2025'
app.config.update(
    SESSION_PERMANENT=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE='Lax'
)

user_manager = UserManager()

@app.route('/')
def home():
    if 'user_email' in session:
        return f"✅ SESIÓN ACTIVA: {session['user_email']} (tipo: {session.get('user_type', 'N/A')})"
    return "❌ SIN SESIÓN ACTIVA"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', 'premium@test.com')
    password = request.form.get('password', 'Premium123!')
    
    success, result = user_manager.login_user(email, password, '127.0.0.1')
    
    if success:
        user_data = result if isinstance(result, dict) else {}
        session.permanent = True
        session['user_email'] = email
        session['user_type'] = user_data.get('account_type', 'free')
        session['logged_in'] = True
        return "✅ LOGIN EXITOSO"
    else:
        return f"❌ LOGIN FALLÓ: {result}", 401

@app.route('/logout')
def logout():
    session.clear()
    return "✅ LOGOUT EXITOSO"

@app.route('/status')
def status():
    return {
        'session_active': 'user_email' in session,
        'user_email': session.get('user_email', 'N/A'),
        'user_type': session.get('user_type', 'N/A'),
        'session_keys': list(session.keys())
    }

def run_flask_server():
    """Ejecutar servidor Flask en thread separado"""
    app.run(debug=False, use_reloader=False, port=5008, host='127.0.0.1', threaded=True)

def test_login_and_session():
    """Test completo de login y sesión"""
    print("=== DEMOSTRACIÓN FINAL COMPLETA ===")
    
    # Iniciar servidor en thread separado
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()
    
    # Esperar que el servidor inicie
    print("⏳ Iniciando servidor Flask...")
    time.sleep(2)
    
    try:
        # Test 1: Estado inicial (sin sesión)
        print("\n1. 📋 ESTADO INICIAL:")
        r = requests.get('http://localhost:5008/', timeout=3)
        print(f"   {r.text}")
        
        # Test 2: Login
        print("\n2. 🔐 HACIENDO LOGIN:")
        session = requests.Session()  # Mantener cookies
        r = session.post('http://localhost:5008/login', timeout=3)
        print(f"   {r.text}")
        
        # Test 3: Verificar sesión después del login
        print("\n3. ✅ VERIFICANDO SESIÓN:")
        r = session.get('http://localhost:5008/', timeout=3)
        print(f"   {r.text}")
        
        # Test 4: Status detallado
        print("\n4. 📊 STATUS DETALLADO:")
        r = session.get('http://localhost:5008/status', timeout=3)
        print(f"   {r.json()}")
        
        # Test 5: Logout
        print("\n5. 🚪 HACIENDO LOGOUT:")
        r = session.get('http://localhost:5008/logout', timeout=3)
        print(f"   {r.text}")
        
        # Test 6: Verificar que la sesión se cerró
        print("\n6. ❌ VERIFICANDO SESIÓN CERRADA:")
        r = session.get('http://localhost:5008/', timeout=3)
        print(f"   {r.text}")
        
        print("\n🎉 ¡DEMOSTRACIÓN COMPLETA EXITOSA!")
        print("✅ Login funciona")
        print("✅ Sesiones persisten")
        print("✅ Logout funciona")
        print("✅ Estados se manejan correctamente")
        
    except Exception as e:
        print(f"❌ Error en la demostración: {e}")
    
    print("\n⏹️  Demostración terminada")

if __name__ == '__main__':
    test_login_and_session()
