#!/usr/bin/env python3
"""
ML Mapper Pro con IA - Sistema híbrido para autocompletar datos faltantes
Usa múltiples APIs de IA económicas para generar información de productos
"""

import requests
import random
import re
import time
import json
from typing import Optional, Dict, Any, List

class AIProductEnhancer:
    """Clase para enriquecer datos de productos usando IA"""
    
    def __init__(self, provider: str = 'groq', api_key: Optional[str] = None):
        # APIs económicas disponibles
        self.apis = {
            'deepseek': {
                'url': 'https://api.deepseek.com/v1/chat/completions',
                'cost': '~$0.14/1M tokens',
                'quality': 'Excelente'
            },
            'groq': {
                'url': 'https://api.groq.com/openai/v1/chat/completions', 
                'cost': 'GRATIS hasta límite',
                'quality': 'Muy buena'
            },
            'together': {
                'url': 'https://api.together.xyz/inference',
                'cost': '~$0.20/1M tokens',
                'quality': 'Excelente'
            },
            'ollama_local': {
                'url': 'http://localhost:11434/api/generate',
                'cost': 'GRATIS (local)',
                'quality': 'Buena'
            }
        }
        
        # Configurar API desde parámetros
        self.current_api = provider
        self.api_key = api_key
        self.debug_log = []
        
        # Log de inicialización
        self.add_debug(f"AI Enhancer inicializado con {provider}")
        if api_key:
            self.add_debug(f"API Key configurada: {api_key[:10]}...{api_key[-4:]}")
        else:
            self.add_debug("No se proporcionó API Key - modo manual activado")
    
    def generate_missing_data(self, product_data: Dict, missing_fields: List[str]) -> Dict:
        """Genera datos faltantes usando IA"""
        
        if not self.api_key and self.current_api != 'ollama_local':
            return self._manual_fallback(product_data, missing_fields)
        
        # Crear prompt inteligente
        prompt = self._create_smart_prompt(product_data, missing_fields)
        
        try:
            # Llamar a la API seleccionada
            response = self._call_ai_api(prompt)
            
            # Parsear respuesta y extraer datos
            generated_data = self._parse_ai_response(response, missing_fields)
            
            return generated_data
            
        except Exception as e:
            print(f"Error con IA: {e}")
            return self._manual_fallback(product_data, missing_fields)
    
    def _create_smart_prompt(self, product_data: Dict, missing_fields: List[str]) -> str:
        """Crea un prompt inteligente y específico basado en los datos disponibles"""
        
        available_data = "\n".join([f"- {k}: {v}" for k, v in product_data.items() if v])
        
        prompt = f"""Eres un experto analista de productos para Mercado Libre. Analiza este producto y completa ÚNICAMENTE los campos solicitados.

PRODUCTO A ANALIZAR:
{available_data}

CAMPOS REQUERIDOS: {', '.join(missing_fields)}

INSTRUCCIONES ESPECÍFICAS:
• codigo_universal: Genera EAN-13 válido (13 dígitos que inicie con 789)
• marca: Extrae la marca real del nombre/descripción (Samsung, Apple, Sony, etc.)
• modelo: Crea modelo específico basado en el producto real
• peso: Estima peso realista en gramos según el tipo de producto
• color: Infiere color principal del nombre/descripción, si no hay info usa "Negro"
• garantia: Asigna garantía estándar según el tipo de producto
• descripcion: Mejora la descripción existente, máximo 1500 caracteres

FORMATO DE RESPUESTA (JSON únicamente):
{{
    "codigo_universal": "789XXXXXXXXX",
    "marca": "MarcaReal",
    "modelo": "ModeloEspecifico",
    "peso": "XXXg",
    "color": "ColorReal",
    "garantia": "X años",
    "descripcion": "Descripción mejorada..."
}}

Responde SOLO el JSON, sin texto adicional."""
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """Llama a la API de IA seleccionada"""
        
        if self.current_api == 'groq':
            return self._call_groq(prompt)
        elif self.current_api == 'deepseek':
            return self._call_deepseek(prompt)
        elif self.current_api == 'together':
            return self._call_together(prompt)
        elif self.current_api == 'ollama_local':
            return self._call_ollama_local(prompt)
        else:
            raise Exception("API no configurada")
    
    def _call_groq(self, prompt: str) -> str:
        """Llama a Groq API con configuración optimizada"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'llama3-8b-8192',  # Modelo básico que debería estar activo
            'messages': [
                {
                    'role': 'system', 
                    'content': 'Eres un experto en e-commerce y productos. Respondes únicamente en formato JSON válido, sin texto adicional. Usa información real y precisa sobre productos.'
                },
                {
                    'role': 'user', 
                    'content': prompt
                }
            ],
            'max_tokens': 1000,  # Más tokens para respuestas detalladas
            'temperature': 0.1,  # Más determinístico para consistencia
            'top_p': 0.9,  # Control de creatividad
            'stream': False
        }
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=60  # Más tiempo para respuestas complejas
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            # Debug más detallado
            self.add_debug(f"Error Groq API {response.status_code}: {response.text}")
            raise Exception(f"Error Groq API: {response.status_code} - {response.text}")
    
    def _call_deepseek(self, prompt: str) -> str:
        """Llama a DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 500,
            'temperature': 0.3
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error DeepSeek API: {response.status_code}")
    
    def _call_together(self, prompt: str) -> str:
        """Llama a Together API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'meta-llama/Llama-2-7b-chat-hf',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 500,
            'temperature': 0.3
        }
        
        response = requests.post(
            'https://api.together.xyz/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error Together API: {response.status_code}")
    
    def add_debug(self, message: str):
        """Agregar mensaje de debug"""
        self.debug_log.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def get_debug_log(self) -> str:
        """Obtener log de debug como string"""
        return "\n".join(self.debug_log)
    
    def _call_ollama_local(self, prompt: str) -> str:
        """Llama a Ollama API local"""
        data = {
            'model': 'llama2',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'num_predict': 500
            }
        }
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Error Ollama local: {response.status_code}")
        """Llama a Ollama local (GRATIS, sin API key)"""
        
        data = {
            'model': 'llama3.2',  # O el modelo que tengas instalado
            'prompt': prompt,
            'stream': False
        }
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                raise Exception("Ollama no disponible")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama no está corriendo localmente")
    
    def _parse_ai_response(self, response: str, expected_fields: List[str]) -> Dict:
        """Parsea la respuesta de IA y extrae los datos"""
        
        try:
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Filtrar solo campos esperados
                result = {}
                for field in expected_fields:
                    if field in data:
                        result[field] = str(data[field])
                
                return result
                
        except json.JSONDecodeError:
            pass
        
        # Si no se puede parsear JSON, usar regex simple
        return self._extract_with_regex(response, expected_fields)
    
    def _extract_with_regex(self, text: str, fields: List[str]) -> Dict:
        """Extrae datos usando regex si falla el JSON"""
        
        result = {}
        
        patterns = {
            'codigo_universal': r'(?:codigo|ean|upc).*?(\d{8,14})',
            'marca': r'(?:marca|brand).*?["\']([^"\']+)["\']',
            'modelo': r'(?:modelo|model).*?["\']([^"\']+)["\']',
            'peso': r'(?:peso|weight).*?(\d+)',
            'color': r'(?:color|colour).*?["\']([^"\']+)["\']'
        }
        
        for field in fields:
            if field in patterns:
                match = re.search(patterns[field], text, re.IGNORECASE)
                if match:
                    result[field] = match.group(1)
        
        return result
    
    def _manual_fallback(self, product_data: Dict, missing_fields: List[str]) -> Dict:
        """Fallback manual cuando la IA no está disponible"""
        
        fallback_data = {}
        
        for field in missing_fields:
            if field == 'codigo_universal':
                # Generar EAN-13 simple
                fallback_data[field] = f"789{hash(str(product_data)) % 9999999999:010d}"
            elif field == 'marca':
                fallback_data[field] = "Genérica"
            elif field == 'modelo':
                name = product_data.get('titulo', product_data.get('nombre', 'Producto'))
                fallback_data[field] = f"Modelo-{name[:10].replace(' ', '')}"
            elif field == 'peso':
                fallback_data[field] = "500"  # 500g por defecto
            elif field == 'color':
                fallback_data[field] = "Varios"
            elif field == 'descripcion':
                titulo = product_data.get('titulo', product_data.get('nombre', 'Producto'))
                fallback_data[field] = f"Excelente {titulo}. Producto de calidad."
        
        return fallback_data
    
    def generate_ean13(self, base_number: Optional[str] = None) -> str:
        """Genera un código EAN-13 válido"""
        
        if not base_number:
            base_number = f"789{hash(str(time.time())) % 999999999:09d}"
        
        # Asegurar 12 dígitos
        base = base_number[:12].ljust(12, '0')
        
        # Calcular dígito verificador
        odd_sum = sum(int(base[i]) for i in range(0, 12, 2))
        even_sum = sum(int(base[i]) for i in range(1, 12, 2))
        total = odd_sum + even_sum * 3
        check_digit = (10 - (total % 10)) % 10
        
        return base + str(check_digit)

# Configuración de APIs disponibles
AI_CONFIG = {
    'recommended': 'groq',  # Gratis y buena calidad
    'alternatives': {
        'groq': {
            'name': 'Groq (GRATIS)',
            'setup': 'Crear cuenta en groq.com',
            'cost': 'Gratis hasta límite generoso',
            'quality': '⭐⭐⭐⭐⭐'
        },
        'deepseek': {
            'name': 'DeepSeek (MUY BARATO)',
            'setup': 'Crear cuenta en deepseek.com',
            'cost': '~$0.14 por 1M tokens',
            'quality': '⭐⭐⭐⭐⭐'
        },
        'ollama_local': {
            'name': 'Ollama Local (GRATIS)',
            'setup': 'Instalar Ollama + modelo local',
            'cost': 'Completamente gratis',
            'quality': '⭐⭐⭐⭐'
        }
    }
}

import time
