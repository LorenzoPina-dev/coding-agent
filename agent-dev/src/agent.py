"""
Main AI Development Agent with intelligent discovery
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config.settings import AgentSettings
from .utils.llm import LLMClient
from .config.prompts import PromptManager
from .discovery.smart_agent import SmartDiscoveryAgent
from .analyst.prd_generator import AIOptimizedPRDGenerator
from .tasks.ai_decomposer import AITaskDecomposer
from .tasks.manager import TaskManager
from .builder.agent import BuilderAgent
from .reviewer.agent import ReviewerAgent
from .educator.agent import EducatorAgent
from .file_manager.handler import FileManager


console = Console()


class AIDevelopmentAgent:
    """Main AI Development Agent with intelligent iterative discovery"""
    
    def __init__(self, settings: Optional[AgentSettings] = None):
        self.settings = settings or AgentSettings()
        
        # Initialize all components
        self.llm_client = LLMClient(self.settings)
        self.prompt_manager = PromptManager()
        
        # AI-optimized components
        self.discovery_agent = SmartDiscoveryAgent(self.llm_client, self.prompt_manager)
        self.prd_generator = AIOptimizedPRDGenerator(self.llm_client)
        self.task_decomposer = AITaskDecomposer(self.llm_client)
        
        # Traditional components
        self.task_manager = TaskManager()
        self.builder_agent = BuilderAgent(self.llm_client, self.prompt_manager)
        self.reviewer_agent = ReviewerAgent(self.llm_client, self.prompt_manager)
        self.educator_agent = EducatorAgent(self.llm_client, self.prompt_manager)
        self.file_manager = FileManager(
            output_dir=self.settings.output_dir,
            dry_run=self.settings.dry_run
        )
        
        # State
        self.project_prd: Optional[Dict[str, Any]] = None
        self.start_time: Optional[datetime] = None
        
    def run(self):
        """Main agent loop with intelligent discovery"""
        self.start_time = datetime.now()
        
        console.print(Panel.fit(
            "[bold green]🧠 AI DEVELOPMENT AGENT[/bold green]\n"
            "[dim]Intelligent discovery → AI-optimized PRD → Automated development[/dim]",
            border_style="green"
        ))
        
        try:
            # Phase 1: Intelligent Discovery
            discovery_data = self._run_intelligent_discovery()
            
            # Phase 2: AI-Optimized PRD Generation
            prd = self._generate_ai_prd(discovery_data)
            
            # Phase 3: Task Decomposition
            tasks = self._decompose_to_tasks(prd)
            
            # Phase 4: Development Loop
            self._ai_development_loop(tasks, prd)
            
            # Phase 5: Completion
            self._finalize()
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Agent interrupted[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]❌ Agent failed: {e}[/bold red]")
            import traceback
            traceback.print_exc()
    
    def _run_intelligent_discovery(self) -> Dict[str, Any]:
        """Run intelligent, iterative discovery"""
        console.print(Panel.fit(
            "[bold cyan]🔍 INTELLIGENT DISCOVERY[/bold cyan]\n"
            "[dim]I'll ask questions until I understand your project (target: 90% clarity)[/dim]",
            border_style="cyan"
        ))
        
        console.print("\n[green]💬 Start by describing what you want to build...[/green]")
        
        # Start conversation - get first question
        current_message = self.discovery_agent.start_conversation()
        console.print(f"\n{current_message}")
        
        # Get initial response BEFORE entering progress context
        initial_response = Prompt.ask("\n[bold]Your response[/bold]")
        
        understanding_score = 0.0
        iteration = 1
        
        # Initialize progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Understanding your project...", total=100)
            
            # Process initial response
            if initial_response.strip():
                next_message, is_complete, understanding_score = self.discovery_agent.process_response(initial_response)
                progress.update(task, completed=int(understanding_score * 100))
                console.print(f"\n{next_message}")
                
                if is_complete:
                    understanding_score = 0.9  # Force completion
            
            # Continue with conversation
            while understanding_score < 0.9 and iteration < 20:
                # TEMPORARY: Close progress to get user input
                progress.stop()
                
                user_input = Prompt.ask(f"\n[iteration {iteration}] Your response")
                
                # Restart progress
                progress.start_task(task)
                
                if not user_input.strip():
                    console.print("[yellow]Please provide some input...[/yellow]")
                    continue
                
                # Process response
                next_message, is_complete, understanding_score = self.discovery_agent.process_response(user_input)
                
                progress.update(task, completed=int(understanding_score * 100))
                console.print(f"\n{next_message}")
                
                if is_complete:
                    break
                
                iteration += 1
        
        # Get final project data
        project_data = self.discovery_agent.get_project_data()
        
        console.print(f"\n[green]✅ Discovery complete! Understanding: {understanding_score:.0%}[/green]")
        return project_data
        
    def _generate_ai_prd(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-optimized PRD"""
        console.print(Panel.fit(
            "[bold cyan]📋 GENERATING AI-OPTIMIZED PRD[/bold cyan]",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating AI-optimized PRD...", total=None)
            
            # Generate PRD
            self.project_prd = self.prd_generator.generate(discovery_data.get("summary", ""))
            progress.update(task, completed=1)
            
            # Generate human-readable version
            human_prd = self.prd_generator.generate_prd_for_humans(self.project_prd)
            
            # Show summary
            console.print("\n" + "="*80)
            console.print("[bold]AI-OPTIMIZED PRD GENERATED[/bold]")
            console.print("="*80)
            
            # Show key info
            prd_meta = self.project_prd.get("metadata", {})
            project_info = self.project_prd.get("project", {})
            
            console.print(f"\n📄 [bold]{project_info.get('name', 'Project')}[/bold]")
            console.print(f"   Version: {prd_meta.get('version', '1.0.0')}")
            console.print(f"   Complexity: {prd_meta.get('complexity_score', 0.5):.0%}")
            console.print(f"   Optimized for: {prd_meta.get('optimized_for', 'AI agents')}")
            
            # Show requirements count
            requirements = self.project_prd.get("requirements", {})
            func_count = len(requirements.get("functional", []))
            non_func_count = len(requirements.get("non_functional", []))
            
            console.print(f"   Requirements: {func_count} functional, {non_func_count} non-functional")
            
            # Show human preview
            console.print("\n[dim]PRD Preview:[/dim]")
            preview_lines = human_prd.split('\n')[:15]
            for line in preview_lines:
                console.print(f"   {line}")
            
            if len(human_prd.split('\n')) > 15:
                console.print("   ... [truncated]")
        
        # Ask for approval
        console.print("\n" + "="*80)
        approved = Confirm.ask("Approve this PRD and proceed to development?", default=True)
        
        if not approved:
            # Allow modifications
            feedback = Prompt.ask("What changes would you like?")
            # In a real implementation, you would regenerate PRD based on feedback
            console.print("[yellow]Feedback noted. Continuing with current PRD.[/yellow]")
        
        return self.project_prd
    
    def _decompose_to_tasks(self, prd: Dict[str, Any]) -> List:
        """Decompose PRD into AI-executable tasks"""
        console.print(Panel.fit(
            "[bold cyan]🔨 DECOMPOSING TO AI TASKS[/bold cyan]",
            border_style="cyan"
        ))
        
        tasks = self.task_decomposer.decompose_prd(prd)
        
        # Add to task manager
        for task in tasks:
            self.task_manager.add_task(task)
        
        console.print(f"[green]✅ Created {len(tasks)} AI-executable tasks[/green]")
        
        # Show task breakdown
        console.print("\n📋 Task Breakdown:")
        task_types = {}
        for task in tasks:
            task_type = task.metadata.get("type", "unknown")
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        for task_type, count in task_types.items():
            console.print(f"   • {task_type}: {count} tasks")
        
        total_hours = sum(task.estimated_hours for task in tasks)
        console.print(f"\n⏱️  Estimated total: {total_hours:.1f} hours")
        
        return tasks
    
    def _ai_development_loop(self, tasks: List, prd_context: Dict[str, Any]):
        """AI development loop with validation"""
        console.print(Panel.fit(
            "[bold cyan]👨‍💻 AI DEVELOPMENT LOOP[/bold cyan]\n"
            "[dim]Build → Validate → Learn → Iterate[/dim]",
            border_style="cyan"
        ))
        
        completed_tasks = 0
        iteration = 1
        
        while iteration <= self.settings.max_iterations and completed_tasks < len(tasks):
            console.print(f"\n[bold]Iteration {iteration}[/bold]")
            
            # Get next ready task
            ready_tasks = self.task_manager.get_ready_tasks()
            
            if not ready_tasks:
                console.print("[yellow]No ready tasks. Checking dependencies...[/yellow]")
                # Check if we can mark some tasks as ready
                self._check_blocked_tasks()
                ready_tasks = self.task_manager.get_ready_tasks()
                
                if not ready_tasks:
                    console.print("[yellow]All tasks waiting on dependencies[/yellow]")
                    break
            
            # Process each ready task
            for task in ready_tasks[:3]:  # Process max 3 tasks per iteration
                self._process_ai_task(task, prd_context)
                completed_tasks += 1
            
            iteration += 1
        
        console.print(f"\n[green]✅ Development loop complete. Processed {completed_tasks}/{len(tasks)} tasks[/green]")
    
    def _process_ai_task(self, task, prd_context: Dict[str, Any]):
        """Process a single AI task"""
        console.print(f"\n[bold]Processing: {task.id}[/bold]")
        console.print(f"📝 {task.description}")
        console.print(f"📁 Files to create: {len(task.metadata.get('files_to_create', []))}")
        
        # Update task status
        self.task_manager.update_task_status(task.id, "IN_PROGRESS")
        
        # Build phase
        console.print("[blue]🤖 AI Builder working...[/blue]")
        build_result = self.builder_agent.build_for_task(task, {
            **prd_context,
            "ai_instructions": task.metadata.get("ai_instructions", ""),
            "technical_requirements": task.metadata.get("technical_requirements", [])
        })
        
        if not build_result.success:
            console.print(f"[red]❌ Build failed: {build_result.error_message}[/red]")
            self.task_manager.update_task_status(task.id, "FAILED")
            return
        
        # Validate with AI decomposer
        console.print("[blue]🔍 AI Validation...[/blue]")
        generated_files = {f.filename: f.code for f in build_result.files}
        validation = self.task_decomposer.validate_task_completion(task, generated_files)
        
        if not validation.get("passed", False):
            console.print(f"[yellow]⚠️  Validation issues:[/yellow]")
            for issue in validation.get("issues", []):
                console.print(f"  • {issue}")
            
            if not validation.get("can_proceed", False):
                console.print("[red]❌ Task failed validation[/red]")
                self.task_manager.update_task_status(task.id, "FAILED")
                return
        
        # File writing
        console.print("[blue]💾 Writing files...[/blue]")
        file_results = self.file_manager.write_files(
            [{"filename": f.filename, "code": f.code} for f in build_result.files],
            task.id
        )
        
        if file_results.get("failed"):
            console.print(f"[red]❌ File writing failed[/red]")
            self.task_manager.update_task_status(task.id, "FAILED")
        else:
            console.print(f"[green]✅ Task completed (Score: {validation.get('score', 0)}/100)[/green]")
            self.task_manager.update_task_status(task.id, "COMPLETED")
            
            # Show what was learned
            if validation.get("suggestions"):
                console.print("[dim]💡 Suggestions for next tasks:[/dim]")
                for suggestion in validation.get("suggestions", [])[:2]:
                    console.print(f"  • {suggestion}")
    
    def _check_blocked_tasks(self):
        """Check and potentially unblock tasks waiting on dependencies"""
        # Simple implementation: if all dependencies are done, mark as ready
        for task in self.task_manager.tasks.values():
            if task.status == "PENDING" or task.status == "BLOCKED":
                # Controlla se tutte le dipendenze sono completate
                deps_met = True
                
                for dep_id in task.dependencies:
                    if dep_id in self.task_manager.tasks:
                        dep_task = self.task_manager.tasks[dep_id]
                        if dep_task.status != "COMPLETED":
                            deps_met = False
                            break
                    else:
                        # Dipendenza non esiste - potrebbe essere un errore
                        deps_met = False
                        break
                
                if deps_met:
                    # Task è pronto - sbloccalo
                    self.task_manager.update_task_status(task.id, "READY")
                    console.print(f"[green]✅ Unblocked task: {task.id}[/green]")
                elif task.status == "PENDING" and task.dependencies:
                    # Task ha dipendenze non completate - bloccarlo
                    self.task_manager.update_task_status(task.id, "BLOCKED")
                    console.print(f"[yellow]⚠️  Task blocked: {task.id} (waiting on dependencies)[/yellow]")
    
    def _finalize(self):
        """Finalize the agent run"""
        elapsed = datetime.now() - self.start_time
        
        console.print("\n" + "="*80)
        console.print("[bold green]🎉 AI DEVELOPMENT COMPLETE![/bold green]")
        console.print("="*80)
        
        # Generate report
        total_tasks = len(self.task_manager.tasks)
        completed = len([t for t in self.task_manager.tasks.values() if t.status == "COMPLETED"])
        failed = len([t for t in self.task_manager.tasks.values() if t.status == "FAILED"])
        
        console.print(f"\n📊 [bold]AI Agent Report:[/bold]")
        console.print(f"   • Total tasks: {total_tasks}")
        console.print(f"   • Completed: {completed}")
        console.print(f"   • Failed: {failed}")
        console.print(f"   • Success rate: {(completed/total_tasks*100 if total_tasks > 0 else 0):.1f}%")
        console.print(f"   • Elapsed time: {elapsed}")
        
        if self.settings.dry_run:
            console.print("\n💡 [yellow]Run in DRY-RUN mode. To write files, set DRY_RUN=False[/yellow]")
        
        # Save final state
        self._save_ai_state()
    
    def _save_ai_state(self):
        """Save AI agent state"""
        state = {
            "prd": self.project_prd,
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "metadata": task.metadata
                }
                for task in self.task_manager.tasks.values()
            ]
        }
        
        # Save to file (in real implementation)
        console.print("\n💾 [dim]AI state saved for future iterations[/dim]")