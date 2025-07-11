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

- index_key
{ Generate index_key as “character varying NOT NULL” and populate each record's tables with a unique character key.
    Example:
    Index_key - 'AC5ACD0D-32C3-46F1-B0EC-B970CAB48CAE' }

- raw_state
{ Provide the name of the state where the document is getting recorded. }

- state
{ It is the value of raw_state field but populate standardized codes for states mentioned below -
    STATE NAME  STATE CODE
    Michigan  MI
    Kentucky  KY
    Oklahoma  OK
    Oregon  OR
  If not found from above then fill whole state name in capital letters. }

- raw_county
{ Provide the name of the county where the document is getting recorded. }

- county
{ It is the value of raw_county with name of county without keyword 'COUNTY' in capital letters. }

- record_type_stnd_code
{ Its default value is 'P'. }

- data_class_stnd_code
{ Populate = 'D' if Document title belongs to 'Deed'.
  Populate = 'M' if Document title belongs to 'Mortgage'.
  Note: Land contract will be considered as deed document. }
  
- raw_recording_date
{ Capture recording date from document.
  Mentioned at top left corner of first page or bottom of last page of document just below document number. }

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

- raw_document_type_stnd_code
{ Get the type of document from its title. }

- document_type_stnd_code
{ Based on raw_document_type_stnd_code field value, fill standard value of document type by referring below table-
    DOCUMENT TYPE DESCRIPTION	DOC TYPE CODE
    Affidavit - Death of Tenant by Entirety	AFDE
    Affidavit - Death of Life Tenant (termination of life interest))	AFDL
    Affidavit - Death of Joint Tenant 	AFDT
    Affidavit	AFDV
    Affidavit - Surviving Joint Tenant	AFSJ
    Affidavit - Surviving Spouse	AFSS
    Affidavit - Survivorship	AFSV
    Affidavit - Transfer on Death 	AFTD
    Agreement of Sale (Agreement for Deed)	AGSL
    Cash Sale Deed	CHDE
    Commissioner's Deed   CMDE
    Court Order/Action	COCA
    Covenant Deed	CTDE
    Contract of Sale	CTSL
    Deed of Distribution	DEDB
    Deed  DEED
    Fulfillment Deed	FLDE
    Gift Deed	GFDE
    Gift Warranty Deed	GFWD
    Grant Deed	GRDE
    Land Contract	LDCT
    Lease	LEAS
    Life Estate Deed/Deed Reserving/Confirming  Life Estate	LFDE
    Life Estate Quitclaim Deed	LFQC
    Life Estate Warranty Deed (Reserving/Confirming Life Estate)	LFWD
    Mortgagee's Deed	MGDE
    Deed of Trust/Mortgage	MTGE
    Quitclaim Deed	QCDE
    Sheriff's Deed	SHDE
    Special Joint Tenancy Warranty Deed	SPJW
    Special Warranty Deed	SPWD
    Survivorship Deed	SVDE
    Survivorship Warranty Deed	SVWD
    Termination of Decedent's Property Interest/Termination of Property Interest	TDPI
    Transfer on Death Deed	TFDD
    Trustee's Deed (non-foreclosure)	TRDE
    Warranty Deed	WRDE
  If value not found from above then leave empty. }

- raw_document_date
{ Capture document date present in the document. Never take it from legal section.
  In mortgage documents, prefer the date which is written in the statement that starts with "Security Instrument".
  It is always typed and not handwritten.
  If not present then leave it as empty but don't take it from paragraph of legal information.
  If document date is given like 12th day of January 2025 then take it as 2025-01-12. }

- document_date
{ It is the value of raw_document_date but first reformat it to 'YYYY-MM-DD'.  THIS IS ABSOLUTELY MANDATORY. The year MUST come FIRST.  The output MUST be in the format 'YYYY-MM-DD' without exception. Double-check the order, YYYY-MM-DD. }

- raw_signature_date
{ Look carefully for signature date in document generally written after 'Dated' keyword.
  It is always handwritten and never typed.
  Do not take signature date from notary section of document in last.
  if no handwritten date is found then leave it as null. }

