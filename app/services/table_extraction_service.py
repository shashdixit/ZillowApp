import os
import asyncio
import aiohttp
import csv
from app.prompts import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import table processors
from app.table_processors.main_table import process_main_table
from app.table_processors.property_info_table import process_property_info_table
from app.table_processors.buyer_mail_addresses_table import process_buyer_mail_addresses
from app.table_processors.buyer_data_table import process_buyer_data
from app.table_processors.seller_names_table import process_seller_names
from app.table_processors.borrower_names_table import process_borrower_names
from app.table_processors.borrower_mail_addresses_table import process_borrower_mail_addresses

class TableExtractionService:
    def __init__(self):
        self.PDF_DIRECTORY = ""  # Will be set dynamically
        self.OUTPUT_DIRECTORY = ""  # Will be set dynamically
        self.BATCH_SIZE = 10  # Define the batch size

    async def process_pdf(self, filename, session, table_processor, system_prompt, message_prompt, all_column_names):
        """Generic PDF processing function."""
        try:
            return await table_processor(filename, session, system_prompt, message_prompt, all_column_names, self.PDF_DIRECTORY)
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return None

    async def process_table(self, table_name, filenames, session, table_processor, system_prompt, message_prompt, all_column_names, task_id, task_status, progress_increment):
        """Process a specific table and write the results to a CSV file."""
        all_rows = []

        for i in range(0, len(filenames), self.BATCH_SIZE):
            batch_files = filenames[i:i + self.BATCH_SIZE]
            batch_results = await asyncio.gather(*(self.process_pdf(filename, session, table_processor, system_prompt, message_prompt, all_column_names) for filename in batch_files))

            for result in batch_results:
                if result is not None:
                    if isinstance(result, list) and all(isinstance(item, list) for item in result):
                        all_rows.extend(result)
                    else:
                        logger.warning(f"Unexpected result type: {type(result)}, skipping.")

        output_file = os.path.join(self.OUTPUT_DIRECTORY, f"{table_name}.csv")
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(all_column_names)  # Write the header row
            csv_writer.writerows(all_rows)  # Write all the data rows

        logger.info(f"Data extraction complete for {table_name}. Results saved to {output_file}")

    async def process_tables(self, filenames, session, table_processor, system_prompt, message_prompt, buyer_names_all_column_names, buyer_desc_all_column_names, task_id, task_status, progress_increment):
        """Process buyer data and write the results to CSV files."""
        all_buyer_names_rows = []
        all_buyer_desc_rows = []

        for i in range(0, len(filenames), self.BATCH_SIZE):
            batch_files = filenames[i:i + self.BATCH_SIZE]
            batch_results = await asyncio.gather(*(self.process_pdf(filename, session, table_processor, system_prompt, message_prompt, []) for filename in batch_files))

            for buyer_names_result, buyer_desc_result in batch_results:
                if buyer_names_result is not None:
                    if isinstance(buyer_names_result, list) and all(isinstance(item, list) for item in buyer_names_result):
                        all_buyer_names_rows.extend(buyer_names_result)
                    else:
                        logger.warning(f"Unexpected result type for buyer_names: {type(buyer_names_result)}, skipping.")

                if buyer_desc_result is not None:
                    if isinstance(buyer_desc_result, list) and all(isinstance(item, list) for item in buyer_desc_result):
                        all_buyer_desc_rows.extend(buyer_desc_result)
                    else:
                        logger.warning(f"Unexpected result type for buyer_desc: {type(buyer_desc_result)}, skipping.")

        # Write buyer names data to CSV
        buyer_names_output_file = os.path.join(self.OUTPUT_DIRECTORY, "buyer_names.csv")
        with open(buyer_names_output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(buyer_names_all_column_names)  # Write the header row
            csv_writer.writerows(all_buyer_names_rows)  # Write all the data rows
        logger.info(f"Data extraction complete for buyer_names. Results saved to {buyer_names_output_file}")

        # Write buyer description data to CSV
        buyer_desc_output_file = os.path.join(self.OUTPUT_DIRECTORY, "buyer_desc.csv")
        with open(buyer_desc_output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(buyer_desc_all_column_names)  # Write the header row
            csv_writer.writerows(all_buyer_desc_rows)  # Write all the data rows
        logger.info(f"Data extraction complete for buyer_desc. Results saved to {buyer_desc_output_file}")

    async def extract_all_tables(self, task_id, task_status, input_dir, output_dir):
        """Main function to orchestrate asynchronous PDF processing for all tables."""
        self.PDF_DIRECTORY = input_dir
        self.OUTPUT_DIRECTORY = output_dir
        os.makedirs(self.OUTPUT_DIRECTORY, exist_ok=True)

        results = []
        async with aiohttp.ClientSession() as session:
            pdf_files = [filename for filename in os.listdir(self.PDF_DIRECTORY) if filename.endswith(".pdf")]
            num_tables = 7  # Number of tables being processed
            initial_progress = 5  # Initial progress before table processing
            progress_per_table = (95 - initial_progress) / num_tables  # Distribute remaining progress

            # Process each table sequentially
            current_table_progress = initial_progress  # Track progress for each table
            task_status[task_id].progress = int(current_table_progress)
            task_status[task_id].message = f"Starting table extraction: {int(current_table_progress)}%"

            # await self.process_table(
            #     "main", pdf_files, session, process_main_table, main_table_system_prompt, main_table_message_prompt, main_table_all_column_names, task_id, task_status, progress_per_table
            # )
            # current_table_progress += progress_per_table
            # task_status[task_id].progress = int(min(current_table_progress, 95))
            # task_status[task_id].message = f"Processing property_info: {task_status[task_id].progress}%"

            # await self.process_table(
            #     "property_info", pdf_files, session, process_property_info_table, property_info_system_prompt, property_info_message_prompt, property_info_all_column_names, task_id, task_status, progress_per_table
            # )
            # current_table_progress += progress_per_table
            # task_status[task_id].progress = int(min(current_table_progress, 95))
            # task_status[task_id].message = f"Processing buyer_data: {task_status[task_id].progress}%"

            # await self.process_tables(
            #     pdf_files, session, process_buyer_data, buyer_data_system_prompt, buyer_data_message_prompt, buyer_names_all_column_names, buyer_desc_all_column_names, task_id, task_status, progress_per_table
            # )
            # current_table_progress += progress_per_table
            # task_status[task_id].progress = int(min(current_table_progress, 95))
            # task_status[task_id].message = f"Processing buyer_addresses: {task_status[task_id].progress}%"

            # await self.process_table(
            #     "buyer_addresses", pdf_files, session, process_buyer_mail_addresses, buyer_mail_address_system_prompt, buyer_mail_address_message_prompt, buyer_mail_address_all_column_names, task_id, task_status, progress_per_table
            # )
            # current_table_progress += progress_per_table
            # task_status[task_id].progress = int(min(current_table_progress, 95))
            # task_status[task_id].message = f"Processing seller_names: {task_status[task_id].progress}%"

            # await self.process_table(
            #     "seller_names", pdf_files, session, process_seller_names, seller_names_system_prompt, seller_names_message_prompt, seller_names_all_column_names, task_id, task_status, progress_per_table
            # )
            # current_table_progress += progress_per_table
            # task_status[task_id].progress = int(min(current_table_progress, 95))
            # task_status[task_id].message = f"Processing borrower_names: {task_status[task_id].progress}%"

            await self.process_table(
                "borrower_names", pdf_files, session, process_borrower_names, borrower_names_system_prompt, borrower_names_message_prompt, borrower_names_all_column_names, task_id, task_status, progress_per_table
            )
            current_table_progress += progress_per_table
            task_status[task_id].progress = int(min(current_table_progress, 95))
            task_status[task_id].message = f"Processing borrower_addresses: {task_status[task_id].progress}%"

            await self.process_table(
                "borrower_addresses", pdf_files, session, process_borrower_mail_addresses, borrower_mail_address_system_prompt, borrower_mail_address_message_prompt, borrower_mail_address_all_column_names, task_id, task_status, progress_per_table
            )

        task_status[task_id].progress = 100
        task_status[task_id].message = "All tables processed."

        return results