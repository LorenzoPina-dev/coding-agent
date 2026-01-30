#!/usr/bin/env python3
"""
Setup script for Ollama and DeepSeek-Coder model
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path


def check_ollama_installed() -> bool:
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ollama() -> bool:
    """Install Ollama"""
    print("Installing Ollama...")
    
    try:
        # This is a simplified install script
        # In production, you'd want platform-specific installation
        import platform
        
        system = platform.system()
        
        if system == "Linux":
            print("Linux detected. Installing via curl...")
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
            ], shell=True, check=True)
            
        elif system == "Darwin":  # macOS
            print("macOS detected. Installing via Homebrew or direct download...")
            try:
                subprocess.run(["brew", "install", "ollama"], check=True)
            except:
                print("Homebrew not found. Please install Ollama manually:")
                print("Visit: https://ollama.ai/download")
                return False
                
        elif system == "Windows":
            print("Windows detected. Please install Ollama manually:")
            print("Download from: https://ollama.ai/download")
            print("Then run: ollama serve")
            return False
            
        else:
            print(f"Unsupported OS: {system}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False


def start_ollama_service() -> bool:
    """Start Ollama service"""
    print("Starting Ollama service...")
    
    try:
        # Try to start Ollama in background
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=1)
                if response.status_code == 200:
                    print("✅ Ollama service started successfully")
                    return True
            except:
                if i % 5 == 0:
                    print(f"Waiting for Ollama... ({i+1}s)")
        
        print("❌ Timeout waiting for Ollama to start")
        return False
        
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False


def pull_deepseek_model() -> bool:
    """Pull DeepSeek-Coder:6.7b model"""
    print("Pulling DeepSeek-Coder:6.7b model...")
    print("This may take several minutes depending on your internet connection...")
    
    try:
        process = subprocess.Popen(
            ["ollama", "pull", "deepseek-coder:6.7b"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ DeepSeek-Coder:6.7b model pulled successfully")
            return True
        else:
            print("❌ Failed to pull model")
            return False
            
    except Exception as e:
        print(f"Error pulling model: {e}")
        return False


def verify_ollama_setup() -> bool:
    """Verify Ollama is setup correctly"""
    print("\nVerifying Ollama setup...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            print(f"Found {len(models)} model(s):")
            for model in models:
                print(f"  - {model.get('name')} ({model.get('size', 'unknown')})")
            
            # Check for deepseek-coder
            has_deepseek = any("deepseek-coder" in model.get("name", "").lower() 
                             for model in models)
            
            if has_deepseek:
                print("✅ Ollama setup verified successfully")
                return True
            else:
                print("⚠️  Ollama is running but DeepSeek-Coder not found")
                return False
        else:
            print(f"❌ Ollama API returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def setup_project_structure():
    """Setup project directory structure"""
    print("\nSetting up project structure...")
    
    directories = [
        "logs",
        "outputs",
        "backups",
        "prompts",
        "config",
        "src/discovery",
        "src/analyst",
        "src/builder",
        "src/reviewer",
        "src/educator",
        "src/tasks",
        "src/file_manager",
        "src/utils",
        "src/state",
        "tests",
        "examples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("✅ Project structure created")


def create_env_file():
    """Create .env file with default settings"""
    print("\nCreating .env file...")
    
    env_content = """# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# Agent Settings
DRY_RUN=True
LOG_LEVEL=INFO
OUTPUT_DIR=outputs

# Optional: OpenAI/Anthropic (if you want to switch providers)
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created")
    print("\nYou can edit .env to change settings like:")
    print("  - DRY_RUN=False (to actually write files)")
    print("  - OLLAMA_MODEL=other-model-name")
    print("  - Add API keys for other providers")


def main():
    """Main setup function"""
    print("="*80)
    print("Ollama & DeepSeek-Coder Setup Script")
    print("="*80)
    
    # Step 1: Check/Install Ollama
    print("\n1. Checking Ollama installation...")
    if not check_ollama_installed():
        print("❌ Ollama not found")
        choice = input("Do you want to install Ollama? (yes/no): ").lower()
        
        if choice in ['yes', 'y']:
            if not install_ollama():
                print("Failed to install Ollama. Please install manually:")
                print("Visit: https://ollama.ai/")
                return False
        else:
            print("Please install Ollama manually from https://ollama.ai/")
            return False
    else:
        print("✅ Ollama is installed")
    
    # Step 2: Start Ollama service
    print("\n2. Starting Ollama service...")
    if not start_ollama_service():
        print("⚠️  Could not start Ollama service automatically")
        print("Please start Ollama manually:")
        print("  Open a new terminal and run: ollama serve")
        print("Then run this setup script again")
        return False
    
    # Step 3: Pull DeepSeek model
    print("\n3. Setting up DeepSeek-Coder model...")
    if not pull_deepseek_model():
        print("⚠️  Failed to pull model. Trying to verify existing models...")
    
    # Step 4: Verify setup
    print("\n4. Verifying setup...")
    if not verify_ollama_setup():
        print("\n⚠️  Setup verification failed")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check if model exists: ollama list")
        print("3. Pull model manually: ollama pull deepseek-coder:6.7b")
        print("4. Restart Ollama service")
        return False
    
    # Step 5: Setup project structure
    print("\n5. Setting up project...")
    setup_project_structure()
    create_env_file()
    
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    print("\nYou can now run the agent:")
    print("\n1. For a test run (dry mode):")
    print("   python examples/ollama_example_run.py")
    print("\n2. For actual development:")
    print("   Edit .env and set DRY_RUN=False")
    print("   Then run: python -c \"")
    print("   from src.agent import SoftwareDevAgent")
    print("   from src.config.settings import AgentSettings, LLMProvider")
    print("   settings = AgentSettings(llm_provider=LLMProvider.OLLAMA)")
    print("   agent = SoftwareDevAgent(settings)")
    print("   agent.run()")
    print("   \"")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)