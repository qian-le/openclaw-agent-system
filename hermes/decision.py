"""
Hermes Decision Engine — Policy Evaluation & Reasoning

WIP: This module is part of the MiMo Token application project.

Hermes is designed to be the policy engine and reasoning core of the
multi-agent system. It evaluates decisions, applies rules, and
orchestrates reasoning paths for complex tasks.

Planned capabilities:
- Rule-based policy evaluation
- Multi-criteria decision analysis (MCDA)
- Reasoning chain orchestration
- Integration with MiMo long-context processing
- Explainable decision output
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any


class DecisionStatus(Enum):
    """Possible decision outcomes."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    UNCERTAIN = "uncertain"


class DecisionConfidence(Enum):
    """Confidence levels for decisions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class DecisionResult:
    """
    Result of a decision evaluation.

    Attributes:
        status: The decision outcome.
        confidence: How confident the system is in this decision.
        reasons: Human-readable reasons for the decision.
        evidence: Supporting evidence or context used.
        alternatives: Alternative options considered.
        policy_id: Which policy rule was applied (if any).
    """
    status: DecisionStatus = DecisionStatus.PENDING
    confidence: DecisionConfidence = DecisionConfidence.UNKNOWN
    reasons: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    alternatives: list[str] = field(default_factory=list)
    policy_id: str | None = None

    def is_approved(self) -> bool:
        """Return True if the decision was approved."""
        return self.status == DecisionStatus.APPROVED

    def is_rejected(self) -> bool:
        """Return True if the decision was rejected."""
        return self.status == DecisionStatus.REJECTED

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {
            "status": self.status.value,
            "confidence": self.confidence.value,
            "reasons": self.reasons,
            "evidence": self.evidence,
            "alternatives": self.alternatives,
            "policy_id": self.policy_id,
        }


class DecisionEngine:
    """
    Hermes Decision Engine — evaluates actions against policies and context.

    WIP: This is the core reasoning module for the multi-agent system.

    Responsibilities:
    - Evaluate incoming requests against defined policies
    - Provide explainable decisions with reasoning chains
    - Handle multi-criteria decision analysis
    - Support rule-based and learned policy evaluation
    - Integrate with MiMo for enhanced reasoning

    Usage:
        engine = DecisionEngine()
        result = engine.evaluate(
            action="delete_file",
            context={"path": "/tmp/test.txt", "size": 1024},
        )
        if result.is_approved():
            # proceed
    """

    def __init__(self):
        """
        Initialize the Decision Engine.
        """
        self.policies: dict[str, dict[str, Any]] = {}
        self.decision_history: list[DecisionResult] = []
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        """Load built-in default policies."""
        self.policies["safe_internal"] = {
            "description": "Allow safe internal read operations",
            "rules": [
                {"type": "operation_in", "value": ["read", "search", "list"]},
                {"type": "target_internal", "value": True},
            ],
            "default_decision": DecisionStatus.APPROVED,
        }
        self.policies["destructive"] = {
            "description": "Deny destructive operations by default",
            "rules": [
                {"type": "operation_in", "value": ["delete", "rm", "drop", "truncate"]},
            ],
            "default_decision": DecisionStatus.REJECTED,
            "requires_confirmation": True,
        }
        self.policies["external"] = {
            "description": "Require confirmation for external actions",
            "rules": [
                {"type": "operation_in", "value": ["send", "email", "post", "publish"]},
            ],
            "default_decision": DecisionStatus.DEFERRED,
            "requires_confirmation": True,
        }

    def add_policy(
        self,
        policy_id: str,
        rules: list[dict[str, Any]],
        default_decision: DecisionStatus,
        description: str = "",
    ) -> None:
        """
        Register a new policy.

        Args:
            policy_id: Unique identifier for the policy.
            rules: List of rule dictionaries.
            default_decision: Default decision if rules match.
            description: Human-readable description.
        """
        self.policies[policy_id] = {
            "description": description,
            "rules": rules,
            "default_decision": default_decision,
        }

    def evaluate(
        self,
        action: str,
        context: dict[str, Any] | None = None,
        policy_hint: str | None = None,
    ) -> DecisionResult:
        """
        Evaluate an action against registered policies.

        Args:
            action: The action description.
            context: Additional context for evaluation.
            policy_hint: Optional specific policy to use.

        Returns:
            DecisionResult with the outcome and reasoning.
        """
        context = context or {}
        action_lower = action.lower()

        result = DecisionResult(evidence={"action": action, "context": context})

        # Check specific policy if hinted
        if policy_hint and policy_hint in self.policies:
            policy = self.policies[policy_hint]
            return self._apply_policy(policy, action, context, result)

        # Evaluate all matching policies
        for policy_id, policy in self.policies.items():
            if self._matches_policy(policy, action_lower, context):
                return self._apply_policy(policy, action_lower, context, result, policy_id)

        # Default: defer if uncertain
        result.status = DecisionStatus.UNCERTAIN
        result.confidence = DecisionConfidence.UNKNOWN
        result.reasons.append("No matching policy found; defaulting to uncertain.")
        self.decision_history.append(result)
        return result

    def _matches_policy(
        self,
        policy: dict[str, Any],
        action: str,
        context: dict[str, Any],
    ) -> bool:
        """
        Check if an action matches a policy's rules.

        Args:
            policy: Policy dictionary.
            action: Lowercased action string.
            context: Evaluation context.

        Returns:
            True if the action matches the policy rules.
        """
        for rule in policy.get("rules", []):
            rule_type = rule.get("type", "")
            rule_value = rule.get("value")

            if rule_type == "operation_in":
                if not any(op in action for op in rule_value):
                    return False
            elif rule_type == "target_internal":
                if context.get("target_internal") != rule_value:
                    return False

        return True

    def _apply_policy(
        self,
        policy: dict[str, Any],
        action: str,
        context: dict[str, Any],
        result: DecisionResult,
        policy_id: str | None = None,
    ) -> DecisionResult:
        """
        Apply a matched policy and produce a decision.

        Args:
            policy: The policy to apply.
            action: The action being evaluated.
            context: Evaluation context.
            result: Result object to populate.
            policy_id: Policy identifier.

        Returns:
            Populated DecisionResult.
        """
        result.policy_id = policy_id
        result.status = policy.get("default_decision", DecisionStatus.UNCERTAIN)
        result.confidence = DecisionConfidence.HIGH
        result.reasons.append(f"Matched policy: {policy.get('description', policy_id)}")
        result.reasons.append(f"Action: {action}")
        self.decision_history.append(result)
        return result

    def history(self) -> list[dict[str, Any]]:
        """
        Return the decision history.

        Returns:
            List of serialized decision results.
        """
        return [d.to_dict() for d in self.decision_history]
