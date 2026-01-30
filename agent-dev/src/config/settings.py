from pydantic_settings import BaseSettings
from typing import Optional, Literal
from enum import Enum


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    OLLAMA = "ollama"


class AgentSettings(BaseSettings):
    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.OLLAMA
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "deepseek-coder:6.7b"
    model_name: str = "deepseek-coder:6.7b"
    temperature: float = 0.1
    max_tokens: int = 4000
    
    # Agent Behavior
    dry_run: bool = True
    max_iterations: int = 100
    task_timeout_seconds: int = 300
    max_retries: int = 3
    
    # File Management
    output_dir: str = "outputs"
    backup_dir: str = "backups"
    max_backups: int = 10
    
    # Safety
    require_confirmation: bool = True
    confidence_threshold: float = 0.7
    max_file_size_mb: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    enable_telemetry: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"