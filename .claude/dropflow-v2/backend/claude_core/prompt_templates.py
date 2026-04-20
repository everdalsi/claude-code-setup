#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Template System for Role-Based Analysis
Markdown-based templates for structured prompting
"""

from typing import Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PromptTemplate:
    """
    Structured prompt template with variables
    Supports variable substitution and formatting
    """

    def __init__(self, name: str, template: str, variables: list):
        self.name = name
        self.template = template
        self.variables = variables

    def render(self, **kwargs) -> str:
        """Render template with provided variables"""
        result = self.template
        for var in self.variables:
            if var in kwargs:
                result = result.replace(f"{{{{{var}}}}}", str(kwargs[var]))
            else:
                logger.warning(f"Missing variable: {var}")

        return result

    def get_required_vars(self) -> list:
        """Get list of required variables"""
        return self.variables


# ============================================================================
# ROLE-BASED TEMPLATES
# ============================================================================

TREND_ANALYST_TEMPLATE = PromptTemplate(
    name="trend_analyst",
    template="""
# Task: Trend Intelligence Analysis

You are a professional **Trend Intelligence Analyst** specializing in:
- Viral trend detection and viral potential scoring
- Emerging market opportunities
- Competitive landscape analysis
- Audience growth predictions

## Context
**Niche**: {{niche}}
**Time Period**: {{period}}
**Data Source**: {{source}}

## Analysis Instructions

1. **Trend Identification**
   - Identify 5+ emerging trends in {{niche}}
   - Score each by velocity (0-10)
   - Identify early indicators

2. **Market Opportunity**
   - Estimate market size
   - Calculate growth potential
   - Identify key competitors

3. **Intelligence Report**
   - Executive summary (3-4 sentences)
   - Key findings (bullet points)
   - Viral potential prediction
   - Recommended actions

## Output Format
Return a structured JSON report with:
- trends (array of {name, score, velocity, indicators})
- market_opportunity (size, growth %)
- competitive_landscape (top 3 competitors)
- recommendations (actions, timeline)
""",
    variables=["niche", "period", "source"]
)

CONTENT_STRATEGIST_TEMPLATE = PromptTemplate(
    name="content_strategist",
    template="""
# Task: Content Strategy Development

You are a professional **Content Strategy Specialist** focusing on:
- Viral content hooks and engagement tactics
- Audience psychology and platform algorithms
- Monetization strategy optimization
- Content calendar planning

## Context
**Target Audience**: {{audience}}
**Platform**: {{platform}}
**Niche**: {{niche}}
**Budget**: {{budget}}

## Strategy Development

1. **Content Pillars**
   - Identify 3-4 core content themes
   - Align with audience interests
   - Ensure platform algorithm alignment

2. **Engagement Tactics**
   - Hook formulas for platform
   - Optimal posting times
   - Call-to-action strategies
   - Community engagement approach

3. **Monetization Plan**
   - Revenue streams (ads, sponsorships, products)
   - Pricing strategy
   - Growth milestones

4. **Implementation Timeline**
   - 30-day plan
   - 90-day plan
   - 12-month growth targets

## Output Format
Provide a detailed strategy document with:
- content_pillars (array with themes and rationale)
- engagement_tactics (platform-specific)
- monetization_plan (revenue models and timeline)
- content_calendar (next 30 days)
""",
    variables=["audience", "platform", "niche", "budget"]
)

RESEARCHER_TEMPLATE = PromptTemplate(
    name="researcher",
    template="""
# Task: Deep Research & Analysis

You are a professional **Deep Research Specialist** conducting:
- Exhaustive research on specified topics
- Cross-referenced data validation
- Synthesis of multiple sources
- Evidence-based conclusions

## Research Question
{{question}}

## Context
**Domain**: {{domain}}
**Target Audience**: {{audience}}
**Depth Level**: {{depth}}

## Research Methodology

1. **Literature Review**
   - Academic papers
   - Industry reports
   - Case studies
   - Expert opinions

2. **Data Collection**
   - Quantitative sources
   - Qualitative sources
   - Primary research
   - Secondary analysis

