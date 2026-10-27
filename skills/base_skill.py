"""
Base class for Specialized Engineering Skills.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class SkillEvaluationResult(BaseModel):
    skill_name: str
    status: str  # "PASS", "WARNING", "FAIL", "RECOMMENDATION"
    summary: str
    calculations: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    cad_parameters: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class BaseEngineeringSkill(ABC):
    """Abstract base engineering skill."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def evaluate(self, request: str, context: Dict[str, Any]) -> SkillEvaluationResult:
        """Evaluate request and return engineering guidance and CAD parameters."""
        pass
