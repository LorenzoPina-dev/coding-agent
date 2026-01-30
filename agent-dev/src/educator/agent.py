from typing import Dict, Any, List
from pydantic import BaseModel, Field
import json
from datetime import datetime
from ..utils.llm import LLMClient
from ..config.prompts import PromptManager
from ..builder.agent import CodeFile
from ..reviewer.agent import ReviewResult


class Explanation(BaseModel):
    title: str
    summary: str
    key_concepts: List[str]
    implementation_details: str
    design_decisions: List[str]
    alternatives_considered: List[str]
    best_practices_applied: List[str]
    learning_points: List[str]


class EducatorAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.explanations: Dict[str, Explanation] = {}
        
    def explain_implementation(
        self,
        task_id: str,
        code_files: List[CodeFile],
        review_results: List[ReviewResult],
        context: Dict[str, Any]
    ) -> Explanation:
        """Explain what was implemented and why"""
        
        explanation_prompt = self.prompt_manager.get_prompt(
            "educator",
            "implementation_explanation",
            task_id=task_id,
            code_files=json.dumps([f.dict() for f in code_files], indent=2),
            review_results=json.dumps([r.dict() for r in review_results], indent=2),
            context=json.dumps(context, indent=2)
        )
        
        response = self.llm_client.generate(
            prompt=explanation_prompt,
            response_format={"type": "json_object"}
        )
        
        explanation_data = json.loads(response)
        
        explanation = Explanation(
            title=explanation_data.get("title", f"Explanation for {task_id}"),
            summary=explanation_data.get("summary", ""),
            key_concepts=explanation_data.get("key_concepts", []),
            implementation_details=explanation_data.get("implementation_details", ""),
            design_decisions=explanation_data.get("design_decisions", []),
            alternatives_considered=explanation_data.get("alternatives_considered", []),
            best_practices_applied=explanation_data.get("best_practices_applied", []),
            learning_points=explanation_data.get("learning_points", [])
        )
        
        self.explanations[task_id] = explanation
        return explanation
    
    def generate_learning_material(self, explanation: Explanation) -> Dict[str, Any]:
        """Generate learning materials from explanation"""
        
        learning_prompt = self.prompt_manager.get_prompt(
            "educator",
            "learning_material",
            explanation=json.dumps(explanation.dict(), indent=2)
        )
        
        response = self.llm_client.generate(
            prompt=learning_prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response)
    
    def get_simplified_explanation(self, explanation: Explanation) -> str:
        """Get a simplified explanation for non-technical stakeholders"""
        
        simple_prompt = self.prompt_manager.get_prompt(
            "educator",
            "simplified_explanation",
            title=explanation.title,
            summary=explanation.summary,
            key_concepts=", ".join(explanation.key_concepts[:3])
        )
        
        return self.llm_client.generate(prompt=simple_prompt)