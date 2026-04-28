"""
Hermes — Decision & Policy Engine

WIP: This module is part of the OpenClaw Agent System project.
Hermes serves as the central decision-making module, providing
policy evaluation, routing logic, and reasoning orchestration.
"""

__version__ = "0.1.0"

from .decision import DecisionEngine, DecisionResult

__all__ = ["DecisionEngine", "DecisionResult"]
