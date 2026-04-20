#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Agent Framework - Base classes and manager
Consolidates dropflow_agents.py + managed_agents_framework.py
Single source of truth for all agent operations
"""

import logging
import asyncio
import time
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    GUARDRAIL_TRIGGERED = "guardrail_triggered"
    RETRYING = "retrying"

class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class AgentType(Enum):
    """Agent specialization types"""
    GENERIC = "generic"
    P1_PRODUCT_DISCOVERY = "p1_product_discovery"
    P2_MEDIA_AUTOMATION = "p2_media_automation"
    P3_KIDS_CONTENT = "p3_kids_content"
    P4_MUSIC_GENERATION = "p4_music_generation"

@dataclass
class Tool:
    """Tool definition"""
    name: str
    description: str
    handler: Callable
    requires_guardrails: bool = True
    category: str = "general"

@dataclass
class Guardrail:
    """Safety guardrail"""
    name: str
    check: Callable[[Dict], bool]
    on_fail: str = "block"  # "block", "warn", "retry"
    max_retries: int = 3

@dataclass
class Task:
    """Individual task"""
    id: str
    name: str
    description: str
    tools: List[str]
    priority: Priority = Priority.MEDIUM
    max_retries: int = 3
    timeout: int = 300
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    attempts: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

@dataclass
class AgentSession:
    """Agent execution session"""
    id: str
    name: str
    agent_type: AgentType = AgentType.GENERIC
    created_at: float = field(default_factory=time.time)
    tasks: List[Task] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_cost: float = 0.0
    metadata: Dict = field(default_factory=dict)

# ============================================================================
# UNIFIED AGENT BASE CLASS
# ============================================================================

class UnifiedAgent:
    """
    Base agent class for all agent types

    Combines features from:
    - dropflow_agents.py (specialized tools, guardrails)
    - managed_agents_framework.py (async workflows, monitoring)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: AgentType = AgentType.GENERIC,
        api_key: Optional[str] = None,
        provider: str = "anthropic"
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.api_key = api_key
        self.provider = provider

        self.tools_registry: Dict[str, Tool] = {}
        self.guardrails: List[Guardrail] = []
        self.sessions: Dict[str, AgentSession] = {}
        self.execution_history = []

        logger.info(f"✅ Created agent: {name} ({agent_type.value})")

    # ========================================================================
    # TOOL MANAGEMENT
    # ========================================================================

    def register_tool(self, tool: Tool) -> bool:
        """Register a new tool"""
        if tool.name in self.tools_registry:
            logger.warning(f"Tool {tool.name} already registered")
            return False

        self.tools_registry[tool.name] = tool
        logger.info(f"📌 Registered tool: {tool.name}")
        return True

    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        if tool_name not in self.tools_registry:
            return False

        del self.tools_registry[tool_name]
        logger.info(f"🗑️ Unregistered tool: {tool_name}")
        return True

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a registered tool"""
        return self.tools_registry.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools_registry.keys())

    # ========================================================================
    # GUARDRAIL MANAGEMENT
    # ========================================================================

    def add_guardrail(self, guardrail: Guardrail) -> bool:
        """Add a safety guardrail"""
        self.guardrails.append(guardrail)
        logger.info(f"🛡️ Added guardrail: {guardrail.name}")
        return True

    def check_guardrails(self, context: Dict) -> tuple[bool, Optional[str]]:
        """Check all guardrails before action"""
        for guardrail in self.guardrails:
            if not guardrail.check(context):
                logger.warning(f"⚠️ Guardrail triggered: {guardrail.name}")
                return False, guardrail.name

        return True, None

    # ========================================================================
    # TASK MANAGEMENT
    # ========================================================================

    def create_session(self, session_id: str, name: str) -> AgentSession:
        """Create a new execution session"""
        session = AgentSession(
            id=session_id,
            name=name,
            agent_type=self.agent_type
        )
        self.sessions[session_id] = session
        logger.info(f"📂 Created session: {session_id}")
        return session

    def add_task(self, session_id: str, task: Task) -> bool:
        """Add task to a session"""
        if session_id not in self.sessions:
            logger.error(f"Session {session_id} not found")
            return False

        session = self.sessions[session_id]
        session.tasks.append(task)
        logger.info(f"➕ Added task: {task.name}")
        return True

    def get_task(self, session_id: str, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        for task in session.tasks:
            if task.id == task_id:
                return task

        return None

    # ========================================================================
    # EXECUTION
    # ========================================================================

    async def execute_task(self, session_id: str, task_id: str) -> Dict:
        """
        Execute a single task with retry logic and guardrails

        Returns:
        {
            "status": "success"|"failed",
            "task_id": str,
            "result": Any,
            "duration": float,
            "attempts": int,
            "error": Optional[str]
        }
        """
        task = self.get_task(session_id, task_id)
        if not task:
            return {
                "status": "failed",
                "error": "Task not found",
                "task_id": task_id
            }

        session = self.sessions[session_id]
        task.status = TaskStatus.RUNNING
        start_time = time.time()

        # Check guardrails
        guardrails_ok, guardrail_name = self.check_guardrails({"task": task})
        if not guardrails_ok:
            task.status = TaskStatus.GUARDRAIL_TRIGGERED
            task.error = f"Guardrail triggered: {guardrail_name}"
            logger.warning(f"Task {task_id} blocked by guardrail")
            return {
                "status": "guardrail_triggered",
                "task_id": task_id,
                "error": task.error
            }

        # Execute with retry logic
        for attempt in range(task.max_retries):
            try:
                task.attempts = attempt + 1
                task.status = TaskStatus.RUNNING if attempt == 0 else TaskStatus.RETRYING

                # Execute tools
                result = await self._execute_tools(task)

                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.time()
                session.completed_tasks += 1

                duration = time.time() - start_time

                logger.info(f"✅ Task completed: {task_id} (attempt {attempt+1})")

                return {
                    "status": "success",
                    "task_id": task_id,
                    "result": result,
                    "duration": duration,
                    "attempts": attempt + 1
                }

            except Exception as e:
                logger.warning(f"❌ Attempt {attempt+1} failed: {e}")
                if attempt == task.max_retries - 1:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    session.failed_tasks += 1

                    duration = time.time() - start_time

                    return {
                        "status": "failed",
                        "task_id": task_id,
                        "error": str(e),
                        "duration": duration,
                        "attempts": attempt + 1
                    }

                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        return {
            "status": "failed",
            "task_id": task_id,
            "error": "Max retries exceeded",
            "attempts": task.max_retries
        }

    async def _execute_tools(self, task: Task) -> Dict:
        """Execute required tools for a task"""
        results = {}

        for tool_name in task.tools:
            tool = self.get_tool(tool_name)
            if not tool:
                logger.warning(f"Tool {tool_name} not found")
                continue

            logger.info(f"🔧 Executing tool: {tool_name}")

            # Check guardrails for tool if required
            if tool.requires_guardrails:
                ok, _ = self.check_guardrails({"tool": tool_name})
                if not ok:
                    results[tool_name] = {"error": "Guardrail check failed"}
                    continue

            # Execute tool handler
            try:
                if asyncio.iscoroutinefunction(tool.handler):
                    result = await tool.handler()
                else:
                    result = tool.handler()

                results[tool_name] = result
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                results[tool_name] = {"error": str(e)}

        return results

    async def execute_sequential(self, session_id: str, task_ids: List[str]) -> List[Dict]:
        """
        Execute tasks sequentially with context passing
        """
        results = []
        context = {}

        for task_id in task_ids:
            task = self.get_task(session_id, task_id)
            if task:
                # Add previous context
                task.metadata = context

                result = await self.execute_task(session_id, task_id)
                results.append(result)

                # Update context for next task
                if result.get("status") == "success":
                    context = result.get("result", {})

        return results

    async def execute_parallel(self, session_id: str, task_ids: List[str]) -> Dict[str, Dict]:
        """
        Execute multiple tasks in parallel
        """
        tasks = [
            self.execute_task(session_id, task_id)
            for task_id in task_ids
        ]

        results = await asyncio.gather(*tasks)

        return {
            task_ids[i]: results[i]
            for i in range(len(task_ids))
        }

    # ========================================================================
    # MONITORING & STATISTICS
    # ========================================================================

    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get session status"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        total_tasks = len(session.tasks)
        pending = sum(1 for t in session.tasks if t.status == TaskStatus.PENDING)
        running = sum(1 for t in session.tasks if t.status == TaskStatus.RUNNING)

        return {
            "session_id": session_id,
            "agent_type": session.agent_type.value,
            "created_at": datetime.fromtimestamp(session.created_at).isoformat(),
            "total_tasks": total_tasks,
            "completed": session.completed_tasks,
            "failed": session.failed_tasks,
            "pending": pending,
            "running": running,
            "success_rate": (session.completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_cost": session.total_cost
        }

    def get_agent_statistics(self) -> Dict:
        """Get overall agent statistics"""
        total_sessions = len(self.sessions)
        total_completed = sum(s.completed_tasks for s in self.sessions.values())
        total_failed = sum(s.failed_tasks for s in self.sessions.values())
        total_cost = sum(s.total_cost for s in self.sessions.values())

        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_sessions": total_sessions,
            "total_tools": len(self.tools_registry),
            "total_guardrails": len(self.guardrails),
            "total_tasks_completed": total_completed,
            "total_tasks_failed": total_failed,
            "total_cost": total_cost,
            "success_rate": (total_completed / (total_completed + total_failed) * 100) if (total_completed + total_failed) > 0 else 0
        }


def main():
    """Demo UnifiedAgent"""
    logging.basicConfig(level=logging.INFO)

    print("\n" + "="*70)
    print("[UNIFIED AGENT] Base Framework Demo")
    print("="*70)

    # Create agent
    agent = UnifiedAgent(
        agent_id="demo_agent_1",
        name="Demo Agent",
        agent_type=AgentType.P1_PRODUCT_DISCOVERY
    )

    # Register tools
    def dummy_tool():
        return {"status": "success", "data": "dummy"}

    agent.register_tool(Tool(
        name="tool1",
        description="Dummy tool",
        handler=dummy_tool
    ))

    # Create session
    session = agent.create_session("session_1", "Demo Session")

    # Add task
    task = Task(
        id="task_1",
        name="Test Task",
        description="Test execution",
        tools=["tool1"]
    )
    agent.add_task("session_1", task)

    print("\n[STATISTICS]")
    stats = agent.get_agent_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
