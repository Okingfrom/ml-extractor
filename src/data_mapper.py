import yaml
import pandas as pd

def map_data(content, config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        mapping = yaml.safe_load(f)
    # If content is a DataFrame, map columns
    if isinstance(content, pd.DataFrame):
        return content.rename(columns=mapping['columns'])
    # If content is a string (from TXT, DOCX, PDF), return as dict for now
    elif isinstance(content, str):
        # Placeholder: return as dict with one field
        return {'description': content}
    else:
        raise ValueError('Unsupported content type for mapping')
