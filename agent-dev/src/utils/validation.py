"""
Validation utilities
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool = True
    issues: List[str] = []
    needs_clarification: bool = False
    suggested_questions: List[str] = []


class ResponseValidator:
    """Validator for user responses during discovery"""
    
    def validate_response(
        self, 
        phase: str, 
        response: str, 
        previous_responses: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a user response for a specific phase"""
        result = ValidationResult()
        
        # Check for empty or very short responses
        if not response or len(response.strip()) < 10:
            result.is_valid = False
            result.needs_clarification = True
            result.issues.append("Response is too short or empty")
            result.suggested_questions.append("Could you provide more details?")
            return result
        
        # Phase-specific validations
        if phase == "INTRO":
            # Check if all three questions are answered
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            if len(lines) < 3:
                result.is_valid = False
                result.needs_clarification = True
                result.issues.append("Please answer all three questions")
                result.suggested_questions.append("Could you provide the project name, problem, and type?")
        
        elif phase == "GOALS":
            # Check for specific objectives
            if "objective" not in response.lower() and "goal" not in response.lower():
                result.is_valid = False
                result.needs_clarification = True
                result.issues.append("Please specify clear objectives")
                result.suggested_questions.append("What are the main goals for version 1.0?")
        
        elif phase == "USERS":
            # Check for user mentions
            user_keywords = ["user", "persona", "customer", "client", "audience"]
            if not any(keyword in response.lower() for keyword in user_keywords):
                result.is_valid = False
                result.needs_clarification = True
                result.issues.append("Please specify who will use the system")
                result.suggested_questions.append("Who are the primary users?")
        
        # Check for vague responses
        vague_indicators = [
            "I don't know", "not sure", "maybe", "possibly", 
            "I think", "probably", "kind of", "sort of"
        ]
        
        vague_found = [indicator for indicator in vague_indicators 
                      if indicator in response.lower()]
        
        if vague_found:
            result.is_valid = False
            result.needs_clarification = True
            result.issues.append(f"Response seems vague: {vague_found[0]}")
            result.suggested_questions.append("Could you be more specific?")
        
        return result
    
    def extract_key_points(self, response: str, phase: str) -> Dict[str, Any]:
        """Extract key points from a response"""
        key_points = {
            "phase": phase,
            "raw_response": response,
            "summary": self._summarize_response(response),
            "keywords": self._extract_keywords(response),
            "has_metrics": self._has_metrics(response),
            "has_timeline": self._has_timeline(response),
        }
        
        return key_points
    
    def _summarize_response(self, response: str) -> str:
        """Create a simple summary of the response"""
        if len(response) <= 200:
            return response
        
        # Simple summary: first 150 chars + "..."
        return response[:150] + "..."
    
    def _extract_keywords(self, response: str) -> List[str]:
        """Extract important keywords from response"""
        # Simple keyword extraction
        common_words = {"the", "and", "for", "with", "that", "this", "will", "can", "are", "is"}
        words = response.lower().split()
        
        keywords = [
            word for word in words 
            if len(word) > 3 
            and word not in common_words
            and word.isalpha()
        ]
        
        # Return unique keywords
        return list(set(keywords))[:10]  # Limit to 10 keywords
    
    def _has_metrics(self, response: str) -> bool:
        """Check if response contains metrics/KPIs"""
        metric_indicators = ["metric", "kpi", "measure", "track", "success", "goal", "target"]
        return any(indicator in response.lower() for indicator in metric_indicators)
    
    def _has_timeline(self, response: str) -> bool:
        """Check if response contains timeline information"""
        timeline_indicators = ["week", "month", "day", "timeline", "schedule", "deadline", "due"]
        return any(indicator in response.lower() for indicator in timeline_indicators)