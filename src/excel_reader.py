import pandas as pd
import os

def read_excel(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if ext == ".xlsx":
        try:
            return pd.read_excel(file_path, engine="openpyxl")
        except Exception as e:
            raise ValueError(f"Failed to read .xlsx file: {e}")
    elif ext == ".xls":
        try:
            return pd.read_excel(file_path, engine="xlrd")
        except Exception as e:
            raise ValueError(f"Failed to read .xls file: {e}")
    else:
        raise ValueError(f"Unsupported Excel file extension: {ext}")
