"""
JSON-based job storage system.
Simple file-based storage for tracking generation jobs.
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# JSON file path
JOBS_FILE = "jobs.json"

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(Enum):
    LOGO = "logo"
    VIDEO = "video"
    BOTH = "both"

def load_jobs() -> Dict[str, Any]:
    """Load jobs from JSON file."""
    try:
        if os.path.exists(JOBS_FILE):
            with open(JOBS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"jobs": []}
    except Exception as e:
        print(f"Warning: Could not load jobs file: {e}")
        return {"jobs": []}

def save_jobs(jobs_data: Dict[str, Any]) -> bool:
    """Save jobs to JSON file."""
    try:
        with open(JOBS_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving jobs file: {e}")
        return False

def create_job(job_id: str, prompt: str, job_type: JobType, user_id: str = "default") -> bool:
    """Create a new generation job."""
    try:
        jobs_data = load_jobs()

        new_job = {
            "job_id": job_id,
            "prompt": prompt,
            "job_type": job_type.value,
            "status": JobStatus.PENDING.value,
            "logo_url": None,
            "video_url": None,
            "error_message": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "progress": 0,
            "user_id": user_id
        }

        jobs_data["jobs"].insert(0, new_job)  # Add to beginning
        return save_jobs(jobs_data)
    except Exception as e:
        print(f"Failed to create job: {e}")
        return False

def update_job_status(job_id: str, status: JobStatus, progress: int = None,
                     logo_url: str = None, video_url: str = None,
                     error_message: str = None) -> bool:
    """Update job status and optionally progress/results."""
    try:
        jobs_data = load_jobs()

        # Find the job
        job_index = -1
        for i, job in enumerate(jobs_data["jobs"]):
            if job["job_id"] == job_id:
                job_index = i
                break

        if job_index == -1:
            return False

        job = jobs_data["jobs"][job_index]

        # Update fields
        job["status"] = status.value

        if progress is not None:
            job["progress"] = progress

        if logo_url is not None:
            job["logo_url"] = logo_url

        if video_url is not None:
            job["video_url"] = video_url

        if error_message is not None:
            job["error_message"] = error_message

        # Add timestamps
        if status == JobStatus.PROCESSING:
            job["started_at"] = datetime.now().isoformat()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            job["completed_at"] = datetime.now().isoformat()
            if progress is None:  # Set to 100% if completed
                job["progress"] = 100

        return save_jobs(jobs_data)
    except Exception as e:
        print(f"Failed to update job: {e}")
        return False

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job details by ID."""
    try:
        jobs_data = load_jobs()
        for job in jobs_data["jobs"]:
            if job["job_id"] == job_id:
                return job
        return None
    except Exception as e:
        print(f"Failed to get job: {e}")
        return None

def get_user_jobs(user_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
    """Get all jobs for a user."""
    try:
        jobs_data = load_jobs()
        user_jobs = []

        for job in jobs_data["jobs"]:
            if job["user_id"] == user_id:
                user_jobs.append(job)
                if len(user_jobs) >= limit:
                    break

        return user_jobs
    except Exception as e:
        print(f"Failed to get user jobs: {e}")
        return []

def get_pending_jobs() -> List[Dict[str, Any]]:
    """Get all pending/processing jobs."""
    try:
        jobs_data = load_jobs()
        pending_jobs = []

        for job in jobs_data["jobs"]:
            if job["status"] in [JobStatus.PENDING.value, JobStatus.PROCESSING.value]:
                pending_jobs.append(job)

        return pending_jobs
    except Exception as e:
        print(f"Failed to get pending jobs: {e}")
        return []

def delete_job(job_id: str) -> bool:
    """Delete a job from storage."""
    try:
        jobs_data = load_jobs()

        # Remove the job
        jobs_data["jobs"] = [job for job in jobs_data["jobs"] if job["job_id"] != job_id]

        return save_jobs(jobs_data)
    except Exception as e:
        print(f"Failed to delete job: {e}")
        return False

# Initialize on import
print("JSON job storage system initialized")