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

- raw_buyer_individual_full_name
{ Identify all buyers or grantees in the document and populate here full names of them as comma separated.
  Only capture grantees mentioned in first page of document.  
  Fill here only if grantee is person name and not an organisation or trust name.
  Read carefully as some sellers are repeated as buyers and even sometimes some buyers are repeated with different descriptions, so look carefully and capture all buyers.
  if a.k.a. or f.k.a. names are mentioned then capture them as separate individual names. For example, if buyer name is William Jack aka John Jack then there are two buyers - William Jack and John Jack (without keyword aka).
  Look carefully who is buyer and who is seller. Don't populate seller or grantor name here. }

- buyer_individual_full_name
{ It is the value of raw_buyer_individual_full_name but remove all punctuations except hyphen ('-') in the names then populate in this field as comma separated.
  If “Samuel M.R. Harvey”, retain spaces & key as “Samuel M R Harvey” (we do not want initials to appear without a space “MR”)
  If “Jennifer Day-St. George”, then key as “Jennifer Day-St George” (retain the hyphen but drop the period and suppress space)
  Populate this field in all capital letters. }

- raw_buyer_non_individual_name
{ If grantee is trust, organisation or govt institution name then populate them in this field as ';' separated otherwise leave empty.
  Look carefully if date is mentioned in trust name then capture only trust name here excluding date and 'dated' keyword. }

- buyer_non_individual_name
{ It is the value of raw_buyer_non_individual_name but remove all punctuations except ampersand ('&') in the names then populate in this field as comma separated.
  Populate this field in all capital letters. }

- raw_buyer_description_stnd_code
{ Extract descriptions of all buyers from the `raw_buyer_individual_full_name` and `raw_buyer_non_individual_name` fields separated by commas.
  If a buyer is described multiple times with different roles, list each buyer and its description.  
  Do not include descriptions of sellers or grantors.  
  Include descriptions only that directly follow the buyer's name. Do not miss description for any buyer.
  Ignore aliases (aka, fka).  Output the descriptions as a comma-separated string.
  If a party name appears multiple times on the document and each time the party is described in a different manner, then the name should be keyed as many times as it appears on the document. For example:
    “John Edwards, as Executor of the John Edwards Revocable Trust, and John Edwards, married man…”
    Key parties as:
    John Edwards as executor
    John Edwards Revocable Trust as trust
    John Edwards as married man
  If a party name is reported one time, but with more than one description, prioritize the description for the facilitator role.  For example:
    “John Edwards, individually and as trustee for John Edwards Trust”
    Code parties as:
    John Edwards as Trustee (prioritize facilitator)
    John Edwards Trust as Trust  
  - Marital codes
        ❖ Use code 'HW' for both husband and wife when document reports:
            ● If 'husband and wife' is mentioned together like this.
            ● If mentioned like this: Joe Smith and wife Sarah Smith or Sarah Smith and husband Joe Smith
            ● If mentioned like this: Joe Smith and his wife Sarah Smith (or Joe Smith and Sarah Smith, his wife)
            ● Sarah Smith and her husband Joe Smith (or “Sarah Smith and Joe Smith, her husband”)
        ❖ Use codes 'HB' and 'WF', only when descriptions are stated per individual.
        ❖ Use code 'MC' (married couple) for both parties as follows:
            ● When the document describes the parties relationship as 'Married To', then key the description code for both parties as MC'.
            ● When two parties are followed by the description “Married”,  as shown below, also code both parties as 'MC'.
        ❖ Use code 'SO' (Spouse) when:
            ● Both parties are identified as 'spouse'
            ● Phrase 'and spouse' is used.
  Number of descriptions will be equal to number of buyers and will be comma separated.
  Refer below table for possible buyer descriptions that can be found.
  'Grantor' and 'Grantee' are not considered as descriptions.
  Capture specific trust type if given. For example, for family trust, populate 'Family trust' instead of just 'Trust'.
  If no buyer descriptions are found, consider the buyer as 'Individual'. }

- buyer_description_stnd_code
{ It is the value of raw_buyer_description_stnd_code field but only standardized codes will be populated here.
    DESCRIPTION	DESCRIPTION CODE
    Alternate Beneficiary	AB
    Administrator	AD
    Assignee	AE
    Affiant	AF
    Agent	AG
    Also Known As	AK
    Assignor	AR
    Builder/Developer	BD
    Beneficiary	BF
    Borrower/Trustor (in default) or Debtor	BR
    Client	CL
    Company 	CO
    Creditor	CR
    Conservator/Conservatee	CS
    Custodian	CU
    Doing Business As	DB 
    Deceased	DC
    Defendant (or Respondent)	DF
    Divorced & Not Remarried	DN
    Domestic Partner	DP
    Divorced & Remarried	DR
    Divorced 	DV
    Et Al	EA
    Estate	ES
    Executor/Executrix	EX
    For Benefit Of	FB
    Family Irrevocable Trust	FI
    Formerly Known As	FK
    Family Living Trust	FL
    Family Revocable Trust	FR
    Family Trust	FT
    Guardian	GD
    General Partner 	GN
    General Partnership	GP
    Government 	GV
    Homeowner Association	HA
    Husband	HB
    Husband of Grantee	HE
    Her Husband	HH
    His Wife	HI
    Husband of Grantor	HO
    Heir	HR
    Husband & Husband	HU
    Husband & Wife	HW
    IRA (Individual Retirement Account)	IA
    Individual 	ID
    Irrevocable Living Trust	IL
    Incompetent	IN
    Irrevocable Trust	IT
    Limited Liability Partnership	LL
    Limited Partner  	LN
    Limited Partnership	LP
    Legally Separated	LS
    Life Tenant	LT
    Living Trust	LV
    Last Will & Testament	LW
    Member	MB
    Married Couple	MC
    Managing Member	MG
    Married Man	MM
    Minor	MN
    Married Person	MP
    Married Man Separated	MS
    Married Woman	MW
    Now Known As	NK
    Never Married Person	NM
    Not Provided	NP
    Non-Titled/Non-Vested Spouse 	NT
    Officer	OF
    Attorney in Fact/Power of Attorney	PA
    Plaintiff (or Petitioner)	PL
    Partner	PN
    Personal Representative	PR
    Partnership	PT
    Revoked Buyer	RB
    Remainderman	RE
    Religious/Church	RG
    Revocable Living Trust	RL
    Revocable Trust	RT
    Receiver	RV
    Sole Member	SB
    Surviving Tenant by Entirety	SE
    Spouse of Grantor	SG
    Sole Proprietorship	SH
    Successor in Interest 	SI
    Surviving Joint Tenant	SJ
    Sole Owner	SL
    Single Man	SM
    Spouse	SO
    Single Person	SP 
    Separated	SR
    Surviving Spouse	SS
    Successor Trustee	ST
    Survivor's Trust	SU
    Survivor	SV
    Single Woman	SW
    Spouse of Grantee	SZ
    Trustee	TE
    Trust 	TR
    Unmarried Man	UM
    Unmarried Person	UP
    Unmarried Woman	UW
    Ward	WD
    Wife of Grantee	WE
    Wife	WF
    Wife & Wife	WI
    Wife of Grantor	WO
    Married Woman Separated	WS
    Who Acquired Title As (WATA); may be referenced as Having Taken Title As (HTTA)	WT
    Widow/Widower (Widowed)	WW

    - Populate Description Code field as 'CO' as a default for parties keyed into the non-individual field. This would only apply if no other codes applies.
    - Populate 'ID' here if no description is given for an individual.
    - if borrower and dower both are mentioned, prioritise borrower code.
    - If a party identifies as survivor, prioritse survivor codes over others.
    - If a seller is identified and reserved himself as Life estate then populate life tenant or vice vera.
    - If a party identified as facilitator prioritse Facilitator code (Trustee, Executor, person repesentative etc.).
  GENERAL NOTE: If multiple descriptions are encountered for a person/entity not mentioned above, then prioritize first description encountered.
  Important: For different kind of trusts, look for description code for that specific type of trust in table and don't just populate 'TR' for that.
  Do not leave this field empty for any buyer.
  Populate this after looking from above table and fill description codes for all buyers as comma separated. }

Important Notes:
- Buyers can also be mentioned as grantee, party of second part or second party, so look carefully and capture them as buyers.
- Always maintain the order of buyers/grantees as they are mentioned in document.
- Capture names only from starting of document and not from later in notary and signature section.
- If any name is given after 'aka' or 'fka' keyword then consider that as separate individual name. For example, if buyer name is William Jack fka John Jack then there are two different buyers - William Jack and John Jack (without keyword fka).
- raw_buyer_individual_full_name and raw_buyer_non_individual_name fields can never be filled together.
- Consider sellers also as buyers if they grant or quit claims themselves also or lifetimes coupled. Also if they convey property to themselves as life tenants then consider them buyers.
- Capture Trustee name in raw_buyer_individual_full_name and Trust name in raw_buyer_non_individual_name.
- If a party name appears multiple times on first page of document and each time the party is described in a different manner, then the name should be keyed as many times as it appears on first page. 

If a piece of information is not found, leave that field empty.
Return the data in CSV format with two columns: ColumnName, Value.
"""

all_names_column_names = [
    "fips",
    "record_id",
    "index_key",
    "data_class_stnd_code",
    "recording_date",
    "recording_document_number",
    "recording_book_number",
    "recording_page_number",
    "raw_buyer_first_middle_name",
    "buyer_first_middle_name",
    "raw_buyer_last_name",
    "buyer_last_name",
    "raw_buyer_individual_full_name",
    "buyer_individual_full_name",
    "raw_buyer_non_individual_name",
    "buyer_non_individual_name",
    "buyer_name_sequence_number",
    "buyer_mail_sequence_number"
]

all_desc_column_names = [
    "fips",
    "record_id",
    "index_key",
    "data_class_stnd_code",
    "recording_date",
    "recording_document_number",
    "recording_book_number",
    "recording_page_number",
    "raw_buyer_description_stnd_code",
    "buyer_description_stnd_code",
    "buyer_desc_sequence_number",
    "buyer_name_sequence_number"
]