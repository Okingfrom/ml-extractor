"""
Mapping Pattern Generator
Generates systematic mapping patterns based on ML template analysis
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd


class MappingConfidence(Enum):
    HIGH = "high"       # 90%+ confidence
    MEDIUM = "medium"   # 70-89% confidence
    LOW = "low"         # 50-69% confidence
    MANUAL = "manual"   # <50% confidence, requires manual mapping


@dataclass
class FieldMapping:
    source_column: str
    target_field: str
    mapping_type: str
    confidence: MappingConfidence
    transformation_rule: Optional[str] = None
    validation_rule: Optional[str] = None
    examples: List[str] = None
    notes: str = ""


@dataclass
class MappingPattern:
    template_type: str
    confidence_score: float
    total_fields: int
    mapped_fields: int
    unmapped_fields: List[str]
    field_mappings: List[FieldMapping]
    transformation_rules: Dict[str, str]
    validation_rules: Dict[str, str]
    recommendations: List[str]


class MappingPatternGenerator:
    """
    Generates intelligent mapping patterns for ML templates
    """
    
    # Standard Mercado Libre fields and their variations
    ML_STANDARD_FIELDS = {
        'titulo': {
            'patterns': ['titulo', 'title', 'nombre', 'product_name', 'name', 'descripcion_corta'],
            'required': True,
            'data_type': 'text',
            'max_length': 60,
            'validation': 'min_length:10,max_length:60,no_special_chars'
        },
        'precio': {
            'patterns': ['precio', 'price', 'cost', 'valor', 'costo', 'importe'],
            'required': True,
            'data_type': 'currency',
            'validation': 'positive_number,min_value:1'
        },
        'stock': {
            'patterns': ['stock', 'cantidad', 'inventory', 'qty', 'disponible', 'existencia'],
            'required': True,
            'data_type': 'integer',
            'validation': 'positive_integer,min_value:0'
        },
        'categoria': {
            'patterns': ['categoria', 'category', 'cat', 'tipo', 'clasificacion'],
            'required': True,
            'data_type': 'text',
            'validation': 'ml_category_validation'
        },
        'marca': {
            'patterns': ['marca', 'brand', 'fabricante', 'manufacturer'],
            'required': False,
            'data_type': 'text',
            'validation': 'brand_validation'
        },
        'modelo': {
            'patterns': ['modelo', 'model', 'version'],
            'required': False,
            'data_type': 'text',
            'validation': 'alphanumeric_allowed'
        },
        'descripcion': {
            'patterns': ['descripcion', 'description', 'desc', 'detalle', 'especificaciones'],
            'required': True,
            'data_type': 'text',
            'max_length': 50000,
            'validation': 'min_length:50,max_length:50000'
        },
        'peso': {
            'patterns': ['peso', 'weight', 'kg', 'gramos', 'grams'],
            'required': False,
            'data_type': 'decimal',
            'validation': 'positive_decimal'
        },
        'garantia': {
            'patterns': ['garantia', 'warranty', 'garantía'],
            'required': False,
            'data_type': 'text',
            'validation': 'warranty_format'
        },
        'condicion': {
            'patterns': ['condicion', 'condition', 'estado', 'condición'],
            'required': True,
            'data_type': 'enum',
            'allowed_values': ['Nuevo', 'Usado', 'Reacondicionado'],
            'validation': 'enum_validation'
        },
        'imagen_principal': {
            'patterns': ['imagen', 'image', 'foto', 'picture', 'url_imagen'],
            'required': False,
            'data_type': 'url',
            'validation': 'url_format,image_extension'
        },
        'sku': {
            'patterns': ['sku', 'codigo', 'code', 'id', 'item_id'],
            'required': False,
            'data_type': 'text',
            'validation': 'unique_identifier'
        }
    }
    
    # Data transformation patterns
    TRANSFORMATION_PATTERNS = {
        'price_cleanup': r'[^\d.,]',  # Remove non-numeric chars except decimal separators
        'text_cleanup': r'[^\w\s\-.,áéíóúñü]',  # Keep only letters, numbers, spaces, basic punctuation
        'url_validation': r'^https?://',
        'remove_extra_spaces': r'\s+',
        'normalize_condition': {
            'nuevo': 'Nuevo',
            'used': 'Usado',
            'refurbished': 'Reacondicionado',
            'recondicionado': 'Reacondicionado'
        }
    }

    def __init__(self):
        self.confidence_threshold = {
            MappingConfidence.HIGH: 0.9,
            MappingConfidence.MEDIUM: 0.7,
            MappingConfidence.LOW: 0.5
        }

    def generate_mapping_pattern(self, ml_analysis: Dict[str, Any]) -> MappingPattern:
        """
        Generate comprehensive mapping pattern from ML template analysis
        """
        template_structure = ml_analysis.get('template_structure', {})
        detected_columns = ml_analysis.get('detected_columns', {})
        sample_data = ml_analysis.get('sample_data', [])
        
        # Analyze each column for mapping potential
        field_mappings = []
        unmapped_fields = []
        total_confidence = 0
        
        for source_column, data_type in detected_columns.items():
            mapping = self._analyze_column_for_mapping(
                source_column, 
                data_type, 
                sample_data
            )
            
            if mapping:
                field_mappings.append(mapping)
                total_confidence += self._confidence_to_score(mapping.confidence)
            else:
                unmapped_fields.append(source_column)
        
        # Calculate overall confidence
        confidence_score = total_confidence / len(detected_columns) if detected_columns else 0
        
        # Generate transformation and validation rules
        transformation_rules = self._generate_transformation_rules(field_mappings)
        validation_rules = self._generate_validation_rules(field_mappings)
        recommendations = self._generate_recommendations(field_mappings, unmapped_fields, ml_analysis)
        
        return MappingPattern(
            template_type="mercado_libre",
            confidence_score=confidence_score,
            total_fields=len(detected_columns),
            mapped_fields=len(field_mappings),
            unmapped_fields=unmapped_fields,
            field_mappings=field_mappings,
            transformation_rules=transformation_rules,
            validation_rules=validation_rules,
            recommendations=recommendations
        )

    def _analyze_column_for_mapping(self, column_name: str, data_type: str, sample_data: List[Dict]) -> Optional[FieldMapping]:
        """
        Analyze a single column to determine its ML field mapping
        """
        column_lower = column_name.lower().strip()
        
        # Try to match against ML standard fields
        best_match = None
        best_confidence = 0
        
        for ml_field, field_info in self.ML_STANDARD_FIELDS.items():
            confidence = self._calculate_field_confidence(column_lower, field_info['patterns'])
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = ml_field
        
        if best_confidence < 0.5:
            return None
        
        # Determine confidence level
        if best_confidence >= 0.9:
            confidence_level = MappingConfidence.HIGH
        elif best_confidence >= 0.7:
            confidence_level = MappingConfidence.MEDIUM
        else:
            confidence_level = MappingConfidence.LOW
        
        # Get sample values for examples
        examples = self._extract_sample_values(column_name, sample_data)
        
        # Generate transformation rule if needed
        transformation_rule = self._suggest_transformation(best_match, examples, data_type)
        
        # Generate validation rule
        validation_rule = self.ML_STANDARD_FIELDS[best_match].get('validation', '')
        
        # Generate notes
        notes = self._generate_field_notes(best_match, confidence_level, examples)
        
        return FieldMapping(
            source_column=column_name,
            target_field=best_match,
            mapping_type="direct" if transformation_rule is None else "transform",
            confidence=confidence_level,
            transformation_rule=transformation_rule,
            validation_rule=validation_rule,
            examples=examples[:3],  # First 3 examples
            notes=notes
        )

    def _calculate_field_confidence(self, column_name: str, patterns: List[str]) -> float:
        """
        Calculate confidence score for field matching
        """
        max_confidence = 0
        
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Exact match
            if column_name == pattern_lower:
                return 1.0
            
            # Contains pattern
            if pattern_lower in column_name:
                confidence = 0.8 + (len(pattern_lower) / len(column_name)) * 0.2
                max_confidence = max(max_confidence, confidence)
            
            # Pattern contains column name
            elif column_name in pattern_lower:
                confidence = 0.7 + (len(column_name) / len(pattern_lower)) * 0.2
                max_confidence = max(max_confidence, confidence)
            
            # Similarity based on common characters
            else:
                similarity = self._calculate_string_similarity(column_name, pattern_lower)
                if similarity > 0.6:
                    max_confidence = max(max_confidence, similarity * 0.6)
        
        return max_confidence

    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using simple ratio
        """
        if not str1 or not str2:
            return 0.0
        
        # Simple character overlap ratio
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def _extract_sample_values(self, column_name: str, sample_data: List[Dict]) -> List[str]:
        """
        Extract sample values from the column
        """
        samples = []
        for row in sample_data:
            if column_name in row and row[column_name] is not None:
                value = str(row[column_name]).strip()
                if value and value not in samples:
                    samples.append(value)
                if len(samples) >= 5:
                    break
        return samples

    def _suggest_transformation(self, ml_field: str, examples: List[str], data_type: str) -> Optional[str]:
        """
        Suggest transformation rules based on field type and examples
        """
        if not examples:
            return None
        
        transformations = []
        
        # Price field transformations
        if ml_field == 'precio':
            if any(re.search(r'[^\d.,]', str(example)) for example in examples):
                transformations.append("remove_non_numeric")
            if any(',' in str(example) for example in examples):
                transformations.append("normalize_decimal_separator")
        
        # Text field transformations
        elif ml_field in ['titulo', 'descripcion', 'marca', 'modelo']:
            if any(re.search(r'[^\w\s\-.,áéíóúñü]', str(example)) for example in examples):
                transformations.append("clean_special_characters")
            if any(re.search(r'\s{2,}', str(example)) for example in examples):
                transformations.append("normalize_spaces")
        
        # Condition field transformations
        elif ml_field == 'condicion':
            transformations.append("normalize_condition_values")
        
        # URL field transformations
        elif ml_field == 'imagen_principal':
            if examples and not all(example.startswith('http') for example in examples):
                transformations.append("ensure_url_protocol")
        
        return ",".join(transformations) if transformations else None

    def _generate_transformation_rules(self, field_mappings: List[FieldMapping]) -> Dict[str, str]:
        """
        Generate comprehensive transformation rules
        """
        rules = {}
        
        for mapping in field_mappings:
            if mapping.transformation_rule:
                rules[mapping.source_column] = mapping.transformation_rule
        
        # Add global transformation rules
        rules['_global'] = {
            'trim_whitespace': True,
            'remove_empty_values': True,
            'normalize_encoding': 'utf-8'
        }
        
        return rules

    def _generate_validation_rules(self, field_mappings: List[FieldMapping]) -> Dict[str, str]:
        """
        Generate comprehensive validation rules
        """
        rules = {}
        
        for mapping in field_mappings:
            if mapping.validation_rule:
                rules[mapping.target_field] = mapping.validation_rule
        
        return rules

    def _generate_recommendations(self, field_mappings: List[FieldMapping], unmapped_fields: List[str], ml_analysis: Dict) -> List[str]:
        """
        Generate actionable recommendations for improving the mapping
        """
        recommendations = []
        
        # Check for missing required fields
        mapped_ml_fields = {mapping.target_field for mapping in field_mappings}
        required_fields = {field for field, info in self.ML_STANDARD_FIELDS.items() if info['required']}
        missing_required = required_fields - mapped_ml_fields
        
        if missing_required:
            recommendations.append(f"Faltan campos obligatorios: {', '.join(missing_required)}")
        
        # Check for low confidence mappings
        low_confidence_mappings = [m for m in field_mappings if m.confidence == MappingConfidence.LOW]
        if low_confidence_mappings:
            recommendations.append(f"Revisar mapeos de baja confianza: {', '.join([m.source_column for m in low_confidence_mappings])}")
        
        # Check for unmapped fields
        if unmapped_fields:
            recommendations.append(f"Considerar mapeo manual para: {', '.join(unmapped_fields)}")
        
        # Data quality recommendations
        total_products = ml_analysis.get('total_products', 0)
        if total_products < 5:
            recommendations.append("Agregue más productos para un mejor análisis de patrones")
        
        # Validation recommendations
        validation_errors = ml_analysis.get('validation_errors', [])
        if validation_errors:
            recommendations.append("Corregir errores de validación antes del mapeo final")
        
        return recommendations

    def _generate_field_notes(self, ml_field: str, confidence: MappingConfidence, examples: List[str]) -> str:
        """
        Generate helpful notes for each field mapping
        """
        notes = []
        
        field_info = self.ML_STANDARD_FIELDS.get(ml_field, {})
        
        if field_info.get('required'):
            notes.append("Campo obligatorio en ML")
        
        if 'max_length' in field_info:
            notes.append(f"Longitud máxima: {field_info['max_length']} caracteres")
        
        if confidence == MappingConfidence.LOW:
            notes.append("⚠️ Verificar mapeo manualmente")
        
        if examples:
            notes.append(f"Ejemplos detectados: {', '.join(examples[:2])}")
        
        return " | ".join(notes)

    def _confidence_to_score(self, confidence: MappingConfidence) -> float:
        """
        Convert confidence enum to numeric score
        """
        return {
            MappingConfidence.HIGH: 1.0,
            MappingConfidence.MEDIUM: 0.8,
            MappingConfidence.LOW: 0.6,
            MappingConfidence.MANUAL: 0.3
        }.get(confidence, 0.0)

    def export_mapping_config(self, pattern: MappingPattern) -> Dict[str, Any]:
        """
        Export mapping pattern as configuration for processing
        """
        return {
            'version': '1.0',
            'template_type': pattern.template_type,
            'confidence_score': pattern.confidence_score,
            'mapping_metadata': {
                'total_fields': pattern.total_fields,
                'mapped_fields': pattern.mapped_fields,
                'unmapped_fields': pattern.unmapped_fields,
                'recommendations': pattern.recommendations
            },
            'field_mappings': [asdict(mapping) for mapping in pattern.field_mappings],
            'transformation_rules': pattern.transformation_rules,
            'validation_rules': pattern.validation_rules,
            'processing_instructions': {
                'apply_transformations': True,
                'validate_required_fields': True,
                'skip_empty_rows': True,
                'error_handling': 'collect_and_report'
            }
        }


# Utility functions for API integration
def generate_mapping_from_analysis(ml_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate mapping pattern from ML analysis
    """
    generator = MappingPatternGenerator()
    pattern = generator.generate_mapping_pattern(ml_analysis)
    
    return {
        'mapping_pattern': generator.export_mapping_config(pattern),
        'summary': {
            'confidence_score': pattern.confidence_score,
            'mapped_fields': pattern.mapped_fields,
            'total_fields': pattern.total_fields,
            'mapping_success_rate': (pattern.mapped_fields / pattern.total_fields) * 100 if pattern.total_fields > 0 else 0,
            'recommendations_count': len(pattern.recommendations),
            'high_confidence_mappings': len([m for m in pattern.field_mappings if m.confidence == MappingConfidence.HIGH]),
            'manual_review_needed': len([m for m in pattern.field_mappings if m.confidence == MappingConfidence.LOW])
        },
        'next_steps': [
            "Revisar mapeos sugeridos",
            "Validar transformaciones propuestas", 
            "Configurar validaciones personalizadas",
            "Procesar datos con el mapeo generado"
        ]
    }
