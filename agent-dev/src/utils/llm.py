import os
from typing import Dict, Any, List, Optional, Union
import json
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI, AsyncOpenAI
from anthropic import Anthropic
import instructor
from pydantic import BaseModel
from ..config.settings import AgentSettings, LLMProvider


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
    
    def generate(self, model: str, prompt: str, system: Optional[str] = None, 
                 temperature: float = 0.1, max_tokens: int = 4000, 
                 format: Optional[str] = None) -> str:
        """Generate text using Ollama API"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
            
        if format:
            payload["format"] = format
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid response from Ollama: {str(e)}")


class LLMClient:
    def __init__(self, settings: AgentSettings):
        self.settings = settings
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        if self.settings.llm_provider == LLMProvider.OPENAI:
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is required")
            return OpenAI(api_key=self.settings.openai_api_key)
        elif self.settings.llm_provider == LLMProvider.ANTHROPIC:
            if not self.settings.anthropic_api_key:
                raise ValueError("Anthropic API key is required")
            return Anthropic(api_key=self.settings.anthropic_api_key)
        elif self.settings.llm_provider == LLMProvider.OLLAMA:
            return OllamaClient(base_url=self.settings.ollama_base_url)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Generate text from LLM"""
        try:
            if self.settings.llm_provider == LLMProvider.OPENAI:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.settings.model_name,
                    messages=messages,
                    temperature=self.settings.temperature,
                    max_tokens=self.settings.max_tokens,
                    response_format=response_format,
                    **kwargs
                )
                return response.choices[0].message.content
            
            elif self.settings.llm_provider == LLMProvider.ANTHROPIC:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.messages.create(
                    model=self.settings.model_name,
                    max_tokens=self.settings.max_tokens,
                    temperature=self.settings.temperature,
                    system=system_prompt,
                    messages=messages,
                    **kwargs
                )
                return response.content[0].text
            
            elif self.settings.llm_provider == LLMProvider.OLLAMA:
                # Format for Ollama
                format_str = None
                if response_format and response_format.get("type") == "json_object":
                    format_str = "json"
                
                return self.client.generate(
                    model=self.settings.ollama_model,
                    prompt=prompt,
                    system=system_prompt,
                    temperature=self.settings.temperature,
                    max_tokens=self.settings.max_tokens,
                    format=format_str
                )
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")
                
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")
    
    def generate_structured(
        self,
        prompt: str,
        response_model: BaseModel,
        system_prompt: Optional[str] = None
    ) -> BaseModel:
        """Generate structured output using Pydantic model"""
        try:
            if self.settings.llm_provider == LLMProvider.OPENAI:
                client = instructor.from_openai(self.client)
                return client.chat.completions.create(
                    model=self.settings.model_name,
                    response_model=response_model,
                    messages=[
                        {"role": "system", "content": system_prompt or ""},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.settings.temperature,
                )
            else:
                # For Ollama and Anthropic, use JSON mode
                format_info = {"type": "json_object"}
                response = self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    response_format=format_info
                )
                
                try:
                    # Parse JSON response
                    json_data = json.loads(response)
                    return response_model.parse_obj(json_data)
                except json.JSONDecodeError:
                    # Try to extract JSON from text response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_data = json.loads(json_match.group())
                        return response_model.parse_obj(json_data)
                    else:
                        raise Exception(f"Failed to parse JSON from response: {response[:200]}")
                        
        except Exception as e:
            raise Exception(f"Structured generation failed: {str(e)}")