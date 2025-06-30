from fastapi import APIRouter, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from app.services.table_extraction_service import TableExtractionService
from typing import Optional, List, Dict

router = APIRouter(
    prefix="/api/table-extraction",
    tags=["table-extraction"],
)

# Data Models (Optional, but Recommended)
from pydantic import BaseModel

class ExtractionTaskStatus(BaseModel):
    status: str
    progress: int  # Changed to int
    message: str
    results: Optional[List[List[str]]] = None

# Dictionary to store background task status
task_status: Dict[str, ExtractionTaskStatus] = {}

async def extract_tables_background(task_id: str, input_dir: str, output_dir: str):
    """Background task to extract data and fill tables from PDFs in a directory."""
    try:
        task_status[task_id] = ExtractionTaskStatus(status="running", progress=0, message="Starting extraction...")

        table_extraction_service = TableExtractionService()

        # Update status
        task_status[task_id].status = "running"
        task_status[task_id].progress = 5
        task_status[task_id].message = "Initialized table extraction service..."

        # Run the extraction
        await table_extraction_service.extract_all_tables(task_id, task_status, input_dir, output_dir)

        # Update status with completion
        task_status[task_id].status = "completed"
        task_status[task_id].progress = 100
        task_status[task_id].message = f"Extraction completed. Check output directory for results."

    except Exception as e:
        task_status[task_id].status = "failed"
        task_status[task_id].progress = 0
        task_status[task_id].message = f"Error: {str(e)}"

@router.post("/extract-all")
async def extract_all_tables(
    background_tasks: BackgroundTasks,
    input_dir: str = Form(...),
    output_dir: str = Form(...)
):
    """
    Extract data and fill tables from all PDF files in the input directory.
    """
    # Validate directories
    if not os.path.isdir(input_dir):
        raise HTTPException(status_code=400, detail=f"Input path is not a directory: {input_dir}")

    if not os.path.isdir(output_dir):
        raise HTTPException(status_code=400, detail=f"Output path is not a directory: {output_dir}")

    # Generate a task ID
    task_id = f"task_{len(task_status) + 1}"

    # Start the background task
    background_tasks.add_task(
        extract_tables_background,
        task_id,
        input_dir,
        output_dir
    )

    return JSONResponse(content={
        "status": "started",
        "message": "Table extraction started in the background",
        "task_id": task_id
    })

@router.get("/task-status/{task_id}", response_model=ExtractionTaskStatus)
async def get_task_status(task_id: str):
    """
    Get the status of a background table extraction task.
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail=f"Task ID not found: {task_id}")

    return task_status[task_id]