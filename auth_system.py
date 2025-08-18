# 🛡️ SISTEMA DE AUTENTICACIÓN Y SEGURIDAD ML EXTRACTOR
# Creado por: Joss Mateo
# Sistema completo de usuarios, seguridad y monetización

import hashlib
import secrets
import sqlite3
import os
import time
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, redirect, url_for, jsonify

# Importaciones condicionales para email
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Importaciones condicionales para SMS
try:
    import requests
    SMS_AVAILABLE = True
except ImportError:
    SMS_AVAILABLE = False

class SecurityManager:
    """🔒 Gestor de seguridad avanzado contra ataques"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.captcha_tokens = {}
        
    def is_ip_blocked(self, ip):
        """Verificar si IP está bloqueada"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
        
    def register_failed_attempt(self, ip):
        """Registrar intento fallido"""
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = {'count': 0, 'last_attempt': datetime.now()}
            
        self.failed_attempts[ip]['count'] += 1
        self.failed_attempts[ip]['last_attempt'] = datetime.now()
        
        # Bloquear después de 5 intentos
        if self.failed_attempts[ip]['count'] >= 5:
            self.blocked_ips[ip] = datetime.now() + timedelta(hours=1)

class DatabaseManager:
    """📊 Gestor de base de datos para usuarios"""
    
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT,
                company_location TEXT,
                user_type TEXT DEFAULT 'seller',
                account_type TEXT DEFAULT 'free',
                is_verified BOOLEAN DEFAULT FALSE,
                verification_code TEXT,
                google_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def hash_password(self, password):
        """Hash seguro de contraseña"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
        
    def verify_password(self, password, hashed):
        """Verificar contraseña"""
        try:
            salt, password_hash = hashed.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
            
    def create_user(self, username, email, phone, first_name, last_name, password, 
                   company_name=None, company_location=None, user_type='seller'):
        """Crear nuevo usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            verification_code = secrets.token_urlsafe(6)
            
            cursor.execute('''
                INSERT INTO users (username, email, phone, first_name, last_name, 
                                 password_hash, company_name, company_location, 
                                 user_type, verification_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, phone, first_name, last_name, password_hash,
                  company_name, company_location, user_type, verification_code))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'verification_code': verification_code}
            
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return {'success': False, 'error': 'El nombre de usuario ya existe'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'El email ya está registrado'}
            elif 'phone' in str(e):
                return {'success': False, 'error': 'El teléfono ya está registrado'}
            else:
                return {'success': False, 'error': 'Error al crear usuario'}
                
    def authenticate_user(self, email, password):
        """Autenticar usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, is_verified, account_type
            FROM users WHERE email = ? AND is_active = TRUE
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[2]):
            if user[3]:  # is_verified
                return {
                    'success': True,
                    'user_id': user[0],
                    'username': user[1],
                    'account_type': user[4]
                }
            else:
                return {'success': False, 'error': 'Cuenta no verificada'}
        else:
            return {'success': False, 'error': 'Credenciales incorrectas'}

class UserManager:
    """👤 Gestor principal de usuarios"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.security = SecurityManager()
        
    def login_required(self, f):
        """Decorador para rutas que requieren login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
        
    def premium_required(self, f):
        """Decorador para funciones premium"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Requiere login', 'premium_required': True})
            if session.get('account_type', 'free') == 'free':
                return jsonify({'error': 'Funcionalidad premium requerida', 'premium_required': True})
            return f(*args, **kwargs)
        return decorated_function

# Instancia global
user_manager = UserManager()
