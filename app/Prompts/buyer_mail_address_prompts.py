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

- buyer_mail_care_of_name
{ Populate in capital letters if C/O, or Care of name is found anywhere in document.
  Capture c/o name here if c/o or care of name keywords are mentioned.
  Remove 'c/o' keyword while populating value here. }

- buyer_mail_house_number
{ Populate house number of buyer address from raw_buyer_mail_full_street_address field.
  Example: For this address, 1475 Hidden Canyon Rd, "1475" is entered here.  
  NOTE:  If House Number is a numeric range, then enter complete range into this field, example "33-39") }

- buyer_mail_house_number_ext
{ Populate house number extension if given in raw_buyer_mail_full_street_address field else leave empty.
  Example: if 1475 1/2, then "1/2", if 1475-B, then "B". }

- raw_buyer_mail_street_pre_directional
{ If direction is given before after buyer address street name in raw_buyer_mail_full_street_address field then populate direction here.
  The directional preceding the Street Name.  
  Example: if 1475 West Hidden Canyon Rd, then “West”. }

- buyer_mail_street_pre_directional
{ It is the value of raw_buyer_mail_street_pre_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- raw_buyer_mail_street_name
{ Populate buyer address street name here, including punctuation, which is mentioned generally after buyer address house number and before street suffix (street or road), excluding direction.
  Populate this field from raw_buyer_mail_full_street_address field.
  Do not add suffix words like street, drive, circle, road, court, cir, lane, way etc in this field and split these words and populate in raw_buyer_mail_street_suffix field.
  Example:  1475 Hidden Canyon Rd, then "Hidden Canyon" is entered here. }

- buyer_mail_street_name
{ It is the value of raw_buyer_mail_street_name field in capital letters. }

- raw_buyer_mail_street_suffix
{ Capture this from raw_buyer_mail_full_street_address field.
  This is the suffix of buyer address street name like street, drive, circle, road, court, cir, lane, way etc.
  Example:  1475 Hidden Canyon Rd, "Rd" is entered here. }

- raw_buyer_mail_street_post_directional
{ If direction is given after buyer address street name in raw_buyer_mail_full_street_address field then populate direction here.
  The directional following the street suffix.  
  Example:  1475 Hidden Canyon Rd Northwest, then "Northwest" is entered here. }

- buyer_mail_street_post_directional
{ It is the value of raw_buyer_mail_street_post_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- raw_buyer_mail_full_street_address
{ Capture full buyer mail street address which includes house number, direction and street name with suffix.
  Look carefully while populating address here. Never capture seller address in this field.
  Buyer address is always available in document so don't leave this.
  Do not capture unit designator in this field.
  Very Important: Prioritize the Tax Mailing Address to populate here (if provided) over buyer address. 
  There will generally be mentioned like Tax bills should be sent to this address or with keyword 'Tax bills' so take that address as priority in place of buyer address mentioned with its name. }

- buyer_mail_full_street_address
{ It is the value of raw_buyer_mail_full_street_address but in capital letters after removing all punctuations from it.
  Capture buyer address which includes only house number, direction and street name with suffix from raw_buyer_mail_full_street_address field.
  Important: Do not take pin code, city name and state name in this field. Example: Format for address for this field should be like this - '361 HORSEFLY HOLLOW ROAD'. }

- buyer_mail_building_name
{ Populate buyer mail address building name here in capital letters if given. }

- buyer_mail_building_number
{ Populate buyer mail address building number here in capital letters if given. }

- buyer_mail_unit_designator
{ If any unit designator among given values is mentioned with buyer mail address then populate correspoing code in this field.
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

- buyer_mail_unit
{ The Unit associated to the buyer mail address is entered here if present. Keyed as presented, including punctuation, except indicator is dropped.
  Look for unit mentioned in address and capture here.  
  Example:  "Suite 5", entered as "5". }

- buyer_mail_city
{ This field reports the full City Name for buyer mail address as presented in the document in capital letters. }

- raw_buyer_mail_state
{ This field reports the state name for buyer mail address as presented in the document in capital letters. }

- buyer_mail_zip
{ This field reports the 5-digit zip code in buyer mail address.
  For example - If given 48879-1260 then populate '48879' here. }

- buyer_mail_zip4
{ When present in buyer mail address, the Zip+4 is captured.
  For example - If given 48879-1260 then populate '1260' here. }

- buyer_mail_address_stnd_code
{ 1. Populate F if buyer_mail_address is not in US
  2. Populate U if address was unlabeled or unclear in its relation to the buyer.
  If not from above, then leave empty.  }

- buyer_mail_sequence_number
{ Populate 1 here. }

Important Notes:
- Buyers may be mentioned as grantees, second party or party of second part.
- Prioritize the Tax Mailing Address when tied to the first Buyer Name in last page over other locations for all details of buyer mail address.
- Never capture seller address as buyer address so look carefully for this.
- Buyer mail address are always available so if not found then look deeply in document.

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
"buyer_mail_care_of_name",
"buyer_mail_house_number",
"buyer_mail_house_number_ext",
"raw_buyer_mail_street_pre_directional",
"buyer_mail_street_pre_directional",
"raw_buyer_mail_street_name",
"buyer_mail_street_name",
"raw_buyer_mail_street_suffix",
"buyer_mail_street_suffix",
"raw_buyer_mail_street_post_directional",
"buyer_mail_street_post_directional",
"raw_buyer_mail_full_street_address",
"buyer_mail_full_street_address",
"raw_buyer_mail_building_name",
"buyer_mail_building_name",
"raw_buyer_mail_building_number",
"buyer_mail_building_number",
"raw_buyer_mail_unit_designator",
"buyer_mail_unit_designator",
"raw_buyer_mail_unit",
"buyer_mail_unit",
"buyer_mail_city",
"raw_buyer_mail_state",
"buyer_mail_state",
"buyer_mail_zip",
"buyer_mail_zip4",
"raw_buyer_mail_address_stnd_code",
"buyer_mail_address_stnd_code",
"buyer_mailing_address_match_code",
"buyer_mailing_address_unit_designator_code",
"buyer_mailing_address_unit_number",
"buyer_mailing_address_carrier_route",
"buyer_mailing_address_fips_code",
"buyer_mail_sequence_number"
]