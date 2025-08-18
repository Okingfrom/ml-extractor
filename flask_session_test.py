#!/usr/bin/env python3
"""
FLASK SESSION TEST - Prueba final completa con sesiones
"""
from flask import Flask, request, session, jsonify
import sys
sys.path.append('/home/keller/ml-extractor')
from auth_system import UserManager

app = Flask(__name__)
app.secret_key = 'test_key_final_2025'
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
        return f"✅ SESIÓN ACTIVA: {session['user_email']} ({session.get('user_type')})"
    return "❌ SIN SESIÓN - Haz POST a /login"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', 'premium@test.com')
    password = request.form.get('password', 'Premium123!')
    
    success, result = user_manager.login_user(email, password, '127.0.0.1')
    
    if success:
        session.permanent = True
        session['user_email'] = email
        session['user_type'] = result.get('account_type', 'free')
        session['logged_in'] = True
        return "✅ LOGIN EXITOSO - Revisar /"
    else:
        return f"❌ LOGIN FALLÓ: {result}", 401

@app.route('/logout')
def logout():
    session.clear()
    return "✅ LOGOUT EXITOSO"

if __name__ == '__main__':
    print("=== FLASK SESSION TEST ===")
    print("curl -X POST http://localhost:5007/login")
    print("curl http://localhost:5007/")
    app.run(debug=False, use_reloader=False, port=5007, host='127.0.0.1')
