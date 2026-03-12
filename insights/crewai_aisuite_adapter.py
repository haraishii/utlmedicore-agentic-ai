"""
CrewAI Adapter for aisuite
Allows CrewAI to use your existing aisuite models
"""

from crewai import LLM
from aisuite import Client
from typing import Any, Dict, Optional

class AISuiteLLM(LLM):
    """
    Custom LLM wrapper for CrewAI that uses aisuite
    
    This allows CrewAI agents to use the same models as your
    monitoring agents (lfm2.5-thinking:1.2b)
    """
    
    def __init__(self, model: str, temperature: float = 0.2):
        """
        Args:
            model: aisuite model string (e.g., "ollama:lfm2.5-thinking:1.2b")
            temperature: Model temperature
        """
        self.model = model
        self.temperature = temperature
        self.client = Client()
        
    def call(self, messages: list, **kwargs) -> str:
        """
        CrewAI calls this method to get LLM response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[CREWAI-AISUITE] Error: {e}")
            return f"Error generating response: {str(e)}"
    
    def __call__(self, *args, **kwargs):
        """Alternative call method"""
        if args and isinstance(args[0], list):
            return self.call(args[0], **kwargs)
        return self.call(*args, **kwargs)


def get_aisuite_llm(model: str = "ollama:lfm2.5-thinking:1.2b", 
                    temperature: float = 0.2) -> AISuiteLLM:
    """
    Factory function to create aisuite-powered LLM for CrewAI
    
    Usage:
        llm = get_aisuite_llm("ollama:lfm2.5-thinking:1.2b")
        agent = Agent(role="Analyst", llm=llm, ...)
    """
    return AISuiteLLM(model=model, temperature=temperature)
