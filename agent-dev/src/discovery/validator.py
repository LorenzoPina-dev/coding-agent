"""
Validator for discovery responses - VERSIONE SEMPLIFICATA
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool = True
    issues: List[str] = []
    needs_clarification: bool = False
    suggested_questions: List[str] = []


class ResponseValidator:
    """Validator for user responses during discovery - VERSIONE SEMPLICE"""
    
    def validate_response(
        self, 
        phase: str, 
        response: str, 
        previous_responses: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a user response - ACCETTA QUASI TUTTO"""
        result = ValidationResult()
        
        # Controllo minimo: risposta non vuota
        if not response or not response.strip():
            result.is_valid = False
            result.needs_clarification = True
            result.issues.append("La risposta è vuota")
            result.suggested_questions.append("Per favore, rispondi alla domanda")
            return result
        
        # Per la fase INTRO, accetta qualsiasi cosa non vuota
        if phase == "INTRO":
            # SEMPLICE: se c'è testo, va bene
            result.is_valid = True
            result.needs_clarification = False
            
            # Suggerimento opzionale se la risposta è molto breve
            if len(response.strip()) < 10:
                result.suggested_questions.append("Vuoi aggiungere altri dettagli? (opzionale)")
            
            return result
        
        # Per altre fasi, controlli minimi
        if len(response.strip()) < 3:
            result.is_valid = False
            result.needs_clarification = True
            result.issues.append("La risposta è troppo breve")
            result.suggested_questions.append("Potresti fornire più dettagli?")
        
        return result
    
    def extract_key_points(self, response: str, phase: str) -> Dict[str, Any]:
        """Extract key points from response"""
        return {
            "phase": phase,
            "raw_response": response,
            "summary": response[:100] + "..." if len(response) > 100 else response,
            "word_count": len(response.split()),
        }