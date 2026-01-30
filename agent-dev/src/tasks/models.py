"""
Task models for the software development agent
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskDependency(BaseModel):
    """Dependency between tasks"""
    task_id: str
    type: str = "blocks"  # "blocks", "requires", "related_to"
    description: Optional[str] = None


class Task(BaseModel):
    """A development task"""
    id: str
    description: str
    target_files: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    estimated_hours: float = 1.0
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Metadata
    assignee: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class TaskUpdate(BaseModel):
    """Update for a task"""
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    notes: Optional[str] = None
    assignee: Optional[str] = None
    confidence_score: Optional[float] = None
    

class TaskFilter(BaseModel):
    """Filter for tasks"""
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None