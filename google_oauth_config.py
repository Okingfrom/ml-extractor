#!/usr/bin/env python3
"""
Google OAuth Configuration for ML Extractor
Configuración GRATUITA de autenticación con Google
"""

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json

class GoogleOAuthConfig:
    """Configuración OAuth de Google - COMPLETAMENTE GRATIS"""
    
    def __init__(self):
        # 🔑 ESTAS CREDENCIALES LAS OBTIENES GRATIS DE GOOGLE CLOUD CONSOLE
        self.client_config = {
            "web": {
                "client_id": "TU_CLIENT_ID_AQUI.apps.googleusercontent.com",
                "client_secret": "TU_CLIENT_SECRET_AQUI",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [
                    "http://localhost:5003/auth/google/callback",
                    "http://127.0.0.1:5003/auth/google/callback"
                ]
            }
        }
        
        # Scopes que necesitamos (GRATIS)
        self.scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        self.redirect_uri = "http://localhost:5003/auth/google/callback"
    
    def create_flow(self):
        """Crear flujo OAuth"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            return flow
        except Exception as e:
            print(f"❌ Error creando flujo OAuth: {e}")
            return None
    
    def get_authorization_url(self):
        """Obtener URL de autorización"""
        flow = self.create_flow()
        if flow:
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            return auth_url, state
        return None, None
    
    def exchange_code_for_token(self, code, state):
        """Intercambiar código por token"""
        try:
            flow = self.create_flow()
            if not flow:
                return None
                
            flow.fetch_token(code=code)
            
            # Obtener información del usuario
            credentials = flow.credentials
            request = requests.Request()
            
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                request,
                self.client_config['web']['client_id']
            )
            
            return {
                'google_id': id_info.get('sub'),
                'email': id_info.get('email'),
                'first_name': id_info.get('given_name', ''),
                'last_name': id_info.get('family_name', ''),
                'picture': id_info.get('picture', ''),
                'verified_email': id_info.get('email_verified', False)
            }
            
        except Exception as e:
            print(f"❌ Error intercambiando código: {e}")
            return None

# Instancia global
google_oauth = GoogleOAuthConfig()
