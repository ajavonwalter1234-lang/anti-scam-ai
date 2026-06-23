import os
import time
import random
import logging
from celery import Celery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Celery configuration
# Using environment variables for Redis URL to follow 12-factor app principles
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(bind=True, name="tasks.generate_media")
def generate_media(self, prompt: str, gen_type: str, aspect_ratio: str):
    """
    Simulates a long-running AI generation task for images or videos.
    Provides granular progress updates via Celery's custom states.
    """
    logger.info(f"Task {self.request.id}: Starting {gen_type} generation for prompt: '{prompt}'")

    try:
        total_steps = 5  # Reduced steps for demonstration, but still simulates duration
        for i in range(total_steps):
            # Simulate heavy computation
            sleep_time = random.uniform(2, 4)
            time.sleep(sleep_time)

            # Calculate progress percentage
            progress = int(((i + 1) / total_steps) * 100)

            # Update task state with custom progress metadata
            # 'PROCESSING' is a custom state we use to indicate active work
            self.update_state(
                state="PROCESSING",
                meta={
                    "progress": progress,
                    "status": f"Rendering {gen_type} frames... {progress}%",
                    "step": i + 1,
                    "total_steps": total_steps
                }
            )
            logger.info(f"Task {self.request.id} progress: {progress}%")

        # Simulate a successful result after finishing all steps
        file_extension = "mp4" if gen_type == "video" else "png"
        random_hash = os.urandom(8).hex()
        simulated_url = f"https://cdn.ai-gen.com/outputs/{random_hash}.{file_extension}"

        logger.info(f"Task {self.request.id}: Generation completed. URL: {simulated_url}")

        return {
            "status": "SUCCESS",
            "url": simulated_url,
            "prompt": prompt,
            "gen_type": gen_type,
            "aspect_ratio": aspect_ratio,
            "completed_at": time.time()
        }

    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}")
        # Re-raise to let Celery handle the task failure state
        raise e
