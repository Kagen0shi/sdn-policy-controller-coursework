import networkx as nx
from models import Subscriber, Service


def create_topology() -> nx.Graph:
    """Create an SDN-like campus topology: access, aggregation, core and service layer."""
    g = nx.Graph()
    switches = {
        "s1": "Core Switch 1",
        "s2": "Core Switch 2",
        "s3": "Aggregation A",
        "s4": "Aggregation B",
        "s5": "Access Students",
        "s6": "Access Teachers",
        "s7": "Guest Access",
        "s8": "Data Center Switch",
        "s9": "Admin Access",
    }
    for node, label in switches.items():
        g.add_node(node, node_type="switch", label=label)

    # Edges contain cost and bandwidth-like weights. The routing algorithm uses cost.
    edges = [
        ("s1", "s2", 1), ("s1", "s3", 1), ("s2", "s4", 1),
        ("s3", "s4", 2), ("s3", "s5", 1), ("s3", "s6", 1),
        ("s4", "s7", 1), ("s4", "s9", 1), ("s1", "s8", 1),
        ("s2", "s8", 1), ("s5", "s7", 3), ("s6", "s9", 2),
        ("s2", "s5", 2), ("s3", "s6", 2), ("s1", "s4", 3),
    ]
    for u, v, cost in edges:
        g.add_edge(u, v, cost=cost)
    return g


def create_subscribers():
    return [
        Subscriber("u01", "student_01", "student", "s5"),
        Subscriber("u02", "student_02", "student", "s5"),
        Subscriber("u03", "student_03", "student", "s7"),
        Subscriber("u04", "teacher_01", "teacher", "s6"),
        Subscriber("u05", "teacher_02", "teacher", "s6"),
        Subscriber("u06", "guest_01", "guest", "s7"),
        Subscriber("u07", "guest_02", "guest", "s7"),
        Subscriber("u08", "admin_01", "admin", "s9"),
        Subscriber("u09", "admin_02", "admin", "s9"),
        Subscriber("u10", "blocked_01", "blocked", "s5"),
        Subscriber("u11", "blocked_02", "blocked", "s7"),
    ]


def create_services():
    return [
        Service("srv_internet", "Internet Gateway", "internet", "s1", 2),
        Service("srv_lms", "LMS Server", "lms", "s8", 4),
        Service("srv_video", "Video Conference Service", "video", "s8", 5),
        Service("srv_file", "Faculty File Server", "file", "s8", 3),
        Service("srv_admin", "Administrative Panel", "admin", "s9", 5),
        Service("srv_db", "Internal Database", "database", "s8", 5),
    ]
