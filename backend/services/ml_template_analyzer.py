import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)

class MLTemplateAnalyzer:
    """
    Analizador especializado para plantillas de Mercado Libre
    Detecta estructura, campos y categorías con análisis exhaustivo
    """
    
    # Campos conocidos de ML según especificación oficial
    ML_TEMPLATE_FIELDS = {
        # Campos básicos identificados en plantilla_ml_ejemplo.xlsx
        'MLID': 'ID interno de ML',
        'Título': 'Título del producto',
        'Categoría': 'Categoría del producto', 
        'Precio': 'Precio del producto',
        'Moneda': 'Tipo de moneda (ARS, USD, etc)',
        'Tipo de publicación': 'Clásica, Premium, etc',
        'Estado': 'Nuevo, Usado, Reacondicionado',
        'Stock disponible': 'Cantidad disponible',
        'Envío gratis': 'Si/No para envío gratuito',
        'Acepta Mercado Pago': 'Si/No acepta MP',
        'Retiro en persona': 'Si/No permite retiro'
    }
    
    # Patrones para detectar campos ML
    ML_FIELD_PATTERNS = [
        r'ml.*id',
        r'título|title',
        r'categoría|category',
        r'precio|price',
        r'moneda|currency',
        r'tipo.*publicación|publication.*type',
        r'estado|condition',
        r'stock|quantity|cantidad',
        r'envío.*gratis|free.*shipping',
        r'mercado.*pago|mercadopago',
        r'retiro|pickup'
    ]
    
    # Categorías comunes de ML
    COMMON_ML_CATEGORIES = [
        'Electrónicos, Audio y Video',
        'Celulares y Teléfonos', 
        'Computación',
        'Consolas y Videojuegos',
        'Cámaras y Accesorios',
        'Televisores',
        'Casa, Muebles y Jardín',
        'Electrodomésticos',
        'Herramientas',
        'Construcción',
        'Industrias y Oficinas',
        'Accesorios para Vehículos',
        'Motos',
        'Ropa y Accesorios',
        'Deportes y Fitness',
        'Libros, Revistas y Comics',
        'Música, Películas y Series',
        'Bebés',
        'Juegos y Juguetes',
        'Arte, Librería y Mercería',
        'Salud y Belleza',
        'Relojes y Joyas',
        'Instrumentos Musicales'
    ]

    def __init__(self):
        self.analysis_result = {}
        
    def analyze_template(self, file_path: str) -> Dict[str, Any]:
        """
        Análisis exhaustivo de plantilla ML
        """
        try:
            logger.info(f"🔍 Iniciando análisis de plantilla ML: {file_path}")
            
            # Leer archivo
            df = self._read_file(file_path)
            if df is None:
                return self._create_error_result("No se pudo leer el archivo")
            
            # Análisis completo
            result = {
                'is_ml_template': False,
                'confidence_score': 0.0,
                'file_analysis': self._analyze_file_structure(df),
                'ml_fields': self._detect_ml_fields(df),
                'categories': self._detect_categories(df),
                'template_type': self._classify_template_type(df),
                'validation': self._validate_template_structure(df),
                'recommendations': []
            }
            
            # Calcular score de confianza
            result['confidence_score'] = self._calculate_confidence_score(result)
            result['is_ml_template'] = result['confidence_score'] > 0.6
            
            # Generar recomendaciones
            result['recommendations'] = self._generate_recommendations(result)
            
            logger.info(f"✅ Análisis completado. ML Template: {result['is_ml_template']}, Confianza: {result['confidence_score']:.2f}")
            
            return {
                'success': True,
                'analysis': result,
                'message': 'Análisis de plantilla ML completado'
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis ML: {str(e)}")
            return self._create_error_result(f"Error en análisis: {str(e)}")
    
    def _read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Lee archivo Excel o CSV"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # Leer Excel sin header para análisis completo
                df = pd.read_excel(file_path, header=None)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path, header=None, encoding='utf-8')
            else:
                return None
                
            logger.info(f"📊 Archivo leído: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error leyendo archivo: {str(e)}")
            return None
    
    def _analyze_file_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza la estructura del archivo"""
        try:
            structure = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'empty_rows': df.isnull().all(axis=1).sum(),
                'data_start_row': self._find_data_start_row(df),
                'header_rows': self._find_header_rows(df),
                'has_merged_cells': self._detect_merged_cells(df),
                'data_density': self._calculate_data_density(df)
            }
            
            logger.info(f"📋 Estructura: {structure['total_rows']}x{structure['total_columns']}, datos desde fila {structure['data_start_row']}")
            return structure
            
        except Exception as e:
            logger.error(f"❌ Error analizando estructura: {str(e)}")
            return {}
    
    def _find_data_start_row(self, df: pd.DataFrame) -> int:
        """Encuentra la fila donde empiezan los datos de productos"""
        # En plantillas ML, los datos suelen empezar en fila 8+ (filas 1-7 son headers/metadata)
        for i in range(min(15, len(df))):
            row = df.iloc[i]
            non_null_count = row.count()
            
            # Si una fila tiene muchos datos, probablemente es donde empiezan los productos
            if non_null_count >= df.shape[1] * 0.5:  # Al menos 50% de campos llenos
                return i + 1  # +1 porque pandas usa índice 0
                
        return 8  # Default para plantillas ML
    
    def _find_header_rows(self, df: pd.DataFrame) -> List[int]:
        """Identifica filas que contienen headers"""
        header_rows = []
        
        for i in range(min(10, len(df))):  # Revisar primeras 10 filas
            row = df.iloc[i]
            row_str = ' '.join([str(cell) for cell in row.dropna()])
            
            # Buscar patrones de headers ML
            ml_keywords = ['ml', 'mercado', 'libre', 'título', 'categoría', 'precio', 'stock']
            keyword_count = sum(1 for keyword in ml_keywords if keyword.lower() in row_str.lower())
            
            if keyword_count >= 2:  # Si tiene al menos 2 keywords ML
                header_rows.append(i + 1)
        
        return header_rows
    
    def _detect_merged_cells(self, df: pd.DataFrame) -> bool:
        """Detecta si hay celdas combinadas (típico en plantillas ML)"""
        # Buscar patrones que indiquen celdas combinadas
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            # Si hay valores idénticos consecutivos, puede indicar merge
            for j in range(len(row) - 1):
                if pd.notna(row.iloc[j]) and row.iloc[j] == row.iloc[j + 1]:
                    return True
        return False
    
    def _calculate_data_density(self, df: pd.DataFrame) -> float:
        """Calcula densidad de datos en el archivo"""
        total_cells = df.size
        filled_cells = df.count().sum()
        return filled_cells / total_cells if total_cells > 0 else 0.0
    
    def _detect_ml_fields(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta campos específicos de ML"""
        ml_fields = []
        
        # Revisar primeras filas buscando headers
        for row_idx in range(min(10, len(df))):
            row = df.iloc[row_idx]
            
            for col_idx, cell in enumerate(row):
                if pd.isna(cell):
                    continue
                    
                cell_str = str(cell).strip().lower()
                
                # Buscar coincidencias con campos ML conocidos
                for field_name, description in self.ML_TEMPLATE_FIELDS.items():
                    if self._is_ml_field_match(cell_str, field_name):
                        ml_fields.append({
                            'field_name': field_name,
                            'detected_text': str(cell),
                            'position': f"Fila {row_idx + 1}, Columna {col_idx + 1}",
                            'description': description,
                            'confidence': self._calculate_field_confidence(cell_str, field_name)
                        })
        
        # Remover duplicados y ordenar por confianza
        unique_fields = []
        seen_fields = set()
        
        for field in sorted(ml_fields, key=lambda x: x['confidence'], reverse=True):
            if field['field_name'] not in seen_fields:
                unique_fields.append(field)
                seen_fields.add(field['field_name'])
        
        logger.info(f"🎯 Campos ML detectados: {len(unique_fields)}")
        return unique_fields
    
    def _is_ml_field_match(self, cell_text: str, field_name: str) -> bool:
        """Verifica si el texto coincide con un campo ML"""
        field_lower = field_name.lower()
        
        # Coincidencia exacta
        if field_lower in cell_text:
            return True
        
        # Coincidencias por patrones
        if 'mlid' in field_lower and any(pattern in cell_text for pattern in ['ml', 'id', 'código']):
            return True
        if 'título' in field_lower and any(pattern in cell_text for pattern in ['título', 'title', 'nombre']):
            return True
        if 'categoría' in field_lower and any(pattern in cell_text for pattern in ['categoría', 'category']):
            return True
        if 'precio' in field_lower and any(pattern in cell_text for pattern in ['precio', 'price']):
            return True
        if 'moneda' in field_lower and any(pattern in cell_text for pattern in ['moneda', 'currency']):
            return True
        if 'stock' in field_lower and any(pattern in cell_text for pattern in ['stock', 'cantidad', 'disponible']):
            return True
        if 'envío' in field_lower and 'gratis' in field_lower and any(pattern in cell_text for pattern in ['envío', 'envio', 'gratis', 'shipping']):
            return True
        
        return False
    
    def _calculate_field_confidence(self, cell_text: str, field_name: str) -> float:
        """Calcula confianza de coincidencia de campo"""
        field_lower = field_name.lower()
        
        # Coincidencia exacta = máxima confianza
        if field_lower in cell_text:
            return 1.0
        
        # Coincidencias parciales
        keywords = field_lower.split()
        matches = sum(1 for keyword in keywords if keyword in cell_text)
        
        if matches > 0:
            return matches / len(keywords) * 0.8
        
        return 0.0
    
    def _detect_categories(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detecta categorías de productos en la plantilla"""
        categories = []
        
        for row_idx in range(len(df)):
            row = df.iloc[row_idx]
            
            for col_idx, cell in enumerate(row):
                if pd.isna(cell):
                    continue
                    
                cell_str = str(cell).strip()
                
                # Buscar coincidencias con categorías conocidas
                for category in self.COMMON_ML_CATEGORIES:
                    if self._is_category_match(cell_str, category):
                        categories.append({
                            'category_name': category,
                            'detected_text': cell_str,
                            'position': f"Fila {row_idx + 1}, Columna {col_idx + 1}",
                            'confidence': self._calculate_category_confidence(cell_str, category)
                        })
        
        # Remover duplicados
        unique_categories = []
        seen_categories = set()
        
        for cat in sorted(categories, key=lambda x: x['confidence'], reverse=True):
            if cat['category_name'] not in seen_categories:
                unique_categories.append(cat)
                seen_categories.add(cat['category_name'])
        
        logger.info(f"📂 Categorías detectadas: {len(unique_categories)}")
        return unique_categories
    
    def _is_category_match(self, cell_text: str, category: str) -> bool:
        """Verifica si el texto coincide con una categoría"""
        # Normalizar textos
        cell_lower = cell_text.lower()
        category_lower = category.lower()
        
        # Coincidencia exacta
        if category_lower == cell_lower:
            return True
        
        # Coincidencia parcial (al menos 60% de palabras)
        category_words = category_lower.split()
        matches = sum(1 for word in category_words if word in cell_lower)
        
        return matches >= len(category_words) * 0.6
    
    def _calculate_category_confidence(self, cell_text: str, category: str) -> float:
        """Calcula confianza de coincidencia de categoría"""
        cell_lower = cell_text.lower()
        category_lower = category.lower()
        
        if category_lower == cell_lower:
            return 1.0
        
        category_words = category_lower.split()
        matches = sum(1 for word in category_words if word in cell_lower)
        
        return matches / len(category_words) if len(category_words) > 0 else 0.0
    
    def _classify_template_type(self, df: pd.DataFrame) -> str:
        """Clasifica el tipo de plantilla"""
        # Analizar estructura para determinar tipo
        structure = self._analyze_file_structure(df)
        
        if structure.get('data_start_row', 0) >= 7:
            return 'ml_official'  # Plantilla oficial ML
        elif structure.get('total_columns', 0) >= 10:
            return 'ml_custom'    # Plantilla ML personalizada
        else:
            return 'unknown'      # Tipo desconocido
    
    def _validate_template_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida la estructura de la plantilla"""
        validation = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Validaciones específicas
        if len(df) < 8:
            validation['issues'].append('La plantilla parece muy corta para ser una plantilla ML oficial')
            validation['is_valid'] = False
        
        if len(df.columns) < 5:
            validation['issues'].append('Muy pocas columnas para una plantilla ML')
            validation['is_valid'] = False
        
        # Verificar estructura típica ML
        data_start = self._find_data_start_row(df)
        if data_start < 7:
            validation['warnings'].append('Los datos parecen empezar muy temprano (plantillas ML oficiales empiezan en fila 8+)')
        
        return validation
    
    def _calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calcula score de confianza general"""
        score = 0.0
        
        # Peso por campos ML detectados
        ml_fields_count = len(result.get('ml_fields', []))
        score += min(ml_fields_count / 8.0, 1.0) * 0.4  # 40% peso
        
        # Peso por categorías detectadas
        categories_count = len(result.get('categories', []))
        score += min(categories_count / 3.0, 1.0) * 0.3  # 30% peso
        
        # Peso por estructura
        structure = result.get('file_analysis', {})
        if structure.get('data_start_row', 0) >= 7:
            score += 0.2  # 20% peso
        
        # Peso por validación
        validation = result.get('validation', {})
        if validation.get('is_valid', False):
            score += 0.1  # 10% peso
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        confidence = result.get('confidence_score', 0.0)
        
        if confidence < 0.3:
            recommendations.append('Este archivo no parece ser una plantilla de Mercado Libre. Descarga la plantilla oficial desde tu cuenta.')
        elif confidence < 0.6:
            recommendations.append('El archivo podría ser una plantilla ML modificada. Verifica que sea la versión oficial.')
        else:
            recommendations.append('Plantilla ML detectada correctamente. Puedes proceder al siguiente paso.')
        
        # Recomendaciones específicas
        ml_fields = result.get('ml_fields', [])
        if len(ml_fields) < 5:
            recommendations.append('Se detectaron pocos campos ML. Verifica que la plantilla esté completa.')
        
        categories = result.get('categories', [])
        if len(categories) == 0:
            recommendations.append('No se detectaron categorías. Asegúrate de que la plantilla tenga categorías definidas.')
        
        return recommendations
    
    def _create_error_result(self, message: str) -> Dict[str, Any]:
        """Crea resultado de error"""
        return {
            'success': False,
            'error': message,
            'analysis': None
        }
