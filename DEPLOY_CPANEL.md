# Guía de Deployment en cPanel - ML Extractor

## Preparación de archivos

### 1. Backend (Python App en cPanel)

#### Pasos en cPanel:
1. Ve a "Python App" en tu cPanel
2. Crea una nueva aplicación Python:
   - **Python version**: 3.8+ (usa la versión más reciente disponible)
   - **Application root**: `/extractor` (o el nombre que prefieras)
   - **Application URL**: `extractor.tu-dominio.com` (puedes usar un subdominio)
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`

3. Una vez creada la app, ve al directorio de la aplicación usando File Manager

#### Archivos a subir al directorio de la app Python:
```
/public_html/extractor/  (o el directorio que hayas elegido)
├── passenger_wsgi.py           # Ya creado
├── simple_backend.py           # Backend principal
├── requirements_production.txt # Dependencias
├── config/
│   └── mapping.yaml           # Configuración de mapeo
├── data/                      # Se creará automáticamente
├── logs/                      # Se creará automáticamente
└── uploads/                   # Se creará automáticamente
```

#### Comandos a ejecutar en el terminal de cPanel:
```bash
# Ir al directorio de la app
cd /home/tu-usuario/extractor

# Instalar dependencias
pip install -r requirements_production.txt

# Crear directorios necesarios
mkdir -p data logs uploads config

# Configurar permisos
chmod 755 data logs uploads
```

### 2. Frontend (Static Files)

#### Generar build de producción:
En tu máquina local, ejecuta:
```bash
cd frontend
npm run build
```

#### Subir archivos al public_html:
Sube todo el contenido de `frontend/build/` a tu `public_html` principal:
```
/public_html/
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── .htaccess              # Configuración de routing
└── manifest.json
```

### 3. Configurar variables de entorno

En la configuración de tu Python App en cPanel, añade:
```
REACT_APP_API_BASE_URL=https://extractor.tu-dominio.com
PRODUCTION=1
```

### 4. Configuración del .htaccess principal

En tu `/public_html/.htaccess`, añade estas reglas para el proxy del API:
```apache
RewriteEngine On

# Proxy API requests to Python app
RewriteCond %{REQUEST_URI} ^/api/(.*)
RewriteRule ^api/(.*)$ https://extractor.tu-dominio.com/$1 [P,L]

# Handle React routing
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api
RewriteRule . /index.html [L]
```

## Estructura Final en cPanel

```
/public_html/                    (Frontend - React App)
├── index.html
├── static/
└── .htaccess

/public_html/extractor/          (Backend - Python App)
├── passenger_wsgi.py
├── simple_backend.py
├── data/
│   └── users.db
└── config/
    └── mapping.yaml
```

## URLs Finales

- **Frontend**: `https://tu-dominio.com`
- **Backend API**: `https://extractor.tu-dominio.com/api/`
- **Admin Panel**: `https://tu-dominio.com/admin`

## Configuración de Base de Datos

El sistema usa SQLite por defecto, que se almacena en `data/users.db`. Para mayor robustez en producción, considera:

1. **Backup automático**: Configura un cron job para respaldar `data/users.db`
2. **Migración a MySQL**: Si necesitas más concurrencia, migra a MySQL de cPanel

## Troubleshooting

### Problemas comunes:

1. **Error 500 en API**: 
   - Revisa los logs en cPanel Python App
   - Verifica que todas las dependencias estén instaladas

2. **Frontend no carga**:
   - Verifica que el .htaccess esté configurado correctamente
   - Asegúrate de que todos los archivos estén en public_html

3. **API no conecta**:
   - Verifica la URL en las variables de entorno
   - Asegúrate de que el proxy esté configurado en .htaccess

## Scripts de Deployment

### Script para actualizar backend:
```bash
#!/bin/bash
# update_backend.sh
cd /home/tu-usuario/extractor
git pull origin main  # Si usas git
pip install -r requirements_production.txt --upgrade
touch passenger_wsgi.py  # Restart app
```

### Script para actualizar frontend:
```bash
#!/bin/bash
# update_frontend.sh
# Ejecutar en local:
npm run build
# Luego subir archivos via FTP/File Manager
```

## Monitoreo

- **Logs del Backend**: `/home/tu-usuario/extractor/logs/`
- **Logs de Python App**: Panel de cPanel > Python App > View logs
- **Logs de Access**: cPanel > Raw Access Logs

## Seguridad

1. **Backup regular** de `data/users.db`
2. **Configurar HTTPS** (SSL/TLS en cPanel)
3. **Actualizar dependencias** regularmente
4. **Monitorear logs** por actividad sospechosa

¡Tu aplicación estará lista para producción siguiendo estos pasos!
