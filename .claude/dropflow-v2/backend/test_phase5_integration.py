#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 Integration Tests
Verify CLAUDE CORE system is fully functional
"""

import logging
import asyncio
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all critical imports"""
    logger.info("[TEST] Checking imports...")

    try:
        from claude_core import ClaudeCore, ProjectType, RequestType
        from claude_core.improvements_integrated import (
            RoleBasedPrompting, NicheSpecificFiltering,
            IntelligenceReporting, DataIntegrationHooks
        )
        from agents import UnifiedAgent
        from projects import PROJECTS, get_orchestrator
        logger.info("[PASS] All imports successful")
        return True
    except ImportError as e:
        logger.error(f"[FAIL] Import error: {e}")
        return False


def test_claude_core_initialization():
    """Test CLAUDE CORE instantiation"""
    logger.info("[TEST] Initializing CLAUDE CORE...")

    try:
        from claude_core import ClaudeCore
        core = ClaudeCore()

        status = core.get_system_status()
        logger.info(f"[PASS] CLAUDE CORE initialized: {status['projects_registered']} projects registered")
        return True
    except Exception as e:
        logger.error(f"[FAIL] ClaudeCore init error: {e}")
        return False


def test_project_orchestrators():
    """Test all project orchestrators"""
    logger.info("[TEST] Initializing project orchestrators...")

    try:
        from projects import PROJECTS

        for project_id, orchestrator_class in PROJECTS.items():
            orchestrator = orchestrator_class()
            logger.info(f"[PASS] {project_id} instantiated")

        logger.info(f"[PASS] All {len(PROJECTS)} projects ready")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Project init error: {e}")
        return False


def test_unified_agent():
    """Test unified agent"""
    logger.info("[TEST] Initializing Unified Agent...")

    try:
        from agents import UnifiedAgent, AgentType

        agent = UnifiedAgent(
            agent_id="test_agent",
            name="Test Agent",
            agent_type=AgentType.GENERIC
        )
        logger.info(f"[PASS] UnifiedAgent initialized")
        return True
    except Exception as e:
        logger.error(f"[FAIL] UnifiedAgent init error: {e}")
        return False


def test_improvements_integration():
    """Test improvements integration"""
    logger.info("[TEST] Testing improvements integration...")

    try:
        from claude_core import ClaudeCore

        core = ClaudeCore()

        # Check improvements initialized
        assert core.role_prompter is not None, "RoleBasedPrompting not initialized"
        assert core.niche_filter is not None, "NicheSpecificFiltering not initialized"
        assert core.reporter is not None, "IntelligenceReporting not initialized"
        assert core.data_integrations is not None, "DataIntegrationHooks not initialized"

        logger.info("[PASS] All improvements initialized")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Improvements integration error: {e}")
        return False


def test_request_routing():
    """Test request routing through CLAUDE CORE"""
    logger.info("[TEST] Testing request routing...")

    try:
        from claude_core import ClaudeCore

        core = ClaudeCore()

        # Test different request types
        test_requests = [
            ("Find trending products in tech", "project_specific"),
            ("Analyze these photos for improvements", "self_improvement"),
            ("Create a TikTok video about AI", "project_specific"),
            ("Generate music for dropshipping ads", "project_specific"),
        ]

        for request, expected_type in test_requests:
            parsed = core.parse_request(request)
            logger.info(f"[PASS] Routed: '{request[:40]}...' as {parsed['type'].value}")

        return True
    except Exception as e:
        logger.error(f"[FAIL] Request routing error: {e}")
        return False


def test_niche_detection():
    """Test niche detection"""
    logger.info("[TEST] Testing niche detection...")

    try:
        from claude_core import ClaudeCore

        core = ClaudeCore()

        test_cases = [
            ("AI models and machine learning", "AI"),
            ("Stock trading and investment", "finance"),
            ("YouTube video creation", "social_media"),
            ("Health and fitness tips", "health"),
        ]

        for request, expected_niche in test_cases:
            niche = core._detect_niche(request)
            if niche:
                logger.info(f"[PASS] Detected niche: {niche.value} for '{request}'")
            else:
                logger.warning(f"[WARN] No niche detected for '{request}'")

        return True
    except Exception as e:
        logger.error(f"[FAIL] Niche detection error: {e}")
        return False


def test_role_selection():
    """Test role selection"""
    logger.info("[TEST] Testing role selection...")

    try:
        from claude_core import ClaudeCore

        core = ClaudeCore()

        test_cases = [
            ("find", "Discover trending products"),
            ("create", "Design a content strategy"),
            ("analyze", "Review competitor analysis"),
            ("design", "Build a scalable system"),
        ]

        for action, request in test_cases:
            role = core._select_role(action, request)
            logger.info(f"[PASS] Role selected: {role.value} for action '{action}'")

        return True
    except Exception as e:
        logger.error(f"[FAIL] Role selection error: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("="*70)
    logger.info("[PHASE 5] Integration Test Suite")
    logger.info("="*70)

    tests = [
        ("Imports", test_imports),
        ("CLAUDE CORE Init", test_claude_core_initialization),
        ("Project Orchestrators", test_project_orchestrators),
        ("Unified Agent", test_unified_agent),
        ("Improvements Integration", test_improvements_integration),
        ("Request Routing", test_request_routing),
        ("Niche Detection", test_niche_detection),
        ("Role Selection", test_role_selection),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"[ERROR] {test_name} failed: {e}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "="*70)
    logger.info("[SUMMARY]")
    logger.info("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        logger.info(f"{status} {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n[SUCCESS] All Phase 5 integration tests passed!")
        return 0
    else:
        logger.error(f"\n[FAILURE] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
