#!/usr/bin/env python3
"""
Test simple de Flask con autenticación
"""
from flask import Flask, request, session, jsonify, redirect
from auth_system import user_manager
import os

app = Flask(__name__)
app.secret_key = 'test_secret_key_for_debugging_12345'

@app.route('/')
def home():
    if 'user_id' in session:
        return f"<h1>¡Hola {session.get('first_name')}!</h1><p>Account: {session.get('account_type')}</p><a href='/logout'>Logout</a>"
    else:
        return '<h1>No autenticado</h1><a href="/login">Login</a>'

@app.route('/login')
def login_page():
    return '''
    <form id="loginForm">
        Email: <input type="email" id="email" value="premium@test.com"><br>
        Password: <input type="password" id="password" value="Premium123!"><br>
        <button type="submit">Login</button>
    </form>
    <script>
    document.getElementById('loginForm').onsubmit = function(e) {
        e.preventDefault();
        fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: document.getElementById('email').value,
                password: document.getElementById('password').value
            })
        })
        .then(r => r.json())
        .then(data => {
            if(data.success) {
                alert('Login exitoso!');
                window.location.href = '/';
            } else {
                alert('Error: ' + data.error);
            }
        });
    }
    </script>
    '''

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        success, result = user_manager.login_user(email, password, request.remote_addr)
        
        if success:
            user = result
            session['user_id'] = user['id']
            session['username'] = user['username'] 
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['account_type'] = user['account_type']
            
            return jsonify({
                'success': True,
                'message': f'Bienvenido {user["first_name"]}!'
            })
        else:
            return jsonify({'success': False, 'error': result}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("🧪 Test App iniciando en http://localhost:5005")
    app.run(debug=True, port=5005)
