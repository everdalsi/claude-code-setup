#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Viral Content Pipeline
From: Razvan Paraschiv's $5k-$10k/month TikTok automation system

Source: Telegram analysis of 6 images showing:
  Step 1: Channel Analysis (scrape all titles)
  Step 2: Niche Trend Strategist (Gemini Deep Research)
  Step 3: Pattern Extraction (identify viral formulas)
  Step 4: New Viral Title Generation (create variants)

Applicable to:
  - Video Automation (YouTube/TikTok title optimization)
  - Dropshipping (product descriptions with viral patterns)
  - Music Generation (analyze hit patterns for composition)
"""

import json
from typing import List, Dict, Any, Optional
from enum import Enum

class ContentNiche(Enum):
    """Content niches that can be analyzed"""
    VEHICLES = "vehicles"
    TECH = "tech"
    FINANCE = "finance"
    LIFESTYLE = "lifestyle"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"

class ViralPatternAnalyzer:
    """
    Analyzes viral content patterns from competitor channels
    Uses: Scraping + Gemini Deep Research + Pattern Matching
    """

    def __init__(self, niche: ContentNiche):
        self.niche = niche
        self.analyzed_titles = []
        self.patterns = {
            "urgency": [],      # "MUST", "BEFORE", "NOW"
            "curiosity": [],    # "WHAT IF", "YOU WONT BELIEVE", "SECRET"
            "numbers": [],      # "5 WAYS", "73%", "#1"
            "emotions": [],     # "SHOCKING", "REVEALED", "DESTROYED"
            "verbs": [],        # Action words that drive engagement
        }

    def extract_title_patterns(self, titles: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of viral titles to extract patterns

        Example titles:
        - "Why Every Truck Buyer Is About to Get Betrayed in 2025"
        - "5 Biggest Changes in Pickup Truck Safety Nobody's Talking About"
        - "New Trucks What the Truck America's Latest Dealt"
        """
        patterns_found = {
            "common_words": {},
            "structures": [],
            "emotional_triggers": [],
            "call_to_actions": []
        }

        for title in titles:
            # Extract urgency words
            urgency_words = ["must", "before", "now", "asap", "hurry", "betrayed", "shocked"]
            for word in urgency_words:
                if word.lower() in title.lower():
                    patterns_found["emotional_triggers"].append(word)

            # Extract numbers/rankings
            if any(char.isdigit() for char in title):
                patterns_found["structures"].append("NUMBERS_IN_TITLE")

            # Extract question format
            if "?" in title:
                patterns_found["structures"].append("QUESTION_FORMAT")

            # Track word frequency
            words = title.lower().split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    patterns_found["common_words"][word] = patterns_found["common_words"].get(word, 0) + 1

        return patterns_found

    def generate_viral_titles(self, topic: str, patterns: Dict[str, Any], count: int = 10) -> List[str]:
        """
        Generate new viral titles based on extracted patterns

        Combines:
        - Emotional triggers (urgency, curiosity)
        - Structural patterns (numbers, questions)
        - Proven formulas (curiosity + specificity)
        """
        generated_titles = []

        # Formula 1: "NUMBER + ADJECTIVE + NOUN + CONSEQUENCE"
        formulas = [
            f"5 {topic} Changes Nobody's Talking About Yet",
            f"Why Every {topic} Buyer Is About to Get Betrayed in 2026",
            f"The {topic} Industry HATES This One Weird Trick",
            f"Shocking {topic} Discovery Has Experts FURIOUS",
            f"NEW {topic}: What They Don't Want You to Know",
            f"{topic} Prices About to SKYROCKET - Here's Why",
            f"This {topic} Secret Will BLOW YOUR MIND",
            f"The #{topic} Mistake That Costs You Thousands",
            f"Scientists Just Discovered Something About {topic}...",
            f"If You {topic} Before Watching This, You're Making a HUGE Mistake",
        ]

        return formulas[:count]

    def analyze_engagement_potential(self, title: str) -> Dict[str, Any]:
        """Score a title for viral potential (0-100)"""
        score = 0
        analysis = {
            "title": title,
            "score": 0,
            "urgency": 0,
            "curiosity": 0,
            "specificity": 0,
            "emotion": 0,
            "recommendation": "low"
        }

        # Urgency check
        urgency_words = ["must", "before", "now", "betrayed", "shocking", "revealed"]
        if any(word in title.lower() for word in urgency_words):
            analysis["urgency"] = 25
            score += 25

        # Curiosity check
        curiosity_words = ["why", "what if", "secret", "hidden", "shocking", "truth"]
        if any(word in title.lower() for word in curiosity_words):
            analysis["curiosity"] = 25
            score += 25

        # Numbers/specificity
        if any(char.isdigit() for char in title):
            analysis["specificity"] = 20
            score += 20

        # Emotional words
        emotional_words = ["destroyed", "shocked", "furious", "blown away", "mind"]
        if any(word in title.lower() for word in emotional_words):
            analysis["emotion"] = 30
            score += 30

        analysis["score"] = min(score, 100)

        if score >= 80:
            analysis["recommendation"] = "high"
        elif score >= 50:
            analysis["recommendation"] = "medium"
        else:
            analysis["recommendation"] = "low"

        return analysis

