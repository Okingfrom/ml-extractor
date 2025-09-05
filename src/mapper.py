import pandas as pd
from .enrichment import apply_enrichments

def apply_mapping(data, mapping, template_columns):
    """
    Apply mapping and enrichment to product data.
    
    Args:
        data: DataFrame or dict containing product data
        mapping: dict of source_column -> template_column mappings
        template_columns: list of Mercado Libre template columns
        
    Returns:
        DataFrame: Mapped and enriched product data
    """
    # Convert DataFrame row to dict if needed
    if isinstance(data, pd.DataFrame):
        if len(data) > 0:
            row_data = data.iloc[0].to_dict()
        else:
            row_data = {}
    else:
        row_data = data.copy() if isinstance(data, dict) else {}
    
    # Apply enrichments first to enhance available data
    enriched_data = apply_enrichments(row_data)
    
    # Apply column mapping
    mapped = {}
    for src_col, tpl_col in mapping.items():
        if src_col in enriched_data:
            mapped[tpl_col] = enriched_data[src_col]
    
    # Ensure all template columns are present
    result = {col: mapped.get(col, "") for col in template_columns}
    
    return pd.DataFrame([result])