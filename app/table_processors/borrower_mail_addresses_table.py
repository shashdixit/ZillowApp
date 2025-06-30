import os
import re
import csv
from app.classify import classify_document
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_borrower_mail_addresses(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the borrower mail addresses table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename)
    print(f"Processing Borrower Mail Addresses Table for {filename}...")

    # Extract recording document number from filename
    match = re.search(r'\d+', filename)
    doc_no = match.group() if match else None

    property_info_csv_path = os.path.join("app/Output Files", "property_info.csv")

    if(classify_document(pdf_path) == 'D'):
        return None
    elif property_info_csv_path and doc_no:
        if check_property_address_in_csv(property_info_csv_path, doc_no):
            return None  

    pdf_base64 = encode_pdf(pdf_path)

    def get_street_suffix(address):
        parts = address.split()
        
        # Ensure there's at least a number and one word after it
        if len(parts) > 2:
            return parts[-1]  # Return the last word
        return ""

    try:
        llm_response = await query_llm(session, pdf_base64, system_prompt, message_prompt)
        parsed_results = parse_csv_response(llm_response)

        output_row = []

        for column_name in all_column_names:
            if column_name == 'recording_document_number':
                if parsed_results.get('fips', "") == '40003':
                    doc_no = doc_no[:4] + '-' + doc_no[4:]
                output_row.append(doc_no)
            else:
                if column_name == 'borrower_mail_street_suffix':
                    output_row.append(get_street_suffix(parsed_results.get("borrower_mail_full_street_address", "")))
                    continue
                output_row.append(parsed_results.get(column_name, ""))

        return [output_row]

    except Exception as e:
        print(f"Error processing Borrower Mail Addresses Table for {filename}: {e}")
        return None
    
def check_property_address_in_csv(csv_path, recording_document_number):
    """
    Check if the property_street_name column is populated for a given recording_document_number in the CSV.
    """
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('recording_document_number') == recording_document_number:
                    if row.get('property_street_name'):  # Check if property_street_name is populated
                        return True
        return False  # recording_document_number not found or property_street_name is empty
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return False
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False