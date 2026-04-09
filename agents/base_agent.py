"""
🧠 BASE AGENT V1.0 — Cerveau commun pour Claude Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du Trading Bot avec 3 domaines d'expertise:
- ANALYST: code quality, patterns, best practices
- EXECUTOR: implementation, refactoring, fixes
- GUARDIAN: security, performance, edge cases

Chaque agent a un domaine (domain_keywords) où il est expert.
Débat collectif automatique quand orchestrator demande "ask_all".
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import json


# ======================== PERSONNALITÉS V1.0 ==================
PERSONALITY_ANALYST    = "ANALYST"     # Détecte les problèmes, patterns
PERSONALITY_EXECUTOR   = "EXECUTOR"    # Implémente, refactorise, corrige
PERSONALITY_GUARDIAN   = "GUARDIAN"    # Sécurité, perfs, edge cases

# Mapping agent → personnalité
AGENT_PERSONALITY_MAP: Dict[str, str] = {
    "code_analyzer":    PERSONALITY_ANALYST,
    "security":         PERSONALITY_GUARDIAN,
    "performance":      PERSONALITY_GUARDIAN,
    "learning":         PERSONALITY_ANALYST,
    "supervisor":       PERSONALITY_EXECUTOR,
}

PERSONALITY_PROFILES: Dict[str, Dict] = {
    PERSONALITY_ANALYST: {
        "label": "🔵 ANALYST",
        "bias": "détection problèmes",
        "description": "Détecte patterns, problèmes, opportunités d'amélioration"
    },
    PERSONALITY_EXECUTOR: {
        "label": "🟢 EXECUTOR",
        "bias": "implémentation directe",
        "description": "Exécute, implémente, refactorise avec confiance"
    },
    PERSONALITY_GUARDIAN: {
        "label": "🔴 GUARDIAN",
        "bias": "protection & compliance",
        "description": "Sécurité, performance, edge cases, veto sur risques"
    },
}

# Mots-clés débat collectif (tous les agents participent)
_DEBATE_KEYWORDS = [
    "analyse code", "code review", "refactor", "sécurité",
    "performance", "bug", "erreur", "synthèse", "débat",
    "cerveau collectif", "décision finale", "orchestrator",
    "ask_all", "round", "collective", "final decision"
]


class BaseAgent(ABC):
    """
    Agent de base pour Claude Code — hérite des concepts du trading bot.
    Chaque agent a:
    - un nom, rôle, domaine d'expertise
    - une personnalité (ANALYST, EXECUTOR, GUARDIAN)
    - des domain_keywords pour savoir s'il doit répondre
    """

    def __init__(
        self,
        name: str,
        role: str = None,
        description: str = None,
        domain_keywords: List[str] = None
    ):
        self.name = name
        self.role = role or description
        self.description = description or role
        self.domain_keywords = domain_keywords or []
        self.created_at = datetime.now().isoformat()

        # Personnalité
        _p_key = AGENT_PERSONALITY_MAP.get(name, PERSONALITY_ANALYST)
        self.personality = _p_key
        self.personality_profile = PERSONALITY_PROFILES[_p_key]

        # History
        self._response_history: List[Dict] = []

    def is_in_my_domain(self, question: str) -> bool:
        """Retourne True si la question touche mon domaine d'expertise."""
        q = question.lower()

        # Débat collectif = tous les agents participent
        if any(kw in q for kw in _DEBATE_KEYWORDS):
            return True

        # Domaine personnel
        return any(kw in q for kw in self.domain_keywords)

    @abstractmethod
    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Répond à une question dans mon domaine.
        Retourne {
            "agent": self.name,
            "confidence": float (0.0-1.0),
            "recommendation": str,
            "reasoning": str,
            "action_items": List[str]
        }
        """
        pass

    def safe_respond(self, context: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        """
        Appelle respond() avec timeout et error handling.
        """
        try:
            response = self.respond(context)

            # Validation réponse
            if not isinstance(response, dict):
                return self._error_response("Invalid response type")

            # Log history
            self._response_history.append({
                "timestamp": datetime.now().isoformat(),
                "input": context,
                "output": response
            })

            return response
        except Exception as e:
            return self._error_response(f"Error: {str(e)}")

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Retourne une réponse d'erreur structurée."""
        return {
            "agent": self.name,
            "confidence": 0.0,
            "recommendation": "ABSTAIN",
            "reasoning": error_msg,
            "action_items": []
        }

    def explain_term(self, term: str) -> str:
        """Explique un terme technique (pour KB)."""
        return f"{term} (explained by {self.name})"

    def get_summary(self) -> Dict[str, Any]:
        """Résumé de l'agent."""
        return {
            "name": self.name,
            "role": self.role,
            "personality": self.personality,
            "domain_keywords": self.domain_keywords,
            "response_count": len(self._response_history),
            "created_at": self.created_at
        }
