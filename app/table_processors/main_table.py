import os
from datetime import datetime
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_main_table(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the main table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename) 
    print(f"Processing Main Table for {filename}...")

    filename_ = os.path.splitext(filename)[0]

    # Extract recording document number from filename
    if filename_.isdigit(): # Exceptions - Clinton
        doc_no = filename_
    elif filename_.startswith('2025_'):
        doc_no = filename_[:4] + filename_[5:]
    else:
        doc_no = filename_[:-2]

    pdf_base64 = encode_pdf(pdf_path)

    try:
        llm_response = await query_llm(session, pdf_base64, system_prompt, message_prompt)
        parsed_results = parse_csv_response(llm_response)

        output_row = []

        for column_name in all_column_names:
            if column_name == 'recording_document_number':
                if parsed_results.get('fips', "") in ['40003', '40005', '40007', '40025', '40029', '40043', '40055', '40059', '40063', '40127', '40139', '40129', '41037']:
                    doc_no = doc_no[:4] + '-' + doc_no[4:]
                elif parsed_results.get('fips', "") == '40067':
                    doc_no = 'W-' + doc_no[:6]
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