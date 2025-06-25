import os
import re
from datetime import datetime
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_main_table(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the main table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename) 
    print(f"Processing Main Table for {filename}...")

    match = re.search(r'\d+', filename)
    doc_no = match.group()

    pdf_base64 = encode_pdf(pdf_path)

    try:
        llm_response = await query_llm(session, pdf_base64, system_prompt, message_prompt)
        parsed_results = parse_csv_response(llm_response)

        output_row = []

        for column_name in all_column_names:
            if column_name == 'recording_document_number':
                if parsed_results.get('county', "").upper() == 'ALFALFA':
                    doc_no = doc_no[:4] + '-' + doc_no[4:]
                output_row.append(doc_no)
            elif column_name in ["raw_buyer_vesting_stnd_code","buyer_vesting_stnd_code","raw_sales_price_amount","sales_price_amount","sales_price_amount_stnd_code","occupancy_status_stnd_code"] and parsed_results.get("data_class_stnd_code") == 'M':
                output_row.append("")
            elif column_name in ["raw_lender_name","lender_name","raw_lender_type_stnd_code","lender_type_stnd_code","raw_lender_dba_name","lender_dba_name","raw_dba_lender_type_stnd_code","dba_lender_type_stnd_code","raw_loan_amount","loan_amount","loan_amount_std_code","maximum_loan_amount","raw_loan_type_stnd_code","loan_type_stnd_code","loan_type_closed_open_end_stnd_code","raw_loan_type_program_stnd_code","loan_type_program_stnd_code","raw_loan_rate_type_stnd_code","loan_rate_type_stnd_code","raw_loan_due_date","loan_due_date","loan_term_months","loan_term_years"] and parsed_results.get("data_class_stnd_code") == 'D':
                output_row.append("")
            elif column_name == 'image_file_name':
                output_row.append(filename)
            elif column_name == 'keyed_date':
                today = datetime.today().strftime('%Y-%m-%d')
                output_row.append(today)
            else:
                output_row.append(parsed_results.get(column_name, ""))

        return [output_row]

    except Exception as e:
        print(f"Error processing Main Table for {filename}: {e}")
        return None