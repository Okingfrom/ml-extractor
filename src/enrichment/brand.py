"""
Brand Enhancement Module
Provides brand detection and normalization functionality.
"""

import re

def enhance_brand(data):
    """
    Enhance brand information in product data.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Data with enhanced brand information
    """
    enhanced_data = data.copy()
    
    # Look for brand in various fields
    brand_fields = ['brand', 'marca', 'fabricante', 'manufacturer', 'title', 'titulo']
    brand_value = None
    
    for field in brand_fields:
        if field in data and data[field]:
            brand_value = str(data[field]).strip()
            break
    
    if brand_value:
        # Basic brand normalization
        brand_value = normalize_brand(brand_value)
        enhanced_data['brand'] = brand_value
        enhanced_data['marca'] = brand_value  # Spanish equivalent
    
    return enhanced_data

def normalize_brand(brand_text):
    """
    Normalize brand name by cleaning and standardizing format.
    
    Args:
        brand_text (str): Raw brand text
        
    Returns:
        str: Normalized brand name
    """
    if not brand_text:
        return ""
    
    # Convert to string and clean
    brand = str(brand_text).strip()
    
    # Remove extra whitespace
    brand = re.sub(r'\s+', ' ', brand)
    
    # Capitalize first letter of each word
    brand = brand.title()
    
    return brand
