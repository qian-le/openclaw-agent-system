"""
Guard Agent — Safety Gate & Risk Review

WIP: This module is part of the MiMo Token application project.
Guard acts as the mandatory safety gate before any execution,
reviewing requests for risk, safety, and authorization.
"""

from typing import Any


class Guard:
    """
    Guard agent — mandatory gate before execution.

    Responsibilities:
    - Review all execution requests before they proceed
    - Check for safety violations, destructive actions, data leaks
    - Require explicit user confirmation for risky operations
    - Deny unsafe requests outright
    """

    APPROVED = "approved"
    DENIED = "denied"
    NEEDS_CONFIRMATION = "needs_explicit_user_confirmation"

    def __init__(self):
        """
        Initialize Guard.
        """
        self.audit_log: list[dict[str, Any]] = []

    async def review(
        self,
        action: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Review an action for safety and risk.

        Args:
            action: The action description to review.
            context: Additional context about the action.

        Returns:
            Review result with status: approved / denied /
            needs_explicit_user_confirmation.
        """
        result = {
            "action": action,
            "status": self.APPROVED,
            "reasons": [],
            "warnings": [],
        }
        # WIP: Implement safety checks
        self.audit_log.append(result)
        return result

    async def check_destructive(
        self,
        action: str,
        targets: list[str] | None = None,
    ) -> bool:
        """
        Check if an action is destructive (delete, truncate, etc.).

        Args:
            action: Action description.
            targets: List of affected targets.

        Returns:
            True if destructive, False otherwise.
        """
        destructive_keywords = ["delete", "remove", "truncate", "drop", "rm -rf"]
        return any(kw in action.lower() for kw in destructive_keywords)

    async def check_external(
        self,
        action: str,
    ) -> bool:
        """
        Check if an action targets external systems (email, post, etc.).

        Args:
            action: Action description.

        Returns:
            True if external, False if internal.
        """
        external_keywords = ["email", "send", "post", "publish", "tweet", "webhook"]
        return any(kw in action.lower() for kw in external_keywords)

    async def require_confirmation(
        self,
        action: str,
        reason: str,
    ) -> dict[str, Any]:
        """
        Prepare a confirmation request for the user.

        Args:
            action: The action requiring confirmation.
            reason: Why confirmation is needed.

        Returns:
            Confirmation request details.
        """
        return {
            "action": action,
            "reason": reason,
            "status": self.NEEDS_CONFIRMATION,
            "user_prompt": f"Confirm: {action} — {reason}",
        }

    def audit(self) -> list[dict[str, Any]]:
        """
        Return the full audit log.

        Returns:
            List of all review records.
        """
        return self.audit_log
