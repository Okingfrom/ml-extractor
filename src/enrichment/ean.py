"""
EAN Enhancement Module
Provides EAN/barcode detection and validation functionality.
"""

import re

def enhance_ean(data):
    """
    Enhance EAN/barcode information in product data.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Data with enhanced EAN information
    """
    enhanced_data = data.copy()
    
    # Look for EAN in various fields
    ean_fields = ['ean', 'barcode', 'codigo_barras', 'upc', 'gtin', 'isbn']
    
    for field in ean_fields:
        if field in data and data[field]:
            ean_value = extract_ean(str(data[field]))
            if ean_value:
                enhanced_data['ean'] = ean_value
                enhanced_data['codigo_barras'] = ean_value  # Spanish equivalent
                enhanced_data['ean_valid'] = validate_ean(ean_value)
                break
    
    return enhanced_data

def extract_ean(text):
    """
    Extract EAN/barcode from text.
    
    Args:
        text (str): Text to search for EAN
        
    Returns:
        str: Extracted EAN code or None if not found
    """
    if not text:
        return None
    
    # Remove spaces and non-numeric characters except hyphens
    clean_text = re.sub(r'[^\d\-]', '', text.strip())
    
    # Look for common EAN patterns
    patterns = [
        r'\b(\d{13})\b',  # EAN-13
        r'\b(\d{12})\b',  # UPC-A
        r'\b(\d{8})\b',   # EAN-8
        r'\b(\d{14})\b',  # GTIN-14
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_text)
        if match:
            return match.group(1)
    
    # If we have a string of digits, check if it's a valid length
    if clean_text.isdigit():
        length = len(clean_text)
        if length in [8, 12, 13, 14]:
            return clean_text
    
    return None

def validate_ean(ean_code):
    """
    Validate EAN code using check digit algorithm.
    
    Args:
        ean_code (str): EAN code to validate
        
    Returns:
        bool: True if EAN is valid, False otherwise
    """
    if not ean_code or not ean_code.isdigit():
        return False
    
    length = len(ean_code)
    
    # Only validate common EAN lengths
    if length not in [8, 12, 13, 14]:
        return False
    
    try:
        # Convert to list of integers
        digits = [int(d) for d in ean_code]
        
        # Check digit is the last digit
        check_digit = digits[-1]
        code_digits = digits[:-1]
        
        # Calculate check digit based on length
        if length == 13:  # EAN-13
            calculated_check = calculate_ean13_check(code_digits)
        elif length == 8:   # EAN-8
            calculated_check = calculate_ean8_check(code_digits)
        elif length == 12:  # UPC-A
            calculated_check = calculate_upc_check(code_digits)
        else:
            # For other lengths, use basic modulo 10 check
            calculated_check = calculate_basic_check(code_digits)
        
        return check_digit == calculated_check
    except (ValueError, IndexError):
        return False

def calculate_ean13_check(digits):
    """Calculate EAN-13 check digit."""
    total = sum(digits[i] * (3 if i % 2 else 1) for i in range(12))
    return (10 - (total % 10)) % 10

def calculate_ean8_check(digits):
    """Calculate EAN-8 check digit."""
    total = sum(digits[i] * (3 if i % 2 else 1) for i in range(7))
    return (10 - (total % 10)) % 10

def calculate_upc_check(digits):
    """Calculate UPC-A check digit."""
    total = sum(digits[i] * (3 if i % 2 else 1) for i in range(11))
    return (10 - (total % 10)) % 10

def calculate_basic_check(digits):
    """Calculate basic modulo 10 check digit."""
    total = sum(digits[i] * (2 if i % 2 else 1) for i in range(len(digits)))
    return (10 - (total % 10)) % 10
