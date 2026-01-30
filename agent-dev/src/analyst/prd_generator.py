"""
AI-Optimized PRD Generator - creates PRDs specifically for AI agents
"""

from typing import Dict, Any, List
import json
from datetime import datetime
from src.utils.llm import LLMClient


class AIOptimizedPRDGenerator:
    """Generate PRDs optimized for AI agent consumption"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate(self, discovery_summary: str) -> Dict[str, Any]:
        """Generate AI-optimized PRD"""
        
        prd_prompt = f"""Create a Product Requirements Document optimized for AI development agents.

PROJECT SUMMARY:
{discovery_summary}

Generate a PRD with this EXACT JSON structure:

{{
  "metadata": {{
    "prd_id": "auto-generated",
    "version": "1.0.0",
    "created_at": "timestamp",
    "optimized_for": "ai_agents",
    "complexity_score": 0.0-1.0
  }},
  "project": {{
    "name": "project name",
    "description": "brief description",
    "problem_statement": "what problem this solves",
    "value_proposition": "unique value"
  }},
  "requirements": {{
    "functional": [
      {{"id": "FUNC-1", "description": "feature", "priority": "high/medium/low", "acceptance_criteria": ["criteria"]}}
    ],
    "non_functional": [
      {{"id": "NF-1", "type": "performance/security/etc", "requirement": "specific requirement"}}
    ]
  }},
  "architecture": {{
    "pattern": "microservices/monolith/serverless/etc",
    "components": [
      {{"name": "component", "purpose": "what it does", "tech_stack": ["technologies"]}}
    ],
    "data_flow": "description of data flow"
  }},
  "development": {{
    "tech_stack": {{
      "backend": ["technologies"],
      "frontend": ["technologies"],
      "database": ["technologies"],
      "infrastructure": ["technologies"]
    }},
    "dependencies": [
      {{"name": "dependency", "version": "version", "purpose": "why needed"}}
    ]
  }},
  "api_specification": {{
    "style": "REST/GraphQL/gRPC",
    "endpoints": [
      {{"method": "GET/POST/etc", "path": "/endpoint", "purpose": "what it does", "auth_required": true/false}}
    ]
  }},
  "data_models": [
    {{"name": "ModelName", "fields": [{{"name": "field", "type": "type", "required": true/false}}]}}
  ],
  "testing": {{
    "strategy": "testing approach",
    "coverage_goal": 0.85,
    "test_types": ["unit", "integration", "e2e"]
  }},
  "deployment": {{
    "environment": ["dev", "staging", "prod"],
    "infrastructure": "description",
    "scaling_strategy": "how it scales"
  }},
  "ai_agent_instructions": {{
    "coding_guidelines": ["specific guidelines for AI agents"],
    "patterns_to_use": ["design patterns"],
    "patterns_to_avoid": ["anti-patterns"],
    "quality_requirements": ["specific quality requirements"]
  }}
}}

Make it detailed, technical, and actionable for AI development agents."""

        try:
            response = self.llm_client.generate(prd_prompt)
            
            # Parse JSON response
            prd_data = json.loads(response)
            
            # Add timestamp if not present
            if "metadata" in prd_data and "created_at" in prd_data["metadata"]:
                if prd_data["metadata"]["created_at"] == "timestamp":
                    prd_data["metadata"]["created_at"] = datetime.now().isoformat()
            
            return prd_data
            
        except json.JSONDecodeError:
            # Fallback to template if JSON parsing fails
            return self._create_fallback_prd(discovery_summary)
    
    def _create_fallback_prd(self, summary: str) -> Dict[str, Any]:
        """Create a fallback PRD if JSON generation fails"""
        return {
            "metadata": {
                "prd_id": f"PRD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "optimized_for": "ai_agents",
                "complexity_score": 0.7
            },
            "project": {
                "name": "Extracted from conversation",
                "description": summary[:200] + "..." if len(summary) > 200 else summary,
                "problem_statement": "To be detailed by development agents",
                "value_proposition": "Automated development system"
            },
            "requirements": {
                "functional": [
                    {
                        "id": "FUNC-1",
                        "description": "Core functionality based on conversation",
                        "priority": "high",
                        "acceptance_criteria": ["Works as described in conversation"]
                    }
                ],
                "non_functional": [
                    {
                        "id": "NF-1",
                        "type": "performance",
                        "requirement": "Response time under 200ms"
                    }
                ]
            },
            "development": {
                "tech_stack": {
                    "backend": ["Python", "FastAPI"],
                    "database": ["PostgreSQL"],
                    "infrastructure": ["Docker"]
                }
            },
            "ai_agent_instructions": {
                "coding_guidelines": [
                    "Follow PEP 8",
                    "Include comprehensive error handling",
                    "Write unit tests",
                    "Add documentation"
                ]
            }
        }
    
    def generate_prd_for_humans(self, ai_prd: Dict[str, Any]) -> str:
        """Convert AI-optimized PRD to human-readable format"""
        human_prompt = f"""Convert this AI-optimized PRD into a human-readable document:

{json.dumps(ai_prd, indent=2)}

Format as a clean, professional document with:
1. Title and version
2. Executive summary
3. Detailed requirements
4. Architecture overview
5. Development plan
6. Deployment strategy

Use markdown formatting with clear sections."""

        return self.llm_client.generate(human_prompt)