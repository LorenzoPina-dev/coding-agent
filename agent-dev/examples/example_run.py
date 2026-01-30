#!/usr/bin/env python3
"""
Example run of the Software Development Agent in dry-run mode.
This simulates creating a simple REST API service.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import SoftwareDevAgent
from src.config.settings import AgentSettings


def main():
    """Example run for a simple REST API service"""
    
    # Configure for dry-run mode
    settings = AgentSettings(
        dry_run=True,
        require_confirmation=True,
        max_iterations=5,
        log_level="INFO"
    )
    
    # Create agent
    agent = SoftwareDevAgent(settings)
    
    print("=" * 80)
    print("SOFTWARE DEVELOPMENT AGENT - EXAMPLE RUN")
    print("Creating a simple REST API service")
    print("Mode: DRY-RUN (no actual files will be written)")
    print("=" * 80)
    print()
    
    try:
        # Run the agent
        agent.run()
        
        print("\n" + "=" * 80)
        print("EXAMPLE RUN COMPLETE")
        print("=" * 80)
        print("\nCheck the 'outputs/' directory for generated files.")
        print("To run with actual file writing, set dry_run=False in settings.")
        
    except KeyboardInterrupt:
        print("\n\nExample run interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nExample run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()