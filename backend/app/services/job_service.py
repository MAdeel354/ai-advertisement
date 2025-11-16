"""
Background job service for async AI generation.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from ..models import create_job, update_job_status, JobStatus, JobType
from .image_service import generate_logo
from .video_service import generate_ad_video

class JobManager:
    """Manages background generation jobs."""

    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}

    async def start_generation_job(self, prompt: str, generate_video: bool = False,
                                  user_id: str = "default") -> str:
        """Start a new generation job and return job ID."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Determine job type
        job_type = JobType.BOTH if generate_video else JobType.LOGO

        # Create job in database
        if not create_job(job_id, prompt, job_type, user_id):
            raise Exception("Failed to create job")

        # Start background task
        task = asyncio.create_task(self._process_job(job_id, prompt, generate_video))

        self.active_jobs[job_id] = {
            "task": task,
            "prompt": prompt,
            "generate_video": generate_video,
            "user_id": user_id,
            "started_at": asyncio.get_event_loop().time()
        }

        logger.info(f"Started generation job: {job_id} for user: {user_id}")
        return job_id

    async def _process_job(self, job_id: str, prompt: str, generate_video: bool):
        """Process a generation job in background."""
        try:
            # Update status to processing
            update_job_status(job_id, JobStatus.PROCESSING, progress=10)

            logo_url = None
            video_url = None

            # Generate logo (run in threadpool to avoid blocking)
            update_job_status(job_id, JobStatus.PROCESSING, progress=30)
            logger.info(f"Generating logo for job {job_id}")

            try:
                # Run synchronous logo generation in thread pool
                loop = asyncio.get_event_loop()
                logo_url = await loop.run_in_executor(None, generate_logo, prompt)
                update_job_status(job_id, JobStatus.PROCESSING,
                                progress=60, logo_url=logo_url)
                logger.info(f"Logo generated for job {job_id}: {logo_url}")
            except Exception as e:
                logger.error(f"Logo generation failed for job {job_id}: {e}")
                update_job_status(job_id, JobStatus.FAILED, error_message=f"Logo generation failed: {str(e)}")
                return

            # Generate video if requested
            if generate_video:
                update_job_status(job_id, JobStatus.PROCESSING, progress=70)
                logger.info(f"Generating video for job {job_id}")

                try:
                    # Use generated logo as reference if available
                    logo_path = None
                    if logo_url:
                        # Convert URL to file path
                        logo_filename = logo_url.split('/')[-1]
                        logo_path = f"output/{logo_filename}"

                    # Run synchronous video generation in thread pool
                    loop = asyncio.get_event_loop()
                    video_url = await loop.run_in_executor(None, generate_ad_video, prompt, logo_path)
                    # Update with both logo and video URLs to ensure both are saved
                    update_job_status(job_id, JobStatus.PROCESSING,
                                    progress=90, logo_url=logo_url, video_url=video_url)
                    logger.info(f"Video generated for job {job_id}: {video_url}")
                except Exception as e:
                    logger.error(f"Video generation failed for job {job_id}: {e}")
                    # Don't fail the job, just note video generation failed
                    video_url = None

            # Mark job as completed
            update_job_status(job_id, JobStatus.COMPLETED,
                            progress=100, logo_url=logo_url, video_url=video_url)
            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            update_job_status(job_id, JobStatus.FAILED, error_message=str(e))

        finally:
            # Clean up from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current job status."""
        from ..models import get_job
        return get_job(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        if job_id in self.active_jobs:
            job_info = self.active_jobs[job_id]
            job_info["task"].cancel()
            del self.active_jobs[job_id]

            # Update database
            update_job_status(job_id, JobStatus.FAILED,
                           error_message="Job cancelled by user")
            return True
        return False

    def get_active_jobs_count(self) -> int:
        """Get number of currently active jobs."""
        return len(self.active_jobs)

# Global job manager instance
job_manager = JobManager()