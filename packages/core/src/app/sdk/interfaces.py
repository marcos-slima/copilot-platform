"""Configuração das interfaces de agentes publicada por um produto."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.mcp.policy import ToolPolicy

if TYPE_CHECKING:
    from app.models import DiagnosisResponse, IncidentRequest


@dataclass(frozen=True)
class MCPTool:
    name: str
    handler: Callable[..., Any]
    policy: ToolPolicy


@dataclass(frozen=True)
class MCPConfig:
    name: str
    version: str
    tools: tuple[MCPTool, ...]
    granted_scopes: frozenset[str]
    instructions: str | None = None


@dataclass(frozen=True)
class A2AConfig:
    card: Mapping[str, Any]
    diagnose: Callable[[IncidentRequest], DiagnosisResponse]
    task_namespace: str | None

    def __post_init__(self) -> None:
        if self.task_namespace is not None and (
            not self.task_namespace or ":" in self.task_namespace
        ):
            raise ValueError("task_namespace deve ser não vazio e sem ':'")


@dataclass(frozen=True)
class AgentInterfaces:
    mcp: MCPConfig | None = None
    a2a: A2AConfig | None = None