- signature_date	
{ It is the value of raw_signature_date but first reformat it to 'YYYY-MM-DD'.  THIS IS ABSOLUTELY MANDATORY. The year MUST come FIRST.  The output MUST be in the format 'YYYY-MM-DD' without exception. Double-check the order, YYYY-MM-DD. }

- raw_effective_date
{ It is specifically mentioned in document with keyword 'effective date'. If not found then leave empty.
  Do not take effective date from notary section of document in last. }

- effective_date
{ It is the value of raw_effective_date but first reformat it to 'YYYY-MM-DD'.  THIS IS ABSOLUTELY MANDATORY. The year MUST come FIRST.  The output MUST be in the format 'YYYY-MM-DD' without exception. Double-check the order, YYYY-MM-DD. }

- raw_buyer_vesting_stnd_code
{ It is only for Deed documents. Only if data_class_stnd_code == 'D' then populate this field otherwise leave it blank.
  Capture buyer vesting details from document on how the buyer or buyers are taking title to their property if given, like Joint tenant, Tenancy in common etc.
  Find values like these with buyer details: Community (Marital) Property, Community Property with Right of Survivorship, Domestic Partner Sole and Separate Property, Joint Tenancy (may be reported as Joint Tenancy with Right of Survivorship), Joint Venture, Married Man Sole and Separate Property, Ownership in Severalty (Tenancy in Severalty) , Right of Survivorship, Survivorship Marital Property, Sole and Separate Property, Tenancy in Common, Tenancy by the Entirety (may be reported as Tenancy by the Entirety with full right of survivorship), Married Woman Sole and Separate Property
  IMPORTANT: Do not populate relationships between buyers like Husband and Wife in this field. }

