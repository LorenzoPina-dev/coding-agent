from typing import Dict, Any
import json
from pathlib import Path


class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._prompts: Dict[str, Dict[str, Any]] = {}
        
    def load_prompts(self, category: str) -> Dict[str, Any]:
        """Load prompts for a specific category"""
        if category in self._prompts:
            return self._prompts[category]
            
        prompt_file = self.prompts_dir / f"{category}_prompts.json"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
            
        self._prompts[category] = prompts
        return prompts
    
    def get_prompt(self, category: str, prompt_name: str, **kwargs) -> str:
        """Get a specific prompt with variable substitution"""
        prompts = self.load_prompts(category)
        if prompt_name not in prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in category '{category}'")
            
        template = prompts[prompt_name]
        return template.format(**kwargs) if kwargs else template