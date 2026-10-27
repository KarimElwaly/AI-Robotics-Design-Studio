"""
Multi-Provider LLM Gateway for AI Robotics Design Studio.
Supports Anthropic Claude, OpenAI, and Local/Mock offline agents.
Reads API keys securely from environment variables (never hard-coded).
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("LLMGateway")


class LLMConfig(BaseModel):
    provider: str = "local"  # "anthropic", "openai", "local"
    model_name: str = "deterministic-engineering-manager"
    temperature: float = 0.2
    max_tokens: int = 4096


class LLMGateway:
    """Manages multi-provider LLM calling with tool schemas and fallbacks."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()

    def set_provider(self, provider: str, model_name: Optional[str] = None):
        self.config.provider = provider.lower()
        if model_name:
            self.config.model_name = model_name
        elif self.config.provider == "anthropic":
            self.config.model_name = "claude-3-5-sonnet-20241022"
        elif self.config.provider == "openai":
            self.config.model_name = "gpt-4o"
        else:
            self.config.model_name = "deterministic-engineering-manager"

    def get_api_key(self) -> Optional[str]:
        if self.config.provider == "anthropic":
            return os.environ.get("ANTHROPIC_API_KEY")
        elif self.config.provider == "openai":
            return os.environ.get("OPENAI_API_KEY")
        return None

    def call_llm(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches prompt to selected LLM provider.
        If API key is missing or provider is 'local', falls back seamlessly
        to deterministic local engineering reasoning engine.
        """
        api_key = self.get_api_key()

        if self.config.provider == "anthropic" and api_key:
            try:
                import urllib.request
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                payload = {
                    "model": self.config.model_name,
                    "max_tokens": self.config.max_tokens,
                    "system": system_prompt,
                    "messages": messages,
                }
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = "".join(b.get("text", "") for b in data.get("content", []))
                    return {"text": text, "provider": "anthropic", "model": self.config.model_name}
            except Exception as e:
                logger.warning(f"Anthropic API call failed ({e}). Falling back to local reasoning.")

        elif self.config.provider == "openai" and api_key:
            try:
                import urllib.request
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                api_messages = [{"role": "system", "content": system_prompt}] + messages
                payload = {
                    "model": self.config.model_name,
                    "messages": api_messages,
                    "temperature": self.config.temperature,
                }
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["choices"][0]["message"]["content"]
                    return {"text": text, "provider": "openai", "model": self.config.model_name}
            except Exception as e:
                logger.warning(f"OpenAI API call failed ({e}). Falling back to local reasoning.")

        # Local deterministic fallback
        last_user_msg = messages[-1]["content"] if messages else ""
        return {
            "text": f"Parsed design requirement: '{last_user_msg}'. Dispatching to specialized engineering skills.",
            "provider": "local",
            "model": "deterministic-engineering-manager",
        }


# Singleton gateway
llm_gateway = LLMGateway()