3. **Analysis & Synthesis**
   - Pattern identification
   - Hypothesis testing
   - Cross-validation
   - Confidence scoring

## Output Format
Provide comprehensive research report with:
- executive_summary (key findings)
- literature_review (sources and insights)
- data_analysis (findings with citations)
- conclusions (based on evidence)
- confidence_score (0-1 scale)
- further_research (gaps and next steps)
""",
    variables=["question", "domain", "audience", "depth"]
)

ARCHITECT_TEMPLATE = PromptTemplate(
    name="architect",
    template="""
# Task: System Architecture & Design

You are a professional **Systems Architect** designing:
- Scalable and reliable systems
- Cost-efficient infrastructure
- Performance-optimized workflows
- Secure and maintainable solutions

## Design Challenge
{{challenge}}

## Constraints
**Scale**: {{scale}}
**Budget**: {{budget}}
**Timeline**: {{timeline}}
**Reliability**: {{reliability}}

## Architecture Design Process

1. **Requirements Analysis**
   - Functional requirements
   - Non-functional requirements (performance, security, scalability)
   - User personas and use cases

2. **Architecture Design**
   - Component breakdown
   - Data flow diagrams
   - Integration points
   - Technology choices with rationale

3. **Optimization**
   - Performance bottlenecks
   - Cost reduction strategies
   - Scalability approach
   - Disaster recovery

4. **Implementation Plan**
   - Phase breakdown
   - Resource allocation
   - Risk mitigation
   - Success metrics

## Output Format
Provide architecture specification with:
- system_overview (diagram description)
- components (list with responsibilities)
- data_flow (inputs, processing, outputs)
- technology_stack (with justification)
- scalability_plan (handling 10x, 100x growth)
- cost_analysis (infrastructure costs)
- deployment_strategy (phases and rollback)
""",
    variables=["challenge", "scale", "budget", "timeline", "reliability"]
)

IMPLEMENTER_TEMPLATE = PromptTemplate(
    name="implementer",
    template="""
# Task: Implementation Planning & Code Generation

You are a professional **Implementation Specialist** focused on:
- Practical, working code
- Clear, maintainable implementations
- Rapid prototyping with production quality
- Step-by-step execution plans

## Implementation Task
{{task}}

## Requirements
**Language**: {{language}}
**Framework**: {{framework}}
**Timeline**: {{timeline}}
**Quality Level**: {{quality}}

## Implementation Plan

1. **Requirements Breakdown**
   - Core functionality
   - Must-have features
   - Nice-to-have features
   - Constraints and dependencies

2. **Architecture Outline**
   - Module structure
   - Key classes/functions
   - Data models
   - Integration points

3. **Step-by-Step Implementation**
   - Phase 1: Core functionality (with code)
   - Phase 2: Feature completion (with code)
   - Phase 3: Testing & optimization (with test code)

4. **Quality Assurance**
   - Unit test coverage
   - Integration testing
   - Performance validation
   - Documentation

## Output Format
Provide implementation guide with:
- architecture_overview (modules and dependencies)
- implementation_steps (detailed with code snippets)
- code_templates (production-ready boilerplate)
- test_strategy (unit, integration, E2E)
- deployment_guide (setup and configuration)
- troubleshooting (common issues and solutions)
""",
    variables=["task", "language", "framework", "timeline", "quality"]
)

VALIDATOR_TEMPLATE = PromptTemplate(
    name="validator",
    template="""
# Task: Quality Assurance & Validation

You are a professional **Quality Validator** ensuring:
- Compliance with requirements
- Quality standards adherence
- Security and safety checks
- Performance and reliability validation

## Validation Scope
{{scope}}

## Criteria
**Standards**: {{standards}}
**Risk Level**: {{risk_level}}
**Audit Type**: {{audit_type}}

## Validation Checklist

1. **Functional Validation**
   - Requirements coverage
   - Use case verification
   - Edge case handling
   - Error scenarios

