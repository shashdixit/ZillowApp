from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from app.services.ocr_service import OCRProcessor
import os

router = APIRouter(
    prefix="/api/ocr",
    tags=["ocr"],
)

@router.post("/process-directory")
async def process_directory(input_dir: str = Form(...), output_dir: str = Form(...), file_types: str = Form(None)):
    """
    Process all files in the input directory with OCR and save text files to the output directory.
    """
    # Validate directories    
    if not os.path.isdir(input_dir):
        raise HTTPException(status_code=400, detail=f"Input path is not a directory: {input_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse file types if provided
    file_type_list = None
    if file_types:
        file_type_list = [ext.strip().lower() for ext in file_types.split(',')]
    
    # Perform OCR processing
    stats = OCRProcessor.process_directory(input_dir, output_dir, file_type_list)
    
    return JSONResponse(content={
        "status": "success",
        "message": f"OCR completed. Processed {stats['processed_files']} files, skipped {stats['skipped_files']} files, failed {stats['failed_files']} files.",
        "stats": stats
    })