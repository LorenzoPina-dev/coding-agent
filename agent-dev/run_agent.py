#!/usr/bin/env python3
"""
Main script to run the Software Development Agent with Ollama
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import SoftwareDevAgent
from config.settings import AgentSettings, LLMProvider


def main():
    """Run the agent with Ollama configuration"""
    
    print("="*80)
    print("🧠 Software Development Agent")
    print("🤖 Using Ollama with DeepSeek-Coder:6.7b")
    print("="*80)
    
    # Configuration
    settings = AgentSettings(
        llm_provider=LLMProvider.OLLAMA,
        ollama_model="deepseek-coder:6.7b",
        ollama_base_url="http://localhost:11434",
        dry_run=False,  # Set to False to actually write files
        require_confirmation=True,
        max_iterations=20,
        log_level="INFO",
        model_name="deepseek-coder:6.7b"
    )
    
    # Create and run agent
    agent = SoftwareDevAgent(settings)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nAgent stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nAgent failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()