from fastapi import APIRouter, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from app.services.title_extractor import TitleExtractor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/api/title-extraction",
    tags=["title-extraction"],
)

# Get LLM credentials from environment variables
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', "https://llmfoundry.straive.com/gemini/v1beta/models/gemini-2.0-flash-001:generateContent")
LLM_TOKEN = os.getenv('LLM_FOUNDRY_TOKEN')

# Dictionary to store background task status
task_status = {}

async def extract_titles_background(task_id, input_dir, output_file, batch_size):
    """Background task to extract titles from PDFs in a directory"""
    try:
        task_status[task_id] = {"status": "running", "progress": 0, "message": "Starting extraction..."}
        
        extractor = TitleExtractor(LLM_ENDPOINT, LLM_TOKEN)
        
        # Update status
        task_status[task_id] = {"status": "running", "progress": 5, "message": "Initialized extractor..."}

        # Get list of PDF files
        pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
                     if f.lower().endswith('.pdf')]

        if not pdf_files:
            task_status[task_id] = {"status": "failed", "progress": 0, "message": f"No PDF files found in {input_dir}"}
            return

        # Run the extraction
        results = await extractor.extract_titles_from_directory(pdf_files, output_file, batch_size, task_id, task_status)

        # Update status with completion
        task_status[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": f"Extraction completed. Processed {len(results)} files."
        }
    except Exception as e:
        task_status[task_id] = {"status": "failed", "progress": 0, "message": f"Error: {str(e)}"}

@router.post("/extract-titles")
async def extract_titles(
    background_tasks: BackgroundTasks,
    input_dir: str = Form(...),
    output_file: str = Form(...),
    batch_size: int = Form(5)
):
    """
    Extract titles from all PDF files in the input directory using LLM.
    """
    # Validate directories
    if not os.path.isdir(input_dir):
        raise HTTPException(status_code=400, detail=f"Input path is not a directory: {input_dir}")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Check if LLM token is available
    if not LLM_TOKEN:
        raise HTTPException(status_code=500, detail="LLM token not configured. Please set the LLM_FOUNDRY_TOKEN environment variable.")

    # Generate a task ID
    task_id = f"task_{len(task_status) + 1}"

    # Start the background task
    background_tasks.add_task(
        extract_titles_background,
        task_id,
        input_dir,
        output_file,
        batch_size
    )

    return JSONResponse(content={
        "status": "started",
        "message": "Title extraction started in the background",
        "task_id": task_id
    })

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a background title extraction task.
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail=f"Task ID not found: {task_id}")

    return JSONResponse(content=task_status[task_id])