"""
File management module
"""

from .handler import FileManager
from .diff_utils import generate_diff, apply_diff

__all__ = [
    "FileManager",
    "generate_diff",
    "apply_diff",
]