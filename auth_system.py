#!/usr/bin/env python3
"""
Sistema de Autenticación Completo para ML Extractor
Incluye seguridad avanzada, gestión de usuarios y validaciones premium
"""

import sqlite3
import hashlib
import secrets
import time
from functools import wraps
from datetime import datetime, timedelta
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import session, request, redirect, url_for, jsonify, flash
import json

class SecurityManager:
    """Gestiona la seguridad y protección anti-bots"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.max_attempts = 5
        self.block_duration = 300  # 5 minutos
    
    def is_ip_blocked(self, ip):
        """Verifica si una IP está bloqueada"""
        if ip in self.blocked_ips:
            if time.time() - self.blocked_ips[ip] > self.block_duration:
                del self.blocked_ips[ip]
                if ip in self.failed_attempts:
                    del self.failed_attempts[ip]
                return False
            return True
        return False
    
    def record_failed_attempt(self, ip):
        """Registra un intento fallido"""
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = 0
        
        self.failed_attempts[ip] += 1
        
        if self.failed_attempts[ip] >= self.max_attempts:
            self.blocked_ips[ip] = time.time()
            print(f"🚫 IP bloqueada: {ip} - {self.failed_attempts[ip]} intentos fallidos")
    
    def reset_attempts(self, ip):
        """Resetea los intentos fallidos para una IP"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]

