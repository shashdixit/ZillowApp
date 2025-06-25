import os
import re
from app.classify import classify_document
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_seller_names(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for the seller names table."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename)
    print(f"Processing Seller Names Table for {filename}...")

    if(classify_document(pdf_path) == 'M'):
        return None

    match = re.search(r'\d+', filename)

    pdf_base64 = encode_pdf(pdf_path)

    try:
        llm_response = await query_llm(session, pdf_base64, system_prompt, message_prompt)
        parsed_results = parse_csv_response(llm_response)

        output_row = []

        rnames = parsed_results.get("raw_seller_individual_full_name", "").split(",")
        names = parsed_results.get("seller_individual_full_name", "").split(",")
        rni_names = parsed_results.get("raw_seller_non_individual_full_name", "").split(";")
        ni_names = parsed_results.get("seller_non_individual_name", "").split(";")

        rn = len(rnames) if rnames[0] != '' else 0
        n = len(names) if names[0] != '' else 0
        rni = len(rni_names) if rni_names[0] != '' else 0
        ni = len(ni_names) if ni_names[0] != '' else 0
        num_names = max(n + ni, 1)
        i = 0
        j = 0
        flag = 1

        all_output_rows = []

        # Write the rows to the CSV file
        while i + j < num_names:

            output_row = []
            
            # Common columns
            output_row.append(parsed_results.get("fips", ""))
            output_row.append(parsed_results.get("record_id", ""))
            output_row.append(parsed_results.get("index_key", ""))
            output_row.append(parsed_results.get("data_class_stnd_code", ""))
            output_row.append(parsed_results.get("recording_date", ""))
            output_row.append(match.group() if match else "")  # recording_document_number
            output_row.append(parsed_results.get("recording_book_number", ""))
            output_row.append(parsed_results.get("recording_page_number", ""))

            # Seller Names columns
            if i < n:
                output_row.append("")
                output_row.append(" ".join(names[i].strip().split()[:-1]))  # seller_first_middle_name
                output_row.append("")
                output_row.append(names[i].strip().split()[-1])  # seller_last_name
                if i < rn:
                    output_row.append(rnames[i].strip())  # raw_seller_individual_full_name
                else:
                    output_row.append("")
                output_row.append(names[i].strip())  # seller_individual_full_name
            else:
                output_row.extend(["", "", "", "", "", ""])  # Empty values if no individual name


            if i == n and j < rni:
                output_row.append(rni_names[j].strip())  # raw_seller_non_individual_full_name
                flag = 0
            else:
                output_row.append("")

            if i == n and j < ni:
                output_row.append(ni_names[j].strip())  # seller_non_individual_name
            else:
                output_row.append("")

            output_row.append(i+j+1)  # seller_name_sequence_number
            output_row.append("")  # seller_mail_sequence_number

            if flag:
                i += 1
            else:
                j += 1
            all_output_rows.append(output_row)

        return all_output_rows  # Return the list of rows

    except Exception as e:
        print(f"Error processing Seller Names Table for {filename}: {e}")
        return None