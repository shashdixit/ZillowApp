from PIL import Image
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TifToPdfConverter:
    @staticmethod
    def convert_file(tif_file, pdf_file=None):
        """
        Converts a single TIF file to PDF format.
        
        Args:
            tif_file (str): Path to the TIF file
            pdf_file (str, optional): Path for the output PDF file. If None, uses the same name as the TIF file.
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            img = Image.open(tif_file)
        except FileNotFoundError:
            logger.error(f"Error: TIFF file not found: {tif_file}")
            return False
        except Exception as e:
            logger.error(f"Error opening TIFF file: {e}")
            return False

        if pdf_file is None:
            pdf_file = os.path.splitext(tif_file)[0] + ".pdf"

        try:
            # Handle multi-page TIFFs
            if getattr(img, "n_frames", 1) > 1:
                images = []
                for i in range(img.n_frames):
                    img.seek(i)
                    # Convert to RGB (removing alpha channel if present)
                    if img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                        images.append(rgb_img)
                    else:
                        images.append(img.convert('RGB'))
                
                # Save the first image as PDF and append the rest
                images[0].save(pdf_file, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
            else:
                # Single-page TIFF
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    rgb_img.save(pdf_file, "PDF", resolution=100.0)
                else:
                    img.convert('RGB').save(pdf_file, "PDF", resolution=100.0)
                    
            logger.info(f"Successfully converted {tif_file} to {pdf_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting to PDF: {e}")
            return False

    @staticmethod
    def convert_directory(input_dir, output_dir):
        """
        Converts all TIFF files in a directory to PDF files.

        Args:
            input_dir (str): Path to the directory containing TIFF files.
            output_dir (str): Path to the directory where PDF files will be saved.
            
        Returns:
            dict: A dictionary with statistics about the conversion process
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        stats = {
            "total_files": 0,
            "converted_files": 0,
            "failed_files": 0,
            "skipped_files": 0
        }
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith((".tif", ".tiff")):
                stats["total_files"] += 1
                tif_file = os.path.join(input_dir, filename)
                pdf_filename = os.path.splitext(filename)[0] + ".pdf"
                output_file = os.path.join(output_dir, pdf_filename)
                
                if os.path.exists(output_file):
                    logger.info(f"Skipping {filename} - PDF already exists")
                    stats["skipped_files"] += 1
                    continue
                    
                success = TifToPdfConverter.convert_file(tif_file, output_file)
                if success:
                    stats["converted_files"] += 1
                else:
                    stats["failed_files"] += 1
        
        return stats