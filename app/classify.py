import os
import base64
import requests
from pypdf import PdfReader, PdfWriter
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def encode_first_page(pdf_path):
    """Encodes the first page of the PDF file to base64."""
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Add the first page to the writer
        writer.add_page(reader.pages[0])

        # Save the first page to a temporary file
        temp_pdf_path = "temp_first_page.pdf"
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            writer.write(temp_pdf_file)

        # Encode the temporary file to base64
        with open(temp_pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding PDF: {e}")
        return None
    finally:
        # Clean up the temporary file
        try:
            os.remove("temp_first_page.pdf")
        except Exception:
            pass


def classify_document(pdf_path):
    """
    Classifies a PDF document as either a 'Mortgage' (M) or 'Deed' (D) document
    using the Gemini 2.0 Flash model.

    Args:
        pdf_path (str): The path to the PDF document.

    Returns:
        str: 'M' if the document is classified as a mortgage document,
             'D' if classified as a deed document,
             None if an error occurred.
    """

    pdf_base64 = encode_first_page(pdf_path)

    if not pdf_base64:
        print("Failed to encode PDF.  Classification aborted.")
        return None

    system_prompt = "You are an expert document classifier.  Your task is to classify a document by reading its title, as either a 'Mortgage' document or a 'Deed' document.  Respond with a single character: 'M' for Mortgage, 'D' for Deed.  Do not provide any other explanation or text."
    message_prompt = "Classify the following document:"

    try:
        response = requests.post(
            "https://llmfoundry.straive.com/gemini/v1beta/models/gemini-2.0-flash-001:generateContent",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('LLM_FOUNDRY_TOKEN')}:my-test-project"
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
            verify=False  # Consider removing verify=False in production for security
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Extract the classification result.  Handle potential errors in the response structure.
        try:
            classification = data['candidates'][0]['content']['parts'][0]['text'].strip().upper()
            if classification in ('M', 'D'):
                return classification
            else:
                print(f"Unexpected classification result: {classification}")
                return None
        except (KeyError, IndexError) as e:
            print(f"Error extracting classification from response: {e}")
            print(f"Full response: {data}") # Print the full response for debugging
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None