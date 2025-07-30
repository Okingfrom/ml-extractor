import argparse
import logging
from src.input_handler import handle_input
from src.data_mapper import map_data
from src.ml_excel_writer import write_ml_excel

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="ML Extrator: Extract and map product data for Mercado Libre bulk upload.")
    parser.add_argument('input', help='Path to input file (Excel, TXT, DOCX, PDF)')
    parser.add_argument('output', help='Path to output Mercado Libre Excel file')
    parser.add_argument('--config', default='config/mapping.yaml', help='Path to mapping configuration file')
    args = parser.parse_args()

    logging.info(f"Reading input: {args.input}")
    content = handle_input(args.input)
    logging.info("Mapping data...")
    mapped = map_data(content, args.config)
    logging.info(f"Writing Mercado Libre Excel: {args.output}")
    write_ml_excel(mapped, args.output)
    logging.info("Done.")

if __name__ == "__main__":
    main()
