"""
File Manager Service

Handles temporary file management and cleanup.
"""

import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class JobInfo:
    """Information about a compression/conversion job."""

    job_id: str
    created_at: datetime
    temp_dir: str
    output_file: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    progress: int = 0
    message: str = ""
    original_filename: str = ""


class FileManager:
    """Manages temporary files and job tracking."""

    def __init__(self):
        self.config = get_config()
        self._jobs: dict[str, JobInfo] = {}
        self._lock = Lock()

        # Use configured temp directory or system temp
        temp_dir = self.config.upload.temp_directory
        if temp_dir:
            self._base_temp_dir = Path(temp_dir)
            self._base_temp_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._base_temp_dir = Path(tempfile.gettempdir()) / "pdf-compression"
            self._base_temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"File manager initialized. Temp directory: {self._base_temp_dir}")

    def create_job(self, original_filename: str = "") -> JobInfo:
        """Create a new job with temporary directory."""
        job_id = str(uuid.uuid4())
        job_dir = self._base_temp_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        job = JobInfo(
            job_id=job_id,
            created_at=datetime.now(),
            temp_dir=str(job_dir),
            original_filename=original_filename,
        )

        with self._lock:
            self._jobs[job_id] = job

        logger.debug(f"Created job: {job_id}")
        return job

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job information by ID."""
        with self._lock:
            return self._jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> Optional[JobInfo]:
        """Update job information."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                if status is not None:
                    job.status = status
                if progress is not None:
                    job.progress = progress
                if message is not None:
                    job.message = message
                if output_file is not None:
                    job.output_file = output_file
                logger.debug(f"Updated job {job_id}: status={job.status}, progress={job.progress}")
        return job

    def get_job_file_path(self, job_id: str, filename: str) -> str:
        """Get full path for a file in job's temp directory."""
        job = self.get_job(job_id)
        if job:
            return str(Path(job.temp_dir) / filename)
        raise ValueError(f"Job not found: {job_id}")

    def save_uploaded_file(
        self,
        job_id: str,
        file_content: bytes,
        filename: str,
    ) -> str:
        """Save uploaded file to job's temp directory."""
        file_path = self.get_job_file_path(job_id, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        logger.debug(f"Saved uploaded file: {file_path}")
        return file_path

    def cleanup_job(self, job_id: str) -> None:
        """Clean up job's temporary files."""
        with self._lock:
            job = self._jobs.pop(job_id, None)
            if job and os.path.exists(job.temp_dir):
                shutil.rmtree(job.temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up job: {job_id}")

    def cleanup_old_jobs(self) -> int:
        """Clean up jobs older than configured max age."""
        if not self.config.cleanup.enabled:
            return 0

        max_age = timedelta(hours=self.config.cleanup.max_age_hours)
        cutoff = datetime.now() - max_age
        cleaned = 0

        with self._lock:
            jobs_to_clean = [
                job_id
                for job_id, job in self._jobs.items()
                if job.created_at < cutoff
            ]

        for job_id in jobs_to_clean:
            self.cleanup_job(job_id)
            cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} old jobs")

        return cleaned

    def get_output_file(self, job_id: str) -> Optional[str]:
        """Get the output file path for a completed job."""
        job = self.get_job(job_id)
        if job and job.output_file and os.path.exists(job.output_file):
            return job.output_file
        return None


# Singleton instance
_file_manager: Optional[FileManager] = None


def get_file_manager() -> FileManager:
    """Get file manager singleton instance."""
    global _file_manager
    if _file_manager is None:
        _file_manager = FileManager()
    return _file_manager
