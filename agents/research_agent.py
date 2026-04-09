"""
🔍 RESEARCH AGENT V1.0 — Recherche et contexte externe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du ResearchAgent du Trading Bot.
Rôle: Recherche contexte externe, meilleures pratiques, patterns connus.
Utilise web search quand disponible.
Domaine: research, context, best practices, patterns, documentation.
Personnalité: ANALYST
"""

from base_agent import BaseAgent, PERSONALITY_ANALYST
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class ResearchAgent(BaseAgent):
    """
    Agent qui recherche contexte externe et meilleures pratiques.
    """

    RESEARCH_DB = ".claude/memory/agent_learning/research.json"

    def __init__(self):
        super().__init__(
            name="research",
            role="Recherche contexte, best practices, patterns connus, documentation",
            domain_keywords=[
                "research", "context", "background", "best practice",
                "pattern", "pattern known", "library", "framework",
                "documentation", "docs", "reference", "example",
                "how to", "comment", "tutorial", "guide",
                "standard", "recommendation", "consensus", "industry",
            ]
        )
        self._research_db: List[Dict] = self._load_research_db()

    def _load_research_db(self) -> List[Dict]:
        """Charge la base de recherches."""
        path = Path(self.RESEARCH_DB)
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_research_db(self):
        """Sauvegarde la base."""
        Path(self.RESEARCH_DB).parent.mkdir(parents=True, exist_ok=True)
        with open(self.RESEARCH_DB, "w") as f:
            json.dump(self._research_db, f, indent=2, default=str)

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche contexte et informations.
        Context:
            - "query": str - sujet à rechercher
            - "language": str - langage/framework
            - "topic": str - sujet spécifique
        """
        query = context.get("query", "")
        language = context.get("language", "")
        topic = context.get("topic", "")

        if not query and not topic:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "NO_QUERY",
                "reasoning": "No search query provided",
                "action_items": []
            }

        search_term = query or topic
        results = self._research(search_term, language)

        if not results:
            return {
                "agent": self.name,
                "confidence": 0.3,
                "recommendation": "NO_RESULTS",
                "reasoning": f"No research results found for '{search_term}'",
                "action_items": ["Try different search terms"]
            }

        # Enregistre recherche
        research_record = {
            "timestamp": datetime.now().isoformat(),
            "query": search_term,
            "language": language,
            "results_count": len(results)
        }
        self._research_db.append(research_record)
        self._save_research_db()

        action_items = [f"📚 {r.get('title', r)}" for r in results[:3]]

        return {
            "agent": self.name,
            "confidence": 0.8,
            "recommendation": "RESEARCH_FOUND",
            "reasoning": f"Found {len(results)} relevant resources for '{search_term}'",
            "results": results,
            "action_items": action_items
        }

    def _research(self, query: str, language: str = "") -> List[Dict]:
        """Recherche interne + best practices."""
        results = []

        # ────────────────────────────────────────────────────────────
        # BEST PRACTICES BUILTIN
        # ────────────────────────────────────────────────────────────

        best_practices = {
            "python": [
                {
                    "title": "PEP 8 - Style Guide",
                    "url": "https://pep8.org",
                    "relevance": "Universal Python standard"
                },
                {
                    "title": "Type Hints (PEP 484)",
                    "relevance": "Improve code clarity and catch errors"
                },
                {
                    "title": "Async/Await",
                    "relevance": "Modern concurrent programming"
                },
                {
                    "title": "Context Managers",
                    "relevance": "Safe resource management (with statement)"
                },
                {
                    "title": "List Comprehensions",
                    "relevance": "Pythonic and efficient data transformation"
                },
            ],
            "javascript": [
                {
                    "title": "ES6+ Features",
                    "relevance": "Modern JavaScript standard"
                },
                {
                    "title": "Async/Await",
                    "relevance": "Better promise handling"
                },
                {
                    "title": "Arrow Functions",
                    "relevance": "Concise and proper 'this' binding"
                },
                {
                    "title": "Destructuring",
                    "relevance": "Clean variable extraction"
                },
                {
                    "title": "Modules (import/export)",
                    "relevance": "Code organization and reusability"
                },
            ],
            "typescript": [
                {
                    "title": "Type Safety",
                    "relevance": "Catch errors at compile time"
                },
                {
                    "title": "Interfaces vs Types",
                    "relevance": "Choose right abstraction"
                },
                {
                    "title": "Strict Mode",
                    "relevance": "Enable strict null/undefined checking"
                },
                {
                    "title": "Generics",
                    "relevance": "Reusable type-safe components"
                },
            ],
        }

        # Pattern-based search
        query_lower = query.lower()

        # OWASP / Security
        if any(x in query_lower for x in ["security", "owasp", "vulnerability", "injection", "xss"]):
            results.extend([
                {"title": "OWASP Top 10", "relevance": "Current security vulnerabilities"},
                {"title": "OWASP Top 10 for API", "relevance": "API-specific security issues"},
                {"title": "CWE (Common Weakness Enumeration)", "relevance": "Comprehensive vulnerability database"},
            ])

        # Testing
        if any(x in query_lower for x in ["test", "unit test", "integration", "pytest", "jest"]):
            results.extend([
                {"title": "Test Coverage Best Practices", "relevance": "Aim for 80%+ coverage"},
                {"title": "AAA Pattern (Arrange-Act-Assert)", "relevance": "Test structure standard"},
                {"title": "Mock vs Integration Tests", "relevance": "When to use each"},
            ])

        # Performance
        if any(x in query_lower for x in ["performance", "optimization", "optimize", "speed", "cache"]):
            results.extend([
                {"title": "Algorithmic Complexity (Big O)", "relevance": "Analyze time/space complexity"},
                {"title": "Profiling Tools", "relevance": "Identify bottlenecks"},
                {"title": "Caching Strategies", "relevance": "Redis, in-memory, CDN"},
            ])

        # Code Quality
        if any(x in query_lower for x in ["quality", "lint", "format", "style", "clean code"]):
            results.extend([
                {"title": "Code Review Best Practices", "relevance": "PR feedback standards"},
                {"title": "Linting Tools", "relevance": "ESLint, Pylint, Prettier"},
                {"title": "Clean Code Principles", "relevance": "Readability and maintainability"},
            ])

        # Language-specific
        if language:
            results.extend(best_practices.get(language, []))

        # Deduplicate
        seen = set()
        unique = []
        for r in results:
            title = r.get("title", "")
            if title not in seen:
                seen.add(title)
                unique.append(r)

        return unique[:10]  # Top 10
