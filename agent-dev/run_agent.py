#!/usr/bin/env python3
"""
Main script for AI Development Agent with intelligent discovery
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import AIDevelopmentAgent
from src.config.settings import AgentSettings, LLMProvider


def main():
    print("="*80)
    print("🤖 AI DEVELOPMENT AGENT")
    print("🚀 Intelligent Discovery → AI-Optimized PRD → Automated Development")
    print("="*80)
    
    # Configuration
    settings = AgentSettings(
        llm_provider=LLMProvider.OLLAMA,
        ollama_model="deepseek-coder:6.7b",
        dry_run=True,  # Set to False to actually write files
        max_iterations=20,
        log_level="INFO"
    )
    
    # Create and run AI agent
    agent = AIDevelopmentAgent(settings)
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\n👋 AI Agent stopped by user")
    except Exception as e:
        print(f"\n\n❌ AI Agent failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()