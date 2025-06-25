system_prompt = """
You are a data extraction expert. Your task is to extract specific data from a document according to the provided table and column names.
For each table and column combination, extract the corresponding value from the document.
If you cannot find a value for a specific field, leave that empty.
Format your response as a CSV with two columns: ColumnName, Value.
Do not include any explanations or additional text in your response.
"""

message_prompt = """
Analyze the provided PDF document and extract the following information:

Here is the list of all properties with specified conditions to help finding them in document. Read the language of document carefully before filling details.

- fips
{ Populate this field based on county name from below table-
  COUNTY NAME FIPS CODE
    Clinton  26037
    Whitley  21235
    Clark  21049
    Mccracken  21145
    Bullitt  21029
    Elliott  21063
    Wolfe  21237
    Alfalfa  40003
    Beaver  40007
    Cimarron  40025
    Coal  40029
    Dewey  40043
    Ellis  40045
    Greer  40055
    Harper  40059
    Jefferson  40067
    Roger Mills  40129
  If county is not from above then leave this empty. }

- data_class_stnd_code
{ Populate = 'D' if Document title belongs to 'Deed'.
  Populate = 'M' if Document title belongs to 'Mortgage'.
  Note: Land contract will be considered as deed document. }

- recording_date
{ Capture recording date from document.
  Mentioned at top left corner of first page or bottom of last page of document just below document number.
  Reformat it to 'YYYY-MM-DD'. THIS IS ABSOLUTELY MANDATORY. The year MUST come FIRST.  The output MUST be in the format 'YYYY-MM-DD' without exception. Double-check the order, YYYY-MM-DD. }

- recording_book_number
{ Capture book number from the last page of document.
  It is mentioned with keyword 'BOOK'. }

- recording_page_number
{ Capture page number from the last page of document.
  It is mentioned as range with keyword 'PAGES' so take first number in range as value for this field.
  For example: If mentioned like PAGES: 256-258 then populate 256 here. }

- raw_seller_individual_full_name
{ Identify all sellers or grantors in the document and populate here full names of them as comma separated.
  Only capture grantors mentioned in first page of document.  
  Fill here only if grantor is person name and not an organisation or trust name.
  if a.k.a. or f.k.a. names are mentioned then capture them as separate individual names. For example, if seller name is William Jack aka John Jack then there are two sellers - William Jack and John Jack (without keyword aka).
  Look carefully who is buyer and who is seller. Don't populate buyer or grantee name here. }

- seller_individual_full_name
{ It is the value of raw_seller_individual_full_name but remove all punctuations except hyphen ('-') in the name then populate in this field as comma separated.
  If “Samuel M.R. Harvey”, retain spaces & key as “Samuel M R Harvey” (we do not want initials to appear without a space “MR”)
  If “Jennifer Day-St. George”, then key as “Jennifer Day-St George” (retain the hyphen but drop the period and suppress space)
  Populate this field in all capital letters. }

- raw_seller_non_individual_full_name
{ If sellers are trusts, organisations or govt institutions then populate them in this field as ';' separated otherwise leave empty.
  Look carefully if date is mentioned in trust name then capture only trust name here excluding date and 'dated' keyword.
  Remove descriptor keywords like dba, fka, aka, a limited Liabilty company from the name. }

- seller_non_individual_name
{ It is the value of raw_seller_non_individual_full_name but remove all punctuations except ampersand ('&') in the name then populate in this field as comma separated.
  Populate this field in all capital letters. }

Important Notes:
- Sellers can also be mentioned as grantor, party of first part or first party, so look carefully and capture them as sellers.
- Always maintain the order of sellers/grantors as they are mentioned in document.
- If any name is given after 'aka' or 'fka' keyword then consider that as separate individual name. For example, if seller name is William Jack fka John Jack then there are two different sellers - William Jack and John Jack (without keyword fka).
- Capture names only from starting of document and not from later in notary and signature section.
- raw_seller_individual_full_name and raw_seller_non_individual_full_name fields can never be filled together.
- Capture Trustee name in raw_seller_individual_full_name and Trust name in raw_seller_non_individual_full_name.
- If a party name appears multiple times on first page of document and each time the party is described in a different manner, then the name should be keyed as many times as it appears on first page. 

If a piece of information is not found, leave that field empty.
Return the data in CSV format with two columns: ColumnName, Value.
"""

all_column_names = [
    "fips",
    "record_id",
    "index_key",
    "data_class_stnd_code",
    "recording_date",
    "recording_document_number",
    "recording_book_number",
    "recording_page_number",
    "raw_seller_first_middle_name",
    "seller_first_middle_name",
    "raw_seller_last_name",
    "seller_last_name",
    "raw_seller_individual_full_name",
    "seller_individual_full_name",
    "raw_seller_non_individual_full_name",
    "seller_non_individual_name",
    "seller_name_sequence_number",
    "seller_mail_sequence_number"
]