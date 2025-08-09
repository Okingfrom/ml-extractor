import pandas as pd
import docx
import PyPDF2

def read_excel(file_path):
    return pd.read_excel(file_path)

def read_csv(file_path):
    return pd.read_csv(file_path)

def read_txt(file_path):
    with open(file_path, "r") as f:
        return f.read()

def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text