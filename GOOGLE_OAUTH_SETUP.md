# 🔧 CONFIGURACIÓN GOOGLE OAUTH - COMPLETAMENTE GRATIS

## ✅ Pasos para Activar Google OAuth (100% Gratuito)

### 1. Ir a Google Cloud Console
- Visita: https://console.cloud.google.com
- Inicia sesión con tu cuenta Google

### 2. Crear Proyecto (GRATIS)
- Clic en "Seleccionar proyecto" → "Nuevo proyecto"
- Nombre: `ML-Extractor-Auth`
- Clic "CREAR"

### 3. Habilitar APIs (GRATIS hasta 1M requests/día)
- Ve a "APIs y servicios" → "Biblioteca"
- Busca: **"Google+ API"** → HABILITAR
- Busca: **"People API"** → HABILITAR

### 4. Configurar Pantalla de Consentimiento
- Ve a "APIs y servicios" → "Pantalla de consentimiento OAuth"
- Tipo: **Externo** (gratis para hasta 100 usuarios)
- Información de la aplicación:
  - Nombre: `ML Extractor Pro`
  - Email de soporte: tu_email@gmail.com
  - Logo: (opcional)
  - Dominios autorizados: `localhost`

### 5. Crear Credenciales OAuth
- Ve a "APIs y servicios" → "Credenciales"
- Clic "+ CREAR CREDENCIALES" → "ID de cliente OAuth 2.0"
- Tipo: **Aplicación web**
- Nombre: `ML Extractor Web Client`
- **URIs de redireccionamiento autorizados:**
  ```
  http://localhost:5003/auth/google/callback
  http://127.0.0.1:5003/auth/google/callback
  ```

### 6. Obtener Credenciales
Después de crear, Google te dará:
- **CLIENT_ID**: algo como `123456789-abc...xyz.apps.googleusercontent.com`
- **CLIENT_SECRET**: algo como `GOCSPX-abc123xyz...`

### 7. Configurar en el Código
Edita `google_oauth_config.py` líneas 15-16:

```python
"client_id": "TU_CLIENT_ID_AQUI.apps.googleusercontent.com",
"client_secret": "TU_CLIENT_SECRET_AQUI",
```

Reemplaza con tus credenciales reales.

### 8. ¡Listo! 🎉

Ahora el botón "Iniciar con Google" funcionará completamente.

## 📊 Límites Gratuitos de Google OAuth:
- ✅ **Usuarios**: 100 usuarios en modo testing (gratis para siempre)
- ✅ **Requests**: 1,000,000 por día (más que suficiente)
- ✅ **APIs**: People API y Google+ API incluidas
- ✅ **Almacenamiento**: Sin límite de datos de usuarios

## 🚀 Para Producción:
Si necesitas más de 100 usuarios, simplemente verifica tu app (proceso gratuito).

## 💡 Alternativa Rápida para Testing:
Si solo quieres probar, usa las cuentas que ya creamos:
- **Premium**: `premium@test.com` / `Premium123!`
- **Gratuito**: `free@test.com` / `Free123!`
