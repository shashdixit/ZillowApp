from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from app.services.converter import TifToPdfConverter
import os

router = APIRouter(
    prefix="/api/conversion",
    tags=["conversion"],
)

@router.post("/convert-directory")
async def convert_directory(input_dir: str = Form(...), output_dir: str = Form(...)):
    """
    Convert all TIF files in the input directory to PDF files in the output directory.
    """
    # Validate directories
    if not os.path.exists(input_dir):
        raise HTTPException(status_code=400, detail=f"Input directory does not exist: {input_dir}")
    
    if not os.path.isdir(input_dir):
        raise HTTPException(status_code=400, detail=f"Input path is not a directory: {input_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Perform conversion
    stats = TifToPdfConverter.convert_directory(input_dir, output_dir)
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Conversion completed. Converted {stats['converted_files']} files, skipped {stats['skipped_files']} files, failed {stats['failed_files']} files.",
        "stats": stats
    })