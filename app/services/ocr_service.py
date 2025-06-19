import io
import os
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    
class OCRProcessor:
    @staticmethod
    def process_pdf(pdf_path, output_path):
        """
        Extracts text from a PDF file using OCR and saves it to a text file.

        Args:
            pdf_path (str): Path to the PDF file.
            output_path (str): Path to save the output text file.
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Open the PDF file using PyMuPDF (fitz)
            pdf_document = fitz.open(pdf_path)

            full_text = ""

            for page_number in range(pdf_document.page_count):
                logger.info(f"Processing {os.path.basename(pdf_path)}, page {page_number+1}/{pdf_document.page_count}")

                page = pdf_document.load_page(page_number)  # Load each page
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")  # Convert to PNG bytes

                # Convert the image bytes to a PIL Image
                image = Image.open(io.BytesIO(img_bytes))

                # Perform OCR on the image
                text = pytesseract.image_to_string(image)
                full_text += text + "\n\n"  # Add page separator

            pdf_document.close()  # Close the PDF document

            # Save the extracted text to a file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            logger.info(f"OCR complete for {os.path.basename(pdf_path)}, text saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"An error occurred while processing {os.path.basename(pdf_path)}: {e}")
            return False

    @staticmethod
    def process_image(image_path, output_path):
        """
        Extracts text from an image file using OCR and saves it to a text file.

        Args:
            image_path (str): Path to the image file.
            output_path (str): Path to save the output text file.
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Open the image file
            image = Image.open(image_path)
            
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            
            # Save the extracted text to a file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
                
            logger.info(f"OCR complete for {os.path.basename(image_path)}, text saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"An error occurred while processing {os.path.basename(image_path)}: {e}")
            return False

    @staticmethod
    def process_directory(input_dir, output_dir, file_types=None):
        """
        Processes all files of specified types in a directory using OCR.

        Args:
            input_dir (str): Path to the directory containing files to process.
            output_dir (str): Path to the directory where text files will be saved.
            file_types (list, optional): List of file extensions to process. Defaults to ['.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png'].
            
        Returns:
            dict: A dictionary with statistics about the OCR process
        """
        if file_types is None:
            file_types = ['.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png']
            
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "skipped_files": 0
        }
        
        for filename in os.listdir(input_dir):
            file_ext = os.path.splitext(filename.lower())[1]
            if file_ext in file_types:
                stats["total_files"] += 1
                input_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + ".txt"
                output_path = os.path.join(output_dir, output_filename)
                
                if os.path.exists(output_path):
                    logger.info(f"Skipping {filename} - Text file already exists")
                    stats["skipped_files"] += 1
                    continue
                
                success = False
                if file_ext == '.pdf':
                    success = OCRProcessor.process_pdf(input_path, output_path)
                else:  # Image file
                    success = OCRProcessor.process_image(input_path, output_path)
                    
                if success:
                    stats["processed_files"] += 1
                else:
                    stats["failed_files"] += 1
        
        return stats