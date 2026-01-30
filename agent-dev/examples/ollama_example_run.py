#!/usr/bin/env python3
"""
Example run of the Software Development Agent with Ollama and DeepSeek-Coder:6.7b
This creates a simple REST API service using Flask.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent  # E:\agent\agent-dev
src_dir = project_root / "src"               # E:\agent\agent-dev\src

# 1. Prima aggiungi src (così Python trova i moduli direttamente)
sys.path.insert(0, str(src_dir))

# 2. Poi aggiungi project_root (per compatibilità)
sys.path.insert(0, str(project_root))
from src.agent import SoftwareDevAgent
from src.config.settings import AgentSettings, LLMProvider


def check_ollama_available():
    """Check if Ollama is running and model is available"""
    import requests
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            print(f"Available Ollama models: {model_names}")
            
            # Check for deepseek-coder:6.7b
            target_model = "deepseek-coder:6.7b"
            if any(target_model in name for name in model_names):
                print(f"✅ Found model: {target_model}")
                return True
            else:
                print(f"❌ Model {target_model} not found. Available models:")
                for model in models:
                    print(f"  - {model.get('name')}")
                return False
        else:
            print(f"❌ Ollama API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure Ollama is running:")
        print("  1. Install Ollama from https://ollama.ai/")
        print("  2. Run: ollama pull deepseek-coder:6.7b")
        print("  3. Start Ollama: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def interactive_discovery_example():
    """Example discovery responses for a Flask REST API"""
    print("\n" + "="*80)
    print("INTERACTIVE DISCOVERY EXAMPLE")
    print("="*80)
    print("\nI'll simulate user responses for creating a Flask REST API service...")
    
    responses = [
        # INTRO phase
        "Product Name: Task Manager API\n"
        "Problem: Users need a simple API to manage tasks and todos\n"
        "Type: REST API service",
        
        # GOALS phase
        "Primary objectives:\n"
        "1. Create CRUD endpoints for tasks\n"
        "2. Implement user authentication\n"
        "3. Add task filtering and search\n"
        "4. Include comprehensive error handling\n"
        "5. Provide API documentation\n"
        "\nSuccess metrics: API responds under 200ms, 99% uptime\n"
        "Timeline: 2 weeks development",
        
        # USERS phase
        "Primary users: Developers integrating the API\n"
        "Needs: Simple, well-documented REST endpoints\n"
        "Technical expertise: Intermediate to advanced\n"
        "Interaction: Via HTTP requests, Swagger UI",
        
        # CONSTRAINTS phase
        "Technical: Python 3.10+, Flask framework, SQLite database\n"
        "Budget: Open source, no budget constraints\n"
        "Timeline: 2 weeks\n"
        "Compliance: None specific",
        
        # NON-GOALS phase
        "Out of scope:\n"
        "1. Web UI frontend\n"
        "2. Mobile apps\n"
        "3. Real-time notifications\n"
        "4. Complex reporting",
        
        # RISKS phase
        "Technical risks: Database scalability\n"
        "Business risks: Simple API may not meet all needs\n"
        "Dependencies: Flask ecosystem stability\n"
        "Assumptions: Users want REST API, not GraphQL",
        
        # CONFIRMATION phase
        "Yes, everything looks correct. Proceed with development."
    ]
    
    return responses


def main():
    """Example run for a Flask REST API with Ollama"""
    
    print("="*80)
    print("SOFTWARE DEVELOPMENT AGENT WITH OLLAMA")
    print("Using DeepSeek-Coder:6.7b")
    print("="*80)
    
    # Check Ollama availability
    print("\n🔍 Checking Ollama availability...")
    if not check_ollama_available():
        print("\nPlease set up Ollama first:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Pull model: ollama pull deepseek-coder:6.7b")
        print("3. Start Ollama: ollama serve")
        sys.exit(1)
    
    # Configure for Ollama
    settings = AgentSettings(
        llm_provider=LLMProvider.OLLAMA,
        ollama_model="deepseek-coder:6.7b",
        ollama_base_url="http://localhost:11434",
        dry_run=True,  # Safe mode - no actual file writing
        require_confirmation=True,
        max_iterations=3,
        log_level="INFO"
    )
    
    # Create agent
    agent = SoftwareDevAgent(settings)
    
    print("\n" + "="*80)
    print("SIMULATING AGENT RUN")
    print("="*80)
    print("\nThis will simulate creating a Flask REST API Task Manager...")
    
    # Simulate interactive responses
    responses = interactive_discovery_example()
    
    try:
        # Simulate the discovery phase
        print("\n[bold cyan]📝 Starting Product Discovery...[/bold cyan]")
        
        # We can't easily simulate the full interactive loop in a script
        # Instead, we'll show what would happen
        print("\nSimulated discovery responses:")
        for i, response in enumerate(responses):
            phase = ["INTRO", "GOALS", "USERS", "CONSTRAINTS", 
                    "NON-GOALS", "RISKS", "CONFIRMATION"][i]
            print(f"\n{phase}:")
            print(f"{response[:100]}..." if len(response) > 100 else response)
            time.sleep(0.5)
        
        print("\n[green]✅ Discovery simulation complete![/green]")
        print("\nIn a real run, the agent would now:")
        print("1. Generate PRD from discovery")
        print("2. Create tasks from PRD")
        print("3. Build code using DeepSeek-Coder")
        print("4. Review and iterate")
        
        # Ask if user wants to run actual agent
        print("\n" + "="*80)
        choice = input("\nDo you want to run the actual agent? (yes/no): ").lower()
        
        if choice in ['yes', 'y']:
            print("\nStarting actual agent run...")
            agent.run()
        else:
            print("\nExample simulation complete.")
            print("\nTo run the full agent:")
            print("python -c \"")
            print("from src.agent import SoftwareDevAgent")
            print("from src.config.settings import AgentSettings, LLMProvider")
            print("")
            print("settings = AgentSettings(")
            print("    llm_provider=LLMProvider.OLLAMA,")
            print("    ollama_model='deepseek-coder:6.7b',")
            print("    dry_run=False  # Set to False for actual file writing")
            print(")")
            print("agent = SoftwareDevAgent(settings)")
            print("agent.run()")
            print("\"")
        
    except KeyboardInterrupt:
        print("\n\nExample run interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nExample run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()