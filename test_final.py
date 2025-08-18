#!/usr/bin/env python3
from flask import Flask, request, session, jsonify
import sys
import os
sys.path.append('/home/keller/ml-extractor')

# Import auth system
from auth_system import UserManager

app = Flask(__name__)
app.secret_key = 'test_secret_key_2025'
app.config.update(
    SESSION_COOKIE_NAME='ml_test_session',
    SESSION_PERMANENT=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,  # False for HTTP testing
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize user manager
user_manager = UserManager()

@app.route('/')
def home():
    if 'user_email' in session:
        return f"LOGGED IN as {session['user_email']} (type: {session.get('user_type', 'unknown')})"
    return "NOT LOGGED IN - Send POST to /login with email and password"

@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email') or (request.json.get('email') if request.json else None)
        password = request.form.get('password') or (request.json.get('password') if request.json else None)
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
            
        # Authenticate
        success, result = user_manager.login_user(email, password, request.remote_addr or '127.0.0.1')
        if success:
            user_data = result if isinstance(result, dict) else {}
            session.permanent = True
            session['user_email'] = email
            session['user_type'] = user_data.get('account_type', 'free')
            session['logged_in'] = True
            return jsonify({
                'success': True, 
                'message': f'Login successful as {user_data.get("account_type", "free")}',
                'user_type': user_data.get('account_type', 'free')
            })
        else:
            return jsonify({'success': False, 'error': str(result)}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status')
def status():
    return jsonify({
        'logged_in': 'user_email' in session,
        'user_email': session.get('user_email'),
        'user_type': session.get('user_type'),
        'session_keys': list(session.keys())
    })

if __name__ == '__main__':
    print("=== TEST APP STARTING ===")
    print("Login endpoint: POST /login")
    print("Status endpoint: GET /status")
    print("Test credentials: premium@test.com / Premium123!")
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5006)
