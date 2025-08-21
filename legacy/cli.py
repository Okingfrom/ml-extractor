#!/usr/bin/env python3
import argparse
import os
import pandas as pd
import streamlit as st
from src.file_reader import read_excel, read_csv, read_txt, read_docx, read_pdf
from src.mapping_loader import load_mapping
from src.mapper import apply_mapping

def main():
    parser = argparse.ArgumentParser(description="Mercado Libre Bulk Mapper CLI")
    parser.add_argument("--input", required=True, help="Input file (Excel, CSV, PDF, DOCX, TXT)")
    parser.add_argument("--config", required=True, help="Mapping config YAML")
    parser.add_argument("--output", required=True, help="Output Excel file")
    args = parser.parse_args()

    # Load mapping config
    template_columns, mapping = load_mapping(args.config)

    # Read input file
    ext = os.path.splitext(args.input)[1].lower()
    if ext in [".xlsx", ".xls"]:
        data = read_excel(args.input)
        # If DataFrame, convert to dict for mapping
        if isinstance(data, pd.DataFrame):
            # Use first row or iterate as needed
            data = data.iloc[0].to_dict()
    elif ext == ".csv":
        data = read_csv(args.input)
        if isinstance(data, pd.DataFrame):
            data = data.iloc[0].to_dict()
    elif ext == ".txt":
        data = {}  # Implement TXT parsing logic here
    elif ext == ".docx":
        doc_text = read_docx(args.input)
        data = {}  # Implement DOCX parsing logic here
    elif ext == ".pdf":
        pdf_text = read_pdf(args.input)
        data = {}  # Implement PDF parsing logic here
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Apply mapping
    df = apply_mapping(data, mapping, template_columns)

    # Write output
    df.to_excel(args.output, index=False)
    print(f"Mapped data written to {args.output}")

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

if __name__ == "__main__":
    main()