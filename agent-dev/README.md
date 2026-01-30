# Software Development Agent

An AI-powered agent that iteratively takes product ideas and produces production-ready codebases through structured discovery, planning, development, and review cycles.

## Features

- **Interactive Product Discovery**: Multi-phase questioning with clarification requests
- **PRD Generation & Approval**: Automatic PRD creation with diff-based approval
- **Task Management**: Granular task breakdown with dependencies and state tracking
- **Code Generation**: Production-ready code with tests and documentation
- **Review & Validation**: Automated code review with quality scoring
- **Educational Explanations**: Clear explanations of implementation choices
- **Safe File Management**: Backup, rollback, and diff tracking
- **Iterative Development**: Agile-style cycles with continuous improvement

## Architecture
software-dev-agent/
├── src/ # Main source code
│ ├── agent.py # Main agent orchestrator
│ ├── discovery/ # Product discovery agent
│ ├── analyst/ # PRD generation and analysis
│ ├── builder/ # Code generation
│ ├── reviewer/ # Code review and validation
│ ├── educator/ # Implementation explanations
│ ├── tasks/ # Task management system
│ ├── file_manager/ # Safe file operations
│ └── utils/ # Shared utilities
├── prompts/ # LLM prompt templates
├── config/ # Configuration settings
├── outputs/ # Generated code output
└── examples/ # Example runs


## Quick Start

1. **Installation**:
```bash
pip install -e .
export OPENAI_API_KEY="your-api-key"
# or
export ANTHROPIC_API_KEY="your-api-key"
```

##  Run Example:

```bash
python examples/example_run.py
```

## Run Full Agent:

```python
from src.agent import SoftwareDevAgent
from src.config.settings import AgentSettings

settings = AgentSettings(dry_run=False)
agent = SoftwareDevAgent(settings)
agent.run()
```