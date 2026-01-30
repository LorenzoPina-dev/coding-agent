import os
import sys
from pathlib import Path

def check_and_fix_structure():
    """Verifica e correggi la struttura del progetto"""
    
    print("="*60)
    print("VERIFICA STRUTTURA PROGETTO")
    print("="*60)
    
    base_path = Path(".")
    
    # Lista di file e directory richieste
    required_items = [
        # Directory
        ("src", True),
        ("src/config", True),
        ("src/utils", True),
        ("src/discovery", True),
        ("src/analyst", True),
        ("src/builder", True),
        ("src/reviewer", True),
        ("src/educator", True),
        ("src/tasks", True),
        ("src/file_manager", True),
        ("src/state", True),
        ("prompts", True),
        ("logs", True),
        ("outputs", True),
        ("examples", True),
        ("tests", True),
        
        # File __init__.py
        ("src/__init__.py", False),
        ("src/config/__init__.py", False),
        ("src/utils/__init__.py", False),
        ("src/discovery/__init__.py", False),
        ("src/analyst/__init__.py", False),
        ("src/builder/__init__.py", False),
        ("src/reviewer/__init__.py", False),
        ("src/educator/__init__.py", False),
        ("src/tasks/__init__.py", False),
        ("src/file_manager/__init__.py", False),
        ("src/state/__init__.py", False),
        ("prompts/__init__.py", False),
        
        # File essenziali
        ("src/config/settings.py", False),
        ("src/config/prompts.py", False),
        ("src/agent.py", False),
        ("src/utils/llm.py", False),
        ("src/utils/logger.py", False),
        ("prompts/discovery_prompts.json", False),
        (".env", False),
        ("requirements.txt", False),
    ]
    
    missing_items = []
    
    for item_path, is_directory in required_items:
        path = base_path / item_path
        
        if is_directory:
            if not path.exists() or not path.is_dir():
                print(f" Manca directory: {item_path}")
                missing_items.append((item_path, is_directory))
            else:
                print(f" Directory: {item_path}/")
        else:
            if not path.exists() or not path.is_file():
                print(f" Manca file: {item_path}")
                missing_items.append((item_path, is_directory))
            else:
                print(f" File: {item_path}")
    
    print("\n" + "="*60)
    
    if missing_items:
        print(f"\n  Mancano {len(missing_items)} elementi")
        
    else:
        print(" Tutti gli elementi richiesti sono presenti!")
        print("\nPuoi eseguire: python examples/ollama_example_run.py")
        
check_and_fix_structure()