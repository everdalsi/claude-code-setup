#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Coordinator - Manage all active projects
Coordinates execution across P1-P5 and self-improvement
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Project status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

class ProjectCoordinator:
    """
    Manages all active projects and their execution
    Ensures proper resource allocation and sequencing
    """

    def __init__(self):
        self.projects = {}
        self.active_project = None
        self.execution_queue = []
        self.completion_history = []

    def register_project(self, project_id: str, project_config: Dict) -> bool:
        """
        Register a new project

        Config should contain:
        {
            "name": str,
            "type": ProjectType,
            "status": ProjectStatus,
            "handler": str (file path to handler),
            "dependencies": List[str],
            "priority": int
        }
        """
        if project_id in self.projects:
            logger.warning(f"Project {project_id} already registered")
            return False

        self.projects[project_id] = {
            "id": project_id,
            "created_at": datetime.now().isoformat(),
            "config": project_config,
            "status": ProjectStatus.IDLE,
            "execution_count": 0,
            "success_count": 0,
            "error_count": 0,
            "last_execution": None,
            "metadata": {}
        }

        logger.info(f"✅ Registered project: {project_id}")
        return True

    def schedule_project(self, project_id: str, priority: int = 5) -> bool:
        """
        Schedule project for execution

        Priority: 1 (highest) - 10 (lowest)
        """
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return False

        self.execution_queue.append({
            "project_id": project_id,
            "priority": priority,
            "scheduled_at": datetime.now().isoformat()
        })

        # Sort by priority
        self.execution_queue.sort(key=lambda x: x["priority"])

        logger.info(f"📋 Scheduled {project_id} with priority {priority}")
        return True

    def execute_project(self, project_id: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute a specific project

        Returns execution result
        """
        if project_id not in self.projects:
            return {
                "status": "error",
                "message": f"Project {project_id} not found"
            }

        project = self.projects[project_id]

        # Check dependencies
        if not self._check_dependencies(project_id):
            return {
                "status": "error",
                "message": "Dependencies not met",
                "project_id": project_id
            }

        # Update status
        project["status"] = ProjectStatus.RUNNING
        project["execution_count"] += 1

        logger.info(f"🚀 Executing project: {project_id}")

        try:
            # Execute the project handler
            result = self._execute_handler(project_id, context)

            # Update status based on result
            if result.get("success"):
                project["status"] = ProjectStatus.COMPLETED
                project["success_count"] += 1
            else:
                project["status"] = ProjectStatus.ERROR
                project["error_count"] += 1

            project["last_execution"] = datetime.now().isoformat()

            # Log to history
            self.completion_history.append({
                "project_id": project_id,
                "timestamp": datetime.now().isoformat(),
                "status": result.get("status", "unknown"),
                "duration": result.get("duration", 0)
            })

            return result

        except Exception as e:
            logger.error(f"❌ Error executing {project_id}: {e}")
            project["status"] = ProjectStatus.ERROR
            project["error_count"] += 1
            return {
                "status": "error",
                "message": str(e),
                "project_id": project_id
            }

    def _check_dependencies(self, project_id: str) -> bool:
        """Check if project dependencies are met"""
        project = self.projects[project_id]
        dependencies = project["config"].get("dependencies", [])

        for dep in dependencies:
            if dep not in self.projects:
                logger.warning(f"Dependency {dep} not found")
                return False

            dep_project = self.projects[dep]
            if dep_project["status"] != ProjectStatus.COMPLETED:
                logger.warning(f"Dependency {dep} not completed")
                return False

        return True

    def _execute_handler(self, project_id: str, context: Optional[Dict] = None) -> Dict:
        """
        Execute project handler
        In real implementation, would import and run the handler
        """
        project = self.projects[project_id]
        handler_path = project["config"].get("handler")

        logger.info(f"[EXECUTE_HANDLER] {handler_path}")

        # This would be replaced with actual handler invocation
        return {
            "status": "success",
            "project_id": project_id,
            "handler": handler_path,
            "message": f"Executed {project_id}",
            "duration": 0
        }

    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get status of a specific project"""
        if project_id not in self.projects:
            return None

        project = self.projects[project_id]
        return {
            "id": project_id,
            "name": project["config"].get("name"),
            "status": project["status"].value,
            "execution_count": project["execution_count"],
            "success_count": project["success_count"],
            "error_count": project["error_count"],
            "last_execution": project["last_execution"],
            "created_at": project["created_at"]
        }

    def get_all_projects_status(self) -> List[Dict]:
        """Get status of all projects"""
        return [
            self.get_project_status(pid)
            for pid in self.projects.keys()
        ]

    def get_execution_queue(self) -> List[Dict]:
        """Get current execution queue"""
        return self.execution_queue.copy()

    def get_statistics(self) -> Dict:
        """Get overall coordination statistics"""
        total_projects = len(self.projects)
        active = sum(1 for p in self.projects.values() if p["status"] == ProjectStatus.RUNNING)
        completed = sum(1 for p in self.projects.values() if p["status"] == ProjectStatus.COMPLETED)
        errors = sum(1 for p in self.projects.values() if p["status"] == ProjectStatus.ERROR)

        total_executions = sum(p["execution_count"] for p in self.projects.values())
        total_successes = sum(p["success_count"] for p in self.projects.values())
        total_errors = sum(p["error_count"] for p in self.projects.values())

        success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0

        return {
            "total_projects": total_projects,
            "active_projects": active,
            "completed_projects": completed,
            "error_projects": errors,
            "total_executions": total_executions,
            "total_successes": total_successes,
            "total_errors": total_errors,
            "success_rate": f"{success_rate:.1f}%",
            "queued_items": len(self.execution_queue),
            "completion_history_count": len(self.completion_history)
        }

    def reset_project(self, project_id: str) -> bool:
        """Reset project status to idle"""
        if project_id not in self.projects:
            return False

        self.projects[project_id]["status"] = ProjectStatus.IDLE
        logger.info(f"🔄 Reset project: {project_id}")
        return True

    def clear_queue(self):
        """Clear execution queue"""
        self.execution_queue.clear()
        logger.info("🗑️ Cleared execution queue")


def main():
    """Demo ProjectCoordinator"""
    import logging
    logging.basicConfig(level=logging.INFO)

    coordinator = ProjectCoordinator()

    print("\n" + "="*70)
    print("[PROJECT COORDINATOR] Multi-Project Management")
    print("="*70)

    # Register projects
    projects_config = {
        "p1": {
            "name": "Product Discovery",
            "type": "p1_product_discovery",
            "handler": "projects/p1_product_discovery/orchestrator.py",
            "dependencies": [],
            "priority": 1
        },
        "p2": {
            "name": "Media Automation",
            "type": "p2_media_automation",
            "handler": "projects/p2_media_automation/orchestrator.py",
            "dependencies": [],
            "priority": 2
        },
        "p3": {
            "name": "Kids Content",
            "type": "p3_kids_content",
            "handler": "projects/p3_kids_content/orchestrator.py",
            "dependencies": [],
            "priority": 3
        },
        "p4": {
            "name": "Music Generation",
            "type": "p4_music_generation",
            "handler": "projects/p4_music_generation/orchestrator.py",
            "dependencies": [],
            "priority": 4
        },
    }

    print("\n[REGISTRATION]")
    for pid, config in projects_config.items():
        coordinator.register_project(pid, config)

    print("\n[SCHEDULING]")
    for pid in projects_config.keys():
        coordinator.schedule_project(pid, priority=5)

    print("\n[EXECUTION QUEUE]")
    queue = coordinator.get_execution_queue()
    for item in queue:
        print(f"  - {item['project_id']} (priority: {item['priority']})")

    print("\n[STATUS]")
    all_status = coordinator.get_all_projects_status()
    for status in all_status:
        print(f"  {status['name']}: {status['status']}")

    print("\n[STATISTICS]")
    stats = coordinator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