- buyer_vesting_stnd_code
{ Based on raw_buyer_vesting_stnd_code value, choose buyer vesting code from below table:
    VESTING 	VESTING CODE	NOTES
    Community (Marital) Property	CP	
    Community Property with Right of Survivorship	CS	
    Domestic Partner Sole and Separate Property	DP	
    Joint Tenancy (may be reported as Joint Tenancy with Right of Survivorship)	JT	
    Joint Venture	JV	
    Married Man Sole and Separate Property	MS	
    Ownership in Severalty (Tenancy in Severalty) 	OS	
    Right of Survivorship	RS	This code used for references such as "joint lives with remainder to survivor" or "jointly for life with remainder to survivor"
    Survivorship Marital Property	SM	May be reported as "Marital Property" - appears in state of WI.
    Sole and Separate Property 	SS	
    Tenancy in Common	TC	
    Tenancy by the Entirety (may be reported as Tenancy by the Entirety with full right of survivorship)	TE	Internal Zillow Note:  Assessment Data assigned code "TT"
    Married Woman Sole and Separate Property	WS	 
  If raw_buyer_vesting_stnd_code is populated then don't leave this field empty. }

- partial_interest_transfer_stnd_code 
{ If total tranfer/seller's ownership interest is less than 100 percent flag then fill 'Y'.
  If transfer involves multiple ownership interest amounts, if the total amount conveyed equals 100 percent, then field is left blank (default value)".
  Do not take this information based on legal description. }	

- raw_sales_price_amount
{ Get sales price amount from document.
  It sales price is mentioned as fair cash price, fair cash value, estimated market price or estimated value then do not take it and leave this field empty.
  It is only for deed documents.}

- sales_price_amount	
{ It is value of raw_sales_price_amount.
  If value is less than or equal to 100 dollars and county transfer tax is not null then follow below steps:
    Compute Sales price from the County Transfer Tax using the formula below and enter amount into this field.
    County Transfer Tax formula:
    $1.10 per $1,000.  "Example: County transfer Tax = $163.35 divide by 1.1 then multiply by 1000 = $148,050. Therefore $148,050 will be populated as sales_price_amount".
  But if value is less than or equal to 100 dollars but county transfer tax is null then leave sales_price_amount field as empty.
  Important - If raw sales price amount is less than or equal to 100 dollars then calculate from above formula or leave it blank but never fill value less than or equal to 100.
  value should start with '$' and with two digits after decimal. Put commas according to international format.
  It is only for deed documents. }

- sales_price_amount_stnd_code
{ Cascading fields from sales price amount
    1. When raw_sales_price_amount is greater than 100 dollars then directly populate 'RD'
    2. If sales price amount is calculated using county transfer tax then populated 'CF'
    3. If Sales price amount is not populated then populate 'NO'
  This is only for deed documents and remains empty for others. }

- county_transfer_tax	
{ First check the county of document, then follow according to rules mentioned below foe specific counties
  For 'Clinton' county, mentioned at top right corner of first page with "-C" after value.
  For all other counties, leave this field as empty.
  value should start with '$' and with two digits after decimal. Put commas according to international format.
  Leave it empty if not found. }

- state_transfer_tax	
{ First check the county of document, then follow according to rules mentioned below foe specific counties
  For 'Clinton' county, mentioned below County Transfer tax with "-S" after value in first page.
  For county in ['Clark', 'Mccracken', 'Bullitt', 'Carroll', 'Gallatin', 'Todd'], look in last page and populate the value written after 'TRANSFER TAX' keyword in this field. Do not take value written after 'TOTAL FEES' keyword. 
  For 'Alfalfa', 'Beaver', 'Cimarron', 'Coal', 'Dewey', 'Ellis', 'Greer', 'Harper', 'Atoka', 'Hughes', 'Pushmataha', 'Texas', 'Jefferson' and 'Roger Mills' county, look in last page and populate the value written after 'Doc' keyword in this field. Do not take value written after 'Fee' keyword. 
  For all other counties, leave this field as empty.
  value should start with '$' and with two digits after decimal. Put commas according to international format.
  Leave it empty if not found. }

- total_transfer_tax	
{ First check the county of document, then follow according to rules mentioned below foe specific counties
  For 'Clinton' county, Populate this field with the sum of the County and State Transfer Taxes.
  For 'Whitley', 'Butler' county, look in last page and populate the value written after 'TRANSFER TAX' keyword in this field. Do not take value written after 'TOTAL FEES' keyword. 
  For 'Wolfe' county, look in last page and populate the value written after 'DEED TAX' keyword in this field.
  For all other counties, leave this field as empty.
  value should start with '$' and with two digits after decimal. Put commas according to international format.
  Leave it empty if not found. }

- intra_family_transfer_flag  
{ Based on the langauge of the document, if the buyers and sellers are individuals and based on the last names of the seller(s) and buyer(s) the conclusion is that the seller and buyer are related to each other, then populate Y.
  If an individual(s) is transferring the title of the property to a trust which is named after a person and that person seems related to the seller(s) based on the last name or vice versa, then populate Y.
  For example, if sellers are William Roberts and John Roberts and buyer is Jeffrey Roberts then populate Y as both seller and buyer have Roberts as last name.
  But if sellers William Roberts and John Roberts and buyer is Jeffrey trump then leave it as empty as buyer is not related to seller.
  Important - Above relation is between seller and buyer and not amongst buyers or amongst sellers.
  If above these cases are not valid for that document then leave this empty.
  IMPORTANT: If sales_price_amount field is populated then leave this field empty. }

- occupancy_status_stnd_code
{ Occupancy Stand code- Current owner must reside in this property 
  It is only valid for deed documents.
    1. Code 'O' (Owner Occupied): #Priority1 (Keyed)
    Whenever document has specifically mentioned 'owner occupied' keyword, populate 'O'.
    2. Code 'H' (Homestead Property): #Priority2 (Keyed)
    When the document has specifically mentioned homestead keyword, populate 'H'.
    3. Code 'A' (Assumed Owner Occupancy): #Priority3 (Programmatic)
    This is very common value for this field so look carefully for buyer address and property address in document then follow below condition.
    Buyer address is given with buyer names or mentioned as tax mailing address.
    Property address is mentioned with keywords 'property address'.
    Also tax bills address are not same as property address.
    If buyer mail full street address is similar to property full street address, only then populate 'A'.
    4. Code 'N' (Non-Owner Occupied)
    5. If the above condition is not met, then check if SecondHomeRiderFlag = Y, then populate Occupancy_Status_Stnd_Code as 'S'.
    6. If none of the above conditions are met, then leave blank. }	

- legal_stnd_code
{ 1. Populate 'O' if Property identifying information for county(ies) outside of FIPS is ignored.
  2. Populate 'N' if Legal description is null {legal description no longer coded, unless programmatic routine in place for coding or code 'O' applies.  All other records default to code 'N' (redefined to 'not coded'}. }

- raw_lender_name	
{ Get lender name from document.
  It is generally present after keyword 'Lender' in documents.
  It is only for Mortage documents. }

- lender_name
{ It is value of raw_lender_name field in capital letters. }

- raw_lender_type_stnd_code	
{ Get lender type description in two or three words. }

- lender_type_stnd_code
{ Choose Lender type code from below table -
    LENDER TYPE DESCRIPTION	LENDER TYPE CODE
    Bank	BK
    Credit Union	CU
    Finance company	FN
    Government entity	GV
    Insurance company	IN
    Internet Storefront	IT
    Lending company	LN
    Mortgage company	MG
    Other 	OT
    Private Party	PP
    REO/Foreclosure Company	RE
    Reverse Mortgage Lender	RM
    Seller	SL
    Subprime Lender	SB
    Undisclosed	UD
    Unknown	UN
  It is only for mortage documents. }

- raw_lender_dba_name	
{ If 'DBA' word is present with lender name, then Lender DBA Name is captured here, excluding the label "dba".  
  If a parent lender name is also reported, it is entered into the Lender Name field.  
  Note:  If an AKA is provided for the lender, it is keyed into this field preceded by label "AKA" (this applies to private party lenders as well).  
  Example:  "AKA F&M Bank".  If both an AKA and a DBA reported, then only the DBA is entered into this field. }

- lender_dba_name
{ It is the value of raw_lender_dba_name field in capital letters. }

- raw_dba_lender_type_stnd_code	
{ Get lender type description in two or three words. }

- dba_lender_type_stnd_code
{ Same as lender_type_stnd_code, populate this field from that table according to raw_dba_lender_type_stnd_code value if lender dba is found. }

- raw_loan_amount	
{ Get loan amount from document.
  If document has multiple loan amounts and the total, then populate the aggregate amount here.
  If there is no maximum word in statement then it is considered as loan amount otherwise leave it empty. 
  It loan amount is mentioned as fair cash price or estimated value then leave this field empty.
  It is only for mortage documents. }

- loan_amount	
{ It is value of raw_loan_amount.
  value should start with '$' and with two digits after decimal. 
  loan_amount and maximum_loan_amount can never be filled together. }

- loan_amount_std_code
{ Populate this on the basis of below condtions -
    Loan amount keyed is an Aggregate amount (multiple loans with an aggregate total provided) - 'A'
    Loan amount keyed is a Calculated Loan amount (multiple amounts reported on document) - 'C'
    Multiple Loan Amounts - 'M'
    Loan amount not reported on recorded document or unreadable/not captured due to complexities - 'N'
    Loan amount keyed is original principal amount of an Assumed or Refinanced loan - 'S' }

- maximum_loan_amount	
{ If maximum word is present in the statement then the amount is considered as maximum loan amount otherwise leave it empty.
  If document has multiple loan amounts but no total amount and the document mentions loans referencing a "maximum" amount, then calculate the total and populate here.
  value should start with '$' and with two digits after decimal.
  loan_amount and maximum_loan_amount can never be filled together. }

- raw_loan_type_stnd_code
{ Give loan type description from document. }

- loan_type_stnd_code
{ Fill Loan type code on basis of loan type description from below table - 
    LOAN TYPE DESCRIPTION	LOAN TYPE CODE	NOTES
    Agricultural/Commercial	AC	May be found at the bottom of the mortgage form "Agricultural/Commercial Security Instrument".  When present on mortgage form and another loan type referenced in the body of the document, give priority to the loan type in the body of the document, except if "purchase money", then prioritize code "AC".
    Assumption	AS	
    Balloon	BL	If another loan type applies, then give priority to other loan type
    Commercial	CM	
    Commercial Construction Loan	CT	Phased in June 2015
    Construction Loan	CS	
    Construction Loan - Credit Line	CC	
    Credit Line (HELOC)	CL	If a Credit Line is mentioned in document then always code "CL" takes priority over others.
    Down Payment Assistance Loan	DP	May reference "First Time Homebuyer Assistance Program"
    Farm Ownership Loan	FO	
    First Lien Home Equity Loan	FE	
    First Mortgage (First Lien Deed of Trust)	FM	(Only if 'First Lien Deed of Trust' keywords are mentioned then populate 'FM' in this field.)
    Home Equity Loan	HE	
    Land Contract (Contract/Agreement of Sale)	LC	
    Loan Modification	MD	Currently inactive.  #Suppress
    Non-Purchase Money (no other loan type applies)	NP	If another loan type applies, then give priority to other loan type.
    Partial Claim Mortgage	PC	This type of mortgage is a subordinate mortgage, prioritize this code over code "SM".
    Purchase Money (no other loan type applies)	PM	If another loan type applies (except balloon loan), then give priority to other loan type
    Refinance	RE	
    Refinance - Credit Line	RC	
    Reverse Mortgage (HECM)	RM	Doc header may report "Home Equity Conversion Mortgage" 
    Reverse Mortgage (HECM) - Credit Line	RV	 
    Second (Subordinate) Mortgage	SM	
    Second Lien Home Equity Loan	SE	
    Seller Take Back	SL	 
    Trade	TR }

- loan_type_closed_open_end_stnd_code	
{ Field identifies if loan is Closed-End or Open-End, otherwise left blank.
  This will be mentioned in title of the document only and if not mentioned then leave it blank.
  Only valid codes:
    'C' for Closed-End Mortgage
    'O' for Open-End Mortgage. }	

- raw_loan_type_program_stnd_code	
{ Capture loan type program from document. }

- loan_type_program_stnd_code	
{ Populate CV if mortgage form mentions "Fannie Mae/Freddie Mac" in document (may also be reported as "FNMA/FHLMC"). It is found at bottom of document so look carefully please.
  If not then based on raw_loan_type_program_stnd_code value, fill this on the basis of below table -
    LOAN TYPE PROGRAM DESCRIPTION	LOAN TYPE PROGRAM CODE
    Conventional Loan	CV  (If "Fannie Mae/Freddie Mac" is mentioned.)
    Farmers Home Administration (FmHA) loan	FA
    Federal Housing Administration (FHA) loan	FH
    FHA Housing Rehabilitation Loan 	FR
    Housing Rehabilitation Loan (non-FHA)	HR
    Small Business Administration (SBA) loan	SB
    State Veteran Loan	SV
    U.S. Department of Agriculture (USDA) Farm Service Agency  loan	UF
    U.S. Department of Agriculture (USDA) Rural Development (Rural Housing Service) loan	UR
    U.S. Department of Agriculture (USDA) loan	US
    U.S. Department of Veterans Affairs loan	VA 
  If not found then leave empty. }

- raw_loan_rate_type_stnd_code
{ Capture the type of interest rate tied to the loan as reported on the document. }

- loan_rate_type_stnd_code	
{ Based on raw_loan_rate_type_stnd_code field value, refer to below table for valid codes, if none apply, field remains blank.
    LOAN RATE TYPE DESCRIPTION	LOAN RATE TYPE CODE
    Adjustable Loan with Capped Two-Year ARM Rider	ADC
    Adjustable Rate	ADJ
    Adjustable Loan with Capped Ten-Year ARM Rider	ADT
    Adjustable Loan with Capped Five-Year ARM Rider	ADV
    Fixed Rate	FIX
    Other	OTH
    Variable Rate	VAR }

- raw_loan_due_date
{ Get loan due date from document. It is generally present in loan amount paragraph.
  It might be present like 'Mortgage matures on'. }

- loan_due_date
{ It is the value of raw_loan_due_date but first reformat it to 'YYYY-MM-DD'.  THIS IS ABSOLUTELY MANDATORY. The year MUST come FIRST. }

- loan_term_months	
{ Capture loan term months if available. }

- loan_term_years	
{ Capture loan term years if available. }

- initial_interest_rate
{ Straight Capture initial_interest_rate if Adjustable Rate Rider (ARM) details available.
  If the loan is an adjustable, this is the initial interest rate of the loan until the first adjustment date.   
  Fixed rate loans generally do not report interest rate on the loan document, if provided, the fixed interest rate is entered here. }

- arm_first_adjustment_date
{ Straight Capture arm_first_adjustment_date and Maintain Format 'YYYY-MM-DD'.
  The date an adjustable rate mortgage converts from an initial fixed rate period to an adjustable rate. }

- arm_first_adjustment_max_rate
{ Straight Capture arm_first_adjustment_max_rate if Adjustable Rate Rider (ARM) details available.
  The maximum interest rate limit at the First Adjustment Date on an adjustable rate mortgage. }

- arm_first_adjustment_min_rate
{ Straight Capture arm_first_adjustment_min_rate if Adjustable Rate Rider (ARM) details available.
  The mimimum interest rate limit at the First Adjustment Date on an adjustable rate mortgage. }

- raw_arm_index_stnd_code
{ Straight Capture if Adjustable Rate Rider (ARM) details available.
  An ARM's interest rate fluctuates based on published indexes. This field identifies the index the ARM is tied to. }

- arm_index_stnd_code
{ Based on raw_arm_index_stnd_code field, look in below table and fill corresponding arm index code in this field.
    ARM INDEX DESCRIPTION	ARM INDEX CODE
    11th District Cost of Funds Index	COFI
    Certificate of Deposit  1 month	CD1M
    Certificate of Deposit 1 year	CD1Y
    Certificate of Deposit 3 month 	CD3M
    Certificate of Deposit 6 month 	CD6M
    Certificate of Deposit Index	CODI
    Constant Maturity Treasury 1 month	C1M
    Constant Maturity Treasury 1 year	C1Y
    Constant Maturity Treasury 10 year	C10Y
    Constant Maturity Treasury 2 year	C2Y
    Constant Maturity Treasury 3 month	C3M
    Constant Maturity Treasury 3 year	C3Y
    Constant Maturity Treasury 30 year	C30Y
    Constant Maturity Treasury 5 year	C5Y
    Constant Maturity Treasury 6 month	C6M
    Cost of Funds Index (other than 11th District)	COFO
    London Inter Bank Offering Rate  ("LIBOR")	LBR
    London Inter Bank Offering Rate ("LIBOR") 1 month	L1M
    London Inter Bank Offering Rate ("LIBOR") 1 year	L1Y
    London Inter Bank Offering Rate ("LIBOR") 3 month 	L3M
    London Inter Bank Offering Rate ("LIBOR") 6 month  	L6M
    Secured Overnight Financing Rate ("SOFR")	SOFR
    Secured Overnight Financing Rate ("SOFR") 1 month	SO1M
    Secured Overnight Financing Rate ("SOFR") 3 month	SO3M
    Secured Overnight Financing Rate ("SOFR") 6 month   	SO6M
    Monthly Treasury Average (12 month Moving Average Treasury)	MTA
    Other (uncommon indices)	OTH
    Prime Rate	PRM
    Treasury Bill 1 month	TB1M
    Treasury Bill 3 month	TB3M
    Treasury Bill 6 month	TB6M
    Treasury Bill 1 year	TB1Y
    Treasury Bill 3 year	TB3Y
    Treasury Bill 5 year	TB5Y
    Treasury Bill 10 year	TB10Y
    Wachovia Cost of Savings Index	WCSI
    Wells Fargo Cost of Savings Index	WFCS }

- raw_arm_adjustment_frequency_stnd_code
{ Straight Capture if Adjustable Rate Rider (ARM) details available.
  This is the frequency at which the ARM interest rate adjusts after the initial fixed-rate period ends. }

- arm_adjustment_frequency_stnd_code
{ Based on value of raw_arm_adjustment_frequency_stnd_code field, populate corresponding frequency code in this field.
    ADJUSTMENT FREQUENCY DESCRIPTION	ADJUSTMENT FREQUENCY CODE	NOTES
    10 Years    T	120 months
    2 Years 2	24 months
    3 Years 3	36 months
    4 Years 4	48 months
    5 Years	5	60 months
    6 Years	6	72 months
    7 Years	7	84 months
    8 Years	8	96 months
    9 Years	9	108 months
    Annually	A	12 months
    15 Years	F	180 months
    Monthly	M	
    Quarterly Q	
    Semi-Annually (every six months) S }

- arm_margin
{ Straight Capture arm_margin if Adjustable Rate Rider (ARM) details available.
  The percentage added to the index rate by the lender. The index rate plus the margin is the fully indexed rate. }

- arm_periodic_cap
{ Straight Capture if Adjustable Rate Rider (ARM) details available.
  The limit (expressed as a percentage) the interest rate can adjust from one adjustment period to the next, after the first adjustment. }

- arm_max_interest_rate
{ Straight Capture if Adjustable Rate Rider (ARM) details available.
  The maximum interest rate of the adjustable rate mortgage. }

- arm_min_interest_rate
{ Straight Capture if Adjustable Rate Rider (ARM) details available.
  The minimum interest rate of the adjustable rate mortgage. }

- interest_only_flag
{ If the loan provides for an Interest-Only period, populate Y here, otherwise leave blank. }

- interest_only_term
{ If interest_only_flag is Y and the interest-only period is known, populate the interest-only term here. }

- prepayment_penalty_flag
{ Capture 'Y' , if 1-4 prepayment penalty flag is ticked in 'Riders' section in document. }

- raw_prepayment_penalty_term	
{ It is the minimum amount of time the loan must be active by borrower to avoid a penalty. Expressed in months.  
  Example:  if penalty period three months, entered as '3'; if two years, entered as '24'. }

- bi_weekly_payment_flag	
{ Capture 'Y' , if bi weekly payment flag is ticked in 'Riders' section in document. }

- assumability_rider_flag	
{ Capture 'Y' , if assumability rider flag is ticked in 'Riders' section in document. }

- balloon_rider_flag
{ Capture 'Y' , if Balloon rider flag is ticked in 'Riders' section in document. }

- second_home_rider_flag
{ Capture 'Y' , if second home rider flag is ticked in 'Riders' section in document. }

- one_to_four_family_rider_flag
{ Capture 'Y' , if one to four Family Rider flag is ticked in 'Riders' section in document. }

- zvendor_stnd_code
{ Its default value is 'SEK' }

Important Notes:
- Loan amount can either be loan_amount or maximum_loan_amount, it can't be both. If maximum word is mentioned then it is considered as maximum_loan_amount and loan_amount will be left empty and vice versa.
- Whichever rider's flag is ticked in 'Riders' section in document, their details is also given in last some pages of document that you can find. So please confirm the details for rider in last pages of document before populating them.

If a piece of information is not found, leave that field empty.
Return the data in CSV format with two columns: ColumnName, Value.
"""

all_column_names = [
    "record_id", "index_key", "raw_fips", "fips", "raw_state", "state", "raw_county", "county", "raw_data_class_stnd_code",
    "data_class_stnd_code", "raw_record_type_stnd_code", "record_type_stnd_code", "raw_recording_date", "recording_date", "recording_document_number", "recording_book_number", "recording_page_number", "re_recorded_correction_stnd_code", "prior_recording_date", "prior_document_date", "prior_document_number", "prior_book_number", "prior_page_number", "raw_document_type_stnd_code", "document_type_stnd_code", "raw_document_date", "document_date", "raw_signature_date",
    "signature_date", "raw_effective_date", "effective_date", "raw_buyer_vesting_stnd_code", "buyer_vesting_stnd_code", "buyer_multi_vesting_flag", "raw_partial_interest_transfer_stnd_code", "partial_interest_transfer_stnd_code", "partial_interest_transfer_percent", "raw_sales_price_amount", "sales_price_amount", "sales_price_amount_stnd_code", "city_transfer_tax", "county_transfer_tax", "state_transfer_tax", "total_transfer_tax", "raw_intra_family_transfer_flag", "intra_family_transfer_flag", "transfer_tax_exempt_flag", "property_use_stnd_code", "assessment_land_use_stnd_code", "raw_occupancy_status_stnd_code",
    "occupancy_status_stnd_code", "raw_legal_stnd_code", "legal_stnd_code", "borrower_vesting_stnd_code", "raw_lender_name", "lender_name", "raw_lender_type_stnd_code", "lender_type_stnd_code", "raw_lender_id_stnd_code", "lender_id_stnd_code", "raw_lender_dba_name", "lender_dba_name", "raw_dba_lender_type_stnd_code", "dba_lender_type_stnd_code", "raw_dba_lender_id_stnd_code", "dba_lender_id_stnd_code", "lender_mail_care_of_name", "lender_mail_house_number", "lender_mail_house_number_ext", "lender_mail_street_pre_directional",
    "lender_mail_street_name", "lender_mail_street_suffix", "lender_mail_street_post_directional", "lender_mail_full_street_address", "lender_mail_building_name", "lender_mail_building_number", "lender_mail_unit_designator", "lender_mail_unit", "lender_mail_city", "lender_mail_state", "lender_mail_zip", "lender_mail_zip4", "raw_loan_amount", "loan_amount",
    "raw_loan_amount_stnd_code", "loan_amount_stnd_code", "maximum_loan_amount", "raw_loan_type_stnd_code", "loan_type_stnd_code", "raw_loan_type_closed_open_end_stnd_code", "loan_type_closed_open_end_stnd_code", "loan_type_future_advance_flag", "raw_loan_type_program_stnd_code", "loan_type_program_stnd_code", "raw_loan_rate_type_stnd_code", "loan_rate_type_stnd_code", "raw_loan_due_date", "loan_due_date", "raw_loan_term_months", "loan_term_months",
    "raw_loan_term_years", "loan_term_years", "initial_interest_rate", "arm_first_adjustment_date", "arm_first_adjustment_max_rate", "arm_first_adjustment_min_rate", "raw_arm_index_stnd_code", "arm_index_stnd_code", "raw_arm_adjustment_frequency_stnd_code", "arm_adjustment_frequency_stnd_code", "arm_margin", "arm_initial_cap", "arm_periodic_cap", "arm_lifetime_cap", "arm_max_interest_rate",
    "arm_min_interest_rate", "raw_interest_only_flag", "interest_only_flag", "raw_interest_only_term", "interest_only_term", "raw_prepayment_penalty_flag", "prepayment_penalty_flag", "raw_prepayment_penalty_term", "prepayment_penalty_term", "raw_bi_weekly_payment_flag", "bi_weekly_payment_flag", "raw_assumability_rider_flag", "assumability_rider_flag", "raw_balloon_rider_flag", "balloon_rider_flag", "condominium_rider_flag", "planned_unit_development_rider_flag",
    "raw_second_home_rider_flag", "second_home_rider_flag", "raw_one_to_four_family_rider_flag", "one_to_four_family_rider_flag", "concurrent_mtge_doc_or_bk_pg", "loan_number", "mersmin_number", "case_number", "mers_flag", "title_company_name", "title_company_id_stnd_code", "accommodation_recording_flag", "unpaid_balance", "installment_amount", "installment_due_date", "total_delinquent_amount", "delinquent_as_of_date", "current_lender",
    "current_lender_type_stnd_code", "current_lender_id_stnd_code", "trustee_sale_number", "attorney_file_number", "auction_date", "auction_time", "auction_full_street_address", "auction_city_name", "starting_bid", "keyed_date", "keyer_id", "subvendor_stnd_code", "zvendor_stnd_code", "image_file_name", "builder_flag", "match_stnd_code", "transaction_type_stnd_code", "reo_stnd_code", "update_ownership_flag"
]