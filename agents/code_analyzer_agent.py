"""
🔍 CODE ANALYZER AGENT V1.0 — Détection d'erreurs et analyse qualité
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du CodeFixerAgent du trading bot.
Rôle: Analyse le code pour erreurs, imports manquants, type issues, patterns.
Domaine: bugs, errors, code quality, imports, types, patterns.
Personnalité: ANALYST (détecte les problèmes)
"""

from base_agent import BaseAgent, PERSONALITY_ANALYST
from typing import Dict, Any, List
import ast
import re
from datetime import datetime


class CodeAnalyzerAgent(BaseAgent):
    """
    Agent spécialisé dans la détection d'erreurs et analyse de qualité du code.
    """

    def __init__(self):
        super().__init__(
            name="code_analyzer",
            role="Détecteur d'erreurs, analyste qualité code — imports, types, patterns, antipatterns",
            domain_keywords=[
                "code", "bug", "error", "import", "type", "analyse",
                "qualité", "pattern", "antipattern", "smell",
                "erreur", "exception", "debug", "crash", "cassé",
                "interface", "contrat", "signature", "lint",
                "complexity", "duplication", "dead code",
                "security", "vulnerability", "injection", "xss",
            ]
        )
        self._error_cache: List[Dict] = []
        self._pattern_cache: Dict[str, int] = {}

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le code fourni et retourne erreurs + recommandations.
        Context doit contenir:
            - "code": str - code à analyser
            - "language": str - langage (js, py, ts, etc)
            - optionnel: "file_path": str
        """
        code = context.get("code", "")
        language = context.get("language", "unknown")
        file_path = context.get("file_path", "")

        if not code.strip():
            return {
                "agent": self.name,
                "confidence": 1.0,
                "recommendation": "ABSTAIN",
                "reasoning": "No code to analyze",
                "action_items": []
            }

        errors = []
        confidence = 0.5

        # ────────────────────────────────────────────────────────────
        # ANALYSE SYNTAXE & STRUCTURE
        # ────────────────────────────────────────────────────────────

        if language in ["python", "py"]:
            errors.extend(self._analyze_python(code))
        elif language in ["javascript", "js", "typescript", "ts"]:
            errors.extend(self._analyze_js_ts(code))

        # ────────────────────────────────────────────────────────────
        # ANTIPATTERNS UNIVERSELS
        # ────────────────────────────────────────────────────────────

        errors.extend(self._detect_universal_antipatterns(code))

        # Confidence basée sur nombre d'erreurs détectées
        if len(errors) == 0:
            confidence = 0.9
            recommendation = "✅ No major issues"
        elif len(errors) <= 2:
            confidence = 0.7
            recommendation = "⚠️ Minor issues found"
        elif len(errors) <= 5:
            confidence = 0.85
            recommendation = "🔴 Multiple issues"
        else:
            confidence = 0.95
            recommendation = "🔴 CRITICAL issues"

        action_items = [f"Fix: {e['issue']}" for e in errors[:5]]

        self._error_cache.append({
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "error_count": len(errors),
            "errors": errors
        })

        return {
            "agent": self.name,
            "confidence": confidence,
            "recommendation": recommendation,
            "reasoning": f"Detected {len(errors)} issues in {language} code",
            "errors": errors,
            "action_items": action_items
        }

    def _analyze_python(self, code: str) -> List[Dict]:
        """Analyse Python: syntax, imports, types."""
        errors = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append({
                "severity": "CRITICAL",
                "issue": f"Syntax error line {e.lineno}: {e.msg}",
                "line": e.lineno,
                "fix": "Check syntax around line"
            })
            return errors

        # Détecte imports manquants communs
        common_imports = re.findall(r'^(?:from|import)\s+(\S+)', code, re.MULTILINE)
        if "import numpy" in code and "np\." in code and "import numpy as np" not in code:
            errors.append({
                "severity": "HIGH",
                "issue": "numpy imported but used as 'np' alias without alias import",
                "fix": "Add: import numpy as np"
            })

        # Détecte None comparisons
        if " == None" in code or " != None" in code:
            errors.append({
                "severity": "MEDIUM",
                "issue": "Comparing to None with == instead of 'is'",
                "fix": "Replace '== None' with 'is None' and '!= None' with 'is not None'"
            })

        # Détecte bare except
        if "except:" in code:
            errors.append({
                "severity": "MEDIUM",
                "issue": "Bare 'except:' clause catches all exceptions",
                "fix": "Catch specific exceptions: except Exception as e:"
            })

        return errors

    def _analyze_js_ts(self, code: str) -> List[Dict]:
        """Analyse JS/TS: var/let/const, null checks, async."""
        errors = []

        # Détecte var (deprecated)
        var_count = len(re.findall(r'\bvar\s+', code))
        if var_count > 0:
            errors.append({
                "severity": "MEDIUM",
                "issue": f"Found {var_count} 'var' declarations (deprecated)",
                "fix": "Replace 'var' with 'let' or 'const'"
            })

        # Détecte == au lieu de ===
        if " == " in code or " != " in code:
            errors.append({
                "severity": "MEDIUM",
                "issue": "Using == or != instead of === or !==",
                "fix": "Replace == with === and != with !=="
            })

        # Détecte console.log en production
        console_count = len(re.findall(r'console\.log', code))
        if console_count > 3:
            errors.append({
                "severity": "LOW",
                "issue": f"Found {console_count} console.log statements",
                "fix": "Remove or use proper logging library"
            })

        return errors

    def _detect_universal_antipatterns(self, code: str) -> List[Dict]:
        """Détecte antipatterns universels."""
        errors = []

        # Hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub token exposed"),
        ]

        for pattern, msg in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append({
                    "severity": "CRITICAL",
                    "issue": msg,
                    "fix": "Move to .env or secrets manager"
                })

        # TODO/FIXME without date
        todo_count = len(re.findall(r'#\s*(TODO|FIXME|XXX|HACK)\b', code, re.IGNORECASE))
        if todo_count > 5:
            errors.append({
                "severity": "LOW",
                "issue": f"Found {todo_count} TODO/FIXME comments",
                "fix": "Track in issue tracker, not code"
            })

        # Very long lines (>120 chars)
        long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > 120]
        if len(long_lines) > 3:
            errors.append({
                "severity": "LOW",
                "issue": f"Found {len(long_lines)} lines > 120 chars",
                "fix": "Break long lines for readability"
            })

        return errors
