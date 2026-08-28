"""Typed evaluation for small completion-claim policies."""

from __future__ import annotations

import json
import queue
import threading
from contextvars import copy_context
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Iterable


DEFAULT_BLOCK_MESSAGE = "This work is not yet complete. Required decision evidence is missing."


class FinalizationAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


@dataclass(frozen=True)
class FinalizationContext:
    session_id: str
    task_id: str | None
    turn_id: str | None
    platform: str
    model: str
    project_root: str
    user_message: Any
    response_text: str
    metadata: Any = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def for_response(
        cls,
        *,
        session_id: str,
        task_id: str | None,
        turn_id: str | None,
        platform: str,
        model: str,
        project_root: str,
        user_message: Any,
        response_text: str,
        metadata: dict[str, Any] | None = None,
    ) -> "FinalizationContext":
        return cls(
            session_id=session_id,
            task_id=task_id,
            turn_id=turn_id,
            platform=platform,
            model=model,
            project_root=project_root,
            user_message=user_message,
            response_text=response_text,
            metadata=MappingProxyType(dict(metadata or {})),
        )


@dataclass(frozen=True)
class FinalizationDecision:
    action: FinalizationAction
    policy_id: str
    reason_code: str
    user_message: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RegisteredFinalizationPolicy:
    id: str
    callback: Callable[[FinalizationContext], FinalizationDecision]
    required: bool = True
    timeout_seconds: float = 30.0
    owner: str = "core"
    turn_predicate: Callable[[str, Any], bool] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("finalization policy id must be a non-empty string")
        if not callable(self.callback):
            raise TypeError("finalization policy callback must be callable")
        if isinstance(self.timeout_seconds, bool) or self.timeout_seconds <= 0:
            raise ValueError("finalization policy timeout_seconds must be positive")
        if self.turn_predicate is not None and not callable(self.turn_predicate):
            raise TypeError("finalization policy turn_predicate must be callable")


def _timed_call(name: str, timeout: float, callback: Callable[[], Any]) -> tuple[str, Any]:
    result_queue: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)
    caller_context = copy_context()

    def run() -> None:
        try:
            result_queue.put_nowait(("ok", callback()))
        except BaseException as exc:
            try:
                result_queue.put_nowait(("error", exc))
            except queue.Full:
                pass

    threading.Thread(
        target=lambda: caller_context.run(run), name=name, daemon=True
    ).start()
    try:
        return result_queue.get(timeout=float(timeout))
    except queue.Empty:
        return "timeout", None


def policy_buffers_turn(
    policy: RegisteredFinalizationPolicy,
    project_root: str,
    user_message: Any,
    *,
    timeout_seconds: float = 2.0,
) -> tuple[bool, str | None]:
    if policy.turn_predicate is None:
        return True, None
    status, value = _timed_call(
        f"finalization-scope-{policy.id}",
        timeout_seconds,
        lambda: policy.turn_predicate(project_root, user_message),
    )
    if status != "ok" or type(value) is not bool:
        return policy.required, f"turn_predicate_{status if status != 'ok' else 'error'}"
    return value, None


@dataclass(frozen=True)
class FinalizationEvaluation:
    action: FinalizationAction
    reason_code: str
    user_message: str
    decisions: tuple[FinalizationDecision, ...]


def _synthetic(policy: RegisteredFinalizationPolicy, reason: str) -> FinalizationDecision:
    prefix = "required" if policy.required else "optional"
    return FinalizationDecision(
        FinalizationAction.BLOCK if policy.required else FinalizationAction.ALLOW,
        policy.id,
        f"{prefix}_policy_{reason}",
        DEFAULT_BLOCK_MESSAGE if policy.required else "",
    )


def _validated(
    policy: RegisteredFinalizationPolicy, value: Any, max_evidence_bytes: int
) -> FinalizationDecision | None:
    if not isinstance(value, FinalizationDecision):
        return None
    if value.policy_id != policy.id or not isinstance(value.action, FinalizationAction):
        return None
    if not value.reason_code or not isinstance(value.user_message, str):
        return None
    try:
        encoded = json.dumps(
            value.evidence, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        return None
    return value if len(encoded) <= max_evidence_bytes else None


def evaluate_finalization_policies(
    context: FinalizationContext,
    policies: Iterable[RegisteredFinalizationPolicy],
    *,
    max_evidence_bytes: int = 65_536,
) -> FinalizationEvaluation:
    if isinstance(max_evidence_bytes, bool) or max_evidence_bytes <= 0:
        raise ValueError("max_evidence_bytes must be positive")
    decisions = []
    denial = None
    for policy in policies:
        status, value = _timed_call(
            f"finalization-policy-{policy.id}",
            policy.timeout_seconds,
            lambda policy=policy: policy.callback(context),
        )
        decision = (
            _validated(policy, value, max_evidence_bytes)
            if status == "ok"
            else None
        )
        if decision is None:
            decision = _synthetic(policy, status if status != "ok" else "malformed")
        decisions.append(decision)
        if policy.required and decision.action is FinalizationAction.BLOCK and denial is None:
            denial = decision
    if denial:
        return FinalizationEvaluation(
            FinalizationAction.BLOCK,
            denial.reason_code,
            denial.user_message or DEFAULT_BLOCK_MESSAGE,
            tuple(decisions),
        )
    return FinalizationEvaluation(
        FinalizationAction.ALLOW,
        "all_required_policies_allowed",
        "",
        tuple(decisions),
    )
