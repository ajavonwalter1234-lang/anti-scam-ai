import logging
from typing import Optional, Any
from enum import Enum
from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field, ConfigDict
from celery.result import AsyncResult

from tasks import celery_app, generate_media

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Image & Video Generation API",
    description="Asynchronous backend for AI media generation using FastAPI, Celery, and Redis.",
    version="1.0.0"
)

# --- Pydantic Models ---

class GenerationType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"

class GenerationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str = Field(..., min_length=3, description="The textual prompt for generation.")
    gen_type: GenerationType = Field(..., alias="generation_type", description="Type of media to generate.")
    aspect_ratio: str = Field("16:9", pattern=r"^\d+:\d+$", description="Desired aspect ratio (e.g., 16:9, 1:1).")

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None

# --- Endpoints ---

@app.post("/api/v1/generate", status_code=status.HTTP_202_ACCEPTED, response_model=TaskStatusResponse)
async def generate_endpoint(request: GenerationRequest):
    """
    Triggers a background generation task.
    Returns 202 Accepted with the task ID.
    """
    try:
        # Push task to Celery
        task = generate_media.delay(
            prompt=request.prompt,
            gen_type=request.gen_type,
            aspect_ratio=request.aspect_ratio
        )
        logger.info(f"Triggered task {task.id} for prompt: {request.prompt}")

        return TaskStatusResponse(
            task_id=task.id,
            status="PENDING",
            progress=0
        )
    except Exception as e:
        logger.error(f"Failed to trigger task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not queue generation task."
        )

@app.get("/api/v1/status/{task_id}", response_model=TaskStatusResponse)
async def get_status_endpoint(task_id: str):
    """
    Polls the status of a specific generation task.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(
        task_id=task_id,
        status=task_result.state,
        progress=0
    )

    if task_result.state == "PENDING":
        # Task is in the queue but not yet started
        response.status = "PENDING"
    elif task_result.state == "PROCESSING":
        # Custom state set in tasks.py during update_state
        response.status = "PROCESSING"
        response.progress = task_result.info.get("progress", 0)
    elif task_result.state == "SUCCESS":
        # Task completed successfully
        response.status = "SUCCESS"
        response.progress = 100
        response.result = task_result.result
    elif task_result.state == "FAILURE":
        # Task failed
        response.status = "FAILED"
        response.error = str(task_result.info)
    elif task_result.state == "STARTED":
        # Celery's built-in state if task_track_started=True
        response.status = "STARTED"
        response.progress = 5 # Initial progress

    return response

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "AI Generation API is running.", "docs": "/docs"}
