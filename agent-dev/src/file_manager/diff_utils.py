"""
Diff utilities for file comparison
"""

import difflib
from typing import Optional


def generate_diff(old_content: str, new_content: str, filename: str) -> str:
    """
    Generate unified diff between old and new content
    
    Args:
        old_content: Original file content
        new_content: New file content
        filename: Name of the file (for diff header)
    
    Returns:
        Unified diff string
    """
    if old_content == new_content:
        return f"No changes in {filename}"
    
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{filename} (old)",
        tofile=f"{filename} (new)",
        lineterm="\n"
    )
    
    return "".join(diff)


def apply_diff(original: str, diff_text: str) -> Optional[str]:
    """
    Apply diff to original content (simplified version)
    
    Note: This is a simplified implementation. For production use,
    consider using a proper patch library like `unidiff` or `patch`.
    
    Args:
        original: Original content
        diff_text: Diff text to apply
    
    Returns:
        Patched content or None if failed
    """
    try:
        # Simple implementation - just parse and apply
        lines = original.splitlines(keepends=True)
        diff_lines = diff_text.splitlines()
        
        result = []
        i = 0
        
        while i < len(diff_lines):
            line = diff_lines[i]
            
            if line.startswith('---') or line.startswith('+++'):
                i += 1
                continue
            
            if line.startswith('@@'):
                # Parse chunk header
                i += 1
                continue
            
            if line.startswith(' '):
                # Context line
                if result or line[1:] != lines[len(result)]:
                    result.append(line[1:])
                else:
                    result.append(lines[len(result)])
                i += 1
            elif line.startswith('-'):
                # Remove line
                i += 1
            elif line.startswith('+'):
                # Add line
                result.append(line[1:])
                i += 1
            else:
                i += 1
        
        return "".join(result) if lines else "\n".join(result)
    
    except Exception:
        # If anything goes wrong, return None
        return None


def get_change_summary(diff_text: str) -> dict:
    """
    Get summary of changes from diff
    
    Args:
        diff_text: Diff text
    
    Returns:
        Dictionary with change summary
    """
    if not diff_text:
        return {"additions": 0, "deletions": 0, "files_changed": 0}
    
    lines = diff_text.splitlines()
    
    additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
    
    # Count unique files from diff headers
    files_changed = len(set(line for line in lines if line.startswith('--- ') or line.startswith('+++ '))) // 2
    
    return {
        "additions": additions,
        "deletions": deletions,
        "files_changed": files_changed,
        "total_changes": additions + deletions
    }


def create_patch_header(filename: str, old_version: str = "1", new_version: str = "2") -> str:
    """
    Create patch file header
    
    Args:
        filename: Name of the file
        old_version: Old version identifier
        new_version: New version identifier
    
    Returns:
        Patch header
    """
    return f"""--- {filename}.{old_version}
+++ {filename}.{new_version}
"""


# Test functions
if __name__ == "__main__":
    # Simple test
    old = "Hello\nWorld\n"
    new = "Hello\nBeautiful\nWorld\n"
    
    diff = generate_diff(old, new, "test.txt")
    print("Generated diff:")
    print(diff)
    
    summary = get_change_summary(diff)
    print("\nChange summary:", summary)