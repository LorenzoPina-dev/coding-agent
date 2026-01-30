import os
import shutil
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import difflib
from datetime import datetime
from ..utils.logger import get_logger
from .diff_utils import generate_diff, apply_diff


logger = get_logger(__name__)


class FileManager:
    def __init__(self, output_dir: str = "outputs", dry_run: bool = False):
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.backup_dir = self.output_dir / "backups"
        self.history_file = self.output_dir / "file_history.json"
        
        self._setup_directories()
        self._load_history()
        
    def _setup_directories(self):
        """Setup necessary directories"""
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.backup_dir.mkdir(exist_ok=True)
        
    def _load_history(self):
        """Load file history"""
        self.history = {}
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = {}
    
    def _save_history(self):
        """Save file history"""
        if self.dry_run:
            return
            
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    def write_files(self, files: List[Dict[str, str]], task_id: str) -> Dict[str, Any]:
        """Write multiple files with backup and diff"""
        results = {
            "success": [],
            "failed": [],
            "backups": [],
            "diffs": {}
        }
        
        for file_info in files:
            filename = file_info["filename"]
            content = file_info["code"]
            
            result = self._write_file_safe(filename, content, task_id)
            
            if result["success"]:
                results["success"].append(filename)
                results["diffs"][filename] = result["diff"]
                if result["backup"]:
                    results["backups"].append(result["backup"])
            else:
                results["failed"].append({
                    "filename": filename,
                    "error": result["error"]
                })
        
        self._save_history()
        return results
    
    def _write_file_safe(self, filename: str, content: str, task_id: str) -> Dict[str, Any]:
        """Safely write a file with backup and diff"""
        filepath = self.output_dir / filename
        
        try:
            # Ensure directory exists
            filepath.parent.mkdir(exist_ok=True, parents=True)
            
            # Read existing content if file exists
            old_content = None
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            
            # Generate diff
            diff = ""
            if old_content is not None:
                diff = generate_diff(old_content, content, str(filepath))
            
            # Create backup
            backup_path = None
            if old_content is not None and not self.dry_run:
                backup_path = self._create_backup(filename, old_content, task_id)
            
            # Write file if not dry run
            if not self.dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Update history
                self._update_file_history(filename, task_id, len(content))
            
            return {
                "success": True,
                "diff": diff,
                "backup": backup_path,
                "file_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Failed to write file {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_backup(self, filename: str, content: str, task_id: str) -> str:
        """Create backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}.{timestamp}.{task_id}.bak"
        backup_path = self.backup_dir / backup_filename
        
        try:
            backup_path.parent.mkdir(exist_ok=True, parents=True)
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def _update_file_history(self, filename: str, task_id: str, size: int):
        """Update file history"""
        if filename not in self.history:
            self.history[filename] = []
        
        self.history[filename].append({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "size": size,
            "backup_count": len([b for b in self.backup_dir.glob(f"{filename}.*.bak")])
        })
        
        # Keep only last 100 entries per file
        if len(self.history[filename]) > 100:
            self.history[filename] = self.history[filename][-100:]
    
    def rollback_to_task(self, task_id: str) -> Dict[str, Any]:
        """Rollback changes made by a specific task"""
        backups = list(self.backup_dir.glob(f"*.{task_id}.bak"))
        
        results = {
            "restored": [],
            "failed": []
        }
        
        for backup in backups:
            try:
                # Extract original filename
                parts = backup.name.split('.')
                original_filename = '.'.join(parts[:-3])  # Remove timestamp and task_id and .bak
                
                if self._restore_backup(backup, original_filename):
                    results["restored"].append(original_filename)
                else:
                    results["failed"].append(original_filename)
                    
            except Exception as e:
                logger.error(f"Failed to restore {backup}: {e}")
                results["failed"].append(str(backup))
        
        return results
    
    def _restore_backup(self, backup_path: Path, original_filename: str) -> bool:
        """Restore file from backup"""
        if self.dry_run:
            return True
            
        try:
            target_path = self.output_dir / original_filename
            
            # Read backup content
            with open(backup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Write to target
            target_path.parent.mkdir(exist_ok=True, parents=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore {original_filename}: {e}")
            return False
    
    def get_file_diff(self, filename: str, version1: str, version2: str) -> Optional[str]:
        """Get diff between two versions of a file"""
        # Implementation for getting diff between specific versions
        # This would compare backup files or use git history
        
        return None