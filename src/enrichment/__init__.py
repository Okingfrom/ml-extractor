"""
ML Extractor Enrichment Module
Provides data enrichment functionality for product mapping.
"""

from .brand import enhance_brand
from .sku import enhance_sku
from .color import enhance_color
from .weight import enhance_weight
from .ean import enhance_ean

__all__ = ['enhance_brand', 'enhance_sku', 'enhance_color', 'enhance_weight', 'enhance_ean']

def apply_enrichments(data):
    """
    Apply all enrichment functions to the data in sequence.
    
    Args:
        data (dict): Product data dictionary
        
    Returns:
        dict: Enriched product data
    """
    enriched_data = data.copy()
    
    # Apply enrichment functions in order
    enriched_data = enhance_brand(enriched_data)
    enriched_data = enhance_sku(enriched_data)
    enriched_data = enhance_color(enriched_data)
    enriched_data = enhance_weight(enriched_data)
    enriched_data = enhance_ean(enriched_data)
    
    return enriched_data
