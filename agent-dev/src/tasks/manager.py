from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import networkx as nx
from datetime import datetime
from .state_machine import TaskStateMachine
from .models import Task, TaskDependency, TaskStatus


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_graph = nx.DiGraph()
        self.state_machine = TaskStateMachine()
        self.task_counter = 0
        
    def create_tasks_from_prd(self, prd: Dict[str, Any]) -> List[Task]:
        """Create granular tasks from PRD"""
        # This would use LLM to break down PRD into tasks
        # For now, return mock tasks
        
        tasks = []
        
        # Example task generation logic
        development_tasks = [
            Task(
                id=f"TASK-{self.task_counter + 1}",
                description="Set up project structure and basic configuration",
                target_files=["package.json", "README.md", "src/"],
                dependencies=[],
                status=TaskStatus.PENDING,
                priority=1,
                estimated_hours=2
            ),
            Task(
                id=f"TASK-{self.task_counter + 2}",
                description="Implement core module with basic functionality",
                target_files=["src/core.py", "src/utils.py"],
                dependencies=["TASK-1"],
                status=TaskStatus.PENDING,
                priority=2,
                estimated_hours=4
            ),
            Task(
                id=f"TASK-{self.task_counter + 3}",
                description="Add unit tests for core functionality",
                target_files=["tests/test_core.py", "tests/test_utils.py"],
                dependencies=["TASK-2"],
                status=TaskStatus.PENDING,
                priority=3,
                estimated_hours=3
            )
        ]
        
        self.task_counter += len(development_tasks)
        
        for task in development_tasks:
            self.add_task(task)
            
        return development_tasks
    
    def add_task(self, task: Task) -> None:
        """Add a task to the manager"""
        self.tasks[task.id] = task
        self.task_graph.add_node(task.id, task=task)
        
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                self.task_graph.add_edge(dep_id, task.id)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (all dependencies satisfied)"""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                dependencies_met = all(
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.tasks
                )
                
                if dependencies_met:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status using state machine"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if self.state_machine.can_transition(task.status, status):
            task.status = status
            task.updated_at = datetime.now()
            
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
            elif status == TaskStatus.IN_PROGRESS:
                task.started_at = datetime.now()
            
            return True
        
        return False
    
    def get_task_dependencies(self, task_id: str) -> List[Task]:
        """Get all dependencies for a task"""
        if task_id not in self.task_graph:
            return []
        
        dependencies = []
        for dep_id in self.task_graph.predecessors(task_id):
            if dep_id in self.tasks:
                dependencies.append(self.tasks[dep_id])
        
        return dependencies
    
    def get_dependent_tasks(self, task_id: str) -> List[Task]:
        """Get all tasks that depend on this task"""
        if task_id not in self.task_graph:
            return []
        
        dependents = []
        for dep_id in self.task_graph.successors(task_id):
            if dep_id in self.tasks:
                dependents.append(self.tasks[dep_id])
        
        return dependents
    
    def get_critical_path(self) -> List[Task]:
        """Get the critical path of tasks"""
        try:
            # Simple critical path calculation
            # In production, you'd want a more sophisticated algorithm
            longest_path = []
            max_duration = 0
            
            for task in self.tasks.values():
                path = self._get_task_path(task.id)
                duration = sum(t.estimated_hours for t in path)
                
                if duration > max_duration:
                    max_duration = duration
                    longest_path = path
            
            return longest_path
        except:
            return list(self.tasks.values())
    
    def _get_task_path(self, task_id: str) -> List[Task]:
        """Get path of tasks leading to this task"""
        path = []
        
        def traverse(current_id: str):
            if current_id in self.tasks:
                task = self.tasks[current_id]
                path.append(task)
                
                for dep_id in task.dependencies:
                    traverse(dep_id)
        
        traverse(task_id)
        return list(reversed(path))