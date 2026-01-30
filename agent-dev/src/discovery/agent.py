"""
Smart Discovery Agent - asks iterative questions until 90% understanding
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
import json
from src.utils.llm import LLMClient
from src.config.prompts import PromptManager


class UnderstandingMetric(BaseModel):
    """Metrics for project understanding"""
    clarity_score: float = 0.0  # 0-1 score
    missing_aspects: List[str] = []
    confidence: float = 0.0
    next_questions: List[str] = []


class SmartDiscoveryAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.conversation_history: List[Dict[str, str]] = []
        self.understanding: UnderstandingMetric = UnderstandingMetric()
        self.project_data: Dict[str, Any] = {}
        
    def start_conversation(self) -> str:
        """Start the discovery conversation"""
        initial_prompt = """I'm your AI development assistant. I'll help you turn your idea into production-ready code.

Let's start with your vision. Tell me about the project you want to build. Be as detailed or brief as you like - I'll ask clarifying questions as needed.

What would you like to create?"""
        
        self.conversation_history.append({
            "role": "assistant",
            "content": initial_prompt
        })
        
        return initial_prompt
    
    def process_response(self, user_input: str) -> Tuple[str, bool, float]:
        """
        Process user response and determine next action
        
        Returns:
            Tuple[next_question, is_complete, understanding_score]
        """
        # Add user response to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Analyze understanding
        self._analyze_understanding()
        
        # If we have > 90% understanding, generate summary
        if self.understanding.clarity_score >= 0.9:
            summary = self._generate_summary()
            self.conversation_history.append({
                "role": "assistant",
                "content": summary
            })
            return summary, True, self.understanding.clarity_score
        
        # Generate next clarifying question
        next_question = self._generate_next_question()
        self.conversation_history.append({
            "role": "assistant",
            "content": next_question
        })
        
        return next_question, False, self.understanding.clarity_score
    
    def _analyze_understanding(self):
        """Analyze current understanding of the project"""
        # Use LLM to analyze understanding
        analysis_prompt = f"""Analyze the current conversation about a software project and determine:
1. Clarity score (0-1): How well do we understand what needs to be built?
2. Missing aspects: What crucial information is still missing?
3. Confidence: How confident are we in the analysis (0-1)?
4. Next questions: List 1-3 specific clarifying questions to ask next.

Conversation history:
{json.dumps(self.conversation_history[-6:], indent=2)}

Return JSON with: clarity_score, missing_aspects (list), confidence, next_questions (list)
"""
        
        try:
            response = self.llm_client.generate(
                analysis_prompt,
                system_prompt="You are a software architect analyzing project requirements. Be precise and technical."
            )
            
            # Try to parse JSON
            try:
                data = json.loads(response)
                self.understanding = UnderstandingMetric(**data)
            except:
                # If JSON parsing fails, estimate
                self.understanding.clarity_score = min(0.7, self.understanding.clarity_score + 0.1)
                self.understanding.next_questions = [
                    "Could you tell me more about the technical requirements?",
                    "What are the main features you envision?",
                    "Who will be using this system?"
                ]
        
        except Exception:
            # Fallback
            self.understanding.clarity_score = min(0.8, self.understanding.clarity_score + 0.15)
    
    def _generate_next_question(self) -> str:
        """Generate the next clarifying question"""
        if self.understanding.next_questions:
            return self.understanding.next_questions[0]
        
        # Default questions based on conversation stage
        conversation_length = len([m for m in self.conversation_history if m["role"] == "user"])
        
        if conversation_length <= 1:
            return "Great start! Could you tell me more about the main features you want to implement?"
        elif conversation_length <= 3:
            return "Who will be using this system and what are their main needs?"
        elif conversation_length <= 5:
            return "What technologies or frameworks are you considering, or should I suggest based on the requirements?"
        else:
            return "Is there anything else I should know about the project architecture or constraints?"
    
    def _generate_summary(self) -> str:
        """Generate summary when understanding is sufficient"""
        summary_prompt = f"""Based on this conversation, create a comprehensive project summary:

{json.dumps(self.conversation_history, indent=2)}

Provide a structured summary with:
1. Project name and purpose
2. Core functionality
3. Target users
4. Technical considerations
5. Key requirements
6. Any constraints mentioned

Format it clearly for the next phase (PRD generation)."""

        summary = self.llm_client.generate(summary_prompt)
        
        # Store for PRD generation
        self.project_data["summary"] = summary
        
        return f"""✅ Excellent! I now have a good understanding of your project.

📋 **Project Summary:**
{summary}

Ready to generate the detailed Product Requirements Document? (yes/no)"""
    
    def get_project_data(self) -> Dict[str, Any]:
        """Get all collected project data"""
        return self.project_data