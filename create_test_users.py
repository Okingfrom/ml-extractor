#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en ML Extractor
"""

import sqlite3
import hashlib
import secrets

def create_test_users():
    """Crear usuarios de prueba"""
    
    def hash_password(password):
        """Hash seguro de contraseña"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    # Conectar a la base de datos
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Crear tabla si no existe
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
    
    print("🔑 Creando usuario PREMIUM de prueba...")
    try:
        premium_password_hash = hash_password("Premium123!")
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, email, phone, first_name, last_name, 
                                        password_hash, company_name, company_location, 
                                        user_type, account_type, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("admin_premium", "premium@test.com", "+573001234567", "Admin", "Premium",
              premium_password_hash, "ML Extractor Pro", "Colombia", "business", "premium", True))
        print("✅ Usuario PREMIUM creado: premium@test.com / Premium123!")
    except Exception as e:
        print(f"❌ Error creando usuario premium: {e}")
    
    print("\n🆓 Creando usuario GRATUITO de prueba...")
    try:
        free_password_hash = hash_password("Free123!")
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, email, phone, first_name, last_name, 
                                        password_hash, user_type, account_type, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("user_free", "free@test.com", "+573009876543", "Usuario", "Gratuito",
              free_password_hash, "seller", "free", True))
        print("✅ Usuario GRATUITO creado: free@test.com / Free123!")
    except Exception as e:
        print(f"❌ Error creando usuario gratuito: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_test_users()
    print("\n🎉 Usuarios de prueba creados exitosamente!")
    print("\n📝 CREDENCIALES:")
    print("   PREMIUM: premium@test.com / Premium123!")
    print("   GRATUITO: free@test.com / Free123!")
