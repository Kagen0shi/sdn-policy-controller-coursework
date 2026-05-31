import random
from typing import List
from config import RANDOM_SEED, SCENARIOS, SERVICE_PRIORITY
from models import FlowRequest
from topology import create_subscribers, create_services


class TrafficGenerator:
    def __init__(self, seed=RANDOM_SEED):
        self.random = random.Random(seed)
        self.subscribers = create_subscribers()
        self.services = create_services()
        self.services_by_type = {s.service_type: s for s in self.services}

    def generate(self, scenario_name: str) -> List[FlowRequest]:
        scenario = SCENARIOS[scenario_name]
        flows = []
        for idx in range(1, scenario["flows"] + 1):
            subscriber = self.random.choice(self.subscribers)
            role = subscriber.role
            role_changed = False

            if scenario.get("role_change") and idx % 9 == 0:
                role_changed = True
                if role == "guest":
                    role = "student"
                elif role == "student":
                    role = "blocked"
                elif role == "teacher":
                    role = "admin"

            service = self._choose_service(role, scenario["unauthorized_ratio"])
            size_mb = round(self.random.uniform(0.2, 25.0) * (1 + service.criticality / 10), 2)
            flows.append(
                FlowRequest(
                    id=f"{scenario_name}_f{idx:03d}",
                    scenario=scenario_name,
                    subscriber_id=subscriber.id,
                    subscriber_role=role,
                    source_switch=subscriber.access_switch,
                    service_id=service.id,
                    service_type=service.service_type,
                    destination_switch=service.host_switch,
                    size_mb=size_mb,
                    priority=SERVICE_PRIORITY[service.service_type],
                    role_changed=role_changed,
                )
            )
        return flows

    def _choose_service(self, role, unauthorized_ratio):
        allowed_map = {
            "student": ["internet", "lms", "video"],
            "teacher": ["internet", "lms", "video", "file"],
            "guest": ["internet"],
            "admin": ["internet", "lms", "video", "file", "admin", "database"],
            "blocked": [],
        }
        all_types = [s.service_type for s in self.services]
        allowed = allowed_map.get(role, [])
        denied = [t for t in all_types if t not in allowed]
        if denied and self.random.random() < unauthorized_ratio:
            chosen_type = self.random.choice(denied)
        elif allowed:
            chosen_type = self.random.choice(allowed)
        else:
            chosen_type = self.random.choice(all_types)
        return self.services_by_type[chosen_type]
