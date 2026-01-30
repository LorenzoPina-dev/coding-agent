"""
Prompt templates directory
"""

import json
from pathlib import Path

def load_prompt(category: str, name: str) -> dict:
    """Load a prompt from JSON file"""
    prompt_file = Path(__file__).parent / f"{category}_prompts.json"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    return prompts.get(name, {})