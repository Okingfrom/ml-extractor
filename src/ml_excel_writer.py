import pandas as pd

def write_ml_excel(data, output_path):
    if isinstance(data, pd.DataFrame):
        data.to_excel(output_path, index=False)
    elif isinstance(data, dict):
        # Convert dict to DataFrame for writing
        pd.DataFrame([data]).to_excel(output_path, index=False)
    else:
        raise ValueError('Unsupported data type for writing')
