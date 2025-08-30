#!/usr/bin/env python3
"""
Product Data Analyzer for ML Extractor
Analyzes product files and suggests mappings to ML template fields
"""

import pandas as pd
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class ProductDataAnalyzer:
    """Analyzes product data files and maps them to ML template structure"""
    
    # ML Template structure based on plantilla_ml_ejemplo.xlsx
    ML_TEMPLATE_FIELDS = {
        'Título': {'required': True, 'type': 'texto', 'column_index': 0},
        'Precio': {'required': True, 'type': 'número', 'column_index': 1},
        'Stock': {'required': True, 'type': 'número', 'column_index': 2},
        'Categoría': {'required': True, 'type': 'texto', 'column_index': 3},
        'Marca': {'required': False, 'type': 'texto', 'column_index': 4},
        'Modelo': {'required': False, 'type': 'texto', 'column_index': 5},
        'Descripción': {'required': True, 'type': 'texto', 'column_index': 6},
        'Peso': {'required': False, 'type': 'número', 'column_index': 7},
        'Garantía': {'required': False, 'type': 'texto', 'column_index': 8},
        'Condición': {'required': True, 'type': 'texto', 'column_index': 9},
        'Imagen Principal': {'required': False, 'type': 'url', 'column_index': 10}
    }
    
    # Common field mapping patterns
    FIELD_MAPPING_PATTERNS = {
        'Título': ['titulo', 'title', 'nombre', 'product_name', 'descripcion_corta', 'name'],
        'Precio': ['precio', 'price', 'cost', 'valor', 'amount', 'costo'],
        'Stock': ['stock', 'cantidad', 'qty', 'quantity', 'inventario', 'disponible'],
        'Categoría': ['categoria', 'category', 'tipo', 'type', 'clasificacion'],
        'Marca': ['marca', 'brand', 'fabricante', 'manufacturer'],
        'Modelo': ['modelo', 'model', 'version', 'variante'],
        'Descripción': ['descripcion', 'description', 'detalle', 'info', 'details'],
        'Peso': ['peso', 'weight', 'kg', 'gramos', 'grams'],
        'Garantía': ['garantia', 'warranty', 'garanty'],
        'Condición': ['condicion', 'condition', 'estado', 'state'],
        'Imagen Principal': ['imagen', 'image', 'foto', 'photo', 'url_imagen', 'img_url']
    }
    
    def __init__(self):
        self.ml_data_start_row = 8  # Row 8 is where product data starts in ML template
        
    def analyze_product_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a product data file and suggest mappings to ML template
        
        Args:
            file_path: Path to the product data file
            
        Returns:
            Dictionary with analysis results and mapping suggestions
        """
        try:
            # Read the file
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            # Basic file analysis
            total_products = len(df.dropna(how='all'))
            detected_columns = list(df.columns)
            
            # Generate field mappings
            field_mappings = self._generate_field_mappings(detected_columns)
            
            # Calculate mapping confidence
            mapping_summary = self._calculate_mapping_summary(field_mappings)
            
            # Extract sample data
            sample_data = self._extract_sample_data(df, min(3, len(df)))
            
            # Generate recommendations
            recommendations = self._generate_recommendations(field_mappings, total_products)
            
            return {
                "file_analysis": {
                    "total_products": total_products,
                    "detected_columns": detected_columns,
                    "column_count": len(detected_columns),
                    "sample_data": sample_data,
                    "file_type": file_extension
                },
                "ml_template_mapping": {
                    "field_mappings": field_mappings,
                    "mapping_summary": mapping_summary,
                    "ml_template_fields": self.ML_TEMPLATE_FIELDS,
                    "data_insertion_row": self.ml_data_start_row
                },
                "recommendations": recommendations,
                "next_steps": [
                    "Revisar mapeos automáticos sugeridos",
                    "Ajustar mapeos manuales si es necesario", 
                    "Validar datos de muestra",
                    "Procesar archivo completo con mapeos",
                    "Generar plantilla ML completa"
                ]
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing product file: {str(e)}")
    
    def _generate_field_mappings(self, columns: List[str]) -> List[Dict[str, Any]]:
        """Generate automatic field mappings from product columns to ML fields"""
        mappings = []
        
        for col in columns:
            col_lower = col.lower().strip()
            
            # Find best ML field match
            best_match = None
            best_confidence = 0
            
            for ml_field, patterns in self.FIELD_MAPPING_PATTERNS.items():
                confidence = 0
                
                # Exact match
                if col_lower in [p.lower() for p in patterns]:
                    confidence = 0.95
                
                # Partial match
                elif any(pattern.lower() in col_lower for pattern in patterns):
                    confidence = 0.75
                
                # Contains match
                elif any(col_lower in pattern.lower() for pattern in patterns):
                    confidence = 0.60
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = ml_field
            
            # Determine mapping status
            if best_confidence >= 0.75:
                status = "high_confidence"
            elif best_confidence >= 0.50:
                status = "medium_confidence"
            else:
                status = "manual_review"
                best_match = "Sin mapear"
            
            mappings.append({
                "source_column": col,
                "target_ml_field": best_match,
                "confidence_score": best_confidence,
                "status": status,
                "ml_field_required": self.ML_TEMPLATE_FIELDS.get(best_match, {}).get('required', False),
                "ml_field_type": self.ML_TEMPLATE_FIELDS.get(best_match, {}).get('type', 'texto'),
                "ml_column_index": self.ML_TEMPLATE_FIELDS.get(best_match, {}).get('column_index', -1)
            })
        
        return mappings
    
    def _calculate_mapping_summary(self, field_mappings: List[Dict]) -> Dict[str, Any]:
        """Calculate overall mapping statistics"""
        total_fields = len(field_mappings)
        high_confidence = len([m for m in field_mappings if m['status'] == 'high_confidence'])
        medium_confidence = len([m for m in field_mappings if m['status'] == 'medium_confidence'])
        manual_review = len([m for m in field_mappings if m['status'] == 'manual_review'])
        
        # Count required ML fields covered
        mapped_required_fields = set()
        for mapping in field_mappings:
            if mapping['ml_field_required'] and mapping['confidence_score'] >= 0.5:
                mapped_required_fields.add(mapping['target_ml_field'])
        
        required_ml_fields = [field for field, info in self.ML_TEMPLATE_FIELDS.items() if info['required']]
        required_coverage = len(mapped_required_fields) / len(required_ml_fields) * 100
        
        overall_confidence = (high_confidence * 0.9 + medium_confidence * 0.6) / total_fields if total_fields > 0 else 0
        
        return {
            "total_source_fields": total_fields,
            "high_confidence_mappings": high_confidence,
            "medium_confidence_mappings": medium_confidence,
            "manual_review_needed": manual_review,
            "required_fields_coverage": round(required_coverage, 1),
            "overall_confidence_score": round(overall_confidence, 2),
            "ready_for_processing": required_coverage >= 80 and overall_confidence >= 0.6
        }
    
    def _extract_sample_data(self, df: pd.DataFrame, sample_size: int) -> List[Dict]:
        """Extract sample data for preview"""
        sample_data = []
        for i in range(min(sample_size, len(df))):
            row_data = {}
            for col in df.columns:
                value = df.iloc[i][col]
                if pd.notna(value):
                    row_data[col] = str(value)
                else:
                    row_data[col] = ""
            sample_data.append(row_data)
        return sample_data
    
    def _generate_recommendations(self, field_mappings: List[Dict], total_products: int) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check required fields
        mapped_required = [m for m in field_mappings if m['ml_field_required'] and m['confidence_score'] >= 0.5]
        required_fields = [field for field, info in self.ML_TEMPLATE_FIELDS.items() if info['required']]
        
        if len(mapped_required) == len(required_fields):
            recommendations.append("✅ Todos los campos obligatorios de ML están mapeados")
        else:
            missing = len(required_fields) - len(mapped_required)
            recommendations.append(f"⚠️ Faltan {missing} campos obligatorios por mapear")
        
        # Check data quality
        if total_products > 0:
            recommendations.append(f"📊 Se detectaron {total_products} productos para procesar")
        else:
            recommendations.append("❌ No se detectaron productos válidos en el archivo")
        
        # Check mapping quality
        high_conf = len([m for m in field_mappings if m['status'] == 'high_confidence'])
        total_fields = len(field_mappings)
        
        if high_conf / total_fields >= 0.8:
            recommendations.append("🎯 Mapeo automático de alta calidad detectado")
        elif high_conf / total_fields >= 0.5:
            recommendations.append("🔧 Mapeo automático parcial - revisar campos sugeridos")
        else:
            recommendations.append("👤 Se recomienda mapeo manual para mejor precisión")
        
        return recommendations

def analyze_product_data(file_path: str) -> Dict[str, Any]:
    """
    Main function to analyze product data file
    
    Args:
        file_path: Path to the product data file
        
    Returns:
        Analysis results with mapping suggestions
    """
    analyzer = ProductDataAnalyzer()
    return analyzer.analyze_product_file(file_path)

# Test with sample file
if __name__ == "__main__":
    # Test with the uploaded file
    test_file = "uploads/Publicar-08-09-10_39_33.xlsx"
    if os.path.exists(test_file):
        result = analyze_product_data(test_file)
        print("🔍 Análisis de Productos - Resultados:")
        print(f"📁 Archivo: {test_file}")
        print(f"📊 Productos detectados: {result['file_analysis']['total_products']}")
        print(f"🏷️ Columnas encontradas: {result['file_analysis']['column_count']}")
        print(f"🎯 Confianza general: {result['ml_template_mapping']['mapping_summary']['overall_confidence_score']}")
        print(f"✅ Campos obligatorios cubiertos: {result['ml_template_mapping']['mapping_summary']['required_fields_coverage']}%")
    else:
        print("Archivo de prueba no encontrado")
