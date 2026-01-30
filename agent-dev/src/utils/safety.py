import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class SafetyChecker:
    """Safety checks for generated code"""
    
    @staticmethod
    def check_for_sensitive_patterns(code: str) -> List[str]:
        """Check for sensitive patterns in code"""
        sensitive_patterns = [
            r"(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]+['\"]",
            r"process\.env\.[A-Z_]+",
            r"os\.getenv\([^)]+\)",
            r"\.env",
            r"config\.(yml|yaml|json|ini|cfg)",
            r"private[_-]?key",
            r"BEGIN\s+(RSA|DSA|EC)\s+PRIVATE\s+KEY",
            r"ssh-rsa\s+[A-Za-z0-9+/]+[=]{0,2}",
        ]
        
        issues = []
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                issues.append(f"Sensitive pattern found: {pattern}")
        
        return issues
    
    @staticmethod
    def check_file_size(filepath: Path, max_size_mb: int = 10) -> bool:
        """Check if file size is within limits"""
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            return size_mb <= max_size_mb
        return True
    
    @staticmethod
    def validate_filename(filename: str) -> List[str]:
        """Validate filename for safety"""
        issues = []
        
        # Check for directory traversal
        if ".." in filename or filename.startswith("/"):
            issues.append("Potential directory traversal in filename")
        
        # Check for unsafe characters
        unsafe_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in unsafe_chars:
            if char in filename:
                issues.append(f"Unsafe character '{char}' in filename")
        
        # Check for reserved names
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 
                         'COM1', 'COM2', 'COM3', 'COM4',
                         'LPT1', 'LPT2', 'LPT3', 'LPT4']
        if filename.upper() in reserved_names:
            issues.append(f"Reserved filename: {filename}")
        
        return issues
    
    @staticmethod
    def check_executable_content(code: str, filename: str) -> List[str]:
        """Check for potentially dangerous executable content"""
        issues = []
        
        # Check for shell commands in Python files
        if filename.endswith('.py'):
            dangerous_imports = [
                'os.system', 'subprocess.run', 'subprocess.Popen',
                'exec', 'eval', '__import__'
            ]
            
            for import_stmt in dangerous_imports:
                if import_stmt in code:
                    issues.append(f"Potentially dangerous import: {import_stmt}")
        
        # Check for file system operations
        fs_patterns = [
            r"open\([^)]+,\s*['\"]w['\"]\)",
            r"open\([^)]+,\s*['\"]a['\"]\)",
            r"shutil\.(copy|move|rmtree)",
            r"os\.(remove|unlink|rmdir)",
        ]
        
        for pattern in fs_patterns:
            if re.search(pattern, code):
                issues.append(f"File system operation detected: {pattern}")
        
        return issues