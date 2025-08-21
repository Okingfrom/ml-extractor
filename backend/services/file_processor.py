"""
File processing service - handles file reading and data extraction
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import existing file readers
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from excel_reader import ExcelReader
from pdf_reader import PDFReader
from docx_reader import DocxReader
from text_reader import TextReader

class FileProcessorService:
    """Service for processing various file types"""
    
    def __init__(self):
        self.excel_reader = ExcelReader()
        self.pdf_reader = PDFReader()
        self.docx_reader = DocxReader()
        self.text_reader = TextReader()
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read file and extract data based on file type
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension in ['.xlsx', '.xls']:
                return self._read_excel_file(file_path)
            elif file_extension == '.csv':
                return self._read_csv_file(file_path)
            elif file_extension == '.pdf':
                return self._read_pdf_file(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._read_docx_file(file_path)
            elif file_extension == '.txt':
                return self._read_text_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
    
    def _read_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Read Excel file using existing ExcelReader"""
        
        try:
            # Use existing excel reader
            data = self.excel_reader.read(file_path)
            
            # Convert to pandas DataFrame for easier processing
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data[1:], columns=data[0])  # First row as headers
            else:
                df = pd.DataFrame()
            
            return {
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "rows": len(df),
                "file_type": "excel",
                "sheets": ["Sheet1"],  # Simplified for now
                "metadata": {
                    "has_headers": True,
                    "encoding": "utf-8"
                }
            }
            
        except Exception as e:
            # Fallback to pandas
            try:
                df = pd.read_excel(file_path)
                return {
                    "data": df.to_dict('records'),
                    "columns": df.columns.tolist(),
                    "rows": len(df),
                    "file_type": "excel",
                    "sheets": ["Sheet1"],
                    "metadata": {
                        "has_headers": True,
                        "encoding": "utf-8"
                    }
                }
            except Exception as fallback_error:
                raise Exception(f"Failed to read Excel file: {str(fallback_error)}")
    
    def _read_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Read CSV file"""
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            used_encoding = 'utf-8'
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise Exception("Could not read CSV file with any supported encoding")
            
            return {
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "rows": len(df),
                "file_type": "csv",
                "metadata": {
                    "has_headers": True,
                    "encoding": used_encoding,
                    "delimiter": ","
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to read CSV file: {str(e)}")
    
    def _read_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Read PDF file using existing PDFReader"""
        
        try:
            # Use existing PDF reader
            text_content = self.pdf_reader.read(file_path)
            
            # For PDFs, we'll extract text and try to parse it as structured data
            # This is simplified - in practice, you might need more sophisticated parsing
            lines = text_content.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            return {
                "data": [{"text": line, "line_number": i+1} for i, line in enumerate(lines)],
                "columns": ["text", "line_number"],
                "rows": len(lines),
                "file_type": "pdf",
                "metadata": {
                    "has_headers": False,
                    "encoding": "utf-8",
                    "extracted_text_length": len(text_content)
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to read PDF file: {str(e)}")
    
    def _read_docx_file(self, file_path: str) -> Dict[str, Any]:
        """Read DOCX file using existing DocxReader"""
        
        try:
            # Use existing DOCX reader
            text_content = self.docx_reader.read(file_path)
            
            # Split into paragraphs
            paragraphs = text_content.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            return {
                "data": [{"paragraph": p, "paragraph_number": i+1} for i, p in enumerate(paragraphs)],
                "columns": ["paragraph", "paragraph_number"],
                "rows": len(paragraphs),
                "file_type": "docx",
                "metadata": {
                    "has_headers": False,
                    "encoding": "utf-8",
                    "extracted_text_length": len(text_content)
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to read DOCX file: {str(e)}")
    
    def _read_text_file(self, file_path: str) -> Dict[str, Any]:
        """Read text file using existing TextReader"""
        
        try:
            # Use existing text reader
            text_content = self.text_reader.read(file_path)
            
            # Split into lines
            lines = text_content.split('\n')
            lines = [line.rstrip() for line in lines]  # Keep empty lines but remove trailing whitespace
            
            return {
                "data": [{"text": line, "line_number": i+1} for i, line in enumerate(lines)],
                "columns": ["text", "line_number"],
                "rows": len(lines),
                "file_type": "text",
                "metadata": {
                    "has_headers": False,
                    "encoding": "utf-8",
                    "total_lines": len(lines)
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to read text file: {str(e)}")
    
    def get_file_preview(self, file_path: str, max_rows: int = 10) -> Dict[str, Any]:
        """
        Get a preview of the file (first few rows)
        
        Args:
            file_path: Path to the file
            max_rows: Maximum number of rows to return
            
        Returns:
            Dictionary containing preview data
        """
        
        try:
            file_data = self.read_file(file_path)
            
            # Limit data to max_rows
            preview_data = file_data["data"][:max_rows]
            
            return {
                "data": preview_data,
                "columns": file_data["columns"],
                "total_rows": file_data["rows"],
                "preview_rows": len(preview_data),
                "file_type": file_data["file_type"],
                "metadata": file_data["metadata"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate file preview: {str(e)}")
    
    def detect_file_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze file structure and suggest mapping options
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing structure analysis
        """
        
        try:
            file_data = self.read_file(file_path)
            
            # Analyze columns/fields
            columns = file_data["columns"]
            sample_data = file_data["data"][:5]  # First 5 rows for analysis
            
            column_analysis = {}
            for col in columns:
                column_analysis[col] = self._analyze_column(col, sample_data)
            
            return {
                "columns": columns,
                "column_count": len(columns),
                "row_count": file_data["rows"],
                "file_type": file_data["file_type"],
                "column_analysis": column_analysis,
                "suggested_mappings": self._suggest_mappings(columns),
                "metadata": file_data["metadata"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to detect file structure: {str(e)}")
    
    def _analyze_column(self, column_name: str, sample_data: List[Dict]) -> Dict[str, Any]:
        """Analyze a column to determine its characteristics"""
        
        # Extract values for this column
        values = []
        for row in sample_data:
            if column_name in row and row[column_name] is not None:
                values.append(str(row[column_name]))
        
        if not values:
            return {
                "data_type": "unknown",
                "has_data": False,
                "sample_values": []
            }
        
        # Determine data type
        data_type = "text"
        if all(self._is_numeric(v) for v in values):
            data_type = "numeric"
        elif all(self._is_date(v) for v in values):
            data_type = "date"
        elif all(self._is_boolean(v) for v in values):
            data_type = "boolean"
        
        return {
            "data_type": data_type,
            "has_data": True,
            "sample_values": values[:3],  # First 3 values
            "unique_values": len(set(values)),
            "contains_nulls": any(v == "" or v.lower() in ["null", "none", "n/a"] for v in values)
        }
    
    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric"""
        try:
            float(value.replace(",", ""))
            return True
        except ValueError:
            return False
    
    def _is_date(self, value: str) -> bool:
        """Check if value looks like a date"""
        try:
            pd.to_datetime(value)
            return True
        except:
            return False
    
    def _is_boolean(self, value: str) -> bool:
        """Check if value is boolean"""
        return value.lower() in ["true", "false", "yes", "no", "1", "0", "si", "no"]
    
    def _suggest_mappings(self, columns: List[str]) -> Dict[str, str]:
        """Suggest target field mappings based on column names"""
        
        # Common mapping patterns (case-insensitive)
        mapping_patterns = {
            # Product fields
            r".*product.*name.*|.*name.*product.*|.*title.*|.*titulo.*": "title",
            r".*description.*|.*desc.*|.*descripcion.*": "description",
            r".*price.*|.*precio.*|.*cost.*|.*costo.*": "price",
            r".*category.*|.*categoria.*|.*cat.*": "category",
            r".*brand.*|.*marca.*|.*manufacturer.*": "brand",
            r".*stock.*|.*inventory.*|.*cantidad.*|.*qty.*": "stock_quantity",
            r".*sku.*|.*code.*|.*codigo.*|.*id.*": "sku",
            r".*weight.*|.*peso.*|.*wt.*": "weight",
            r".*color.*|.*colour.*": "color",
            r".*size.*|.*talla.*|.*tamano.*": "size",
            
            # Contact fields
            r".*email.*|.*correo.*": "email",
            r".*phone.*|.*telefono.*|.*tel.*": "phone",
            r".*address.*|.*direccion.*": "address",
            r".*city.*|.*ciudad.*": "city",
            r".*country.*|.*pais.*": "country",
            
            # General fields
            r".*date.*|.*fecha.*": "date",
            r".*status.*|.*estado.*": "status",
            r".*notes.*|.*notas.*|.*comments.*": "notes"
        }
        
        import re
        suggested = {}
        
        for column in columns:
            for pattern, target_field in mapping_patterns.items():
                if re.match(pattern, column.lower()):
                    suggested[column] = target_field
                    break
        
        return suggested
