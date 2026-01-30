from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import difflib
from datetime import datetime
from ..utils.llm import LLMClient
from ..config.prompts import PromptManager
from .prd_generator import PRDGenerator


class PRDSection(BaseModel):
    title: str
    content: str
    version: int = 1
    last_modified: datetime = Field(default_factory=datetime.now)


class PRDDocument(BaseModel):
    id: str
    title: str
    version: int = 1
    created_date: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)
    sections: Dict[str, PRDSection]
    status: str = "draft"
    approved: bool = False
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None


class PRDChange(BaseModel):
    section: str
    old_content: Optional[str]
    new_content: str
    change_type: str  # "added", "modified", "deleted"


class AnalystAgent:
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.prd_generator = PRDGenerator(llm_client, prompt_manager)
        self.current_prd: Optional[PRDDocument] = None
        self.prd_history: list[PRDDocument] = []
        
    def generate_prd(self, discovery_data: Dict[str, Any]) -> PRDDocument:
        """Generate PRD from discovery data"""
        prd_content = self.prd_generator.generate(discovery_data)
        
        self.current_prd = PRDDocument(
            id=f"PRD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=prd_content.get("title", "Product Requirements Document"),
            sections={
                section["title"]: PRDSection(
                    title=section["title"],
                    content=section["content"]
                )
                for section in prd_content.get("sections", [])
            }
        )
        
        self.prd_history.append(self.current_prd)
        return self.current_prd
    
    def get_prd_summary(self) -> str:
        """Get a formatted summary of the PRD"""
        if not self.current_prd:
            return "No PRD generated yet."
        
        summary = f"# {self.current_prd.title}\n"
        summary += f"Version: {self.current_prd.version}\n"
        summary += f"Status: {self.current_prd.status}\n\n"
        
        for section_name, section in self.current_prd.sections.items():
            summary += f"## {section.title}\n"
            # Truncate long content for summary
            content_preview = section.content[:500] + "..." if len(section.content) > 500 else section.content
            summary += f"{content_preview}\n\n"
        
        return summary
    
    def update_prd(self, feedback: str) -> Dict[str, Any]:
        """Update PRD based on feedback"""
        if not self.current_prd:
            raise ValueError("No PRD to update")
        
        # Generate updated PRD
        update_prompt = self.prompt_manager.get_prompt(
            "analyst",
            "prd_update",
            current_prd=json.dumps(self.current_prd.dict(), indent=2),
            feedback=feedback
        )
        
        updated_content = self.llm_client.generate(
            prompt=update_prompt,
            response_format={"type": "json_object"}
        )
        
        # Create new version
        old_prd = self.current_prd
        updated_data = json.loads(updated_content)
        
        new_prd = PRDDocument(
            id=old_prd.id,
            title=updated_data.get("title", old_prd.title),
            version=old_prd.version + 1,
            sections={
                section["title"]: PRDSection(
                    title=section["title"],
                    content=section["content"],
                    version=old_prd.sections.get(section["title"], PRDSection(title=section["title"], content="")).version + 1
                )
                for section in updated_data.get("sections", [])
            }
        )
        
        # Calculate changes
        changes = self._calculate_changes(old_prd, new_prd)
        
        self.prd_history.append(new_prd)
        self.current_prd = new_prd
        
        return {
            "new_prd": new_prd,
            "changes": changes,
            "diff": self._generate_diff(old_prd, new_prd)
        }
    
    def approve_prd(self, approver: str = "user") -> bool:
        """Approve the current PRD"""
        if not self.current_prd:
            return False
        
        self.current_prd.status = "approved"
        self.current_prd.approved = True
        self.current_prd.approved_by = approver
        self.current_prd.approval_date = datetime.now()
        
        return True
    
    def _calculate_changes(self, old_prd: PRDDocument, new_prd: PRDDocument) -> list[PRDChange]:
        """Calculate changes between PRD versions"""
        changes = []
        
        # Check for modified sections
        for section_name in set(old_prd.sections.keys()) | set(new_prd.sections.keys()):
            old_section = old_prd.sections.get(section_name)
            new_section = new_prd.sections.get(section_name)
            
            if old_section and not new_section:
                # Section deleted
                changes.append(PRDChange(
                    section=section_name,
                    old_content=old_section.content,
                    new_content="",
                    change_type="deleted"
                ))
            elif not old_section and new_section:
                # Section added
                changes.append(PRDChange(
                    section=section_name,
                    old_content=None,
                    new_content=new_section.content,
                    change_type="added"
                ))
            elif old_section.content != new_section.content:
                # Section modified
                changes.append(PRDChange(
                    section=section_name,
                    old_content=old_section.content,
                    new_content=new_section.content,
                    change_type="modified"
                ))
        
        return changes
    
    def _generate_diff(self, old_prd: PRDDocument, new_prd: PRDDocument) -> str:
        """Generate diff between PRD versions"""
        diff_output = []
        
        for section_name in set(old_prd.sections.keys()) | set(new_prd.sections.keys()):
            old_content = old_prd.sections.get(section_name, PRDSection(title=section_name, content="")).content
            new_content = new_prd.sections.get(section_name, PRDSection(title=section_name, content="")).content
            
            if old_content != new_content:
                diff = difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f"{section_name} (v{old_prd.version})",
                    tofile=f"{section_name} (v{new_prd.version})",
                    lineterm=""
                )
                diff_output.extend(diff)
        
        return "\n".join(diff_output)