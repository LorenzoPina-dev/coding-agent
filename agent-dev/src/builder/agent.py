from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
from datetime import datetime
from ..utils.llm import LLMClient
from ..config.prompts import PromptManager
from ..tasks.models import Task


class CodeFile(BaseModel):
    filename: str
    code: str
    language: str
    dependencies: List[str] = Field(default_factory=list)
    tests: Optional[str] = None
    documentation: Optional[str] = None
    confidence_score: float = Field(ge=0.0, le=1.0)


class BuildResult(BaseModel):
    task_id: str
    files: List[CodeFile]
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    build_time: float
    created_at: datetime = Field(default_factory=datetime.now)


class BuilderAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.build_history: List[BuildResult] = []
        
    def build_for_task(self, task: Task, context: Dict[str, Any]) -> BuildResult:
        """Generate code for a specific task"""
        start_time = datetime.now()
        
        try:
            # Prepare build prompt
            build_prompt = self.prompt_manager.get_prompt(
                "builder",
                "code_generation",
                task_description=task.description,
                target_files=", ".join(task.target_files),
                dependencies=", ".join(task.dependencies),
                context=json.dumps(context, indent=2)
            )
            
            # Generate code
            response = self.llm_client.generate(
                prompt=build_prompt,
                system_prompt=self.prompt_manager.get_prompt("builder", "system_prompt"),
                response_format={"type": "json_object"}
            )
            
            # Parse response
            code_data = json.loads(response)
            files = []
            
            for file_data in code_data.get("files", []):
                file = CodeFile(
                    filename=file_data["filename"],
                    code=file_data["code"],
                    language=file_data.get("language", self._detect_language(file_data["filename"])),
                    dependencies=file_data.get("dependencies", []),
                    tests=file_data.get("tests"),
                    documentation=file_data.get("documentation"),
                    confidence_score=file_data.get("confidence_score", 0.8)
                )
                files.append(file)
            
            # Calculate build time
            build_time = (datetime.now() - start_time).total_seconds()
            
            result = BuildResult(
                task_id=task.id,
                files=files,
                success=True,
                build_time=build_time
            )
            
            self.build_history.append(result)
            return result
            
        except Exception as e:
            build_time = (datetime.now() - start_time).total_seconds()
            
            result = BuildResult(
                task_id=task.id,
                files=[],
                success=False,
                error_message=str(e),
                build_time=build_time
            )
            
            self.build_history.append(result)
            return result
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rs': 'rust',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        for ext, lang in extensions.items():
            if filename.endswith(ext):
                return lang
        
        return 'text'
    
    def validate_code(self, code_file: CodeFile) -> Dict[str, Any]:
        """Validate generated code"""
        validation_prompt = self.prompt_manager.get_prompt(
            "builder",
            "code_validation",
            filename=code_file.filename,
            code=code_file.code,
            language=code_file.language
        )
        
        response = self.llm_client.generate(
            prompt=validation_prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response)
    
    def generate_tests(self, code_file: CodeFile) -> Optional[str]:
        """Generate unit tests for code file"""
        if not code_file.tests:
            test_prompt = self.prompt_manager.get_prompt(
                "builder",
                "test_generation",
                filename=code_file.filename,
                code=code_file.code,
                language=code_file.language
            )
            
            response = self.llm_client.generate(prompt=test_prompt)
            return response
        
        return code_file.tests