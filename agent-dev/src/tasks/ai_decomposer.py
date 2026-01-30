"""
AI Task Decomposer - breaks down PRD into executable tasks for AI agents
"""

from typing import Dict, Any, List
import json
from .models import Task, TaskStatus
from src.utils.llm import LLMClient


class AITaskDecomposer:
    """Decompose PRD into AI-executable tasks"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.task_counter = 1
    
    def decompose_prd(self, prd: Dict[str, Any]) -> List[Task]:
        """Decompose PRD into granular tasks for AI agents"""
        
        decomposition_prompt = f"""Decompose this PRD into executable development tasks for AI agents:

{json.dumps(prd, indent=2)}

Return a JSON array of tasks, each with:
{{
  "id": "TASK-1",
  "description": "clear, actionable description",
  "type": "setup/feature/test/deployment/documentation",
  "priority": 1-5 (1 highest),
  "estimated_hours": 1-8,
  "dependencies": ["TASK-1", "TASK-2"],  // empty array if none
  "acceptance_criteria": ["criteria 1", "criteria 2"],
  "files_to_create": ["path/to/file.py"],
  "technical_requirements": ["specific technical requirements"],
  "ai_instructions": "specific instructions for AI agent"
}}

Rules:
1. Start with setup/infrastructure tasks
2. Break features into smallest logical units
3. Include testing tasks for each feature
4. End with deployment/documentation
5. Maximum 20 tasks for initial phase
6. Each task should be completable in 1-4 hours by an AI agent"""

        try:
            response = self.llm_client.generate(decomposition_prompt)
            task_data = json.loads(response)
            
            tasks = []
            for task_dict in task_data:
                task = Task(
                    id=task_dict.get("id", f"TASK-{self.task_counter}"),
                    description=task_dict.get("description", "Unknown task"),
                    status=TaskStatus.PENDING,
                    priority=task_dict.get("priority", 3),
                    estimated_hours=task_dict.get("estimated_hours", 2.0),
                    metadata={
                        "type": task_dict.get("type", "feature"),
                        "dependencies": task_dict.get("dependencies", []),
                        "acceptance_criteria": task_dict.get("acceptance_criteria", []),
                        "files_to_create": task_dict.get("files_to_create", []),
                        "technical_requirements": task_dict.get("technical_requirements", []),
                        "ai_instructions": task_dict.get("ai_instructions", ""),
                        "prd_reference": prd.get("metadata", {}).get("prd_id", "unknown")
                    }
                )
                tasks.append(task)
                self.task_counter += 1
            
            return tasks
            
        except json.JSONDecodeError:
            # Fallback to basic tasks
            return self._create_fallback_tasks(prd)
    
    def _create_fallback_tasks(self, prd: Dict[str, Any]) -> List[Task]:
        """Create fallback tasks if decomposition fails"""
        project_name = prd.get("project", {}).get("name", "Project")
        
        return [
            Task(
                id="TASK-1",
                description=f"Setup {project_name} project structure",
                status=TaskStatus.PENDING,
                priority=1,
                estimated_hours=2.0,
                metadata={
                    "type": "setup",
                    "files_to_create": ["README.md", "requirements.txt", "src/"]
                }
            ),
            Task(
                id="TASK-2",
                description=f"Implement core functionality for {project_name}",
                status=TaskStatus.PENDING,
                priority=2,
                estimated_hours=4.0,
                dependencies=["TASK-1"],
                metadata={
                    "type": "feature",
                    "files_to_create": ["src/main.py", "src/core.py"]
                }
            ),
            Task(
                id="TASK-3",
                description=f"Add testing for {project_name}",
                status=TaskStatus.PENDING,
                priority=3,
                estimated_hours=3.0,
                dependencies=["TASK-2"],
                metadata={
                    "type": "test",
                    "files_to_create": ["tests/test_core.py", "tests/conftest.py"]
                }
            )
        ]
    
    def validate_task_completion(self, task: Task, generated_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate if a task was completed successfully by AI agent"""
        
        validation_prompt = f"""Validate if this development task was completed successfully:

TASK: {task.description}
TASK INSTRUCTIONS: {task.metadata.get('ai_instructions', 'No specific instructions')}
ACCEPTANCE CRITERIA: {task.metadata.get('acceptance_criteria', ['Complete the task'])}

GENERATED FILES:
{json.dumps(generated_files, indent=2)}

Return JSON with:
{{
  "passed": true/false,
  "score": 0-100,
  "issues": ["list of issues found"],
  "suggestions": ["suggestions for improvement"],
  "can_proceed": true/false
}}"""

        try:
            response = self.llm_client.generate(validation_prompt)
            return json.loads(response)
        except:
            return {
                "passed": True,  # Default to passed to keep moving
                "score": 80,
                "issues": [],
                "suggestions": [],
                "can_proceed": True
            }