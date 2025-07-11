system_prompt = """
You are a data extraction expert. Your task is to extract specific data from a document according to the provided table and column names.
For each table and column combination, extract the corresponding value from the document.
If you cannot find a value for a specific field, leave that empty.
Format your response as a CSV with two columns: ColumnName, Value.
Do not include any explanations or additional text in your response.
"""

message_prompt = """
Analyze the provided PDF document and extract the following information:

Here is the list of all properties with specified conditions to help finding them in document.  

- fips
{ Populate this field based on county name from below table-
  COUNTY NAME  FIPS CODE
    Alfalfa  40003
    Atoka  40005
    Beaver  40007
    Bullitt  21029
    Butler  21031
    Carroll  21041
    Cimarron  40025
    Clark  21049
    Clinton  26037
    Coal  40029
    Dewey  40043
    Elliott  21063
    Ellis  40045
    Gallatin  21077
    Greer  40055
    Harper  40059
    Hughes  40063
    Jefferson  40067
    Lake  41037
    Mccracken  21145
    Pushmataha  40127
    Roger Mills  40129
    Texas  40139
    Todd  21219
    Whitley  21235
    Wolfe  21237
  IMPORTANT: Populate FIPS code from given table for county mentioned in document. Do not leave this empty as this field is must to populate. }

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

- borrower_mail_care_of_name
{ Populate in capital letters if C/O, or Care of name keyword found in Borrower details.
  Capture c/o name here if c/o or care of name keywords are mentioned without keyword 'c/o'. }

- borrower_mail_house_number
{ Populate house number of borrower address from raw_borrower_mail_full_street_address field.
  Example: For this address, 1475 Hidden Canyon Rd, "1475" is entered here.  
  NOTE:  If House Number is a numeric range, then enter complete range into this field, example "33-39") }

- borrower_mail_house_number_ext
{ Populate house number extension if given in raw_borrower_mail_full_street_address field else leave empty.
  Example: if 1475 1/2, then "1/2", if 1475-B, then "B". }

- raw_borrower_mail_street_pre_directional
{ If direction is given before after borrower address street name in raw_borrower_mail_full_street_address field then populate direction here.
  The directional preceding the Street Name.  
  Example: if 1475 West Hidden Canyon Rd, then “West”. }

- borrower_mail_street_pre_directional
{ It is the value of raw_borrower_mail_street_pre_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- raw_borrower_mail_street_name
{ Populate borrower address street name here, including punctuation, which is mentioned generally after borrower address house number and before street suffix (street or road), excluding direction.
  Populate this field from raw_borrower_mail_full_street_address field.
  Do not add suffix words like street, drive, circle, road, court, cir, lane, way etc in this field and split these words and populate in raw_borrower_mail_street_suffix field.
  Example:  1475 Hidden Canyon Rd, then "Hidden Canyon" is entered here. }

- borrower_mail_street_name
{ It is the value of raw_borrower_mail_street_name field in capital letters. }

- raw_borrower_mail_street_suffix
{ Capture this from raw_borrower_mail_full_street_address field.
  This is the suffix of borrower address street name like street, drive, circle, road, court, cir, lane, way etc.
  Example:  1475 Hidden Canyon Rd, "Rd" is entered here. }

- raw_borrower_mail_street_post_directional
{ If direction is given after borrower address street name in raw_borrower_mail_full_street_address field then populate direction here.
  The directional following the street suffix.  
  Example:  1475 Hidden Canyon Rd Northwest, then "Northwest" is entered here. }

- borrower_mail_street_post_directional
{ It is the value of raw_borrower_mail_street_post_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- raw_borrower_mail_full_street_address
{ Capture full borrower mail street address which includes house number, direction and street name with suffix.
  Look carefully while populating address here. Never capture lender address in this field.
  Borrower address is always available in document so don't leave this.
  Do not capture unit designator in this field. }

- borrower_mail_full_street_address
{ It is the value of raw_borrower_mail_full_street_address but in capital letters after removing all punctuations from it.
  Capture borrower address which includes only house number, direction and street name with suffix from raw_borrower_mail_full_street_address field.
  Important: Do not take pin code, city name and state name in this field. Example: Format for address for this field should be like this - '361 HORSEFLY HOLLOW ROAD'. }

- borrower_mail_building_name
{ Populate borrower mail address building name here in capital letters if given. }

- borrower_mail_building_number
{ Populate borrower mail address building number here in capital letters if given. }

- borrower_mail_unit_designator
{ If any unit designator among given values is mentioned with borrower mail address then populate correspoing code in this field.
  DESIGNATOR	DESIGNATOR CODE
    APARTMENT	APT
    BASEMENT	BSMT
    BUILDING	BLDG
    DEPARTMENT	DEPT
    FLOOR	FL
    FRONT	FRNT
    HANGAR	HNGR
    KEY	KEY
    LOBBY	LBBY
    LOT	LOT
    LOWER	LOWR
    OFFICE	OFC
    PENTHOUSE	PH
    PIER	PIER
    REAR	REAR
    ROOM	RM
    SIDE	SIDE
    SLIP	SLIP
    SPACE	SPC
    STOP	STOP
    SUITE	STE
    TRAILER	TRLR
    UNIT	UNIT
    UPPER	UPPR
  Example:  "Suite 5", entered as "STE". }

- borrower_mail_unit
{ The Unit associated to the borrower mail address is entered here if present. Keyed as presented, including punctuation, except indicator is dropped.
  Look for unit mentioned in address and capture here.  
  Example:  "Suite 5", entered as "5". }

- borrower_mail_city
{ This field reports the full City Name for borrower mail address as presented on the document in capital letters. }

- raw_borrower_mail_state
{ This field reports the state name for borrower mail address as presented on the document in capital letters. }

- borrower_mail_zip
{ This field reports the 5-digit zip code in borrower mail address.
  For example - If given 48879-1260 then populate '48879' here. }

- borrower_mail_zip4
{ When present in borrower mail address, the Zip+4 is captured.
  For example - If given 48879-1260 then populate '1260' here. }

- borrower_mail_address_stnd_code
{ 1. Populate F if borrower_mail_address is not in US
  2. Populate U if address was unlabeled or unclear in its relation to the borrower.
  If not from above, then leave empty.  }

- borrower_mail_sequence_number
{ Populate 1 here. }
   
Important Notes:
- Never capture lender address as borrower address so look carefully for this.

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
    "borrower_mail_care_of_name",
    "borrower_mail_house_number",
    "borrower_mail_house_number_ext",
    "raw_borrower_mail_street_pre_directional",
    "borrower_mail_street_pre_directional",
    "raw_borrower_mail_street_name",
    "borrower_mail_street_name",
    "raw_borrower_mail_street_suffix",
    "borrower_mail_street_suffix",
    "raw_borrower_mail_street_post_directional",
    "borrower_mail_street_post_directional",
    "raw_borrower_mail_full_street_address",
    "borrower_mail_full_street_address",
    "raw_borrower_mail_building_name",
    "borrower_mail_building_name",
    "raw_borrower_mail_building_number",
    "borrower_mail_building_number",
    "raw_borrower_mail_unit_designator",
    "borrower_mail_unit_designator",
    "raw_borrower_mail_unit",
    "borrower_mail_unit",
    "borrower_mail_city",
    "raw_borrower_mail_state",
    "borrower_mail_state",
    "borrower_mail_zip",
    "borrower_mail_zip4",
    "raw_borrower_mail_address_stnd_code",
    "borrower_mail_address_stnd_code",
    "borrower_mailing_address_match_code",
    "borrower_mailing_address_unit_designator_code",
    "borrower_mailing_address_unit_number",
    "borrower_mailing_address_carrier_route",
    "borrower_mailing_address_fips_code",
    "borrower_mail_sequence_number"
]