"""
🎯 PATTERN AGENT V1.0 — Reconnaissance de patterns et anti-patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du PatternRecognitionAgent du Trading Bot.
Rôle: Détecte patterns connus dans le code (design patterns, antipatterns).
Domaine: pattern, design pattern, antipattern, smell, architecture.
Personnalité: ANALYST
"""

from base_agent import BaseAgent, PERSONALITY_ANALYST
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path
import re


class PatternAgent(BaseAgent):
    """
    Agent qui reconnaît patterns et anti-patterns dans le code.
    """

    PATTERNS_DB = ".claude/memory/agent_learning/patterns_detected.json"

    def __init__(self):
        super().__init__(
            name="pattern",
            role="Reconnaissance de design patterns, anti-patterns, architecture patterns",
            domain_keywords=[
                "pattern", "design pattern", "antipattern", "anti-pattern",
                "smell", "code smell", "architecture", "structure",
                "singleton", "factory", "builder", "observer", "strategy",
                "decorator", "adapter", "facade", "proxy", "chain",
                "recogni", "détecte", "détect", "identify",
            ]
        )
        self._patterns_db: List[Dict] = self._load_patterns_db()

    def _load_patterns_db(self) -> List[Dict]:
        """Charge la base de patterns."""
        path = Path(self.PATTERNS_DB)
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_patterns_db(self):
        """Sauvegarde la base."""
        Path(self.PATTERNS_DB).parent.mkdir(parents=True, exist_ok=True)
        with open(self.PATTERNS_DB, "w") as f:
            json.dump(self._patterns_db, f, indent=2, default=str)

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconnaît les patterns dans le code.
        Context:
            - "code": str
            - "language": str
        """
        code = context.get("code", "")
        language = context.get("language", "python")

        if not code.strip():
            return {
                "agent": self.name,
                "confidence": 0.5,
                "recommendation": "ABSTAIN",
                "reasoning": "No code to analyze",
                "action_items": []
            }

        patterns = self._detect_patterns(code, language)
        antipatterns = self._detect_antipatterns(code, language)

        if not patterns and not antipatterns:
            return {
                "agent": self.name,
                "confidence": 0.7,
                "recommendation": "GENERIC",
                "reasoning": "No specific patterns recognized",
                "action_items": ["Code structure is straightforward"]
            }

        confidence = 0.85
        action_items = []

        if patterns:
            action_items.extend([f"✅ {p['name']}: {p['description']}" for p in patterns[:3]])

        if antipatterns:
            action_items.extend([f"⚠️ {a['name']}: {a['description']}" for a in antipatterns[:3]])

        # Enregistre détection
        record = {
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "patterns_count": len(patterns),
            "antipatterns_count": len(antipatterns),
            "patterns": patterns,
            "antipatterns": antipatterns,
        }
        self._patterns_db.append(record)
        self._save_patterns_db()

        recommendation = "PATTERNS_FOUND" if patterns else "ANTIPATTERNS_FOUND"

        return {
            "agent": self.name,
            "confidence": confidence,
            "recommendation": recommendation,
            "reasoning": f"Detected {len(patterns)} pattern(s) and {len(antipatterns)} antipattern(s)",
            "patterns": patterns,
            "antipatterns": antipatterns,
            "action_items": action_items
        }

    def _detect_patterns(self, code: str, language: str) -> List[Dict]:
        """Détecte design patterns."""
        patterns = []

        # ────────────────────────────────────────────────────────────
        # PATTERNS PYTHON
        # ────────────────────────────────────────────────────────────

        if language in ["python", "py"]:
            # Singleton pattern
            if "_instance = None" in code and "get_instance()" in code:
                patterns.append({
                    "name": "Singleton",
                    "description": "Single instance management",
                    "benefit": "Global access to shared state",
                    "caution": "Can make testing harder"
                })

            # Factory pattern
            if "def create_" in code or "def make_" in code:
                patterns.append({
                    "name": "Factory",
                    "description": "Object creation abstraction",
                    "benefit": "Decouples creation from usage",
                })

            # Context Manager (with statement)
            if "__enter__" in code and "__exit__" in code:
                patterns.append({
                    "name": "Context Manager",
                    "description": "Resource management with cleanup",
                    "benefit": "Safe resource handling",
                })

            # Decorator pattern
            if "@property" in code or "def wrapper(" in code:
                patterns.append({
                    "name": "Decorator/Property",
                    "description": "Add behavior without modifying class",
                    "benefit": "Clean API, lazy evaluation",
                })

        # ────────────────────────────────────────────────────────────
        # PATTERNS JAVASCRIPT/TYPESCRIPT
        # ────────────────────────────────────────────────────────────

        elif language in ["javascript", "js", "typescript", "ts"]:
            # Module pattern
            if "export" in code or "export default" in code:
                patterns.append({
                    "name": "Module Pattern",
                    "description": "Encapsulation with imports/exports",
                    "benefit": "Namespace management and reusability",
                })

            # Observer pattern (event listeners)
            if "addEventListener" in code or ".on(" in code:
                patterns.append({
                    "name": "Observer/Event Pattern",
                    "description": "Event-driven communication",
                    "benefit": "Loose coupling between components",
                })

            # Promise/Async pattern
            if "async " in code or ".then(" in code:
                patterns.append({
                    "name": "Async Pattern",
                    "description": "Asynchronous operation handling",
                    "benefit": "Non-blocking operations",
                })

        # ────────────────────────────────────────────────────────────
        # UNIVERSAL PATTERNS
        # ────────────────────────────────────────────────────────────

        # MVC/MVVM structure
        if any(x in code for x in ["Model", "View", "Controller"]):
            patterns.append({
                "name": "MVC Architecture",
                "description": "Separation of concerns",
                "benefit": "Organized, testable code",
            })

        # DRY (Don't Repeat Yourself) via extraction
        if code.count("def ") >= 10 or code.count("class ") >= 3:
            patterns.append({
                "name": "Modular Design",
                "description": "Code broken into functions/classes",
                "benefit": "Reusability and maintainability",
            })

        return patterns

    def _detect_antipatterns(self, code: str, language: str) -> List[Dict]:
        """Détecte anti-patterns."""
        antipatterns = []

        # ────────────────────────────────────────────────────────────
        # UNIVERSAL ANTIPATTERNS
        # ────────────────────────────────────────────────────────────

        # God object (too many responsibilities)
        class_methods = len(re.findall(r'def \w+\(self', code))
        if class_methods > 20:
            antipatterns.append({
                "name": "God Object",
                "description": "Class with too many responsibilities",
                "problem": f"{class_methods} methods in one class",
                "solution": "Break into smaller, focused classes",
                "severity": "MEDIUM"
            })

        # Feature envy (accessing other object's data)
        if code.count(".get(") > 10 or code.count(".__") > 5:
            antipatterns.append({
                "name": "Feature Envy",
                "description": "Class overly interested in other objects",
                "solution": "Move logic closer to data",
                "severity": "LOW"
            })

        # Magic numbers
        magic_nums = len(re.findall(r'\b(?!0|1|2|10|100)\d{2,}\b', code))
        if magic_nums > 5:
            antipatterns.append({
                "name": "Magic Numbers",
                "description": f"Found {magic_nums} unexplained numeric literals",
                "solution": "Extract to named constants",
                "severity": "LOW"
            })

        # ────────────────────────────────────────────────────────────
        # PYTHON ANTIPATTERNS
        # ────────────────────────────────────────────────────────────

        if language in ["python", "py"]:
            # Mutable default arguments
            if "def " in code and "= [" in code and ":" in code:
                if re.search(r'def \w+\([^)]*=\s*\[', code):
                    antipatterns.append({
                        "name": "Mutable Default Argument",
                        "description": "Using mutable objects as defaults",
                        "problem": "Shared state across function calls",
                        "solution": "def func(x=None): if x is None: x = []",
                        "severity": "MEDIUM"
                    })

            # Bare except
            if "except:" in code:
                antipatterns.append({
                    "name": "Bare Except",
                    "description": "Catching all exceptions generically",
                    "problem": "Masks unexpected errors",
                    "solution": "Catch specific exceptions",
                    "severity": "MEDIUM"
                })

        # ────────────────────────────────────────────────────────────
        # JAVASCRIPT ANTIPATTERNS
        # ────────────────────────────────────────────────────────────

        elif language in ["javascript", "js"]:
            # Callback hell
            if code.count(".then(") >= 5 or code.count("callback") >= 5:
                antipatterns.append({
                    "name": "Callback Hell",
                    "description": "Deep nesting of callbacks",
                    "solution": "Use async/await or Promise chains",
                    "severity": "MEDIUM"
                })

            # Global state
            if "window." in code and "=" in code:
                antipatterns.append({
                    "name": "Global State",
                    "description": "Polluting global namespace",
                    "solution": "Use modules or encapsulation",
                    "severity": "MEDIUM"
                })

        return antipatterns
