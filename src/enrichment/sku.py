"""
SKU Enhancement Module
Provides SKU generation and normalization functionality.
"""

import re
import hashlib

def enhance_sku(data):
    """
    Enhance SKU information in product data.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Data with enhanced SKU information
    """
    enhanced_data = data.copy()
    
    # Look for existing SKU
    sku_fields = ['sku', 'codigo', 'code', 'item_code', 'product_code']
    sku_value = None
    
    for field in sku_fields:
        if field in data and data[field]:
            sku_value = str(data[field]).strip()
            break
    
    if not sku_value:
        # Generate SKU from available data
        sku_value = generate_sku(data)
    
    if sku_value:
        enhanced_data['sku'] = normalize_sku(sku_value)
    
    return enhanced_data

def generate_sku(data):
    """
    Generate SKU from product data if not present.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        str: Generated SKU
    """
    # Try to build SKU from brand, model, or title
    components = []
    
    # Add brand prefix
    if 'brand' in data and data['brand']:
        brand = str(data['brand'])[:3].upper()
        components.append(brand)
    
    # Add model or title component
    model_fields = ['model', 'modelo', 'title', 'titulo', 'name', 'nombre']
    for field in model_fields:
        if field in data and data[field]:
            model = str(data[field])
            # Extract alphanumeric chars and take first 8
            model_clean = re.sub(r'[^A-Za-z0-9]', '', model)[:8].upper()
            if model_clean:
                components.append(model_clean)
                break
    
    if components:
        return '-'.join(components)
    
    # Fallback: generate from hash of available data
    data_str = str(sorted(data.items()))
    hash_obj = hashlib.md5(data_str.encode())
    return f"GEN-{hash_obj.hexdigest()[:8].upper()}"

def normalize_sku(sku_text):
    """
    Normalize SKU format.
    
    Args:
        sku_text (str): Raw SKU text
        
    Returns:
        str: Normalized SKU
    """
    if not sku_text:
        return ""
    
    # Convert to string and clean
    sku = str(sku_text).strip().upper()
    
    # Remove extra whitespace and non-alphanumeric except hyphens
    sku = re.sub(r'[^A-Z0-9\-]', '', sku)
    
    return sku
