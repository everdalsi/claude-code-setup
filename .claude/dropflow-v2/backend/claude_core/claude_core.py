#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Core - Central Brain & Decision Engine
The unified orchestrator for all projects and self-improvement
"""

import json
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pathlib import Path

from .improvements_integrated import (
    RoleBasedPrompting, NicheSpecificFiltering,
    IntelligenceReporting, DataIntegrationHooks,
    AgentRole, NicheCategory
)

logger = logging.getLogger(__name__)

class ProjectType(Enum):
    """All available projects"""
    P1_PRODUCT_DISCOVERY = "p1_product_discovery"
    P2_MEDIA_AUTOMATION = "p2_media_automation"
    P3_KIDS_CONTENT = "p3_kids_content"
    P4_MUSIC_GENERATION = "p4_music_generation"
    P5_FUTURE = "p5_future"
    CLAUDE_CORE = "claude_core"

class RequestType(Enum):
    """Types of requests"""
    SELF_IMPROVEMENT = "self_improvement"
    PROJECT_SPECIFIC = "project_specific"
    INFRASTRUCTURE = "infrastructure"
    ANALYSIS = "analysis"
    CONFIGURATION = "configuration"

class ClaudeCore:
    """
    Central orchestrator and decision engine for all systems

    Responsibilities:
    - Parse incoming requests
    - Classify requests by type and project
    - Route to appropriate handler
    - Manage self-improvement loop
    - Coordinate all projects
    - Maintain system state
    """

    def __init__(self, state_file: str = "memory/claude_core_state.json"):
        self.state_file = Path(state_file)
        self.state = self._load_state()
        self.projects = {}
        self.agents = {}
        self.memory = {}

        # Initialize improvements
        self.role_prompter = RoleBasedPrompting()
        self.niche_filter = NicheSpecificFiltering()
        self.reporter = IntelligenceReporting()
        self.data_integrations = DataIntegrationHooks()

        logger.info("✅ ClaudeCore initialized with improvements")

    def _load_state(self) -> Dict:
        """Load persistent state from disk"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "created_at": datetime.now().isoformat(),
            "sessions": [],
            "decisions": [],
            "improvements": []
        }

    def _save_state(self):
        """Save state to disk"""
        self.state_file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def parse_request(self, request: str, context: Optional[Dict] = None) -> Dict:
        """
        Parse user request and classify it using role-based and niche-specific analysis

        Returns:
        {
            "type": RequestType,
            "project": ProjectType,
            "action": str,
            "parameters": Dict,
            "confidence": float,
            "role": AgentRole (optional),
            "niche": NicheCategory (optional)
        }
        """
        logger.info(f"[PARSE] {request[:100]}")

        request_lower = request.lower()

        # Check for self-improvement indicators
        if any(word in request_lower for word in ["improve", "analyse", "photo", "video", "tiktok", "self", "strengthen"]):
            return {
                "type": RequestType.SELF_IMPROVEMENT,
                "project": ProjectType.CLAUDE_CORE,
                "action": "analyze_media",
                "parameters": {"raw_request": request},
                "confidence": 0.9,
                "role": AgentRole.RESEARCHER
            }

        # Check for project-specific requests
        project_keywords = {
            ProjectType.P1_PRODUCT_DISCOVERY: ["product", "dropshipping", "supplier", "trending", "niche", "sourcing"],
            ProjectType.P2_MEDIA_AUTOMATION: ["video", "youtube", "tiktok", "media", "content", "script"],
            ProjectType.P3_KIDS_CONTENT: ["kids", "children", "kidz", "family", "education"],
            ProjectType.P4_MUSIC_GENERATION: ["music", "song", "audio", "suno", "beat", "track"],
        }

        for project, keywords in project_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                return {
                    "type": RequestType.PROJECT_SPECIFIC,
                    "project": project,
                    "action": self._extract_action(request),
                    "parameters": {"raw_request": request},
                    "confidence": 0.85
                }

        # Default to configuration/unknown
        return {
            "type": RequestType.CONFIGURATION,
            "project": ProjectType.CLAUDE_CORE,
            "action": "ask_clarification",
            "parameters": {"raw_request": request},
            "confidence": 0.5
        }

    def _extract_action(self, request: str) -> str:
        """Extract main action from request"""
        actions = {
            "find": ["find", "search", "discover", "locate"],
            "create": ["create", "generate", "make", "build"],
            "analyze": ["analyze", "examine", "review", "check"],
            "publish": ["publish", "post", "launch", "deploy"],
            "optimize": ["optimize", "improve", "enhance", "refine"],
        }

        request_lower = request.lower()
        for action, keywords in actions.items():
            if any(keyword in request_lower for keyword in keywords):
                return action

        return "unknown"

    def _detect_niche(self, request: str) -> Optional[NicheCategory]:
        """Detect which niche the request relates to"""
        request_lower = request.lower()

        niche_keywords = {
            NicheCategory.TECH: ["tech", "software", "ai", "code", "development", "innovation"],
            NicheCategory.FINANCE: ["finance", "money", "investment", "trading", "roi", "profit"],
            NicheCategory.HEALTH: ["health", "fitness", "wellness", "medical", "diet"],
            NicheCategory.EDUCATION: ["learning", "education", "course", "skill", "training"],
            NicheCategory.AI: ["ai", "machine learning", "neural", "model", "training"],
            NicheCategory.LIFESTYLE: ["lifestyle", "fashion", "travel", "home", "lifestyle"],
            NicheCategory.ECOMMERCE: ["ecommerce", "shopify", "store", "sell", "commerce"],
            NicheCategory.ENTERTAINMENT: ["entertainment", "funny", "meme", "comedy"],
            NicheCategory.SOCIAL_MEDIA: ["social", "tiktok", "instagram", "youtube", "viral"],
        }

        for niche, keywords in niche_keywords.items():
            if any(kw in request_lower for kw in keywords):
                return niche

        return None

    def _select_role(self, action: str, request: str) -> AgentRole:
        """Select optimal role based on action and request type"""
        action_lower = action.lower()
        request_lower = request.lower()

        if any(w in action_lower for w in ["find", "analyze", "discover"]):
            if "trend" in request_lower or "viral" in request_lower:
                return AgentRole.TREND_ANALYST
            return AgentRole.RESEARCHER
        elif any(w in action_lower for w in ["create", "strategy", "plan"]):
            return AgentRole.CONTENT_STRATEGIST
        elif any(w in action_lower for w in ["design", "architect", "system"]):
            return AgentRole.ARCHITECT
        elif any(w in action_lower for w in ["implement", "build"]):
            return AgentRole.IMPLEMENTER
        else:
            return AgentRole.VALIDATOR

    def route_request(self, parsed_request: Dict) -> Dict:
        """
        Route parsed request to appropriate handler
        """
        request_type = parsed_request["type"]
        project = parsed_request["project"]
        action = parsed_request["action"]

        logger.info(f"[ROUTE] {project.value} → {action} (confidence: {parsed_request['confidence']})")

        if request_type == RequestType.SELF_IMPROVEMENT:
            return self._handle_self_improvement(parsed_request)
        elif request_type == RequestType.PROJECT_SPECIFIC:
            return self._handle_project_request(parsed_request)
        else:
            return {
                "status": "clarification_needed",
                "message": "I need clarification about your request. Which project/section?",
                "suggestions": [p.value for p in ProjectType if p != ProjectType.CLAUDE_CORE]
            }

    def _handle_self_improvement(self, request: Dict) -> Dict:
        """Handle self-improvement requests"""
        logger.info("[SELF_IMPROVEMENT] Analyzing media for improvements")

        return {
            "status": "routed",
            "handler": "self_improvement_analyzer.py",
            "action": "analyze_media",
            "message": "Will analyze photos/videos/TikTok links and propose improvements",
            "next_step": "Launch synthesis pipeline"
        }

    def _handle_project_request(self, request: Dict) -> Dict:
        """Route to specific project handler with role and niche awareness"""
        project = request["project"]
        action = request["action"]
        raw_request = request.get("parameters", {}).get("raw_request", "")

        handlers = {
            ProjectType.P1_PRODUCT_DISCOVERY: f"projects/p1_product_discovery/orchestrator.py",
            ProjectType.P2_MEDIA_AUTOMATION: f"projects/p2_media_automation/orchestrator.py",
            ProjectType.P3_KIDS_CONTENT: f"projects/p3_kids_content/orchestrator.py",
            ProjectType.P4_MUSIC_GENERATION: f"projects/p4_music_generation/orchestrator.py",
            ProjectType.P5_FUTURE: f"projects/p5_future/orchestrator.py",
        }

        # Detect niche and select role
        niche = self._detect_niche(raw_request)
        role = self._select_role(action, raw_request)

        logger.info(f"[ROUTE_PROJECT] {project.value} → {action} (role: {role.value}, niche: {niche.value if niche else 'generic'})")

        return {
            "status": "routed",
            "handler": handlers.get(project, "unknown"),
            "project": project.value,
            "action": action,
            "role": role.value,
            "niche": niche.value if niche else None,
            "parameters": request["parameters"],
            "message": f"Routing to {project.value} with {role.value} role"
        }

    def process_request(self, request: str, context: Optional[Dict] = None) -> Dict:
        """
        Main entry point: Parse → Route → Execute
        """
        logger.info("="*70)
        logger.info(f"[PROCESS_REQUEST] {request}")
        logger.info("="*70)

        # Parse
        parsed = self.parse_request(request, context)

        # Save decision
        self.state["decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "parsed": {
                "type": parsed["type"].value,
                "project": parsed["project"].value,
                "action": parsed["action"]
            }
        })

        # Route
        result = self.route_request(parsed)

        # Save state
        self._save_state()

        return result

    def register_project(self, project_type: ProjectType, handler: Any):
        """Register a project handler"""
        self.projects[project_type] = handler
        logger.info(f"✅ Registered {project_type.value}")

    def register_agent(self, project_type: ProjectType, agent: Any):
        """Register a project agent"""
        self.agents[project_type] = agent
        logger.info(f"✅ Registered agent for {project_type.value}")

    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "projects_registered": len(self.projects),
            "agents_registered": len(self.agents),
            "decisions_made": len(self.state["decisions"]),
            "improvements_tracked": len(self.state["improvements"]),
            "projects": [p.value for p in self.projects.keys()],
            "agents": [p.value for p in self.agents.keys()]
        }

    def log_improvement(self, improvement: Dict):
        """Log an improvement made"""
        self.state["improvements"].append({
            "timestamp": datetime.now().isoformat(),
            "improvement": improvement
        })
        self._save_state()
        logger.info(f"✅ Logged improvement: {improvement.get('name', 'unknown')}")


def main():
    """Demo ClaudeCore"""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    # Create core
    core = ClaudeCore()

    print("\n" + "="*70)
    print("[CLAUDE CORE] Central Brain & Decision Engine")
    print("="*70)

    # Test requests
    test_requests = [
        "Analyse these photos and improve my capabilities",
        "Find trending products in the tech niche",
        "Create a viral TikTok video about AI",
        "Generate music for a video",
        "How am I doing?",
    ]

    for request in test_requests:
        print(f"\n[USER] {request}")
        result = core.process_request(request)
        print(f"[CORE] Status: {result['status']}")
        print(f"[CORE] Handler: {result.get('handler', 'N/A')}")

    # Show status
    print("\n[STATUS]")
    status = core.get_system_status()
    for key, value in status.items():
        if key != "timestamp":
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
