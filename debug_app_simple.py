#!/usr/bin/env python3
"""
Aplicación simplificada para debug de sesiones
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, session, jsonify, redirect, render_template_string

# Importar el sistema de autenticación
from auth_system import user_manager

app = Flask(__name__)
app.secret_key = 'debug_secret_key_for_testing'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuración adicional de sesiones
app.config['SESSION_COOKIE_SECURE'] = False  # Para desarrollo (HTTP)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Template HTML simple
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Debug Login</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .form-group { margin: 10px 0; }
        input { padding: 8px; width: 200px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h1>Debug Login Form</h1>
    <form method="POST" action="/login">
        <div class="form-group">
            <label>Email:</label><br>
            <input type="email" name="email" value="premium@test.com" required>
        </div>
        <div class="form-group">
            <label>Password:</label><br>
            <input type="password" name="password" value="Premium123!" required>
        </div>
        <div class="form-group">
            <button type="submit">Login</button>
        </div>
    </form>
    
    <h2>Debug Info</h2>
    <p>Session Keys: {{ session_keys }}</p>
    <p>User ID: {{ user_id }}</p>
    
    <h2>Links</h2>
    <a href="/debug-session">Ver Debug Session</a> | 
    <a href="/dashboard">Dashboard (protegido)</a> |
    <a href="/logout">Logout</a>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
    <h1>Dashboard - Login Exitoso!</h1>
    <p>User ID: {{ user_id }}</p>
    <p>Username: {{ username }}</p>
    <p>Email: {{ email }}</p>
    <p>Account Type: {{ account_type }}</p>
    <p>Session completa: {{ session_data }}</p>
    <br>
    <a href="/logout">Logout</a> | <a href="/debug-session">Debug Session</a>
</body>
</html>
'''

@app.route('/')
def home():
    """Ruta principal"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login simplificado"""
    if request.method == 'GET':
        return render_template_string(LOGIN_TEMPLATE, 
                                    session_keys=list(session.keys()),
                                    user_id=session.get('user_id', 'None'))
    
    # POST - procesar login
    email = request.form.get('email')
    password = request.form.get('password')
    
    print(f"[DEBUG] Intentando login: {email}")
    
    success, result = user_manager.login_user(email, password, request.remote_addr)
    
    if success:
        user = result
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['first_name'] = user['first_name']
        session['last_name'] = user['last_name']
        session['account_type'] = user['account_type']
        session['user_type'] = user['user_type']
        
        print(f"[DEBUG] Login exitoso - Session keys: {list(session.keys())}")
        print(f"[DEBUG] User ID guardado: {session.get('user_id')}")
        print(f"[DEBUG] Cookies: {dict(request.cookies)}")
        
        return redirect('/dashboard')
    else:
        return f"<h1>Error: {result}</h1><a href='/login'>Volver</a>"

@app.route('/dashboard')
def dashboard():
    """Dashboard protegido"""
    if 'user_id' not in session:
        print(f"[DEBUG] Dashboard - Acceso denegado. Session keys: {list(session.keys())}")
        print(f"[DEBUG] Dashboard - Cookies recibidas: {dict(request.cookies)}")
        return redirect('/login')
    
    print(f"[DEBUG] Dashboard - Acceso permitido. User ID: {session.get('user_id')}")
    
    return render_template_string(DASHBOARD_TEMPLATE,
                                user_id=session.get('user_id'),
                                username=session.get('username'),
                                email=session.get('email'),
                                account_type=session.get('account_type'),
                                session_data=dict(session))

@app.route('/debug-session')
def debug_session():
    """Debug de sesión"""
    print(f"[DEBUG] Debug session - Session keys: {list(session.keys())}")
    print(f"[DEBUG] Debug session - Session dict: {dict(session)}")
    print(f"[DEBUG] Debug session - Cookies: {dict(request.cookies)}")
    
    return f"""
    <h1>Debug de Sesion</h1>
    <p><strong>Session Keys:</strong> {list(session.keys())}</p>
    <p><strong>Session Dict:</strong> {dict(session)}</p>
    <p><strong>Cookies:</strong> {dict(request.cookies)}</p>
    <p><strong>Request Headers:</strong> {dict(request.headers)}</p>
    <br>
    <a href="/login">Login</a> | <a href="/dashboard">Dashboard</a>
    """

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("Iniciando app de debug en http://localhost:5004")
    app.run(debug=True, host='localhost', port=5004)