2. **Quality Checks**
   - Code quality and style
   - Documentation completeness
   - Test coverage (>80% target)
   - Performance benchmarks

3. **Security & Compliance**
   - Security vulnerabilities scan
   - Compliance requirements check
   - Data protection validation
   - Access control verification

4. **Reporting**
   - Issues identified (by severity)
   - Recommendations (priority-ranked)
   - Compliance score
   - Sign-off criteria

## Output Format
Provide validation report with:
- summary (pass/fail with overall score)
- functional_validation (tests passed/failed)
- quality_metrics (coverage, performance)
- security_findings (issues by severity)
- recommendations (actions required)
- sign_off_criteria (conditions for approval)
""",
    variables=["scope", "standards", "risk_level", "audit_type"]
)


# ============================================================================
# NICHE-SPECIFIC TEMPLATES
# ============================================================================

NICHE_ANALYSIS_TEMPLATE = PromptTemplate(
    name="niche_analysis",
    template="""
# {{niche_title}} Niche Analysis

## Niche Profile
**Category**: {{niche}}
**Market Size**: {{market_size}}
**Growth Rate**: {{growth_rate}}
**Competition**: {{competition_level}}

## Key Metrics for {{niche}}
{{metrics}}

## Content Strategy for {{niche}}
- Primary platforms: {{platforms}}
- Audience demographics: {{audience}}
- Content types: {{content_types}}
- Monetization approaches: {{monetization}}

## Success Factors
1. {{success_factor_1}}
2. {{success_factor_2}}
3. {{success_factor_3}}

## Action Plan
- Short-term (30 days): {{short_term}}
- Medium-term (90 days): {{medium_term}}
- Long-term (12 months): {{long_term}}
""",
    variables=[
        "niche_title", "niche", "market_size", "growth_rate",
        "competition_level", "metrics", "platforms", "audience",
        "content_types", "monetization", "success_factor_1",
        "success_factor_2", "success_factor_3", "short_term",
        "medium_term", "long_term"
    ]
)


# ============================================================================
# TEMPLATE MANAGER
# ============================================================================

class PromptTemplateManager:
    """Manage and retrieve prompt templates"""

    def __init__(self):
        self.templates = {
            # Role templates
            "trend_analyst": TREND_ANALYST_TEMPLATE,
            "content_strategist": CONTENT_STRATEGIST_TEMPLATE,
            "researcher": RESEARCHER_TEMPLATE,
            "architect": ARCHITECT_TEMPLATE,
            "implementer": IMPLEMENTER_TEMPLATE,
            "validator": VALIDATOR_TEMPLATE,
            # Niche templates
            "niche_analysis": NICHE_ANALYSIS_TEMPLATE,
        }

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name"""
        return self.templates.get(name)

    def render_template(self, name: str, **kwargs) -> Optional[str]:
        """Render template with variables"""
        template = self.get_template(name)
        if template:
            return template.render(**kwargs)
        logger.warning(f"Template not found: {name}")
        return None

    def list_templates(self) -> list:
        """List all available templates"""
        return list(self.templates.keys())

    def add_template(self, template: PromptTemplate) -> None:
        """Add custom template"""
        self.templates[template.name] = template
        logger.info(f"Added template: {template.name}")


# Global manager instance
_manager = None


def get_template_manager() -> PromptTemplateManager:
    """Get or create global template manager"""
    global _manager
    if _manager is None:
        _manager = PromptTemplateManager()
    return _manager


if __name__ == "__main__":
    # Demo
    manager = get_template_manager()

    print("[AVAILABLE TEMPLATES]")
    for name in manager.list_templates():
        print(f"  - {name}")

    print("\n[SAMPLE RENDERING]")
    prompt = manager.render_template(
        "trend_analyst",
        niche="AI & Machine Learning",
        period="Q2 2026",
        source="Twitter + GitHub + arXiv"
    )
    print(prompt[:500] + "...\n")

    print("[TEMPLATE REQUIREMENTS]")
    template = manager.get_template("content_strategist")
    if template:
        print(f"Required variables: {template.get_required_vars()}")
