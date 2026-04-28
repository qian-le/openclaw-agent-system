"""
Multi-Agent System — MiMo Project

WIP: Work-in-progress multi-agent orchestration framework.
This module provides Scout, Analyst, Guard, Executor, and Coordinator agents.
"""

__version__ = "0.1.0"

from .scout import Scout
from .analyst import Analyst
from .guard import Guard
from .executor import Executor
from .coordinator import Coordinator

__all__ = ["Scout", "Analyst", "Guard", "Executor", "Coordinator"]
