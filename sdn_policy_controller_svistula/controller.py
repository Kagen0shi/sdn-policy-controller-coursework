from models import RouteDecision, FlowRequest
from policy_engine import PolicyEngine
from routing_engine import RoutingEngine


class SDNController:
    """Controller that makes allow/deny decisions, builds routes and generates flow rules."""

    def __init__(self, graph):
        self.policy = PolicyEngine()
        self.routing = RoutingEngine(graph)
        self.static_acl = {
            # Static ACL imitates a manually maintained access table.
            # It intentionally does not react well to role changes and is too broad for students.
            "student": {"internet", "lms", "video", "file"},
            "teacher": {"internet", "lms", "video", "file"},
            "guest": {"internet", "lms"},
            "admin": {"internet", "lms", "video", "file", "admin", "database"},
            "blocked": {"internet"},
        }

    def decide(self, flow: FlowRequest, algorithm: str, failed_edges=None) -> RouteDecision:
        policy_allowed = self.policy.is_allowed(flow.subscriber_role, flow.service_type)
        failed_edges = failed_edges or []
        explanation = ""
        path = []
        unreachable = False
        rerouted = False

        if algorithm == "static_acl":
            controller_allowed = flow.service_type in self.static_acl.get(flow.subscriber_role, set())
            path, unreachable = self.routing.static_path(flow.source_switch, flow.destination_switch)
            # If a static path includes a failed edge, static routing cannot recover.
            if path and self._path_uses_failed_edge(path, failed_edges):
                unreachable = True
                path = []
            explanation = "статична таблиця ACL і наперед заданий маршрут"

        elif algorithm == "sdn_shortest_path":
            controller_allowed = True
            path, unreachable = self.routing.shortest_path(flow.source_switch, flow.destination_switch, failed_edges)
            if failed_edges and path:
                rerouted = True
            explanation = "SDN-контролер будує найкоротший маршрут, але не застосовує політики ролей"

        elif algorithm == "sdn_policy":
            controller_allowed = policy_allowed
            if controller_allowed:
                # Basic policy controller is topology-aware but does not use backup after failures.
                path, unreachable = self.routing.static_path(flow.source_switch, flow.destination_switch)
                if path and self._path_uses_failed_edge(path, failed_edges):
                    unreachable = True
                    path = []
                explanation = "перевірка політики доступу та встановлення маршруту без резервного обходу"
            else:
                explanation = self.policy.explain(flow.subscriber_role, flow.service_type)

        elif algorithm == "sdn_resilient_policy":
            controller_allowed = policy_allowed
            if controller_allowed:
                static_path, static_unreachable = self.routing.static_path(flow.source_switch, flow.destination_switch)
                path, unreachable = self.routing.shortest_path(flow.source_switch, flow.destination_switch, failed_edges)
                rerouted = bool(failed_edges and path and static_path != path)
                explanation = "перевірка політики доступу, динамічна побудова маршруту та обхід відмовлених каналів"
            else:
                explanation = self.policy.explain(flow.subscriber_role, flow.service_type)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        if not controller_allowed:
            path = []
            unreachable = False
            rerouted = False

        violation = controller_allowed and not policy_allowed
        rules_count = self.routing.rules_count_for_path(path) if controller_allowed and not unreachable else 0
        decision = "allow" if controller_allowed and not unreachable else ("unreachable" if controller_allowed and unreachable else "deny")

        return RouteDecision(
            scenario=flow.scenario,
            algorithm=algorithm,
            flow_id=flow.id,
            subscriber_id=flow.subscriber_id,
            role=flow.subscriber_role,
            service_id=flow.service_id,
            service_type=flow.service_type,
            allowed_by_policy=policy_allowed,
            controller_decision=decision,
            policy_violation=violation,
            path=path,
            path_length=max(len(path) - 1, 0),
            rerouted=rerouted,
            unreachable=unreachable,
            generated_rules=rules_count,
            explanation=explanation,
        )

    @staticmethod
    def _path_uses_failed_edge(path, failed_edges):
        normalized = {tuple(sorted(edge)) for edge in failed_edges}
        for u, v in zip(path[:-1], path[1:]):
            if tuple(sorted((u, v))) in normalized:
                return True
        return False
