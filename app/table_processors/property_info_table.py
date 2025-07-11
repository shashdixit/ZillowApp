import os
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_property_info_table(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the property info table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename)
    print(f"Processing Property Info Table for {filename}...")

    filename_ = os.path.splitext(filename)[0]

    # Extract recording document number from filename
    if filename_.isdigit(): # Exceptions - Clinton
        doc_no = filename_
    elif filename_.startswith('2025_'):
        doc_no = filename_[:4] + filename_[5:]
    else:
        doc_no = filename_[:-2]

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

        # Extract APNs and format them into a list
        apns = parsed_results.get("assessor_parcel_number", "").split(",")
        unformatted_apns = parsed_results.get("unformatted_assessor_parcel_number", "").split(",")

        # Determine the number of rows to write (at least 1)
        num_apns = max(len(apns), 1) if apns[0] != '' else 1

        all_output_rows = []

        # Write the rows to the CSV file
        for i in range(num_apns):
            output_row = []
            for column_name in all_column_names:
                if column_name == 'recording_document_number':
                    if parsed_results.get('fips', "") in ['40003', '40005', '40007', '40025', '40029', '40043', '40055', '40059', '40063', '40127', '40139', '40129', '41037']:
                        doc_no = doc_no[:4] + '-' + doc_no[4:]
                    elif parsed_results.get('fips', "") == '40067':
                        doc_no = 'W-' + doc_no[:6]
                    output_row.append(doc_no)
                elif column_name in ["fips","recording_book_number","recording_page_number","data_class_stnd_code","recording_date"]:
                    output_row.append(parsed_results.get(column_name, ""))
                elif column_name in ["raw_legal_lot", "legal_lot", "raw_legal_block", "legal_block", "raw_legal_subdivision_name", "legal_subdivision_name", "legal_condo_project_pud_dev_name", "legal_building_number", "raw_legal_unit", "legal_unit", "raw_legal_section", "legal_section", "raw_legal_phase", "legal_phase", "raw_legal_tract", "legal_tract", "raw_legal_district", "legal_district", "raw_legal_municipality", "legal_municipality", "raw_legal_city", "legal_city", "raw_legal_township", "legal_township", "raw_legal_sec_twn_rng_mer", "legal_sec_twn_rng_mer", "raw_legal_recorders_map_reference", "legal_recorders_map_reference", "raw_legal_description", "legal_description"] and parsed_results.get("data_class_stnd_code") == 'M':
                    output_row.append("")
                elif column_name == 'property_sequence_number':
                    output_row.append(i+1)
                elif column_name == "assessor_parcel_number" and i < len(apns):
                    output_row.append(apns[i].strip())
                elif column_name == "unformatted_assessor_parcel_number" and i < len(unformatted_apns):
                    output_row.append(unformatted_apns[i].strip())
                elif column_name == "apn_indicator_stnd_code" and i == 99:
                    output_row.append('H')
                elif i > 0:  # For subsequent rows, leave other columns empty
                    output_row.append("")
                else:
                    if column_name == 'property_street_suffix':
                        output_row.append(get_street_suffix(parsed_results.get("property_full_street_address", "")))
                        continue
                    output_row.append(parsed_results.get(column_name, ""))
            
            all_output_rows.append(output_row)
        
        return all_output_rows

    except Exception as e:
        print(f"Error processing Property Info Table for {filename}: {e}")
        return None