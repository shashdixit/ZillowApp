import os
import re
from app.classify import classify_document
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_buyer_mail_addresses(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the buyer mail addresses table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename)
    print(f"Processing Buyer Mail Addresses Table for {filename}...")

    if(classify_document(pdf_path) == 'M'):
        return None

    match = re.search(r'\d+', filename)
    doc_no = match.group() if match else None

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
                if column_name == 'buyer_mail_street_suffix':
                    output_row.append(get_street_suffix(parsed_results.get("buyer_mail_full_street_address", "")))
                    continue
                output_row.append(parsed_results.get(column_name, ""))

        return [output_row]

    except Exception as e:
        print(f"Error processing Buyer Mail Addresses Table for {filename}: {e}")
        return None