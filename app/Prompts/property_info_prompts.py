system_prompt = """
You are a data extraction expert. Your task is to extract specific data from a document according to the provided table and column names.
For each table and column combination, extract the corresponding value from the document.
If you cannot find a value for a specific field, leave that empty.
Format your response as a CSV with two columns: ColumnName, Value.
Do not include any explanations or additional text in your response.
"""

message_prompt = """
Analyze the provided PDF document carefully and deeply then extract the following information:

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

- assessor_parcel_number
{ The APN is a 10 to 14 digit number separated into segments with dashes.
  This is labelled with following keywords in document - APN, PIN, Parcel, Parcel ID, Unlabeled (vertically written on left margin of page), TAX ID, Tax Parcel ID.
  Capture all unique apn(s) from document from all possible places and populate here with comma separated.
  Below are specified formats for some counties to help search for apn numbers in document.
  For county 'Clinton'
    This is the default format of this number - 999-999-999-999-99 (Predominant Format)
    But only exception is for legal city of East Lancing, it's format is 19-99-99-99-999-999 (Non-Predominant Format)
  For county 'Clark'
    This is the default format of this number - 999-9999-999-99 (Predominant Format)
  For counties 'Mccracken', 'Elliott', 'Butler' and 'Wolfe'
    999-99-99-999
    999-99-99-999.99
  For county 'Bullitt'
    999-XXX-99-999
    999-XXX-99-999A
    where X = Alpha or Numeric, A = Alpha
  For county 'Alfalfa'
    020000999
    If less than 9 digits is reported for 'Alfalfa' county, add leading "02" followed by zero(s), and conform to a 9 digit format.
  For county 'Beaver', 'Coal', 'Greer', 'Atoka', 'Hughes' and 'Roger Mills'
    "9999-99-99X-XXX-9-X99-99
    X = Alpha or Numeric
  For county 'Cimarron'
    130000999
    If less than 9 digits is reported for 'Cimarron' county, add leading "13" followed by zero(s), and conform to a 9 digit format.
  For county 'Dewey'
    220000999
    If less than 9 digits is reported for 'Dewey' county, add leading "22" followed by zero(s), and conform to a 9 digit format.
  For county 'Ellis'
    230000999
    If less than 9 digits is reported for 'Ellis' county, add leading "23" followed by zero(s), and conform to a 9 digit format.
  For county 'Harper'
    300000999
    If less than 9 digits is reported for 'Harper' county, add leading "30" followed by zero(s), and conform to a 9 digit format.
  For county 'Jefferson'
    340000999
    If less than 9 digits is reported for 'Jefferson' county, add leading "34" followed by zero(s), and conform to a 9 digit format.
  For county 'Pushmataha'
    649999999
    If less than 9 digits is reported for 'Pushmataha' county, add leading "64" followed by zero(s), and conform to a 9 digit format.
  For county 'Texas'
    709999999
    If less than 9 digits is reported for 'Texas' county, add leading "70" followed by zero(s), and conform to a 9 digit format.
  Format all found apn(s) and populate here as comma separated.
  If Assessor parcel number is split from any main parcel, then please do not capture main parcel number. For example: If mentioned, Tax Parcel ID: 040-016-300-010-15 (Split 1999 from # 040-016-300-010-00) then capture only 040-016-300-010-15 and not other one.
  If the keyword 'through' is found in APN you need to increase the seq up to the limit, max limit = 100. Populate 100 records for this document and 100 apns should be populated in all these fields.
  For example, if mentioned 19-20-50-36-203-001 through 103 then capture 100 apns starting from 19-20-50-36-203-001 to 19-20-50-36-203-100. }

- apn_indicator_stnd_code
{ Populate 'P' if Portion of APN Transferred. }

- unformatted_assessor_parcel_number
{ It is the value of assessor_parcel_number but remove all dashes from it and just populate numbers.
  For example - 150-210-000-229-00 formats to 15021000022900.
  Keep different apn(s) comma separated. }

- property_house_number
{ Populate house number of property from raw_property_full_street_address field.
  Example: For this address, 1475 Hidden Canyon Rd, "1475" is entered here.  
  NOTE:  If House Number is a numeric range, then enter complete range into this field, example "33-39") }

- property_house_number_ext
{ Populate house number extension from raw_property_full_street_address field if given else leave empty.
  Example: if 1475 1/2, then "1/2", if 1475-B, then "B". 
  Numbers after '#' are considered as unit number so do not populate them here. }

- raw_property_street_pre_directional
{ If direction is given before property subdivision name then populate direction here.
  The directional preceding the Street Name.  
  Example: if 1475 West Hidden Canyon Rd, then “West”. }

- property_street_pre_directional
{ It is the value of raw_property_street_pre_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- property_street_name
{ Populate property street name here, including punctuation, which is mentioned generally after property house number and before street suffix like street or road, excluding direction.
  Do not populate property street suffixes like street, road, drive etc here but only fill just street name.
  Populate this field in capital letters.
  Do not add suffix words like street, drive, circle, road, court, cir, lane, way etc in this field and split these words and populate in raw_property_street_suffix field.
  Example:  1475 Hidden Canyon Rd, then "HIDDEN CANYON" is entered here. }

- raw_property_street_suffix
{ This is the suffix of property street name like street, drive, circle, road, court, cir, lane, way etc.
  Example:  1475 Hidden Canyon Rd, "Rd" is entered here. }

- raw_property_street_post_directional
{ If direction is given after property subdivision name then populate direction here.
  The directional following the street suffix.  
  Example:  1475 Hidden Canyon Rd Northwest, then "Northwest" is entered here. }

- property_street_post_directional
{ It is the value of raw_property_street_post_directional but populate only standardized value of it.
  Directionals are standardized according to the USPS address standards:  N, S, E, W, NE, NW, SE, SW. }

- raw_property_full_street_address
{ Capture full property street address from house number to zip code in this field.
  Do not populate addresses mentioned after buyers, sellers or borrowers names.
  Only populate property address which is clearly mentioned with 'property address' keyword.
  Do not take tax mail address as property address.
  Buyer and seller addresses are mentioned with their names so don't take these addresses as property address.
  Do not take mailing address mentioned in the document as property address.
  If property address is not given then leave it as empty. }

- property_full_street_address
{ Capture property street address which includes only house number, direction and street name with suffix from raw_property_full_street_address field.
  Important: Do not take pin code, city name and state name in this field. Example: Format for address for this field should be like this - '361 HORSEFLY HOLLOW ROAD'.
  Note: When a legal description/property use is given as part of the address, then that information is ignored.
  Populate this field in capital letters.  
  Example: Property Address: "Lot 3, Union OH", the reference to "Lot 3" is ignored; or, "Rural Property, Geyser NV", the reference to "Rural Property" is ignored. }

- property_building_number
{ Populate property building number here if given. }

- property_unit_designator
{ If any unit designator among given values is mentioned with property address then populate correspoing code in this field.
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

- property_unit
{ The Unit associated to the property address is entered here if present.  Keyed as presented, including punctuation, except indicator is dropped.  
  Example:  "Suite 5", entered as "5".
  Do not capture legal unit here. }

- property_city
{ This field reports the full City Name of property as presented in the document in capital letters.
  Do not capture legal city here. }

- raw_property_state
{ This field reports the state name of property as presented in the document in capital letters. }

- property_zip
{ This field reports the 5-digit zip code in property address.
  For example - If given 48879-1260 then populate '48879' here. }

- property_zip4
{ When present, the Zip+4 is captured.
  For example - If given 48879-1260 then populate '1260' here. }

- property_address_stnd_code
{ 1. Populate 'M' if Multiple property addresses reported, however due to document presentation, only the first reported Property Address has been keyed.
  2. Populate 'P' if Property address partially created from buyer/borrower mailing address (City and/or Zip Code)    }
   
- raw_legal_lot
{ Legal descriptions for platted, subdivided land may include a Lot(s), and if so, it is captured here.   
  Capture as it is mentioned in document.
  For example: "portion of lot 5",  "portion of lot 4 and all of lot 5 and portion of lot 8" and "Lot 2 and portion of 4 and 6-8" - like this would be given in document. }

- legal_lot
{ It is the formatted value of raw_legal_lot field.
  Multiple lots are separated with either an ampersand, comma or a dash.
  Example "1&2", "4&10"; "2, 6, 9" or "10-14".  
  If a portion of a lot is transferred, then "POR" is keyed in front of the lot value and for corner, "COR" is keyed.  
  Example:  "portion of lot 5", keyed as "POR 5".  
  If mixture of full and partial lots, the full lots are keyed first followed by the portion lots.  
  Example: "portion of lot 4 and all of lot 5 and portion of lot 8", keyed as "5, POR 4&8"; Lot 2 and portion of 4 and 6-8.  keyed as "2, POR 4, 6-8". 
  Don't repeat numbers like '17&18, POR 18'. Here correct format would be '17, POR 18'.
  Consider sequential numbers in range like '7, 8, 9&10' should be '7-10'. }

- legal_other_lot
{ For Alfalfa county only, The legal description will sometimes reference "Government Lots" which we will key into the "legal other lot" field.
  Otherwise, leave it empty. }

- raw_legal_block
{ Legal descriptions for platted, subdivided land may include a Block(s), and if so, it is captured here in capital letters.
  Capture as it is mentioned in the document. }
  
- legal_block
{ It is the value of raw_legal_block.
  If multiple, sequential blocks are transferred in a range, then a dash is used. Example "1-2", "10-12".  
  If multiple, sequential ranges are reported or multiple blocks not in sequence, then a comma and space is used to separate the ranges or individual blocks.  Example: "1, 4". }

- raw_legal_subdivision_name
{ The Subdivision Name of the platted and subdivided property is entered here.  The phase, section, of subdivisions are keyed into their respective legal component field. 
  Example:  "Happy Trails Unit 2 Phase 3", keyed as:
  raw_legal_subdivision_name = "Happy Trails Unit 2"
  Note:  In absence of a Subdivision Name, this field may contain the Plat Name or Plat Number depending upon document/data presentation.  
  Assessment Note:  If both a Plat Name and Number given, the Plat Name only is output.
  These phrases can be dropped:
    ❖ “Map of”
    ❖ “Plat of”
    ❖ “Final Map of”
    ❖ “Final Plat of” 
    
  These phrases should be retained whenever encountered within a Subdivision
    ❖ “Revised”
    ❖ “Recombination”
    ❖ “Replat”
    ❖ “Amended”

  Do Not Key
    1. Surveyor's/engineer's name who prepared the plat
    2. Name of person/entity the plat was prepared for 
    3. Person/entity whose property it is 
    4. Ignore generic references such as 'minor subdivision on the lands of' }

- legal_condo_project_pud_dev_name
{ This is a secondary, overflow field populated for Condo/PUD parcels when the legal description reports both a Condo Project Name (or PUD Dev Name) and a Subdivision. 
  In these cases, the Condo/PUD name is entered into this field and the Subdivision is entered into the Subdivision Name field.
  If only one name is reported in the legal description, then it is entered into the Legal Subdivision Name field and this field is left blank.
  Populate this field in capital letters. }

- legal_building_number
{ The Building Number reported in the legal description is entered here. }

- legal_unit
{ Straight capture: The Unit reported in the legal description in capital letters. The value entered here may represent a different value than the property unit. }

- legal_section
{ The Section as reported in the legal description is entered here in capital letters.
  Only populate the details if 'section' keyword is specifically mentioned with it.
  Important - Do not key if section already mapped in raw_legal_sec_twn_rng_mer field. }

- legal_phase
{ The Phase as reported in the legal description is entered here in capital letters.
  Only populate the details if 'phase' keyword is specifically mentioned with it. }

- legal_tract
{ The Tract as reported in the legal description is entered here in capital letters. An area of land where the parcel is located (generally a large or measured area).
  If 'tract' keyword is mentioned in document then capture that in this field. }

- legal_district
{ 1. Field reports the District as reported in the legal description, may be numeric or text, dependent upon the jurisdiction. 
  2. If both a District code and a text description are reported, then the District Code is entered here and the District Name is reported in the legal_municipality field.
  Populate this field in capital letters. }
  
- legal_municipality
{ This field reports the jurisdiction, other than city or township as reported in the legal description in capital letters.  Other jurisdictions may include village or hamlet names.
  Fill this if city and township are not given. }

- legal_city
{ 1.The City where the parcel is situated as reported in the legal description.  This name may not match the property city name.  
  2.If the document indicates the property is located in an "unincorporated" area, then "unincorporated" is entered here.
  If 'City of' and 'Village of' keywords are written then populate them here in capital letters without these keywords. }

- legal_township
{ Capture the Township where the parcel is situated as reported in the legal description in capital letters.
  If keyword 'township' is available then populate in this field without township keyword. }

- raw_legal_sec_twn_rng_mer
{ Section-Township-Range legal descriptions are based on a land division system known as the Public Land Survey System.  
  The complete STR legal is populated here as mentioned in document.
  For example: "North 1/2 Southeast quarter of Section 24 Township 32 north Range 18 east in 6th Principal Meridian" }

- legal_sec_twn_rng_mer
{ It is value of raw_legal_sec_twn_rng_mer field with the following requirements:
    1) Each element is separated by one space
    2) Abbreviations used:  S = Section, T=Township; R=Range
    3) Each element will be ordered or placed in Section-Township-Range order
    4) Quarter section information will precede the Section information
    5) Meridian information will follow the Range element

    EXAMPLES:  
    if reported as "North 1/2 Southeast quarter of Section 24 Township 32 north Range 18 east in 6th Principal Meridian", enter as "POR S24 T32N R18E 6PM".  
    NOTE:  Detailed sectional information will be reported as "POR" to reflect a portion of section    
    NOTE1: If reference to "corner", abbreviated to "COR".  Example, "NW COR"; if reference to "Southwest Part", abbreviated to "SW POR".
    NOTE2: If reference to "Quarter Township" ("Quarter Township 3" or "Third Quarter"), abbreviated to "QT".  Example "QT3".
    NOTE3: If the legal description references "Indian Base and Meridian" or "Indian Meridian"  It is permissible to abbreviate to "IBM" or "IM". }

- raw_legal_recorders_map_reference
{ Recording reference for Plat/Parcel Map is captured here. The most current recording reference is captured.
  Do not fill older legal map reference in this field. If some date older than document date is mentioned with legal map reference, then do not populate it in this field.
  Sample input: 
  "Plat Book 30 Page 5", "Volume 30 Pages 6 and 7", "Book of Maps 1999, Page 1953 re-recorded in Book of Maps 2000, Page 2229"
  NOTE1: For Condos/PUD, if a Recorder's Map Reference is not reported but a Condominium Declaration or Master Deed recording reference is provided instead, then the Condo Declaration/Master Deed reference is entered here.
  NOTE2: If both a Plat Map and a Condo Dec (or Master Deed) are referenced, give priority to Plat Map reference.
  NOTE3: If a paragraph is starting from 'Being a part of' or some older date is mentioned in that paragraph then that legal description is of some older transaction and do not take legal recorder reference from that paragraph. If no other legal reference is present then leave it empty. }

- legal_recorders_map_reference
{ Based on raw_legal_recorders_map_reference field value, populate this field in standard form as mentioned in below examples.
  Map Format the value as per below examples and lookup table-
    REFERENCE DESCRIPTION	REFERENCE CODE
    Auditor's File Number	AF
    Book	BK
    Cabinet	CAB
    Card Number	CARD
    Card  CARD
    Case Number	CASE
    Condominium Map Number	CM
    Deeds	DD
    Document Number	DOC
    Drawer	DR
    Envelope	ENV
    File Number	FILE
    Film Number	FILM
    Folder	FLR
    Folio	FO
    Hanger	HNGR
    Jacket	JKT
    Liber	LB
    Map Book	MB
    Map Number (Map File Number)  MAP
    Map  MAP
    Misc. Maps	MP
    Misc. Records	MR
    Official Records	OR
    Page	PG
    Parcel Map	PM
    Plat Book	PB
    Plat Number	PL
    Plat  PL
    Pocket	PKT
    Reel	RL
    Section SEC
    Sheet	SH
    Side	SIDE
    Slide/Slot	SL 
    Sleeve	SLV
    Records of Survey/Survey	RS
    Survey Volume	SRVL
    Tube	TUBE
    Volume	VOL
  1. The Reference is tied back to a plat/map/survey recording:  
  Example:  "on the official plat filed on…”
  2. The Reference itself contains words such as “Plat Book” or “Map Book” or “Plat” or similar
  Example:  “…of record in Plat Slide 9 Page 14&15” should collect PL SL 9 PG 14&15
  Recorded in Volume 40, Page 104  as VOL 40 PG 104
  Recorded in amended plat filed april 2024 as Instrument Number 226384 should be keyed as DOC 226384
  Recorded in Liber 1 Page 3, should be keyed as  LB 1 PG 3
  Recorded in Plat Section A, Page 152, should be keyed as  PL SEC A PG 152
  3. if Legal description reports both recorder reference and Condo Declaration, then prioritise the Recorders Reference. }

- raw_legal_description
{ Capture legal description from document.
  Invalid Legal description {Metes and Bounds} will start with 'Beginning or Commencing at' and end with 'to the Point of Beginning or POB'. If the legal elements are within the start and end phrases, do not key any legal data components.
  If legal elements are presented outside of the Metes & Bounds legal description, then capture the legal paragraph in this field. }

Important Notes:
- Always give output in given format only and never return blank output.
- Important: Only take property address which are clearly mentioned as property address with 'property' keyword.
- Legal description mentioned between 'Beginning' or 'Commencing' and 'point of beginning' keywords will be ignored and not be keyed in any legal related fields.
- If data_class_stnd_code = 'M', then any legal related field will not be captured. All legal fields will be empty for mortgage documents. 
- raw_legal_sec_twn_rng_mer and legal_section will never be populated together. Populate legal_section only when raw_legal_sec_twn_rng_mer field is empty. 

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
    "raw_assessor_parcel_number",
    "assessor_parcel_number",
    "raw_apn_indicator_stnd_code",
    "apn_indicator_stnd_code",
    "tax_id_number",
    "tax_id_indicator_stnd_code",
    "raw_tax_id_indicator_stnd_code",
    "unformatted_assessor_parcel_number",
    "alternate_parcel_number",
    "hawaii_condo_cpr_code",
    "property_house_number",
    "property_house_number_ext",
    "raw_property_street_pre_directional",
    "property_street_pre_directional",
    "raw_property_street_name",
    "property_street_name",
    "raw_property_street_suffix",
    "property_street_suffix",
    "raw_property_street_post_directional",
    "property_street_post_directional",
    "raw_property_full_street_address",
    "property_full_street_address",
    "raw_property_building_number",
    "property_building_number",
    "raw_property_unit_designator",
    "property_unit_designator",
    "raw_property_unit",
    "property_unit",
    "property_city",
    "raw_property_state",
    "property_state",
    "property_zip",
    "property_zip4",
    "raw_property_address_stnd_code",
    "property_address_stnd_code",
    "raw_legal_lot",
    "legal_lot",
    "legal_other_lot",
    "legal_lot_code",
    "raw_legal_block",
    "legal_block",
    "raw_legal_subdivision_name",
    "legal_subdivision_name",
    "legal_condo_project_pud_dev_name",
    "legal_building_number",
    "raw_legal_unit",
    "legal_unit",
    "raw_legal_section",
    "legal_section",
    "raw_legal_phase",
    "legal_phase",
    "raw_legal_tract",
    "legal_tract",
    "raw_legal_district",
    "legal_district",
    "raw_legal_municipality",
    "legal_municipality",
    "raw_legal_city",
    "legal_city",
    "raw_legal_township",
    "legal_township",
    "legal_str_section",
    "legal_str_township",
    "legal_str_range",
    "legal_str_meridian",
    "raw_legal_sec_twn_rng_mer",
    "legal_sec_twn_rng_mer",
    "raw_legal_recorders_map_reference",
    "legal_recorders_map_reference",
    "raw_legal_description",
    "legal_description",
    "legal_lot_size",
    "property_address_match_code",
    "property_address_unit_designator",
    "property_address_unit_number",
    "property_address_carrier_route",
    "property_address_geocode_match_code",
    "property_address_latitude",
    "property_address_longitude",
    "property_address_census_tract_and_block",
    "property_sequence_number"
]