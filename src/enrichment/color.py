"""
Color Enhancement Module
Provides color detection and normalization functionality.
"""

import re

# Common color mappings in Spanish and English
COLOR_MAPPINGS = {
    # Spanish to English
    'rojo': 'red',
    'azul': 'blue', 
    'verde': 'green',
    'amarillo': 'yellow',
    'naranja': 'orange',
    'rosa': 'pink',
    'morado': 'purple',
    'violeta': 'purple',
    'negro': 'black',
    'blanco': 'white',
    'gris': 'gray',
    'marrón': 'brown',
    'café': 'brown',
    # English variations
    'red': 'red',
    'blue': 'blue',
    'green': 'green',
    'yellow': 'yellow',
    'orange': 'orange',
    'pink': 'pink',
    'purple': 'purple',
    'black': 'black',
    'white': 'white',
    'gray': 'gray',
    'grey': 'gray',
    'brown': 'brown'
}

def enhance_color(data):
    """
    Enhance color information in product data.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Data with enhanced color information
    """
    enhanced_data = data.copy()
    
    # Look for color in various fields
    color_fields = ['color', 'colour', 'title', 'titulo', 'description', 'descripcion', 'name', 'nombre']
    detected_colors = []
    
    for field in color_fields:
        if field in data and data[field]:
            colors = extract_colors(str(data[field]))
            detected_colors.extend(colors)
    
    if detected_colors:
        # Take the first detected color and normalize it
        primary_color = detected_colors[0]
        normalized_color = normalize_color(primary_color)
        
        enhanced_data['color'] = normalized_color
        enhanced_data['color_es'] = get_spanish_color(normalized_color)
    
    return enhanced_data

def extract_colors(text):
    """
    Extract color names from text.
    
    Args:
        text (str): Text to search for colors
        
    Returns:
        list: List of detected colors
    """
    if not text:
        return []
    
    text_lower = text.lower()
    detected_colors = []
    
    # Search for known colors
    for color_key in COLOR_MAPPINGS.keys():
        if re.search(r'\b' + re.escape(color_key) + r'\b', text_lower):
            detected_colors.append(color_key)
    
    return detected_colors

def normalize_color(color):
    """
    Normalize color to standard English name.
    
    Args:
        color (str): Color name to normalize
        
    Returns:
        str: Normalized color name
    """
    if not color:
        return ""
    
    color_lower = color.lower().strip()
    return COLOR_MAPPINGS.get(color_lower, color.title())

def get_spanish_color(english_color):
    """
    Get Spanish equivalent of English color.
    
    Args:
        english_color (str): English color name
        
    Returns:
        str: Spanish color name
    """
    reverse_mapping = {v: k for k, v in COLOR_MAPPINGS.items() if v == english_color.lower()}
    spanish_colors = [k for k in reverse_mapping.keys() if k in ['rojo', 'azul', 'verde', 'amarillo', 'naranja', 'rosa', 'morado', 'negro', 'blanco', 'gris', 'marrón']]
    
    return spanish_colors[0] if spanish_colors else english_color
