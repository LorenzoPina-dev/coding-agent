import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config.settings import AgentSettings
from .utils.llm import LLMClient
from .utils.logger import get_logger
from .config.prompts import PromptManager
from .discovery.agent import DiscoveryAgent
from .analyst.agent import AnalystAgent
from .builder.agent import BuilderAgent
from .reviewer.agent import ReviewerAgent
from .educator.agent import EducatorAgent
from .tasks.manager import TaskManager
from .file_manager.handler import FileManager


logger = get_logger(__name__)
console = Console()


class SoftwareDevAgent:
    def __init__(self, settings: Optional[AgentSettings] = None):
        self.settings = settings or AgentSettings()
        self.prompt_manager = PromptManager()
        
        # Initialize components
        self.llm_client = LLMClient(self.settings)
        self.discovery_agent = DiscoveryAgent(self.llm_client, self.prompt_manager)
        self.analyst_agent = AnalystAgent(self.llm_client, self.prompt_manager)
        self.builder_agent = BuilderAgent(self.llm_client, self.prompt_manager)
        self.reviewer_agent = ReviewerAgent(self.llm_client, self.prompt_manager)
        self.educator_agent = EducatorAgent(self.llm_client, self.prompt_manager)
        self.task_manager = TaskManager()
        self.file_manager = FileManager(
            output_dir=self.settings.output_dir,
            dry_run=self.settings.dry_run
        )
        
        # State
        self.current_state = "IDLE"
        self.current_task: Optional[str] = None
        self.iteration_count = 0
        self.start_time: Optional[datetime] = None
        
    def run(self):
        """Main agent loop"""
        self.start_time = datetime.now()
        console.print("[bold green]🚀 Software Development Agent Started[/bold green]")
        
        try:
            # Phase 1: Discovery
            discovery_data = self._run_discovery()
            
            # Phase 2: PRD Generation and Approval
            prd = self._generate_and_approve_prd(discovery_data)
            
            # Phase 3: Task Generation
            tasks = self._generate_tasks(prd)
            
            # Phase 4: Development Loop
            self._development_loop(tasks, prd)
            
            # Phase 5: Completion
            self._finalize()
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Agent interrupted by user[/bold yellow]")
            self._handle_interruption()
        except Exception as e:
            logger.error(f"Agent failed: {e}", exc_info=True)
            console.print(f"[bold red]❌ Agent failed: {e}[/bold red]")
            raise
    
    def _run_discovery(self):
        """Run interactive product discovery"""
        console.print("\n[bold cyan]📝 PRODUCT DISCOVERY[/bold cyan]")
        console.print("[yellow]Rispondi su UNA RIGA per ogni domanda[/yellow]")
        console.print("-" * 60)
        
        # Inizia discovery
        current_prompt = self.discovery_agent.start_discovery()
        
        while True:
            # Mostra la domanda in modo chiaro
            console.print(f"\n[bold]{current_prompt}[/bold]")
            
            # Prendi input
            user_input = Prompt.ask("➤ Your answer")
            
            # Processa
            result = self.discovery_agent.process_response(user_input)
            
            # Debug
            console.print(f"[dim]Phase: {result.phase}, Complete: {result.is_complete}[/dim]")
            
            if result.needs_clarification:
                console.print("[yellow]🤔 Need clarification:[/yellow]")
                for issue in result.needs_clarification:
                    console.print(f"  - {issue}")
                current_prompt = f"Please clarify: {result.needs_clarification[0]}"
                continue
            
            if result.is_complete:
                console.print("[green]✅ Discovery complete![/green]")
                return result.answers
            
            # Prepara prossima domanda
            current_prompt = self.prompt_manager.get_prompt(
                "discovery",
                f"phase_{result.phase.lower()}"
            )
    
    def _generate_and_approve_prd(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRD and get user approval"""
        console.print("[bold cyan]📋 PRD Generation Phase[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating PRD...", total=None)
            
            # Generate PRD
            prd_doc = self.analyst_agent.generate_prd(discovery_data)
            progress.update(task, completed=1)
            
            # Show PRD summary
            console.print("\n" + "="*80)
            console.print("[bold]Generated PRD Summary:[/bold]")
            console.print(self.analyst_agent.get_prd_summary())
            console.print("="*80)
            
            # Get approval
            approved = False
            while not approved:
                approval = Confirm.ask("Do you approve this PRD?", default=False)
                
                if approval:
                    self.analyst_agent.approve_prd()
                    approved = True
                    console.print("[green]✅ PRD Approved![/green]")
                else:
                    feedback = Prompt.ask("What changes would you like?")
                    
                    # Update PRD
                    update_result = self.analyst_agent.update_prd(feedback)
                    
                    # Show diff
                    console.print("\n[bold]Changes made:[/bold]")
                    console.print(update_result["diff"])
                    
                    # Show updated summary
                    console.print("\n[bold]Updated PRD Summary:[/bold]")
                    console.print(self.analyst_agent.get_prd_summary())
        
        return prd_doc.dict()
    
    def _generate_tasks(self, prd: Dict[str, Any]) -> list:
        """Generate tasks from PRD"""
        console.print("[bold cyan]📋 Task Generation Phase[/bold cyan]")
        
        tasks = self.task_manager.create_tasks_from_prd(prd)
        
        console.print(f"[green]✅ Generated {len(tasks)} tasks[/green]")
        for task in tasks:
            console.print(f"  • {task.id}: {task.description}")
        
        return tasks
    
    def _development_loop(self, tasks: list, prd_context: Dict[str, Any]):
        """Main development loop"""
        console.print("[bold cyan]👨‍💻 Development Phase[/bold cyan]")
        
        self.iteration_count = 0
        
        while self.iteration_count < self.settings.max_iterations:
            self.iteration_count += 1
            console.print(f"\n[bold]Iteration {self.iteration_count}[/bold]")
            
            # Get ready tasks
            ready_tasks = self.task_manager.get_ready_tasks()
            
            if not ready_tasks:
                console.print("[yellow]⚠️  No ready tasks. Checking for completion...[/yellow]")
                if self._check_completion():
                    break
                continue
            
            # Process each ready task
            for task in ready_tasks:
                self._process_task(task, prd_context)
            
            # Check if we should continue
            if not self._should_continue():
                break
        
        console.print("[green]✅ Development loop complete![/green]")
    
    def _process_task(self, task, prd_context):
        """Process a single task through builder-reviewer-educator loop"""
        console.print(f"\n[bold]Processing Task: {task.id}[/bold]")
        console.print(f"Description: {task.description}")
        
        # Update task status
        self.task_manager.update_task_status(task.id, "IN_PROGRESS")
        
        # Build phase
        console.print("[blue]🔨 Building...[/blue]")
        build_result = self.builder_agent.build_for_task(task, prd_context)
        
        if not build_result.success:
            console.print(f"[red]❌ Build failed: {build_result.error_message}[/red]")
            self.task_manager.update_task_status(task.id, "FAILED")
            return
        
        console.print(f"[green]✅ Built {len(build_result.files)} files[/green]")
        
        # Review phase
        console.print("[blue]🔍 Reviewing...[/blue]")
        all_passed = True
        
        for code_file in build_result.files:
            review_result = self.reviewer_agent.review_code(task.id, code_file)
            
            if not review_result.passed:
                all_passed = False
                console.print(f"[yellow]⚠️  Review issues in {code_file.filename}:[/yellow]")
                for issue in review_result.issues:
                    console.print(f"  • {issue.severity.upper()}: {issue.description}")
        
        if not all_passed:
            console.print("[red]❌ Review failed. Task marked for revision.[/red]")
            self.task_manager.update_task_status(task.id, "FAILED")
            return
        
        # Educator phase
        console.print("[blue]📚 Generating explanation...[/blue]")
        review_results = [r for r in self.reviewer_agent.review_history if r.task_id == task.id]
        explanation = self.educator_agent.explain_implementation(
            task.id, build_result.files, review_results, prd_context
        )
        
        console.print(f"[green]✅ Explanation generated: {explanation.title}[/green]")
        
        # File writing phase
        console.print("[blue]💾 Writing files...[/blue]")
        file_results = self.file_manager.write_files(
            [{"filename": f.filename, "code": f.code} for f in build_result.files],
            task.id
        )
        
        if file_results["failed"]:
            console.print(f"[red]❌ Failed to write {len(file_results['failed'])} files[/red]")
            for failed in file_results["failed"]:
                console.print(f"  • {failed['filename']}: {failed['error']}")
            self.task_manager.update_task_status(task.id, "FAILED")
        else:
            console.print(f"[green]✅ Successfully wrote {len(file_results['success'])} files[/green]")
            self.task_manager.update_task_status(task.id, "COMPLETED")
            
            # Show educator summary
            console.print("\n[bold]📖 What was implemented:[/bold]")
            console.print(explanation.summary)
            
            console.print("\n[bold]🎯 Key concepts:[/bold]")
            for concept in explanation.key_concepts[:3]:
                console.print(f"  • {concept}")
    
    def _check_completion(self) -> bool:
        """Check if all tasks are complete"""
        pending_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.status not in ["COMPLETED", "FAILED"]
        ]
        
        return len(pending_tasks) == 0
    
    def _should_continue(self) -> bool:
        """Determine if development should continue"""
        if self.iteration_count >= self.settings.max_iterations:
            console.print(f"[yellow]⚠️  Reached max iterations ({self.settings.max_iterations})[/yellow]")
            return False
        
        # Check for incomplete tasks
        incomplete_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.status not in ["COMPLETED"]
        ]
        
        if not incomplete_tasks:
            return False
        
        # Ask user if they want to continue
        if self.settings.require_confirmation:
            return Confirm.ask("Continue development?", default=True)
        
        return True
    
    def _finalize(self):
        """Finalize the agent run"""
        elapsed = datetime.now() - self.start_time
        
        console.print("\n" + "="*80)
        console.print("[bold green]🎉 Development Complete![/bold green]")
        console.print("="*80)
        
        # Generate report
        total_tasks = len(self.task_manager.tasks)
        completed_tasks = len([t for t in self.task_manager.tasks.values() if t.status == "COMPLETED"])
        failed_tasks = len([t for t in self.task_manager.tasks.values() if t.status == "FAILED"])
        
        console.print(f"\n[bold]📊 Summary Report:[/bold]")
        console.print(f"  • Total iterations: {self.iteration_count}")
        console.print(f"  • Total tasks: {total_tasks}")
        console.print(f"  • Completed: {completed_tasks}")
        console.print(f"  • Failed: {failed_tasks}")
        console.print(f"  • Elapsed time: {elapsed}")
        
        if self.settings.dry_run:
            console.print("\n[yellow]⚠️  Run in DRY-RUN mode - no files were actually written[/yellow]")
        
        # Save final state
        self._save_state()
    
    def _handle_interruption(self):
        """Handle user interruption gracefully"""
        console.print("\n[yellow]Saving current state...[/yellow]")
        self._save_state()
        
        # Offer rollback
        if Confirm.ask("Rollback to last stable state?", default=False):
            if self.current_task:
                self.file_manager.rollback_to_task(self.current_task)
                console.print("[green]✅ Rollback complete[/green]")
    
    def _save_state(self):
        """Save agent state"""
        state = {
            "iteration_count": self.iteration_count,
            "current_task": self.current_task,
            "task_states": {
                task_id: task.status
                for task_id, task in self.task_manager.tasks.items()
            }
        }
        
        state_file = self.file_manager.output_dir / "agent_state.json"
        
        if not self.settings.dry_run:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)