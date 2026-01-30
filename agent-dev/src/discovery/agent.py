from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import json
from pydantic import BaseModel, Field
from ..utils.llm import LLMClient
from ..config.prompts import PromptManager
from .phases import DiscoveryPhase, PhaseState
from .validator import ResponseValidator


class DiscoveryResponse(BaseModel):
    phase: str
    answers: Dict[str, Any]
    is_complete: bool = False
    needs_clarification: Optional[List[str]] = None


class DiscoveryAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.validator = ResponseValidator()
        self.current_phase: Optional[DiscoveryPhase] = None
        self.responses: Dict[str, Any] = {}
        self.phase_history: List[PhaseState] = []
        
    def start_discovery(self) -> str:
        """Start the discovery process"""
        self.current_phase = DiscoveryPhase.INTRO
        return self.prompt_manager.get_prompt("discovery", "phase_intro")
    
    def process_response(self, user_input: str) -> DiscoveryResponse:
        """Process user response for current phase"""
        if not self.current_phase:
            raise ValueError("Discovery not started")
        
        print(f"\n[DEBUG] Current phase: {self.current_phase}")
        print(f"[DEBUG] User input: {user_input[:50]}...")
        
        # Validazione semplice
        if not user_input or not user_input.strip():
            print(f"[DEBUG] Empty response, asking for clarification")
            return DiscoveryResponse(
                phase=self.current_phase.value if hasattr(self.current_phase, 'value') else str(self.current_phase),
                answers={},
                is_complete=False,
                needs_clarification=["La risposta è vuota"]
            )
        
        # Salva risposta - usa il valore stringa della fase
        phase_key = self.current_phase.value if hasattr(self.current_phase, 'value') else str(self.current_phase)
        self.responses[phase_key] = user_input.strip()
        print(f"[DEBUG] Saved response for phase {phase_key}")
        
        # Passa alla fase successiva - usa i valori stringa dell'enum
        phases = ["INTRO", "GOALS", "USERS", "CONSTRAINTS", "NON_GOALS", "RISKS", "CONFIRMATION"]
        
        try:
            # Converti current_phase a stringa per il confronto
            current_phase_str = self.current_phase.value if hasattr(self.current_phase, 'value') else str(self.current_phase)
            current_index = phases.index(current_phase_str)
            
            if current_index < len(phases) - 1:
                next_phase_str = phases[current_index + 1]
                
                # Converti la stringa di nuovo in enum
                from .phases import DiscoveryPhase
                self.current_phase = DiscoveryPhase(next_phase_str)
                
                print(f"[DEBUG] Moving to next phase: {next_phase_str}")
                
                if next_phase_str == "CONFIRMATION":
                    # Genera summary
                    summary = self._generate_summary()
                    print(f"[DEBUG] Generating confirmation summary")
                    
                    return DiscoveryResponse(
                        phase=next_phase_str,
                        answers=self.responses,
                        is_complete=True
                    )
                else:
                    # Prepara domanda per la prossima fase
                    return DiscoveryResponse(
                        phase=next_phase_str,
                        answers={},
                        is_complete=False
                    )
            else:
                # Tutte le fasi completate
                print(f"[DEBUG] All phases completed")
                return DiscoveryResponse(
                    phase="COMPLETE",
                    answers=self.responses,
                    is_complete=True
                )
                
        except ValueError as e:
            print(f"[DEBUG] Error in phase transition: {e}")
            print(f"[DEBUG] Current phase string: {current_phase_str}")
            print(f"[DEBUG] Phases list: {phases}")
            
            return DiscoveryResponse(
                phase="ERROR",
                answers={},
                is_complete=False,
                needs_clarification=[f"Errore di transizione fase: {e}"]
            )
    
    def _get_next_phase(self) -> Optional[DiscoveryPhase]:
        """Get the next phase in sequence"""
        phases = list(DiscoveryPhase)
        current_index = phases.index(self.current_phase)
        
        if current_index < len(phases) - 1:
            return phases[current_index + 1]
        return None
    
    def _extract_key_points(self, response: str) -> Dict[str, Any]:
        """Extract structured information from response"""
        prompt = f"""
        Extract key points from this response and organize them:
        
        Response: {response}
        
        Return as JSON with relevant categories based on the phase.
        """
        
        result = self.llm_client.generate(
            prompt=prompt,
            response_format={"type": "json_object"}
        )
        
        return json.loads(result)
    
    def _generate_summary(self) -> str:
        """Generate a summary of all discovery responses"""
        summary_prompt = f"""
        Create a comprehensive summary of the product discovery:
        
        {json.dumps(self.responses, indent=2)}
        
        Organize by:
        1. Product Overview
        2. Goals and Objectives
        3. User Profiles
        4. Constraints
        5. Non-Goals
        6. Risks and Assumptions
        """
        
        return self.llm_client.generate(prompt=summary_prompt)