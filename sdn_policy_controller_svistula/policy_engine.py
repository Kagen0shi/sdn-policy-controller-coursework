from config import POLICIES


class PolicyEngine:
    """Role-based access control for SDN flow requests."""

    def __init__(self, policies=None):
        self.policies = policies or POLICIES

    def is_allowed(self, role: str, service_type: str) -> bool:
        return service_type in self.policies.get(role, set())

    def explain(self, role: str, service_type: str) -> str:
        if self.is_allowed(role, service_type):
            return f"доступ дозволено політикою RBAC: роль {role} -> сервіс {service_type}"
        return f"доступ заборонено політикою RBAC: роль {role} -> сервіс {service_type}"
