"""
♻️ REFACTOR AGENT V1.0 — Agent d'évolution + Auto-amélioration du code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du EvolutionAgent du Trading Bot.
Rôle: Analyse code pour propositions d'amélioration/refactoring.
Ne modifie pas directement, mais propose des changements.
Domaine: refactor, improvement, optimization, cleanup.
Personnalité: EXECUTOR (exécute les améliorations)
"""

from base_agent import BaseAgent, PERSONALITY_EXECUTOR
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class RefactorAgent(BaseAgent):
    """
    Agent qui propose et exécute des améliorations de code.
    """

    CHANGES_LOG = ".claude/memory/agent_learning/refactor_changes.json"

    def __init__(self):
        super().__init__(
            name="refactor",
            role="Propositions d'amélioration code, refactoring, optimisations",
            domain_keywords=[
                "refactor", "refactoring", "amélioration", "improvement",
                "optimization", "optim", "cleanup", "nettoyage",
                "simplify", "simplification", "duplication", "duplicate",
                "complexity", "trop complexe", "could be", "should be",
                "suggestion", "propose", "proposer", "restructure",
            ]
        )
        self._changes_log: List[Dict] = self._load_changes_log()

    def _load_changes_log(self) -> List[Dict]:
        """Charge l'historique des changements."""
        path = Path(self.CHANGES_LOG)
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_changes_log(self):
        """Sauvegarde le log des changements."""
        Path(self.CHANGES_LOG).parent.mkdir(parents=True, exist_ok=True)
        with open(self.CHANGES_LOG, "w") as f:
            json.dump(self._changes_log, f, indent=2, default=str)

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse et propose des améliorations.
        Context:
            - "code": str - code à analyser
            - "language": str - langage
            - "action": "analyze" ou "suggest" ou "apply"
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        action = context.get("action", "analyze")

        if not code.strip():
            return {
                "agent": self.name,
                "confidence": 0.5,
                "recommendation": "ABSTAIN",
                "reasoning": "No code to analyze",
                "action_items": []
            }

        if action == "analyze":
            return self._analyze_code(code, language)
        elif action == "suggest":
            return self._suggest_improvements(code, language)
        elif action == "apply":
            return self._apply_suggestion(context)
        else:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "UNKNOWN",
                "reasoning": f"Unknown action: {action}",
                "action_items": []
            }

    def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyse le code pour trouver points d'amélioration."""
        issues = self._find_improvement_opportunities(code, language)

        if not issues:
            return {
                "agent": self.name,
                "confidence": 0.9,
                "recommendation": "CLEAN",
                "reasoning": "Code looks good, no obvious improvements",
                "action_items": ["Code is well-structured"]
            }

        confidence = min(0.95, 0.5 + len(issues) * 0.1)

        action_items = [f"Improve: {i['issue']}" for i in issues[:5]]

        return {
            "agent": self.name,
            "confidence": confidence,
            "recommendation": "IMPROVEMENTS_POSSIBLE",
            "reasoning": f"Found {len(issues)} opportunities for improvement",
            "improvements": issues,
            "action_items": action_items
        }

    def _suggest_improvements(self, code: str, language: str) -> Dict[str, Any]:
        """Suggère des changements spécifiques."""
        suggestions = []

        # ────────────────────────────────────────────────────────────
        # PATTERNS UNIVERSELS
        # ────────────────────────────────────────────────────────────

        lines = code.split('\n')

        # Détecte fonctions très longues (>50 lignes)
        func_length = 0
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('async def'):
                func_length = 0
            else:
                func_length += 1
                if func_length > 50:
                    suggestions.append({
                        "type": "SPLIT_FUNCTION",
                        "issue": f"Function is {func_length} lines long",
                        "suggestion": "Break into smaller, focused functions",
                        "severity": "MEDIUM"
                    })
                    break

        # Détecte code dupliqué (mêmes patterns)
        import re
        patterns = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20:
                if stripped in patterns:
                    patterns[stripped] += 1
                else:
                    patterns[stripped] = 1

        dupes = [p for p, c in patterns.items() if c >= 3]
        if dupes:
            suggestions.append({
                "type": "EXTRACT_PATTERN",
                "issue": f"Found {len(dupes)} code patterns repeated 3+ times",
                "suggestion": "Extract into reusable function or constant",
                "severity": "MEDIUM"
            })

        # Détecte nested complexity
        if '    ' * 4 in code:  # 4+ levels indent
            suggestions.append({
                "type": "REDUCE_NESTING",
                "issue": "Deep nesting (4+ levels)",
                "suggestion": "Extract helper functions to reduce nesting",
                "severity": "LOW"
            })

        # ────────────────────────────────────────────────────────────
        # SPÉCIFIQUE PYTHON
        # ────────────────────────────────────────────────────────────

        if language in ["python", "py"]:
            # List comprehension au lieu de boucles
            if "for " in code and "append(" in code:
                suggestions.append({
                    "type": "USE_COMPREHENSION",
                    "issue": "Using loop with append instead of comprehension",
                    "suggestion": "Use list/dict/set comprehension",
                    "example": "[x*2 for x in items]",
                    "severity": "LOW"
                })

            # Type hints manquants
            if "def " in code and "->" not in code:
                suggestions.append({
                    "type": "ADD_TYPE_HINTS",
                    "issue": "Function parameters lack type hints",
                    "suggestion": "Add type annotations for clarity",
                    "example": "def func(x: int) -> str:",
                    "severity": "LOW"
                })

        # ────────────────────────────────────────────────────────────
        # SPÉCIFIQUE JS/TS
        # ────────────────────────────────────────────────────────────

        if language in ["javascript", "js", "typescript", "ts"]:
            # Promises vs async/await
            if ".then(" in code and "async " not in code:
                suggestions.append({
                    "type": "USE_ASYNC_AWAIT",
                    "issue": "Using .then() chains instead of async/await",
                    "suggestion": "Modernize to async/await syntax",
                    "severity": "LOW"
                })

        if not suggestions:
            suggestions = self._find_improvement_opportunities(code, language)

        action_items = [f"💡 {s['suggestion']}" for s in suggestions[:5]]

        return {
            "agent": self.name,
            "confidence": 0.85,
            "recommendation": "SUGGESTIONS",
            "reasoning": f"Found {len(suggestions)} refactoring suggestions",
            "suggestions": suggestions,
            "action_items": action_items
        }

    def _apply_suggestion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre une suggestion appliquée."""
        suggestion = context.get("suggestion", "")
        result = context.get("result", "unknown")

        change_record = {
            "timestamp": datetime.now().isoformat(),
            "suggestion": suggestion,
            "result": result,
            "applied": result == "success"
        }
        self._changes_log.append(change_record)
        self._save_changes_log()

        return {
            "agent": self.name,
            "confidence": 0.95,
            "recommendation": "RECORDED",
            "reasoning": f"Suggestion {result}",
            "action_items": [
                f"Total changes applied: {sum(1 for c in self._changes_log if c['applied'])}"
            ]
        }

    def _find_improvement_opportunities(self, code: str, language: str) -> List[Dict]:
        """Trouve opportunités d'amélioration."""
        opportunities = []

        # Très général
        if "TODO" in code or "FIXME" in code:
            opportunities.append({
                "type": "UNRESOLVED_TODO",
                "issue": "Contains unresolved TODO/FIXME comments",
                "severity": "LOW"
            })

        if code.count('\n') > 500:
            opportunities.append({
                "type": "LARGE_FILE",
                "issue": "File is very large (500+ lines)",
                "suggestion": "Consider splitting into modules",
                "severity": "LOW"
            })

        return opportunities
