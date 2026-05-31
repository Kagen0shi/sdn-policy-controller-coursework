RANDOM_SEED = 42

ROLES = ["student", "teacher", "guest", "admin", "blocked"]

POLICIES = {
    "student": {"internet", "lms", "video"},
    "teacher": {"internet", "lms", "video", "file"},
    "guest": {"internet"},
    "admin": {"internet", "lms", "video", "file", "admin", "database"},
    "blocked": set(),
}

SERVICE_PRIORITY = {
    "internet": 2,
    "lms": 4,
    "video": 5,
    "file": 3,
    "admin": 5,
    "database": 5,
}

SCENARIOS = {
    "normal_access": {
        "flows": 90,
        "description": "звичайний день роботи мережі з типовими зверненнями абонентів",
        "unauthorized_ratio": 0.10,
        "failure_edges": [],
        "role_change": False,
    },
    "unauthorized_attempts": {
        "flows": 90,
        "description": "підвищена кількість спроб доступу до службових сервісів",
        "unauthorized_ratio": 0.42,
        "failure_edges": [],
        "role_change": False,
    },
    "link_failure": {
        "flows": 90,
        "description": "відмова частини каналів між комутаторами та потреба перебудови маршрутів",
        "unauthorized_ratio": 0.12,
        "failure_edges": [("s2", "s5"), ("s3", "s6")],
        "role_change": False,
    },
    "role_change": {
        "flows": 90,
        "description": "динамічна зміна ролей частини абонентів і оновлення політик доступу",
        "unauthorized_ratio": 0.22,
        "failure_edges": [],
        "role_change": True,
    },
    "high_request_load": {
        "flows": 150,
        "description": "велика кількість одночасних запитів до різних сервісів",
        "unauthorized_ratio": 0.20,
        "failure_edges": [("s1", "s4")],
        "role_change": False,
    },
}

ALGORITHMS = [
    "static_acl",
    "sdn_shortest_path",
    "sdn_policy",
    "sdn_resilient_policy",
]
