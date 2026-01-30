from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
from datetime import datetime
from ..utils.llm import LLMClient
from ..config.prompts import PromptManager
from ..builder.agent import CodeFile


class CodeIssue(BaseModel):
    type: str  # "bug", "security", "performance", "style", "maintainability"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


class ReviewResult(BaseModel):
    task_id: str
    filename: str
    issues: List[CodeIssue] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=1.0)
    passed: bool = False
    review_time: float
    reviewed_at: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(default_factory=list)


class ReviewerAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.review_history: List[ReviewResult] = []
        
    def review_code(self, task_id: str, code_file: CodeFile) -> ReviewResult:
        """Review generated code"""
        start_time = datetime.now()
        
        try:
            review_prompt = self.prompt_manager.get_prompt(
                "reviewer",
                "code_review",
                filename=code_file.filename,
                code=code_file.code,
                language=code_file.language,
                task_id=task_id
            )
            
            response = self.llm_client.generate(
                prompt=review_prompt,
                system_prompt=self.prompt_manager.get_prompt("reviewer", "system_prompt"),
                response_format={"type": "json_object"}
            )
            
            review_data = json.loads(response)
            
            issues = []
            for issue_data in review_data.get("issues", []):
                issue = CodeIssue(
                    type=issue_data.get("type", "style"),
                    severity=issue_data.get("severity", "low"),
                    description=issue_data.get("description", ""),
                    location=issue_data.get("location"),
                    suggestion=issue_data.get("suggestion"),
                    code_snippet=issue_data.get("code_snippet")
                )
                issues.append(issue)
            
            review_time = (datetime.now() - start_time).total_seconds()
            
            # Determine if passed (no critical issues)
            passed = not any(
                issue.severity == "critical" and issue.type in ["bug", "security"]
                for issue in issues
            )
            
            result = ReviewResult(
                task_id=task_id,
                filename=code_file.filename,
                issues=issues,
                overall_score=review_data.get("overall_score", 0.8),
                passed=passed,
                review_time=review_time,
                recommendations=review_data.get("recommendations", [])
            )
            
            self.review_history.append(result)
            return result
            
        except Exception as e:
            review_time = (datetime.now() - start_time).total_seconds()
            
            result = ReviewResult(
                task_id=task_id,
                filename=code_file.filename,
                issues=[CodeIssue(
                    type="system",
                    severity="critical",
                    description=f"Review failed: {str(e)}"
                )],
                overall_score=0.0,
                passed=False,
                review_time=review_time
            )
            
            self.review_history.append(result)
            return result
    
    def get_review_summary(self, task_id: str) -> Dict[str, Any]:
        """Get summary of reviews for a task"""
        task_reviews = [r for r in self.review_history if r.task_id == task_id]
        
        if not task_reviews:
            return {}
        
        total_issues = sum(len(review.issues) for review in task_reviews)
        critical_issues = sum(
            1 for review in task_reviews
            for issue in review.issues
            if issue.severity == "critical"
        )
        
        avg_score = sum(review.overall_score for review in task_reviews) / len(task_reviews)
        
        return {
            "total_files": len(task_reviews),
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "average_score": avg_score,
            "all_passed": all(review.passed for review in task_reviews)
        }