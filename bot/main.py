from ingestion.pdf_extractor import extract_pdf_to_json
from processing.clean_data import process_bronze_to_silver

def main():
    
    raw_bronze_path = "data/processed/bronze_output.json"
    silver_path = "data/processed/silver_output.json"
    process_bronze_to_silver(raw_bronze_path, silver_path)
    
    """ pdf_file = "data/raw/Harman DTS Handbook 2025.pdf"
    output_file = "data/processed/bronze_ouput.json"
    extract_pdf_to_json(pdf_file , output_file) """
    

if __name__ == "__main__":
    main()