class VideoContentOptimizer:
    """
    Optimize YouTube/TikTok videos using analyzed patterns
    """

    def __init__(self):
        self.patterns = ViralPatternAnalyzer(ContentNiche.VEHICLES)

    def optimize_video_title(self, current_title: str, channel_context: str) -> str:
        """Suggest better title based on patterns"""
        analysis = self.patterns.analyze_engagement_potential(current_title)

        if analysis["score"] < 60:
            # Generate better alternatives
            suggestions = self.patterns.generate_viral_titles(
                topic=channel_context,
                patterns={},
                count=3
            )
            return {
                "current_title": current_title,
                "current_score": analysis["score"],
                "suggestions": suggestions,
                "improvement_potential": f"+{100 - analysis['score']} points"
            }

        return {"status": "good", "score": analysis["score"]}

class DropshippingProductOptimizer:
    """
    Use viral patterns for product descriptions & titles
    """

    def __init__(self):
        self.analyzer = ViralPatternAnalyzer(ContentNiche.LIFESTYLE)

    def optimize_product_description(self, product_name: str, current_description: str) -> Dict[str, Any]:
        """
        Apply viral content patterns to dropshipping products

        Example: "Smart Watch Band" →
        "This Hidden Smart Watch Hack Will BLOW YOUR MIND - Doctors HATE It"
        """
        optimized = {
            "original": current_description,
            "original_length": len(current_description),
            "optimizations": []
        }

        # Add urgency
        if "limited" not in current_description.lower():
            optimized["optimizations"].append(
                f"Add: 'Only {3} left in stock - Order NOW before they're gone!'"
            )

        # Add curiosity
        if "secret" not in current_description.lower():
            optimized["optimizations"].append(
                f"Add: 'Discover the {product_name} secret doctors don't want you to know about'"
            )

        # Add social proof
        optimized["optimizations"].append(
            "Add: '★★★★★ 2,547 customers bought this week - Join them!'"
        )

        return optimized

class MusicPatternAnalyzer:
    """
    Analyze viral music patterns for composition
    """

    def __init__(self):
        self.analyzer = ViralPatternAnalyzer(ContentNiche.ENTERTAINMENT)

    def analyze_hit_patterns(self, song_title: str, metadata: Dict) -> Dict[str, Any]:
        """
        Analyze what makes songs go viral
        Patterns: BPM, structure, emotional arc, drop timing
        """
        return {
            "song": song_title,
            "viral_factors": [
                "High energy intro (0-15s)",
                "Hook/Chorus repeated early",
                "Drops at 0:30-0:40 mark",
                "Emotional build-up to peak",
                "TikTok-friendly duration (15-30s clips)"
            ],
            "composition_recommendations": [
                "Start with recognizable sample or hook",
                "Build to drop within first 30 seconds",
                "Include 2-3 variations to prevent boredom",
                "End on emotional peak for loop-ability"
            ]
        }
