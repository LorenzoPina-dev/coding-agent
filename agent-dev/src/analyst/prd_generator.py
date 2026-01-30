"""
PRD Generator module
"""

from typing import Dict, Any
import json
from src.utils.llm import LLMClient  # Aggiungi se serve
from src.config.prompts import PromptManager  # Aggiungi se serve


class PRDGenerator:
    """Generate PRD from discovery data"""
    
    def __init__(self, llm_client: LLMClient = None, prompt_manager: PromptManager = None):
        """Initialize PRD generator"""
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
    
    def generate(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRD from discovery data"""
        
        # Se abbiamo LLM, usalo per generare PRD
        if self.llm_client and self.prompt_manager:
            return self._generate_with_llm(discovery_data)
        else:
            # Altrimenti usa template semplice
            return self._generate_simple(discovery_data)
    
    def _generate_with_llm(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRD using LLM"""
        try:
            prompt = f"""
            Generate a Product Requirements Document (PRD) based on this discovery data:
            
            {json.dumps(discovery_data, indent=2)}
            
            Return a JSON with:
            - title: Project title
            - version: Version number
            - overview: Brief overview
            - objectives: List of objectives
            - features: List of features
            - timeline: Development timeline
            """
            
            response = self.llm_client.generate(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback se la risposta non è JSON valido
                return self._generate_simple(discovery_data)
                
        except Exception:
            return self._generate_simple(discovery_data)
    
    def _generate_simple(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simple PRD from template"""
        return {
            "title": discovery_data.get("project_name", "Untitled Project"),
            "version": "1.0.0",
            "overview": "Product Requirements Document",
            "sections": [
                {
                    "title": "Introduction",
                    "content": "Project overview and purpose"
                },
                {
                    "title": "Objectives", 
                    "content": "Main goals and objectives"
                },
                {
                    "title": "Requirements",
                    "content": "Functional and non-functional requirements"
                }
            ]
        }