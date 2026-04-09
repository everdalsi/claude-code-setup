"""
🏥 HEALTH MONITOR AGENT V1.0 — Watchdog + Santé du système
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Adapté du SelfImprovementAgent du Trading Bot.
Rôle: Monitore la santé de tous les agents, détecte anomalies, logs, erreurs.
Domaine: health, monitoring, watchdog, diagnostic, santé système.
Personnalité: GUARDIAN (protection + monitoring)
"""

from base_agent import BaseAgent, PERSONALITY_GUARDIAN
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class HealthMonitorAgent(BaseAgent):
    """
    Agent de surveillance et diagnostic de la santé du système multi-agents.
    """

    HEALTH_LOG_FILE = ".claude/memory/agent_learning/health.json"

    def __init__(self):
        super().__init__(
            name="health_monitor",
            role="Surveillance santé système, watchdog, détection anomalies",
            domain_keywords=[
                "monitor", "health", "santé", "watchdog", "diagnostic",
                "erreur", "crash", "anomalie", "performance", "timeout",
                "log", "error log", "debug", "status", "état système",
                "amélioration", "surveillance", "synthèse", "débat",
            ]
        )
        self._health_log: List[Dict] = self._load_health_log()
        self._anomaly_log: List[str] = []
        self._last_check = datetime.now().isoformat()

    def _load_health_log(self) -> List[Dict]:
        """Charge l'historique santé."""
        path = Path(self.HEALTH_LOG_FILE)
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_health_log(self):
        """Sauvegarde le log santé."""
        Path(self.HEALTH_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(self.HEALTH_LOG_FILE, "w") as f:
            json.dump(self._health_log, f, indent=2, default=str)

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitore la santé et retourne rapport diagnostique.
        Context:
            - "action": "check_health" ou "report" ou "logs"
            - "agent_responses": List[Dict] - réponses des agents
        """
        action = context.get("action", "check_health")

        if action == "check_health":
            return self._check_health(context)
        elif action == "report":
            return self._generate_report(context)
        elif action == "logs":
            return self._get_logs(context)
        else:
            return {
                "agent": self.name,
                "confidence": 0.0,
                "recommendation": "UNKNOWN_ACTION",
                "reasoning": f"Unknown action: {action}",
                "action_items": []
            }

    def _check_health(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie la santé globale."""
        agent_responses = context.get("agent_responses", [])

        if not agent_responses:
            return {
                "agent": self.name,
                "confidence": 0.5,
                "recommendation": "NO_DATA",
                "reasoning": "No agent responses to analyze",
                "action_items": ["Start collecting agent responses"]
            }

        # ────────────────────────────────────────────────────────────
        # ANALYSE SANTÉ
        # ────────────────────────────────────────────────────────────

        errors = []
        warnings = []
        confidence_scores = []
        timeouts = []

        for resp in agent_responses:
            if not isinstance(resp, dict):
                errors.append(f"Invalid response format from agent")
                continue

            agent_name = resp.get("agent", "unknown")
            confidence = resp.get("confidence", 0.5)
            recommendation = resp.get("recommendation", "")
            error = resp.get("error", None)

            confidence_scores.append(confidence)

            # Détecte timeout
            if error and "timeout" in str(error).lower():
                timeouts.append(agent_name)
                warnings.append(f"⏱️ {agent_name} timed out")

            # Détecte très basse confiance
            if confidence < 0.3:
                warnings.append(f"⚠️ {agent_name} low confidence ({confidence:.2%})")

            # Détecte erreurs
            if error:
                errors.append(f"❌ {agent_name}: {error}")

        # ────────────────────────────────────────────────────────────
        # CALCUL SCORE SANTÉ GLOBAL
        # ────────────────────────────────────────────────────────────

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        health_score = avg_confidence

        if errors:
            health_score -= 0.2
        if warnings:
            health_score -= 0.1
        if timeouts:
            health_score -= 0.15

        health_score = max(0.0, min(1.0, health_score))

        # Détermine statut
        if errors:
            recommendation = "CRITICAL"
            reasoning = f"🔴 CRITICAL: {len(errors)} error(s) detected"
        elif warnings:
            recommendation = "WARNING"
            reasoning = f"🟠 WARNING: {len(warnings)} warning(s)"
        else:
            recommendation = "HEALTHY"
            reasoning = "✅ System healthy"

        # Enregistre
        health_record = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "avg_confidence": avg_confidence,
            "agent_count": len(agent_responses),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "timeout_count": len(timeouts),
            "errors": errors,
            "warnings": warnings,
        }
        self._health_log.append(health_record)
        self._save_health_log()

        action_items = []
        if timeouts:
            action_items.append(f"⏱️ {len(timeouts)} agent(s) timed out: {', '.join(timeouts)}")
        if errors:
            action_items.append(f"Fix {len(errors)} errors")
        if warnings:
            action_items.append(f"Address {len(warnings)} warnings")

        return {
            "agent": self.name,
            "confidence": health_score,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "health_score": health_score,
            "avg_confidence": avg_confidence,
            "errors": errors,
            "warnings": warnings,
            "timeouts": timeouts,
            "action_items": action_items or ["System healthy, no action needed"]
        }

    def _generate_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un rapport de santé sur les 10 derniers checks."""
        recent = self._health_log[-10:] if self._health_log else []

        if not recent:
            return {
                "agent": self.name,
                "confidence": 0.3,
                "recommendation": "NO_DATA",
                "reasoning": "No health data collected yet",
                "action_items": ["Start collecting health data"]
            }

        avg_score = sum(h["health_score"] for h in recent) / len(recent)
        trend = "↗️ IMPROVING" if recent[-1]["health_score"] > recent[0]["health_score"] else "↘️ DECLINING"

        action_items = [
            f"📊 Avg Health: {avg_score:.2%}",
            f"📈 Trend: {trend}",
            f"🔴 Total Errors: {sum(h['error_count'] for h in recent)}",
            f"⚠️ Total Warnings: {sum(h['warning_count'] for h in recent)}",
        ]

        return {
            "agent": self.name,
            "confidence": 0.85,
            "recommendation": "REPORT",
            "reasoning": f"Health report: avg {avg_score:.2%}, {trend}",
            "report": {
                "avg_health_score": avg_score,
                "trend": trend,
                "recent_checks": len(recent),
                "total_errors": sum(h["error_count"] for h in recent),
                "total_warnings": sum(h["warning_count"] for h in recent),
            },
            "action_items": action_items
        }

    def _get_logs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retourne les logs."""
        limit = context.get("limit", 5)
        recent_logs = self._health_log[-limit:]

        return {
            "agent": self.name,
            "confidence": 0.9,
            "recommendation": "LOGS",
            "reasoning": f"Last {len(recent_logs)} health checks",
            "logs": recent_logs,
            "action_items": [f"Total log entries: {len(self._health_log)}"]
        }
