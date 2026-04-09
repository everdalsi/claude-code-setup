"""
Claude Code Agent System V1.0 — Multi-agent orchestration pour développement software

9 Agents specialisés (adapté du Trading Bot avec 57 agents):

Core Agents:
- base_agent: Classe de base — 3 personnalités (ANALYST, EXECUTOR, GUARDIAN)
- supervisor_agent: Orchestre décisions collectives via vote pondéré
- learning_agent: Mémoire persistante + scoring patterns

Analysis Agents:
- code_analyzer_agent: Détecte erreurs, imports cassés, antipatterns
- security_agent: OWASP Top 10 — injection, XSS, auth, secrets
- pattern_agent: Design patterns et anti-patterns

Improvement Agents:
- refactor_agent: Propositions refactoring, optimisations, simplifications
- health_monitor_agent: Watchdog — santé système, anomalies, diagnostics
- research_agent: Best practices, documentation, contexte

Usage:
    from agents.supervisor_agent import SupervisorAgent
    from agents.orchestrator import CodeOrchestrator

    orch = CodeOrchestrator()
    result = orch.analyze_code("code", "python")
"""

from .base_agent import BaseAgent, PERSONALITY_ANALYST, PERSONALITY_EXECUTOR, PERSONALITY_GUARDIAN
from .code_analyzer_agent import CodeAnalyzerAgent
from .learning_agent import LearningAgent
from .supervisor_agent import SupervisorAgent
from .security_agent import SecurityAgent
from .health_monitor_agent import HealthMonitorAgent
from .refactor_agent import RefactorAgent
from .research_agent import ResearchAgent
from .pattern_agent import PatternAgent

__all__ = [
    "BaseAgent",
    "CodeAnalyzerAgent",
    "LearningAgent",
    "SupervisorAgent",
    "SecurityAgent",
    "HealthMonitorAgent",
    "RefactorAgent",
    "ResearchAgent",
    "PatternAgent",
    "PERSONALITY_ANALYST",
    "PERSONALITY_EXECUTOR",
    "PERSONALITY_GUARDIAN",
]

__version__ = "1.0.0"
__agents__ = [
    "code_analyzer",
    "security",
    "pattern",
    "learning",
    "health_monitor",
    "refactor",
    "research",
    "supervisor",
]
