import streamlit as st
import pandas as pd
from src.file_reader import read_excel, read_csv, read_txt, read_docx, read_pdf
from src.mapping_loader import load_mapping
from src.mapper import apply_mapping

st.title("Mercado Libre Bulk Mapper")

uploaded_template = st.file_uploader("Upload Mercado Libre Template (.xlsx)", type=["xlsx"])
uploaded_content = st.file_uploader("Upload Product Data (Excel, CSV, PDF, DOCX, TXT)", type=["xlsx", "xls", "csv", "pdf", "docx", "txt"])
config_path = st.text_input("Mapping Config Path", "config/mapping.yaml")

if st.button("Process") and uploaded_template and uploaded_content:
    ext = uploaded_content.name.split('.')[-1].lower()
    # Save uploaded files temporarily
    template_path = f"temp_template.xlsx"
    content_path = f"temp_content.{ext}"
    with open(template_path, "wb") as f:
        f.write(uploaded_template.getbuffer())
    with open(content_path, "wb") as f:
        f.write(uploaded_content.getbuffer())

    template_columns, mapping = load_mapping(config_path)
    if ext in ["xlsx", "xls"]:
        data = read_excel(content_path)
        if isinstance(data, pd.DataFrame):
            data = data.iloc[0].to_dict()
    elif ext == "csv":
        data = read_csv(content_path)
        if isinstance(data, pd.DataFrame):
            data = data.iloc[0].to_dict()
    elif ext == "txt":
        data = {}  # Add TXT parsing logic
    elif ext == "docx":
        doc_text = read_docx(content_path)
        data = {}  # Add DOCX parsing logic
    elif ext == "pdf":
        pdf_text = read_pdf(content_path)
        data = {}  # Add PDF parsing logic
    else:
        st.error("Unsupported file type.")
        st.stop()

    df = apply_mapping(data, mapping, template_columns)
    output_path = "output.xlsx"
    df.to_excel(output_path, index=False)
    st.success(f"Mapped data written to {output_path}")
    with open(output_path, "rb") as f:
        st.download_button("Download Output Excel", f, file_name="output.xlsx")