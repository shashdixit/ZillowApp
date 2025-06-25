import os
import asyncio
import base64
import urllib3
from dotenv import load_dotenv 
from tenacity import retry, stop_after_attempt, wait_random_exponential
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', "https://llmfoundry.straive.com/gemini/v1beta/models/gemini-2.0-flash-001:generateContent")
LLM_TOKEN = os.getenv('LLM_FOUNDRY_TOKEN')
RETRY_ATTEMPTS = 3
CONCURRENCY_LIMIT = 4  # Adjust as needed

# Disable SSL warnings (only for development)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def encode_pdf(pdf_path):
    """Encodes the PDF file to base64."""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

# Initialize rate limiter
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_random_exponential(multiplier=1, min=1, max=10))
async def query_llm(session, pdf_base64, system_prompt, message_prompt):
    """Query the LLM with retry logic."""
    async with semaphore:  # Acquire semaphore before making the request
        try:
            async with session.post(
                LLM_ENDPOINT,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LLM_TOKEN}:my-test-project"
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
                ssl=False  # Use ssl=False instead of verify=False with aiohttp
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # Extract the text response from the LLM
                if 'candidates' in data and len(data['candidates']) > 0:
                    if 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content']:
                        return data['candidates'][0]['content']['parts'][0]['text']

                return "Error: Unexpected response format"

        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise  # Re-raise the exception for tenacity to handle


def parse_csv_response(response_text):
    """Parse the CSV response from the LLM."""
    results = {}
    lines = response_text.strip().split('\n')

    start_idx = 0
    if lines and ('ColumnName' in lines[0] or 'Value' in lines[0]):
        start_idx = 1

    start_idx += 1

    for line in lines[start_idx:-1]:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 2:
                column_name = parts[0].strip()
                value = ','.join(parts[1:]).strip()
                results[column_name] = value
            elif len(parts) == 1:
                column_name = parts[0].strip()
                results[column_name] = "null"

    return results