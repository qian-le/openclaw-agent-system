"""
Coordinator Agent — Task Orchestration

WIP: This module is part of the OpenClaw Agent System project.
Coordinator manages the full agent pipeline, routing tasks through
Scout -> Analyst -> Guard -> Executor, and aggregating results.
"""

from typing import Any

from .scout import Scout
from .analyst import Analyst
from .guard import Guard
from .executor import Executor


class TaskType:
    """Task type constants."""
    INFO = "Info"
    ANALYSIS = "Analysis"
    EXECUTION = "Execution"
    RISKY_EXECUTION = "Risky Execution"


class Coordinator:
    """
    Coordinator — orchestrates the multi-agent pipeline.

    Responsibilities:
    - Classify incoming tasks
    - Route through the appropriate agent chain
    - Aggregate results from all agents
    - Handle error recovery
    """

    def __init__(self, workspace_path: str | None = None):
        """
        Initialize Coordinator with all sub-agents.

        Args:
            workspace_path: Workspace root path.
        """
        self.scout = Scout(workspace_path=workspace_path)
        self.analyst = Analyst()
        self.guard = Guard()
        self.executor = Executor(workspace_path=workspace_path)
        self.pipeline_log: list[dict[str, Any]] = []

    def classify(self, task: str) -> str:
        """
        Classify a task into one of four types.

        Args:
            task: Natural language task description.

        Returns:
            Task type: Info, Analysis, Execution, or RiskyExecution.
        """
        task_lower = task.lower()
        if any(kw in task_lower for kw in ["delete", "rm -rf", "drop", "truncate"]):
            return TaskType.RISKY_EXECUTION
        if any(kw in task_lower for kw in ["create", "write", "run", "execute", "modify"]):
            return TaskType.EXECUTION
        if any(kw in task_lower for kw in ["analyze", "compare", "assess", "evaluate", "recommend"]):
            return TaskType.ANALYSIS
        return TaskType.INFO

    async def dispatch(self, task: str) -> dict[str, Any]:
        """
        Dispatch a task through the appropriate agent pipeline.

        Args:
            task: The task description.

        Returns:
            Aggregated result from all agents in the pipeline.
        """
        task_type = self.classify(task)
        result = {
            "task": task,
            "type": task_type,
            "status": "dispatched",
            "steps": [],
        }
        self.pipeline_log.append(result)

        if task_type in (TaskType.INFO, TaskType.ANALYSIS, TaskType.RISKY_EXECUTION):
            findings = await self.scout.investigate(task)
            result["steps"].append({"agent": "scout", "result": findings})

        if task_type in (TaskType.ANALYSIS, TaskType.RISKY_EXECUTION):
            analysis = await self.analyst.analyze(task, result["steps"][-1]["result"].get("findings", []))
            result["steps"].append({"agent": "analyst", "result": analysis})

        if task_type in (TaskType.EXECUTION, TaskType.RISKY_EXECUTION):
            guard_result = await self.guard.review(task)
            result["steps"].append({"agent": "guard", "result": guard_result})

            if guard_result["status"] == Guard.DENIED:
                result["status"] = "denied"
                return result

            if guard_result["status"] == Guard.NEEDS_CONFIRMATION:
                result["status"] = "awaiting_confirmation"
                return result

            exec_result = await self.executor.execute(task)
            result["steps"].append({"agent": "executor", "result": exec_result})

        result["status"] = "complete"
        return result

    def summary(self) -> dict[str, Any]:
        """
        Return a summary of all dispatches.

        Returns:
            Summary of pipeline activity.
        """
        return {
            "total_tasks": len(self.pipeline_log),
            "logs": self.pipeline_log,
        }
