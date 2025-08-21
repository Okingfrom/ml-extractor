#!/bin/bash
# Script de limpieza automática para ML Extractor
# Ejecutar con cron: 0 2 * * * /home/granaventura/Desktop/ML\ EXTRACTOR/cleanup.sh

LOG_FILE="/home/granaventura/Desktop/ML EXTRACTOR/logs/cleanup.log"
UPLOAD_DIR="/home/granaventura/Desktop/ML EXTRACTOR/uploads"
LOGS_DIR="/home/granaventura/Desktop/ML EXTRACTOR/logs"
BACKUPS_DIR="/home/granaventura/Desktop/ML EXTRACTOR/backups"

echo "🧹 $(date): Iniciando limpieza automática" >> "$LOG_FILE"

# Crear directorios si no existen
mkdir -p "$LOGS_DIR" "$BACKUPS_DIR"

# 1. Eliminar archivos de uploads mayores a 3 días
echo "📁 Limpiando archivos temporales (>3 días)..." >> "$LOG_FILE"
find "$UPLOAD_DIR" -type f -mtime +3 -exec rm -f {} \; 2>/dev/null
DELETED_UPLOADS=$(find "$UPLOAD_DIR" -type f -mtime +3 2>/dev/null | wc -l)
echo "   Eliminados: $DELETED_UPLOADS archivos temporales" >> "$LOG_FILE"

# 2. Eliminar logs de debug mayores a 3 semanas (21 días)
echo "📋 Limpiando logs de debug (>21 días)..." >> "$LOG_FILE"
find "$LOGS_DIR" -name "*.log" -type f -mtime +21 -exec rm -f {} \; 2>/dev/null
DELETED_LOGS=$(find "$LOGS_DIR" -name "*.log" -type f -mtime +21 2>/dev/null | wc -l)
echo "   Eliminados: $DELETED_LOGS logs de debug" >> "$LOG_FILE"

# 3. Eliminar backups mayores a 3 meses (90 días)
echo "💾 Limpiando backups (>90 días)..." >> "$LOG_FILE"
find "$BACKUPS_DIR" -type f -mtime +90 -exec rm -f {} \; 2>/dev/null
DELETED_BACKUPS=$(find "$BACKUPS_DIR" -type f -mtime +90 2>/dev/null | wc -l)
echo "   Eliminados: $DELETED_BACKUPS backups antiguos" >> "$LOG_FILE"

# 4. Limpiar archivos de análisis y reportes temporales
echo "📊 Limpiando archivos de análisis..." >> "$LOG_FILE"
find "/home/granaventura/Desktop/ML EXTRACTOR" -name "analysis_*.json" -mtime +7 -exec rm -f {} \; 2>/dev/null
find "/home/granaventura/Desktop/ML EXTRACTOR" -name "test_*.xlsx" -mtime +3 -exec rm -f {} \; 2>/dev/null
find "/home/granaventura/Desktop/ML EXTRACTOR" -name "*.log" -mtime +14 -exec rm -f {} \; 2>/dev/null

# 5. Mantener solo los últimos 10 archivos de log de limpieza
cd "$LOGS_DIR" && ls -t cleanup.log.* 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

# 6. Rotar log de limpieza si es muy grande (>10MB)
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE") -gt 10485760 ]; then
    mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d)"
    echo "🧹 $(date): Log rotado por tamaño" > "$LOG_FILE"
fi

echo "✅ $(date): Limpieza completada" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
