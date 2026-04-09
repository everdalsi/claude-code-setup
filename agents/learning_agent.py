"""
🧠 LEARNING AGENT V1.0 — Mémoire infinie + Scoring de patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du LearningAgent du trading bot pour Claude Code.
Rôle: Apprendre des décisions passées, scorer les patterns, améliorer confiance.
Stockage: JSON pour persistence simple.
Domaine: learning, improvement, patterns, history.
Personnalité: ANALYST (analyste des patterns)
"""

from base_agent import BaseAgent, PERSONALITY_ANALYST
from typing import Dict, Any, List
from datetime import datetime
import json
import os
from pathlib import Path


class LearningAgent(BaseAgent):
    """
    Agent qui apprend des décisions passées et recommande patterns à réutiliser.
    """

    MEMORY_DIR = ".claude/memory/agent_learning"
    PATTERNS_FILE = f"{MEMORY_DIR}/patterns.json"
    DECISIONS_FILE = f"{MEMORY_DIR}/decisions.json"

    def __init__(self):
        super().__init__(
            name="learning",
            role="Mémoire infinie, scoring de patterns, ajustement de confiance",
            domain_keywords=[
                "learn", "apprendre", "pattern", "pattern matching",
                "memory", "history", "past", "précédent", "improvement",
                "amélioration", "score", "confiance", "confidence",
                "what worked", "ce qui a marché", "leçon", "lesson"
            ]
        )
        self._ensure_memory_dirs()
        self.patterns = self._load_patterns()
        self.decisions = self._load_decisions()

    def _ensure_memory_dirs(self):
        """Crée les répertoires de mémoire."""
        Path(self.MEMORY_DIR).mkdir(parents=True, exist_ok=True)

    def _load_patterns(self) -> Dict[str, Dict]:
        """Charge les patterns depuis JSON."""
        if os.path.exists(self.PATTERNS_FILE):
            try:
                with open(self.PATTERNS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _load_decisions(self) -> List[Dict]:
        """Charge l'historique des décisions."""
        if os.path.exists(self.DECISIONS_FILE):
            try:
                with open(self.DECISIONS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_patterns(self):
        """Sauvegarde les patterns."""
        with open(self.PATTERNS_FILE, "w") as f:
            json.dump(self.patterns, f, indent=2)

    def _save_decisions(self):
        """Sauvegarde les décisions."""
        with open(self.DECISIONS_FILE, "w") as f:
            json.dump(self.decisions, f, indent=2, default=str)

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Répond avec des insights basés sur la mémoire.
        Context peut contenir:
            - "action": "record_decision" ou "find_similar" ou "get_stats"
            - "decision": description de la décision
            - "outcome": résultat (success/failure/partial)
            - "query": recherche de patterns similaires
        """
        action = context.get("action", "get_stats")
        confidence = 0.6

        if action == "record_decision":
            return self._record_decision(context)
        elif action == "find_similar":
            return self._find_similar(context)
        elif action == "get_stats":
            return self._get_stats(context)
        else:
            return {
                "agent": self.name,
                "confidence": 0.5,
                "recommendation": "UNKNOWN_ACTION",
                "reasoning": f"Unknown action: {action}",
                "action_items": []
            }

    def _record_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre une décision + outcome pour apprentissage."""
        decision_desc = context.get("decision", "")
        outcome = context.get("outcome", "unknown")

        if not decision_desc:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "INVALID_INPUT",
                "reasoning": "No decision description provided",
                "action_items": []
            }

        # Crée entrée
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision_desc,
            "outcome": outcome,
            "category": context.get("category", "general")
        }

        self.decisions.append(entry)
        self._save_decisions()

        # Extrait patterns de la décision
        self._extract_pattern(decision_desc, outcome)

        return {
            "agent": self.name,
            "confidence": 0.95,
            "recommendation": f"RECORDED ({outcome})",
            "reasoning": f"Decision recorded and pattern extracted",
            "action_items": [
                f"Category: {entry['category']}",
                f"Outcome: {outcome}",
                f"Total decisions: {len(self.decisions)}"
            ]
        }

    def _extract_pattern(self, decision: str, outcome: str):
        """Extrait et score un pattern."""
        # Pattern simple: première phrase
        pattern_key = decision.split(".")[0][:50]

        if pattern_key not in self.patterns:
            self.patterns[pattern_key] = {
                "pattern": decision,
                "successes": 0,
                "failures": 0,
                "score": 0.5,
                "last_used": None
            }

        if outcome == "success":
            self.patterns[pattern_key]["successes"] += 1
        elif outcome == "failure":
            self.patterns[pattern_key]["failures"] += 1

        # Recalcule score
        total = self.patterns[pattern_key]["successes"] + self.patterns[pattern_key]["failures"]
        if total > 0:
            self.patterns[pattern_key]["score"] = (
                self.patterns[pattern_key]["successes"] / total
            )

        self.patterns[pattern_key]["last_used"] = datetime.now().isoformat()
        self._save_patterns()

    def _find_similar(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Cherche des patterns similaires."""
        query = context.get("query", "")

        if not query:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "NO_QUERY",
                "reasoning": "No search query provided",
                "action_items": []
            }

        # Recherche simple (substring)
        matches = [
            (k, v) for k, v in self.patterns.items()
            if query.lower() in v["pattern"].lower()
        ]

        # Trie par score (meilleurs en premier)
        matches.sort(key=lambda x: x[1]["score"], reverse=True)

        if not matches:
            return {
                "agent": self.name,
                "confidence": 0.3,
                "recommendation": "NO_MATCHES",
                "reasoning": f"No patterns found matching '{query}'",
                "action_items": ["Try different search terms"]
            }

        top_matches = matches[:3]
        action_items = [
            f"✅ {m[1]['pattern'][:40]}... (score: {m[1]['score']:.2f})"
            for m in top_matches
        ]

        return {
            "agent": self.name,
            "confidence": 0.85,
            "recommendation": "PATTERNS_FOUND",
            "reasoning": f"Found {len(matches)} similar patterns, top 3 recommended",
            "similar_patterns": [m[1] for m in top_matches],
            "action_items": action_items
        }

    def _get_stats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retourne statistiques d'apprentissage."""
        if not self.decisions:
            return {
                "agent": self.name,
                "confidence": 0.5,
                "recommendation": "NO_DATA",
                "reasoning": "No decisions recorded yet",
                "action_items": ["Start recording decisions to build patterns"]
            }

        success_count = sum(1 for d in self.decisions if d.get("outcome") == "success")
        failure_count = sum(1 for d in self.decisions if d.get("outcome") == "failure")
        total = len(self.decisions)

        success_rate = (success_count / total) if total > 0 else 0.0

        top_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )[:3]

        action_items = [
            f"📊 Success rate: {success_rate*100:.1f}%",
            f"📈 Total decisions: {total}",
            f"⭐ Top patterns: {len(top_patterns)}"
        ]

        return {
            "agent": self.name,
            "confidence": 0.9,
            "recommendation": "STATS",
            "reasoning": f"Learning progress: {success_rate*100:.1f}% success rate over {total} decisions",
            "stats": {
                "total_decisions": total,
                "successes": success_count,
                "failures": failure_count,
                "success_rate": success_rate,
                "pattern_count": len(self.patterns)
            },
            "top_patterns": [
                {
                    "pattern": p[1]["pattern"][:50],
                    "score": p[1]["score"],
                    "uses": p[1]["successes"] + p[1]["failures"]
                }
                for p in top_patterns
            ],
            "action_items": action_items
        }
