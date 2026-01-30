"""
Task state machine
"""

from enum import Enum
from typing import Dict, Set

# CORREZIONE: TaskStatus, non TaskState
from .models import TaskStatus  # ← AGGIUNGI QUESTA RIGA


class TaskStateMachine:
    """State machine for task status transitions"""
    
    def __init__(self):
        # Define valid transitions
        self.transitions: Dict[TaskStatus, Set[TaskStatus]] = {
            TaskStatus.PENDING: {
                TaskStatus.IN_PROGRESS,
            },
            TaskStatus.IN_PROGRESS: {
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
            },
            TaskStatus.FAILED: {
                TaskStatus.PENDING,
                TaskStatus.IN_PROGRESS,
            },
            TaskStatus.COMPLETED: set()  # Terminal state
        }
    
    def can_transition(self, from_state: TaskStatus, to_state: TaskStatus) -> bool:
        """Check if transition is valid"""
        return to_state in self.transitions.get(from_state, set())