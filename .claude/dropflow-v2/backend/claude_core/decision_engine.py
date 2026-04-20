#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decision Engine - Interpret and classify requests
Analyzes user input and determines the correct action
"""

import logging
from typing import Dict, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence in decision"""
    VERY_HIGH = 0.95
    HIGH = 0.85
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30

class DecisionEngine:
    """
    Analyzes requests and makes routing decisions
    Maintains decision history for learning
    """

    def __init__(self):
        self.decision_history = []
        self._initialize_keywords()

    def _initialize_keywords(self):
        """Initialize keyword mappings for classification"""
        self.keyword_map = {
            "self_improvement": {
                "words": ["improve", "analyse", "photo", "video", "tiktok", "strengthen",
                         "capability", "skill", "power", "enhancement", "upgrade"],
                "context": ["from telegram", "media analysis", "self-evolution"]
            },
            "product_discovery": {
                "words": ["product", "dropshipping", "supplier", "trending", "niche",
                         "sourcing", "aliexpress", "find", "discover", "search", "winning"],
                "context": ["dropship", "ecommerce", "store", "shopify", "margin"]
            },
            "media_automation": {
                "words": ["video", "youtube", "tiktok", "content", "script", "media",
                         "short", "viral", "publish", "channel", "automation"],
                "context": ["youtube automation", "tiktok bot", "video creation", "content pipeline"]
            },
            "kids_content": {
                "words": ["kids", "children", "kidz", "family", "education", "safe",
                         "pg", "appropriate", "youth", "junior"],
                "context": ["youtube kids", "family content", "educational", "child-friendly"]
            },
            "music_generation": {
                "words": ["music", "song", "audio", "suno", "beat", "track", "compose",
                         "generate", "create music", "sound"],
                "context": ["music generation", "ai music", "soundtrack", "audio composition"]
            }
        }

    def classify_request(self, request: str) -> Dict:
        """
        Classify a request and return decision with confidence

        Returns:
        {
            "category": str,
            "action": str,
            "confidence": float,
            "reasoning": str,
            "alternatives": List[Tuple[str, float]]
        }
        """
        request_lower = request.lower()

        scores = {}

        # Score each category
        for category, keywords_data in self.keyword_map.items():
            score = self._calculate_score(request_lower, keywords_data)
            scores[category] = score

        # Get top matches
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_category, top_score = sorted_scores[0]

        # Get alternatives (top 3)
        alternatives = [(cat, score) for cat, score in sorted_scores[1:4]]

        # Determine confidence level
        confidence = self._map_score_to_confidence(top_score)

        # Extract action
        action = self._extract_action(request_lower, top_category)

        decision = {
            "category": top_category,
            "action": action,
            "confidence": confidence.value,
            "confidence_level": confidence.name,
            "score": top_score,
            "reasoning": self._generate_reasoning(request, top_category, top_score),
            "alternatives": alternatives,
            "full_request": request
        }

        # Log decision
        self.decision_history.append(decision)

        return decision

    def _calculate_score(self, request: str, keywords_data: Dict) -> float:
        """Calculate match score for a category"""
        words = keywords_data["words"]
        context = keywords_data.get("context", [])

        # Count word matches
        word_matches = sum(1 for word in words if word in request)
        word_score = word_matches / len(words) if words else 0

        # Count context matches (weighted higher)
        context_matches = sum(1 for phrase in context if phrase in request)
        context_score = (context_matches / len(context)) * 1.5 if context else 0

        # Combined score
        total_score = (word_score * 0.6) + (context_score * 0.4)
        return total_score

    def _map_score_to_confidence(self, score: float) -> ConfidenceLevel:
        """Map numerical score to confidence level"""
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.6:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _extract_action(self, request: str, category: str) -> str:
        """Extract specific action from request"""
        action_keywords = {
            "analyze": ["analyze", "examine", "review", "check", "assess"],
            "create": ["create", "generate", "make", "build", "produce"],
            "find": ["find", "search", "discover", "locate", "source"],
            "optimize": ["optimize", "improve", "enhance", "refine"],
            "publish": ["publish", "post", "launch", "deploy", "release"],
            "validate": ["validate", "verify", "check", "test"],
        }

        for action, keywords in action_keywords.items():
            if any(keyword in request for keyword in keywords):
                return action

        return "process"

    def _generate_reasoning(self, request: str, category: str, score: float) -> str:
        """Generate human-readable reasoning"""
        if score >= 0.8:
            return f"Strong match to {category} (score: {score:.2f})"
        elif score >= 0.6:
            return f"Likely {category} (score: {score:.2f})"
        elif score >= 0.4:
            return f"Possible {category} (score: {score:.2f}), consider alternatives"
        else:
            return f"Weak match, clarification recommended (score: {score:.2f})"

    def ask_clarification(self, decision: Dict) -> Dict:
        """
        Generate clarification questions when confidence is low
        """
        category = decision["category"]
        confidence = decision["confidence"]

        if confidence >= 0.7:
            return {"needs_clarification": False}

        alternatives = decision.get("alternatives", [])

        return {
            "needs_clarification": True,
            "message": f"I'm {(confidence*100):.0f}% confident this is about {category}.",
            "question": "Could you clarify which section this relates to?",
            "suggestions": [alt[0] for alt in alternatives] if alternatives else [],
            "request_orig": decision["full_request"]
        }

    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Get recent decision history"""
        return self.decision_history[-limit:]

    def get_statistics(self) -> Dict:
        """Get decision statistics"""
        if not self.decision_history:
            return {"total_decisions": 0}

        categories = {}
        for decision in self.decision_history:
            cat = decision["category"]
            categories[cat] = categories.get(cat, 0) + 1

        avg_confidence = sum(d["confidence"] for d in self.decision_history) / len(self.decision_history)

        return {
            "total_decisions": len(self.decision_history),
            "categories": categories,
            "average_confidence": avg_confidence,
            "top_category": max(categories.items(), key=lambda x: x[1])[0] if categories else None
        }


def main():
    """Demo DecisionEngine"""
    import logging
    logging.basicConfig(level=logging.INFO)

    engine = DecisionEngine()

    print("\n" + "="*70)
    print("[DECISION ENGINE] Request Classification")
    print("="*70)

    test_requests = [
        "Analyze these 37 photos I sent from Telegram and improve yourself",
        "Find a trending product in the gadgets niche",
        "Create a viral TikTok video about cryptocurrency",
        "Generate music for my video project",
        "What should I do?",
    ]

    for request in test_requests:
        print(f"\n[INPUT] {request}")
        decision = engine.classify_request(request)
        print(f"[DECISION] Category: {decision['category']}")
        print(f"[ACTION] {decision['action']}")
        print(f"[CONFIDENCE] {decision['confidence_level']} ({decision['confidence']*100:.0f}%)")
        print(f"[REASONING] {decision['reasoning']}")

        # Check if clarification needed
        clarification = engine.ask_clarification(decision)
        if clarification["needs_clarification"]:
            print(f"[CLARIFICATION] {clarification['message']}")
            print(f"[SUGGESTION] {', '.join(clarification['suggestions'])}")

    # Show stats
    print("\n[STATISTICS]")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
