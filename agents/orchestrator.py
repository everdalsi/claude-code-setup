"""
🎭 ORCHESTRATOR V1.0 — Coordinateur des agents Claude Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Orchestre les décisions collectives de tous les agents.

Workflow:
1. Question posée
2. Tous les agents pertinents répondent (débat collectif)
3. Supervisor agrège les réponses
4. Décision finale avec raison explicite
5. Learning agent enregistre le pattern

Exemple:
    orch = CodeOrchestrator()
    result = orch.analyze_code(code, language)
    # retourne: recommendation + reasoning + action items
"""

from typing import Dict, Any, List
from datetime import datetime
import json


class CodeOrchestrator:
    """
    Orchestre les agents pour analyser du code et fournir décision collective.
    """

    def __init__(self, agents: Dict[str, Any] = None):
        """
        Initialise avec tous les agents disponibles.
        Si agents=None, crée automatiquement le full stack (9 agents).
        """
        if agents is None:
            from .code_analyzer_agent import CodeAnalyzerAgent
            from .security_agent import SecurityAgent
            from .learning_agent import LearningAgent
            from .supervisor_agent import SupervisorAgent
            from .health_monitor_agent import HealthMonitorAgent
            from .refactor_agent import RefactorAgent
            from .research_agent import ResearchAgent
            from .pattern_agent import PatternAgent

            self.agents = {
                "code_analyzer": CodeAnalyzerAgent(),
                "security": SecurityAgent(),
                "pattern": PatternAgent(),
                "learning": LearningAgent(),
                "health_monitor": HealthMonitorAgent(),
                "refactor": RefactorAgent(),
                "research": ResearchAgent(),
                "supervisor": SupervisorAgent(),
            }
        else:
            self.agents = agents

        self._decision_log: List[Dict] = []

    def analyze_code(self, code: str, language: str = "python", file_path: str = "") -> Dict[str, Any]:
        """
        Lance une analyse collective du code.
        Retourne: synthèse finale avec recommandation de tous les agents.
        """
        context = {
            "code": code,
            "language": language,
            "file_path": file_path,
        }

        # ────────────────────────────────────────────────────────────
        # PHASE 1: Tous les agents spécialisés répondent
        # ────────────────────────────────────────────────────────────

        agent_responses = []
        for agent_name, agent in self.agents.items():
            if agent_name == "supervisor":
                continue  # supervisor répond en dernier

            if agent.is_in_my_domain("code analysis"):  # domaine par défaut
                response = agent.safe_respond(context)
                agent_responses.append(response)

        # ────────────────────────────────────────────────────────────
        # PHASE 2: Supervisor synthétise
        # ────────────────────────────────────────────────────────────

        supervisor_context = {
            "agent_responses": agent_responses,
            "question": f"Analyze {language} code: {file_path}",
            "threshold": 0.60
        }

        supervisor = self.agents.get("supervisor")
        if supervisor:
            final_decision = supervisor.respond(supervisor_context)
        else:
            final_decision = {"recommendation": "NO_SUPERVISOR"}

        # ────────────────────────────────────────────────────────────
        # PHASE 3: Learning agent enregistre
        # ────────────────────────────────────────────────────────────

        learning = self.agents.get("learning")
        if learning:
            learning.respond({
                "action": "record_decision",
                "decision": final_decision.get("recommendation", "UNKNOWN"),
                "category": "code_analysis",
                "outcome": "recorded"
            })

        # ────────────────────────────────────────────────────────────
        # PHASE 4: Assemble résultat final
        # ────────────────────────────────────────────────────────────

        result = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "language": language,
            "final_decision": final_decision.get("recommendation", "ABSTAIN"),
            "confidence": final_decision.get("confidence", 0.0),
            "reasoning": final_decision.get("reasoning", ""),
            "all_agents_responses": agent_responses,
            "action_items": final_decision.get("action_items", []),
        }

        self._decision_log.append(result)
        return result

    def code_review(self, code: str, language: str = "python") -> str:
        """
        Lance une review complète: code analysis + security + learning.
        Retourne un rapport en markdown.
        """
        analysis = self.analyze_code(code, language)

        report = f"""
# Code Review Report
**Timestamp:** {analysis['timestamp']}
**Language:** {analysis['language']}

## Final Decision
**Recommendation:** {analysis['final_decision']}
**Confidence:** {analysis['confidence']:.2%}

## Reasoning
{analysis['reasoning']}

## Agent Responses

"""
        for resp in analysis['all_agents_responses']:
            agent_name = resp.get('agent', 'unknown')
            rec = resp.get('recommendation', 'N/A')
            conf = resp.get('confidence', 0.0)
            reasoning = resp.get('reasoning', '')

            report += f"""
### {agent_name.upper()}
- **Recommendation:** {rec}
- **Confidence:** {conf:.2%}
- **Reasoning:** {reasoning}
"""

        report += f"""

## Action Items
"""
        for item in analysis['action_items']:
            report += f"- {item}\n"

        return report

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Retourne les N dernières décisions."""
        return self._decision_log[-limit:]

    def export_decisions_json(self, filepath: str):
        """Exporte l'historique des décisions en JSON."""
        with open(filepath, "w") as f:
            json.dump(self._decision_log, f, indent=2, default=str)


# ════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    orch = CodeOrchestrator()

    sample_code = """
    import os
    from flask import Flask, request

    app = Flask(__name__)

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form.get("username")
        password = request.form.get("password")

        # ❌ SQL Injection!
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = db.execute(query)

        # ❌ Hardcoded password!
        admin_password = "admin123"

        # ❌ XSS!
        return f"<html><h1>Welcome {username}</h1></html>"
    """

    print("🎭 Code Orchestrator Demo")
    print("=" * 60)

    result = orch.analyze_code(sample_code, language="python", file_path="app.py")

    print(f"Final Decision: {result['final_decision']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")

    # Generate full report
    report = orch.code_review(sample_code, "python")
    print("\n" + report)
