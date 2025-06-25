import os
import re
from app.classify import classify_document
from app.llm_utils import encode_pdf, query_llm, parse_csv_response

async def process_buyer_data(filename, session, system_prompt, message_prompt, all_column_names, PDF_DIRECTORY):
    """Process data for both buyer names and buyer description code tables."""
    pdf_path = os.path.join(PDF_DIRECTORY, filename)
    print(f"Processing Buyer Data (Names and Descriptions) for {filename}...")

    if(classify_document(pdf_path) == 'M'):
        return None, None

    match = re.search(r'\d+', filename)

    pdf_base64 = encode_pdf(pdf_path)

    try:
        llm_response = await query_llm(session, pdf_base64, system_prompt, message_prompt)
        parsed_results = parse_csv_response(llm_response)

        # Extract data for buyer names
        rnames = parsed_results.get("raw_buyer_individual_full_name", "").split(",")
        names = parsed_results.get("buyer_individual_full_name", "").split(",")
        rni_names = parsed_results.get("raw_buyer_non_individual_name", "").split(";")
        ni_names = parsed_results.get("buyer_non_individual_name", "").split(";")

        rn = len(rnames) if rnames[0] != '' else 0
        n = len(names) if names[0] != '' else 0
        rni = len(rni_names) if rni_names[0] != '' else 0
        ni = len(ni_names) if ni_names[0] != '' else 0
        num_names = max(n + ni, 1)

        # Extract data for buyer descriptions
        raw_desc = parsed_results.get("raw_buyer_description_stnd_code", "").split(",")
        desc = parsed_results.get("buyer_description_stnd_code", "").split(",")

        buyer_names_rows = []
        buyer_desc_rows = []
        i = 0
        j = 0
        flag = 1

        # Combine and write rows
        while i + j < num_names:
            # Buyer Names data
            buyer_names_row = []

            # Common columns
            buyer_names_row.append(parsed_results.get("fips", ""))
            buyer_names_row.append(parsed_results.get("record_id", ""))
            buyer_names_row.append(parsed_results.get("index_key", ""))
            buyer_names_row.append(parsed_results.get("data_class_stnd_code", ""))
            buyer_names_row.append(parsed_results.get("recording_date", ""))
            buyer_names_row.append(match.group() if match else "")  # recording_document_number
            buyer_names_row.append(parsed_results.get("recording_book_number", ""))
            buyer_names_row.append(parsed_results.get("recording_page_number", ""))

            # Buyer Names columns
            if i < n:
                buyer_names_row.append("")
                buyer_names_row.append(" ".join(names[i].strip().split()[:-1]))  # buyer_first_middle_name
                buyer_names_row.append("")
                buyer_names_row.append(names[i].strip().split()[-1])  # buyer_last_name
                if i < rn:
                    buyer_names_row.append(rnames[i].strip())  # raw_buyer_individual_full_name
                else:
                    buyer_names_row.append("")
                buyer_names_row.append(names[i].strip())  # buyer_individual_full_name
            else:
                buyer_names_row.extend(["", "", "", "", "", ""])  # Empty values if no individual name


            if i == n and j < rni:
                buyer_names_row.append(rni_names[j].strip())  # raw_buyer_non_individual_name
                flag = 0
            else:
                buyer_names_row.append("")

            if i == n and j < ni:
                buyer_names_row.append(ni_names[j].strip())  # buyer_non_individual_name
            else:
                buyer_names_row.append("")

            buyer_names_row.append(i+j+1)  # buyer_name_sequence_number
            buyer_names_row.append(1)  # buyer_mail_sequence_number

            buyer_names_rows.append(buyer_names_row)

            # Buyer Description data
            buyer_desc_row = []

            # Common columns
            buyer_desc_row.append(parsed_results.get("fips", ""))
            buyer_desc_row.append(parsed_results.get("record_id", ""))
            buyer_desc_row.append(parsed_results.get("index_key", ""))
            buyer_desc_row.append(parsed_results.get("data_class_stnd_code", ""))
            buyer_desc_row.append(parsed_results.get("recording_date", ""))
            buyer_desc_row.append(match.group() if match else "")  # recording_document_number
            buyer_desc_row.append(parsed_results.get("recording_book_number", ""))
            buyer_desc_row.append(parsed_results.get("recording_page_number", ""))

            # Buyer Description columns
            if i + j < len(raw_desc):
                buyer_desc_row.append(raw_desc[i + j].strip())  # raw_buyer_description_stnd_code
            else:
                buyer_desc_row.append("")

            if i + j < len(desc):
                buyer_desc_row.append(desc[i + j].strip())  # buyer_description_stnd_code
            else:
                buyer_desc_row.append("")

            buyer_desc_row.append(1)  # buyer_desc_sequence_number
            buyer_desc_row.append(i+j+1)  # buyer_name_sequence_number

            buyer_desc_rows.append(buyer_desc_row)

            if flag:
                i += 1
            else:
                j += 1

        return buyer_names_rows, buyer_desc_rows

    except Exception as e:
        print(f"Error processing Buyer Data for {filename}: {e}")
        return None, None