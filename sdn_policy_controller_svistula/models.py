from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Subscriber:
    id: str
    name: str
    role: str
    access_switch: str


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    service_type: str
    host_switch: str
    criticality: int


@dataclass(frozen=True)
class FlowRequest:
    id: str
    scenario: str
    subscriber_id: str
    subscriber_role: str
    source_switch: str
    service_id: str
    service_type: str
    destination_switch: str
    size_mb: float
    priority: int
    role_changed: bool = False


@dataclass
class RouteDecision:
    scenario: str
    algorithm: str
    flow_id: str
    subscriber_id: str
    role: str
    service_id: str
    service_type: str
    allowed_by_policy: bool
    controller_decision: str
    policy_violation: bool
    path: List[str]
    path_length: int
    rerouted: bool
    unreachable: bool
    generated_rules: int
    explanation: str
