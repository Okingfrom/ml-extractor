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
            SELECT id, username, email, first_name, last_name, password_hash, is_verified, account_type, user_type
            FROM users WHERE email = ? AND is_active = TRUE
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[5]):  # password_hash is now at index 5
            if user[6]:  # is_verified is now at index 6
                return {
                    'success': True,
                    'id': user[0],           # Add 'id' key for compatibility
                    'user_id': user[0],      # Keep 'user_id' for backward compatibility
                    'username': user[1],
                    'email': user[2],
                    'first_name': user[3],
                    'last_name': user[4],
                    'account_type': user[7],
                    'user_type': user[8]
                }
            else:
                return {'success': False, 'error': 'Cuenta no verificada'}
        else:
            return {'success': False, 'error': 'Credenciales incorrectas'}
    
    def get_user_by_email(self, email):
        """Obtener usuario por email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, first_name, last_name, account_type, is_verified
            FROM users WHERE email = ? AND is_active = TRUE
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1], 
                'email': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'account_type': user[5],
                'is_verified': user[6]
            }
        return None
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def log_activity(self, user_id, activity_type, details, ip_address):
        """Registrar actividad del usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Crear tabla de actividades si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO user_activities (user_id, activity_type, details, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, activity_type, details, ip_address))
        
        conn.commit()
        conn.close()

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
    
    def login_user(self, email, password, ip_address):
        """Método para hacer login de usuario con validación de seguridad"""
        # Verificar si la IP está bloqueada
        if self.security.is_ip_blocked(ip_address):
            return False, {'error': 'IP bloqueada temporalmente por múltiples intentos fallidos'}
        
        # Intentar autenticar
        result = self.db.authenticate_user(email, password)
        
        if result['success']:
            # Login exitoso - limpiar intentos fallidos
            if ip_address in self.security.failed_attempts:
                del self.security.failed_attempts[ip_address]
            
            return True, result
        else:
            # Login fallido - registrar intento
            self.security.register_failed_attempt(ip_address)
            return False, result
    
    def register_user(self, data, ip_address):
        """Método para registrar nuevo usuario"""
        try:
            result = self.db.create_user(
                data['username'], data['email'], data['phone'],
                data['first_name'], data['last_name'], data['password'],
                data.get('company_name'), data.get('company_location'),
                data.get('user_type', 'seller')
            )
            if result['success']:
                return True, 'Usuario registrado exitosamente'
            else:
                return False, result['error']
        except Exception as e:
            return False, f'Error al registrar usuario: {str(e)}'
    
    def verify_account(self, email, code):
        """Verificar cuenta de usuario"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, verification_code FROM users 
            WHERE email = ? AND is_active = TRUE
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user and user[1] == code:
            cursor.execute('''
                UPDATE users SET is_verified = TRUE, verification_code = NULL
                WHERE id = ?
            ''', (user[0],))
            conn.commit()
            conn.close()
            return True, 'Cuenta verificada exitosamente'
        else:
            conn.close()
            return False, 'Código de verificación inválido'
    
    def generate_verification_code(self):
        """Generar código de verificación"""
        return secrets.token_urlsafe(6)
    
    def login_with_google(self, google_data, ip_address):
        """Login con Google OAuth"""
        # Implementación básica - se puede expandir
        try:
            email = google_data.get('email')
            if not email:
                return False, {'error': 'Email no encontrado en datos de Google'}
            
            # Buscar usuario existente
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, account_type FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user:
                return True, {
                    'success': True,
                    'user_id': user[0],
                    'username': user[1],
                    'account_type': user[2]
                }
            else:
                conn.close()
                return False, {'error': 'Usuario no encontrado. Debe registrarse primero.'}
                
        except Exception as e:
            return False, {'error': f'Error en login con Google: {str(e)}'}
    
    @property
    def notifications(self):
        """Propiedad para compatibilidad - retorna un objeto simple"""
        class NotificationManager:
            def send_verification_email(self, email, code, first_name="Usuario"):
                # Implementación básica - se puede expandir con email real
                print(f"[MOCK EMAIL] Enviando código {code} a {email} para {first_name}")
                return True
        
        return NotificationManager()

# Instancia global
user_manager = UserManager()

# Funciones de conveniencia para importación directa
def login_required(f):
    """Decorador standalone para rutas que requieren login"""
    return user_manager.login_required(f)

def premium_required(f):
    """Decorador standalone para funciones premium"""
    return user_manager.premium_required(f)

def create_user(username, email, phone, first_name, last_name, password, 
               company_name=None, company_location=None, user_type='seller'):
    """Función standalone para crear usuario"""
    return user_manager.db.create_user(username, email, phone, first_name, last_name, 
                                      password, company_name, company_location, user_type)

def authenticate(email, password):
    """Función standalone para autenticar usuario"""
    return user_manager.db.authenticate_user(email, password)

def is_premium(user_id=None):
    """Verificar si el usuario actual es premium"""
    if user_id is None:
        account_type = session.get('account_type', 'free')
    else:
        # Obtener account_type de la base de datos para el user_id
        conn = sqlite3.connect(user_manager.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT account_type FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        account_type = result[0] if result else 'free'
    
    return account_type == 'premium'

# Exportar funciones principales para compatibilidad
__all__ = ['user_manager', 'login_required', 'premium_required', 'create_user', 'authenticate', 'is_premium']
