"""
🎯 SUPERVISOR AGENT V1.0 — Orchestration + Synthèse finale
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du SupervisorAgent du trading bot.
Rôle: Orchestre tous les agents, synthétise les recommandations, décision finale.
Vote pondéré par confiance de chaque agent.
Personnalité: EXECUTOR (exécute la décision).
"""

from base_agent import BaseAgent, PERSONALITY_EXECUTOR
from typing import Dict, Any, List
from datetime import datetime


class SupervisorAgent(BaseAgent):
    """
    Agent superviseur qui orchestre les décisions de tous les autres agents.
    """

    # Poids de chaque agent dans la synthèse
    AGENT_WEIGHTS = {
        "code_analyzer":    0.25,  # Détection erreurs → très important
        "security":         0.25,  # Sécurité → critique
        "performance":      0.15,  # Perf
        "learning":         0.15,  # Patterns appris
        "research":         0.10,  # Context externe
        "supervisor":       0.00,  # Pas self-voting
    }

    # Agents pouvant opposer veto (bloquent la décision)
    VETO_AGENTS = {"security"}

    def __init__(self):
        super().__init__(
            name="supervisor",
            role="Synthèse finale, vote pondéré, décision risk-adjusted",
            domain_keywords=[
                "synthétise", "synthèse", "summarize", "summary",
                "final decision", "décision finale", "vote",
                "débat", "orchestrator", "consensus", "cerveau collectif",
                "arbitrage", "supervisor", "portfolio", "orchestrate",
            ]
        )
        self._decision_history: List[Dict] = []

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestre une décision finale basée sur les réponses de tous les agents.
        Context doit contenir:
            - "agent_responses": List[Dict] - réponses de tous les agents
            - "question": str - question posée
            - "threshold": float (0.0-1.0) - confiance minimale pour décision
        """
        agent_responses = context.get("agent_responses", [])
        question = context.get("question", "")
        threshold = context.get("threshold", 0.60)

        if not agent_responses:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "NO_AGENTS",
                "reasoning": "No agent responses provided",
                "action_items": []
            }

        # ────────────────────────────────────────────────────────────
        # DÉTECTE VÉTOS
        # ────────────────────────────────────────────────────────────

        vetos = [
            r for r in agent_responses
            if r.get("agent") in self.VETO_AGENTS
            and r.get("confidence", 0) > 0.7
            and r.get("recommendation") in ["BLOCK", "REJECT", "ABORT"]
        ]

        if vetos:
            action_items = [f"🚫 Veto from {v['agent']}: {v.get('reasoning', '')}" for v in vetos]
            return {
                "agent": self.name,
                "confidence": 0.95,
                "recommendation": "BLOCKED",
                "reasoning": f"Blocked by {len(vetos)} agent(s) with strong conviction",
                "action_items": action_items,
                "vetos": vetos
            }

        # ────────────────────────────────────────────────────────────
        # VOTE PONDÉRÉ
        # ────────────────────────────────────────────────────────────

        weighted_vote = self._compute_weighted_vote(agent_responses)

        # ────────────────────────────────────────────────────────────
        # DÉCISION FINALE
        # ────────────────────────────────────────────────────────────

        consensus_confidence = weighted_vote["consensus_confidence"]
        dominant_direction = weighted_vote["dominant_direction"]
        participating_agents = weighted_vote["participating_agents"]

        if consensus_confidence < threshold:
            recommendation = "ABSTAIN"
            reasoning = f"Low confidence ({consensus_confidence:.2f}) below threshold ({threshold})"
        else:
            if dominant_direction == "APPROVE":
                recommendation = "PROCEED"
            elif dominant_direction == "REJECT":
                recommendation = "REJECT"
            else:
                recommendation = "REVIEW_NEEDED"

            reasoning = f"Consensus: {recommendation} (confidence: {consensus_confidence:.2f})"

        # Action items
        action_items = [
            f"✅ {a['agent']}: {a.get('recommendation', 'N/A')} ({a['confidence']:.2f})"
            for a in participating_agents[:5]
        ]

        # Enregistre décision
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "recommendation": recommendation,
            "confidence": consensus_confidence,
            "agents_count": len(participating_agents),
            "vetos": len(vetos)
        }
        self._decision_history.append(decision_record)

        return {
            "agent": self.name,
            "confidence": consensus_confidence,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "consensus_score": weighted_vote["consensus_score"],
            "participating_agents": participating_agents,
            "action_items": action_items
        }

    def _compute_weighted_vote(self, agent_responses: List[Dict]) -> Dict[str, Any]:
        """
        Calcule le vote pondéré de tous les agents.
        Retourne: {
            consensus_confidence: float,
            dominant_direction: str (APPROVE/REJECT/NEUTRAL),
            consensus_score: float (-1.0 to +1.0),
            participating_agents: List[Dict]
        }
        """
        approve_score = 0.0
        reject_score = 0.0
        total_weight = 0.0
        participating = []

        for response in agent_responses:
            if not isinstance(response, dict):
                continue

            agent_name = response.get("agent", "unknown")
            confidence = max(0.0, min(1.0, float(response.get("confidence", 0.5))))
            recommendation = str(response.get("recommendation", "ABSTAIN")).upper()

            # Poids
            weight = self.AGENT_WEIGHTS.get(agent_name, 0.05)

            # Direction
            direction = 0.0
            if any(x in recommendation for x in ["APPROVE", "PROCEED", "YES", "OK", "PASS"]):
                direction = 1.0
            elif any(x in recommendation for x in ["REJECT", "NO", "BLOCK", "FAIL", "ABORT"]):
                direction = -1.0

            # Vote pondéré
            weighted = weight * confidence * direction
            if direction > 0:
                approve_score += abs(weighted)
            elif direction < 0:
                reject_score += abs(weighted)

            total_weight += weight
            participating.append({
                "agent": agent_name,
                "confidence": confidence,
                "recommendation": recommendation,
                "weight": weight,
                "vote_strength": round(abs(weighted), 4)
            })

        # Normalise
        norm = total_weight if total_weight > 0 else 1.0
        approve_norm = approve_score / norm
        reject_norm = reject_score / norm
        net_score = approve_norm - reject_norm  # [-1, +1]

        # Consensus confidence
        max_score = max(approve_norm, reject_norm)
        consensus_confidence = max_score

        # Direction dominante
        if net_score > 0.1:
            direction = "APPROVE"
        elif net_score < -0.1:
            direction = "REJECT"
        else:
            direction = "NEUTRAL"

        # Trie par vote strength
        participating.sort(key=lambda x: x["vote_strength"], reverse=True)

        return {
            "consensus_confidence": consensus_confidence,
            "dominant_direction": direction,
            "consensus_score": net_score,
            "approve_score": round(approve_norm, 3),
            "reject_score": round(reject_norm, 3),
            "participating_agents": participating
        }
