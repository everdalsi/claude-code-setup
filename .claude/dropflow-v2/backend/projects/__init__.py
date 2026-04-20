#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Projects - All business automation projects (P1-P5)"""

from .p1_product_discovery import P1Orchestrator
from .p2_media_automation import P2Orchestrator
from .p3_kids_content import P3Orchestrator
from .p4_music_generation import P4Orchestrator
from .p5_future import P5Orchestrator

__all__ = [
    'P1Orchestrator',
    'P2Orchestrator',
    'P3Orchestrator',
    'P4Orchestrator',
    'P5Orchestrator',
]

__version__ = '1.0.0'

# Project registry
PROJECTS = {
    'p1_product_discovery': P1Orchestrator,
    'p2_media_automation': P2Orchestrator,
    'p3_kids_content': P3Orchestrator,
    'p4_music_generation': P4Orchestrator,
    'p5_future': P5Orchestrator,
}

def get_orchestrator(project_id: str):
    """Get orchestrator for a project"""
    orchestrator_class = PROJECTS.get(project_id)
    if orchestrator_class:
        return orchestrator_class()
    return None
