import os
import csv
import base64
import aiohttp
import asyncio
from PyPDF2 import PdfReader, PdfWriter
from tenacity import retry, stop_after_attempt, wait_random_exponential
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALL_COLUMN_NAMES = [
    "S. No.",
    "File Type",
    "File Name",
    "Page Count",
    "FIPS",
    "County",
    "State",
    "Batch",
    "Delivery",
    "Segregation VA Allocation",
    "Segregation VA Status",
    "Segregation QA Status",
    "Doc Title",
    "Data Class",
    "OCR Allocation",
    "Valid/Invalid",
    "Valid/Invalid Allocation",
    "OCR Status",
    "DC Allocation",
    "DC Status",
    "DC Completion Date",
    "VA Name",
    "VA Status",
    "VA RWK Status",
    "QC Allocation",
    "QC Alloc. Date",
    "QA comments-Valid check",
    "Comments"
]

class TitleExtractor:
    def __init__(self, llm_endpoint, llm_token):
        self.llm_endpoint = llm_endpoint
        self.llm_token = llm_token
    

    @staticmethod
    def encode_first_page(pdf_path):
        """Encodes the first page of the PDF file to base64."""
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Add the first page to the writer
            if len(reader.pages) > 0:
                writer.add_page(reader.pages[0])

                # Save the first page to a temporary file
                temp_pdf_path = os.path.join(os.path.dirname(pdf_path), "temp_first_page.pdf")
                with open(temp_pdf_path, "wb") as temp_pdf_file:
                    writer.write(temp_pdf_file)

                # Encode the temporary file to base64
                with open(temp_pdf_path, "rb") as pdf_file:
                    encoded = base64.b64encode(pdf_file.read()).decode('utf-8')

                # Clean up temporary file
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

                return encoded
            else:
                logger.error(f"PDF file has no pages: {pdf_path}")
                return None
        except Exception as e:
            logger.error(f"Error encoding PDF: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, min=1, max=5))
    async def query_llm_with_pdf(self, session, pdf_base64):
        """Query the LLM to extract title and FIPS code from the PDF file with retry."""
        system_prompt = """
        You are a data extraction expert. Your task is to extract the document title and the county FIPS code from the provided document.
        Format your response as a JSON object with two keys: "title" and "fips_code".
        The "title" should contain only the title of the document.
        The "fips_code" should contain the FIPS code of the county mentioned in the document.
        If you cannot determine the county or the FIPS code, set "fips_code" to "Unknown".
        Do not include any explanations or additional text in your response.

        Here is a table of county names and their corresponding FIPS codes:
        COUNTY NAME,FIPS CODE
        Clinton,26037
        Whitley,21235
        Clark,21049
        Mccracken,21145
        Bullitt,21029
        Elliott,21063
        Wolfe,21237
        Alfalfa,40003
        Beaver,40007
        Cimarron,40025
        Coal,40029
        Dewey,40043
        Ellis,40045
        Greer,40055
        Harper,40059
        Jefferson,40067
        Roger Mills,40129
        """

        message_prompt = """
        Analyze the provided document and extract its title and the county it pertains to.
        Return a JSON object containing the "title" and the "fips_code".
        If the document contains "Discharge of Mortgage" in the title, use "Discharge of Mortgage" as the title.
        If you cannot determine the county or the FIPS code, set "fips_code" to "Unknown".
        Respond only with a raw JSON object, without any Markdown formatting or code fences.
        """

        try:
            async with session.post(
                self.llm_endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.llm_token}:my-test-project"
                },
                json={
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": message_prompt
                                },
                                {
                                    "inline_data": {
                                        "data": pdf_base64,
                                        "mime_type": "application/pdf"
                                    }
                                }
                            ]
                        }
                    ],
                    "generationConfig": {"temperature": 0.1}
                },
                ssl=False  # Equivalent to verify=False
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # Extract the text response from the LLM
                if 'candidates' in data and len(data['candidates']) > 0:
                    if 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content']:
                        llm_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
                        try:
                            import json
                            lines = llm_response.strip().splitlines()
                            if lines[0].strip().startswith('```') and lines[-1].strip().startswith('```'):
                                llm_response = '\n'.join(lines[1:-1])  # extract lines in between
                            response_json = json.loads(llm_response)
                            title = response_json.get('title', 'Unknown Title')
                            fips_code = response_json.get('fips_code', 'Unknown')
                            return title, fips_code
                        except json.JSONDecodeError as e:
                            logger.error(f"Could not decode JSON response: {llm_response}. Error: {e}")
                            return "Unknown Title", "Unknown"

                return "Unknown Title", "Unknown"

        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise

    async def process_pdf(self, session, pdf_path, results_list):
        """Process a single PDF file and return its title and FIPS code."""
        try:
            # Encode the PDF file
            pdf_base64 = self.encode_first_page(pdf_path)
            if not pdf_base64:
                return os.path.basename(pdf_path), "Error: Could not encode PDF", "Error"

            # Query LLM to extract title and FIPS code
            title, fips_code = await self.query_llm_with_pdf(session, pdf_base64)
            file_name_without_extension = os.path.basename(pdf_path).split('.')[0]
            
            output_row = []
            for column_name in ALL_COLUMN_NAMES:
                if column_name == "File Name":
                    output_row.append(file_name_without_extension)
                elif column_name == "FIPS":
                    output_row.append(fips_code)
                elif column_name == "Doc Title":
                    output_row.append(title)
                else:
                    output_row.append("")

            # Append the row to the results list
            results_list.append(output_row)

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return os.path.basename(pdf_path), f"Error: {str(e)}", "Error"

    async def process_batch(self, session, pdf_paths, task_id, task_status, total_files, batch_start_index, results_list, batch_size=5):
        """Process a batch of PDF files concurrently."""
        tasks = [self.process_pdf(session, path, results_list) for path in pdf_paths]
        await asyncio.gather(*tasks)
        logger.info(f"Processed batch starting from index {batch_start_index//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}")

        # Calculate and update progress
        processed_count = batch_start_index + len(pdf_paths)
        progress = int((processed_count / total_files) * 95)  # Scale to 95% to leave room for completion
        task_status[task_id]["progress"] = progress
        task_status[task_id]["message"] = f"Processed {processed_count}/{total_files} files ({progress}%)"

    async def extract_titles_from_directory(self, pdf_files, output_csv, batch_size, task_id, task_status):
        """Extract titles and FIPS codes from all PDF files in a directory."""

        total_files = len(pdf_files)
        logger.info(f"Found {total_files} PDF files")

        all_results = []
        async with aiohttp.ClientSession() as session:
            for i in range(0, total_files, batch_size):
                batch = pdf_files[i:i + batch_size]
                await self.process_batch(session, batch, task_id, task_status, total_files, i, all_results, batch_size)

        # Write results to CSV if output_csv is provided
        if output_csv:
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(ALL_COLUMN_NAMES)
                csv_writer.writerows(all_results)
            logger.info(f"Results saved to {output_csv}")

        return all_results