"""
Weight Enhancement Module
Provides weight extraction and normalization functionality.
"""

import re

def enhance_weight(data):
    """
    Enhance weight information in product data.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Data with enhanced weight information
    """
    enhanced_data = data.copy()
    
    # Look for weight in various fields
    weight_fields = ['weight', 'peso', 'mass', 'masa', 'title', 'titulo', 'description', 'descripcion', 'specifications', 'especificaciones']
    
    for field in weight_fields:
        if field in data and data[field]:
            weight_info = extract_weight(str(data[field]))
            if weight_info:
                enhanced_data['weight'] = weight_info['value']
                enhanced_data['weight_unit'] = weight_info['unit']
                enhanced_data['peso'] = weight_info['value']  # Spanish equivalent
                enhanced_data['unidad_peso'] = get_spanish_unit(weight_info['unit'])
                break
    
    return enhanced_data

def extract_weight(text):
    """
    Extract weight value and unit from text.
    
    Args:
        text (str): Text to search for weight
        
    Returns:
        dict: Dictionary with 'value' and 'unit' keys, or None if not found
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Pattern to match weight with units
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(kg|kilogram|kilos?|kilogramo)',
        r'(\d+(?:\.\d+)?)\s*(g|gram|gramo|gr)',
        r'(\d+(?:\.\d+)?)\s*(lb|pound|libra)',
        r'(\d+(?:\.\d+)?)\s*(oz|ounce|onza)',
        r'(\d+(?:\.\d+)?)\s*(ton|tonelada)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            value = float(match.group(1))
            unit = normalize_weight_unit(match.group(2))
            return {'value': value, 'unit': unit}
    
    return None

def normalize_weight_unit(unit):
    """
    Normalize weight unit to standard format.
    
    Args:
        unit (str): Weight unit to normalize
        
    Returns:
        str: Normalized weight unit
    """
    if not unit:
        return ""
    
    unit_lower = unit.lower().strip()
    
    unit_mappings = {
        'kg': 'kg',
        'kilogram': 'kg',
        'kilo': 'kg',
        'kilos': 'kg',
        'kilogramo': 'kg',
        'g': 'g',
        'gram': 'g',
        'gramo': 'g',
        'gr': 'g',
        'lb': 'lb',
        'pound': 'lb',
        'libra': 'lb',
        'oz': 'oz',
        'ounce': 'oz',
        'onza': 'oz',
        'ton': 'ton',
        'tonelada': 'ton'
    }
    
    return unit_mappings.get(unit_lower, unit_lower)

def get_spanish_unit(english_unit):
    """
    Get Spanish equivalent of English weight unit.
    
    Args:
        english_unit (str): English weight unit
        
    Returns:
        str: Spanish weight unit
    """
    spanish_mappings = {
        'kg': 'kg',
        'g': 'g',
        'lb': 'libra',
        'oz': 'onza',
        'ton': 'tonelada'
    }
    
    return spanish_mappings.get(english_unit.lower(), english_unit)
