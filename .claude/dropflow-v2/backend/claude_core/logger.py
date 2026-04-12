#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Logging System for DropFlow v2
Tracks all decisions, requests, and system events
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class StructuredLogger:
    """
    Structured logging for decision tracking and system monitoring
    Captures decisions with confidence scores, outcomes, and metadata
    """

    def __init__(self, log_dir: str = "logs", log_name: str = "dropflow"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Setup file handler for structured logs
        self.log_file = self.log_dir / f"{log_name}.json"
        self.decision_file = self.log_dir / f"{log_name}_decisions.json"

        # Setup standard logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(self.log_dir / f"{log_name}.log")
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_decision(
        self,
        request: str,
        decision: Dict[str, Any],
        confidence: float,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log a decision with full context"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "decision",
            "request": request[:200],  # Truncate long requests
            "decision": {
                "type": decision.get("type", "unknown"),
                "project": decision.get("project", "unknown"),
                "action": decision.get("action", "unknown"),
            },
            "confidence": confidence,
            "metadata": metadata or {}
        }

        # Append to JSON log
        self._append_json(self.decision_file, event)

        # Log to standard logger (ASCII-safe)
        self.logger.info(
            f"DECISION: {decision.get('type')} -> {decision.get('project')} "
            f"(confidence: {confidence:.2f})"
        )

    def log_request(self, request: str, source: Optional[str] = None) -> None:
        """Log incoming request"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "request": request[:200],
            "source": source or "unknown"
        }

        self._append_json(self.log_file, event)
        self.logger.info(f"REQUEST: {request[:100]}...")

    def log_success(
        self,
        action: str,
        result: Dict[str, Any],
        duration_ms: float
    ) -> None:
        """Log successful action execution"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "success",
            "action": action,
            "result": result,
            "duration_ms": duration_ms
        }

        self._append_json(self.log_file, event)
        self.logger.info(f"SUCCESS: {action} ({duration_ms:.1f}ms)")

    def log_error(
        self,
        action: str,
        error: str,
        traceback: Optional[str] = None
    ) -> None:
        """Log error with context"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "action": action,
            "error": error,
            "traceback": traceback
        }

        self._append_json(self.log_file, event)
        self.logger.error(f"ERROR in {action}: {error}")

    def log_improvement(
        self,
        improvement: str,
        category: str,
        impact: str
    ) -> None:
        """Log system improvements and enhancements"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "improvement",
            "improvement": improvement,
            "category": category,
            "impact": impact
        }

        self._append_json(self.log_file, event)
        self.logger.info(f"IMPROVEMENT: {improvement} ({category}) - Impact: {impact}")

    def log_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "count"
    ) -> None:
        """Log system metrics"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "metric",
            "metric": metric_name,
            "value": value,
            "unit": unit
        }

        self._append_json(self.log_file, event)
        self.logger.info(f"METRIC: {metric_name} = {value} {unit}")

    def _append_json(self, filepath: Path, event: Dict) -> None:
        """Append event to JSON log file"""
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
            else:
                data = []

            data.append(event)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write log: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "log_file": str(self.log_file),
            "decision_file": str(self.decision_file),
            "log_dir_size_kb": sum(f.stat().st_size for f in self.log_dir.glob("**/*")) / 1024
        }

        if self.decision_file.exists():
            with open(self.decision_file, 'r') as f:
                decisions = json.load(f)
                stats["total_decisions"] = len(decisions)
                if decisions:
                    confidences = [d.get("confidence", 0) for d in decisions]
                    stats["avg_confidence"] = sum(confidences) / len(confidences)

        return stats


# Global logger instance
_logger = None


def get_logger() -> StructuredLogger:
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger


if __name__ == "__main__":
    # Demo
    logger = get_logger()

    logger.log_request("Find trending products in tech", source="demo")
    logger.log_decision(
        "Find trending products in tech",
        {"type": "project_specific", "project": "p1_product_discovery", "action": "find"},
        0.92,
        {"niche": "technology", "role": "trend_analyst"}
    )
    logger.log_success("route_to_orchestrator", {"status": "routed"}, 45.2)
    logger.log_improvement("role-based prompting", "enhancements", "high")
    logger.log_metric("decision_confidence_avg", 0.88, "percentage")

    print("\n[LOG STATS]")
    for key, value in logger.get_stats().items():
        print(f"  {key}: {value}")
