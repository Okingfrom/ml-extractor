import pandas as pd

def apply_mapping(data, mapping, template_columns):
    # data: DataFrame or dict
    # mapping: dict of source_column -> template_column
    # template_columns: list of Mercado Libre template columns
    mapped = {}
    for src_col, tpl_col in mapping.items():
        if src_col in data:
            mapped[tpl_col] = data[src_col]
    # Ensure all template columns are present
    result = {col: mapped.get(col, "") for col in template_columns}
    return pd.DataFrame([result])