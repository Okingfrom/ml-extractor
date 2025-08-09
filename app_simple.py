import streamlit as st
import openpyxl
import csv
import docx
import PyPDF2
import yaml
import os

st.title("Mercado Libre Bulk Mapper")

# Test if streamlit works without numpy/pandas
st.write("Streamlit is working!")

uploaded_template = st.file_uploader("Upload Mercado Libre Template (.xlsx)", type=["xlsx"])
uploaded_content = st.file_uploader("Upload Product Data (Excel, CSV, PDF, DOCX, TXT)", type=["xlsx", "xls", "csv", "pdf", "docx", "txt"])
config_path = st.text_input("Mapping Config Path", "config/mapping.yaml")

if st.button("Process") and uploaded_template and uploaded_content:
    st.write("Processing files...")
    st.write(f"Template: {uploaded_template.name}")
    st.write(f"Content: {uploaded_content.name}")
    st.write(f"Config: {config_path}")
    
    # For now, just show that the files were uploaded
    st.success("Files uploaded successfully! (Processing logic needs to be implemented without pandas)")
