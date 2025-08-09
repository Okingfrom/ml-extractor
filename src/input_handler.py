import os
from src.file_reader import read_excel, read_csv, read_txt, read_docx, read_pdf

def handle_input(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return read_excel(file_path)
    elif ext == ".csv":
        return read_csv(file_path)
    elif ext == ".txt":
        return read_txt(file_path)
    elif ext == ".docx":
        return read_docx(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
