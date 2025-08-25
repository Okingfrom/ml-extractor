import functools
from typing import Tuple, Dict, Any

# Simple in-memory store for users and activities for local testing
class _InMemoryDB:
    def __init__(self):
        self.users = {}
        self.activities = []
        # Seed a demo premium user
        self.users['demo@example.com'] = {
            'id': 1,
            'username': 'demo',
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User',
            'account_type': 'premium',
            'user_type': 'premium',
            'password': 'password'
        }

    def get_connection(self):  # placeholder for API compatibility
        return self

    def get_user_by_email(self, email):
        return self.users.get(email)

    def log_activity(self, user_id, action, details, ip):
        self.activities.append({
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip': ip
        })

class _Notifications:
    def send_verification_email(self, email, code):
        # No-op for local testing
        pass

class UserManagerStub:
    def __init__(self):
        self.db = _InMemoryDB()
        self.notifications = _Notifications()

    # Interface methods expected by the app
    def login_user(self, email, password, ip) -> Tuple[bool, Any]:
        user = self.db.get_user_by_email(email)
        if not user or password != user.get('password'):
            return False, 'Credenciales inválidas'
        self.db.log_activity(user['id'], 'user_login', None, ip)
        return True, user

    def register_user(self, data: Dict[str, Any], ip) -> Tuple[bool, str]:
        email = data.get('email')
        if not email:
            return False, 'Email requerido'
        if email in self.db.users:
            return False, 'Usuario ya existe'
        new_id = max((u['id'] for u in self.db.users.values()), default=0) + 1
        user = {
            'id': new_id,
            'username': data.get('username', email.split('@')[0]),
            'email': email,
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'account_type': 'free',
            'user_type': 'free',
            'password': data.get('password', 'password')
        }
        self.db.users[email] = user
        self.db.log_activity(user['id'], 'user_register', None, ip)
        return True, 'Registro exitoso'

    def verify_account(self, email, code) -> Tuple[bool, str]:
        # Always succeed locally
        return True, 'Cuenta verificada'

    def generate_verification_code(self):
        return '000000'

    def login_with_google(self, google_data, ip):
        email = google_data.get('email')
        user = self.db.get_user_by_email(email)
        if not user:
            # auto-register
            user = {
                'id': max((u['id'] for u in self.db.users.values()), default=0) + 1,
                'username': google_data.get('name', 'google_user'),
                'email': email,
                'first_name': google_data.get('given_name', ''),
                'last_name': google_data.get('family_name', ''),
                'account_type': 'free',
                'user_type': 'free',
                'password': ''
            }
            self.db.users[email] = user
        self.db.log_activity(user['id'], 'google_login', None, ip)
        return True, user

user_manager = UserManagerStub()

# Decorators
from flask import session, redirect, url_for, flash

def login_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('Necesitas iniciar sesión', 'error')
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

def premium_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get('account_type') != 'premium':
            flash('Función solo para usuarios premium', 'warning')
            return redirect(url_for('index'))
        return fn(*args, **kwargs)
    return wrapper