class DatabaseManager:
    """Gestiona todas las operaciones de base de datos"""
    
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos con todas las tablas necesarias"""
        conn = sqlite3.connect(self.db_name)
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
        
        # Tabla de sesiones activas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de logs de actividad
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_name)
    
    def create_user(self, user_data):
        """Crea un nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, phone, first_name, last_name, 
                                 password_hash, company_name, company_location, 
                                 user_type, account_type, verification_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', user_data)
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email):
        """Obtiene un usuario por email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'phone': result[3],
                'first_name': result[4],
                'last_name': result[5],
                'password_hash': result[6],
                'company_name': result[7],
                'company_location': result[8],
                'user_type': result[9],
                'account_type': result[10],
                'is_verified': result[11],
                'verification_code': result[12],
                'google_id': result[13],
                'created_at': result[14],
                'last_login': result[15],
                'is_active': result[16]
            }
        return None
    
    def update_user_verification(self, email, is_verified=True):
        """Actualiza el estado de verificación del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET is_verified = ?, verification_code = NULL 
            WHERE email = ?
        ''', (is_verified, email))
        
        conn.commit()
        conn.close()
    
    def update_last_login(self, user_id):
        """Actualiza la última fecha de login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def log_activity(self, user_id, action, details=None, ip_address=None):
        """Registra actividad del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_logs (user_id, action, details, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, details, ip_address))
        
        conn.commit()
        conn.close()

class NotificationManager:
    """Gestiona el envío de notificaciones y emails"""
    
    def __init__(self, smtp_server=None, smtp_port=587, email_user=None, email_password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_password = email_password
    
    def send_verification_email(self, email, verification_code, name):
        """Envía email de verificación (simulado si no hay configuración SMTP)"""
        if not self.smtp_server:
            print(f"📧 EMAIL SIMULADO para {email}:")
            print(f"   Código de verificación: {verification_code}")
            print(f"   Hola {name}, verifica tu cuenta con este código")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = email
            msg['Subject'] = "Verifica tu cuenta en ML Extractor"
            
            body = f"""
            Hola {name},
            
            Gracias por registrarte en ML Extractor.
            Tu código de verificación es: {verification_code}
            
            Este código expira en 10 minutos.
            
            ¡Bienvenido al futuro del comercio electrónico!
            
            Equipo ML Extractor
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

class UserManager:
    """Gestiona la lógica principal de usuarios y autenticación"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.security = SecurityManager()
        self.notifications = NotificationManager()
    
    def hash_password(self, password):
        """Genera un hash seguro de la contraseña"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, password_hash):
        """Verifica una contraseña contra su hash"""
        try:
            salt, hash_value = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except:
            return False
    
    def validate_password_strength(self, password):
        """Valida la fortaleza de la contraseña"""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "Debe contener al menos una mayúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "Debe contener al menos una minúscula"
        
        if not re.search(r'\d', password):
            return False, "Debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*]', password):
            return False, "Debe contener al menos un símbolo (!@#$%^&*)"
        
        return True, "Contraseña válida"
    
    def validate_email(self, email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone):
        """Valida formato de teléfono"""
        # Formato: +país + número (ej: +573001234567)
        pattern = r'^\+\d{10,15}$'
        return bool(re.match(pattern, phone))
    
    def generate_verification_code(self):
        """Genera código de verificación de 6 dígitos"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def register_user(self, form_data, ip_address):
        """Registra un nuevo usuario"""
        # Validar datos
        if not self.validate_email(form_data['email']):
            return False, "Email inválido"
        
        if not self.validate_phone(form_data['phone']):
            return False, "Teléfono inválido (formato: +país + número)"
        
        valid_password, password_message = self.validate_password_strength(form_data['password'])
        if not valid_password:
            return False, password_message
        
        # Verificar si el usuario ya existe
        existing_user = self.db.get_user_by_email(form_data['email'])
        if existing_user:
            return False, "Este email ya está registrado"
        
        # Generar código de verificación
        verification_code = self.generate_verification_code()
        
        # Preparar datos del usuario
        user_data = (
            form_data['username'],
            form_data['email'],
            form_data['phone'],
            form_data['first_name'],
            form_data['last_name'],
            self.hash_password(form_data['password']),
            form_data.get('company_name'),
            form_data.get('company_location'),
            form_data['user_type'],
            form_data.get('account_type', 'free'),
            verification_code
        )
        
        # Crear usuario
        user_id = self.db.create_user(user_data)
        if not user_id:
            return False, "Error creando usuario"
        
        # Enviar email de verificación
        self.notifications.send_verification_email(
            form_data['email'], 
            verification_code, 
            form_data['first_name']
        )
        
        # Log de actividad
        self.db.log_activity(user_id, 'user_registered', None, ip_address)
        
        return True, "Usuario registrado exitosamente. Revisa tu email para verificar la cuenta."
    
    def login_user(self, email, password, ip_address):
        """Autentica un usuario"""
        # Verificar si la IP está bloqueada
        if self.security.is_ip_blocked(ip_address):
            return False, "IP bloqueada por múltiples intentos fallidos. Intenta en 5 minutos."
        
        # Obtener usuario
        user = self.db.get_user_by_email(email)
        if not user:
            self.security.record_failed_attempt(ip_address)
            return False, "Credenciales incorrectas"
        
        # Verificar contraseña
        if not self.verify_password(password, user['password_hash']):
            self.security.record_failed_attempt(ip_address)
            return False, "Credenciales incorrectas"
        
        # Verificar si la cuenta está verificada
        if not user['is_verified']:
            return False, "Cuenta no verificada. Revisa tu email."
        
        # Verificar si la cuenta está activa
        if not user['is_active']:
            return False, "Cuenta desactivada. Contacta soporte."
        
        # Login exitoso
        self.security.reset_attempts(ip_address)
        self.db.update_last_login(user['id'])
        self.db.log_activity(user['id'], 'user_login', None, ip_address)
        
        return True, user
    
    def verify_account(self, email, verification_code):
        """Verifica una cuenta con el código"""
        user = self.db.get_user_by_email(email)
        if not user:
            return False, "Usuario no encontrado"
        
        if user['verification_code'] != verification_code:
            return False, "Código de verificación incorrecto"
        
        # Actualizar como verificado
        self.db.update_user_verification(email, True)
        self.db.log_activity(user['id'], 'account_verified')
        
        return True, "Cuenta verificada exitosamente"
    
    def create_or_update_google_user(self, google_data):
        """Crea o actualiza un usuario de Google OAuth"""
        try:
            # Buscar usuario existente por email o google_id
            user = self.db.get_user_by_email(google_data['email'])
            
            if user:
                # Usuario existe, actualizar google_id si no lo tiene
                if not user['google_id']:
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE users SET google_id = ?, is_verified = TRUE 
                        WHERE email = ?
                    ''', (google_data['google_id'], google_data['email']))
                    conn.commit()
                    conn.close()
                    
                    # Actualizar datos del usuario
                    user['google_id'] = google_data['google_id']
                    user['is_verified'] = True
                
                return True, user
            else:
                # Crear nuevo usuario con Google
                username = google_data['email'].split('@')[0]
                
                # Generar contraseña temporal (no se usará)
                temp_password = secrets.token_urlsafe(32)
                password_hash = self.hash_password(temp_password)
                
                user_data = (
                    username,
                    google_data['email'],
                    '000000000',  # Teléfono temporal
                    google_data['first_name'],
                    google_data['last_name'],
                    password_hash,
                    None,  # company_name
                    None,  # company_location
                    'seller',  # user_type
                    'free',  # account_type por defecto
                    None   # verification_code (no necesario para Google)
                )
                
                user_id = self.db.create_user(user_data)
                if user_id:
                    # Actualizar con google_id y verificado
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE users SET google_id = ?, is_verified = TRUE 
                        WHERE id = ?
                    ''', (google_data['google_id'], user_id))
                    conn.commit()
                    conn.close()
                    
                    # Obtener usuario completo
                    user = self.db.get_user_by_email(google_data['email'])
                    self.db.log_activity(user_id, 'google_registration', 'Registro con Google OAuth')
                    
                    return True, user
                else:
                    return False, "Error creando usuario de Google"
                    
        except Exception as e:
            print(f"❌ Error en Google OAuth: {e}")
            return False, "Error en autenticación con Google"
    
    def login_with_google(self, google_data, ip_address=None):
        """Realiza login con datos de Google"""
        try:
            success, user = self.create_or_update_google_user(google_data)
            
            if success:
                # Actualizar último login
                self.db.update_last_login(user['id'])
                self.db.log_activity(user['id'], 'google_login', None, ip_address)
                
                return True, user
            else:
                return False, user  # user contiene el mensaje de error
                
        except Exception as e:
            print(f"❌ Error en login de Google: {e}")
            return False, "Error en autenticación con Google"

# Decoradores para proteger rutas
def login_required(f):
    """Decorador que requiere login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def premium_required(f):
    """Decorador que requiere cuenta premium"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if session.get('account_type') != 'premium':
            return jsonify({
                'success': False,
                'error': 'Esta funcionalidad requiere cuenta Premium'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador que requiere permisos de admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        if session.get('user_type') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acceso denegado'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Instancia global del gestor de usuarios
user_manager = UserManager()
