from config import SCENARIOS, ALGORITHMS
from topology import create_topology
from traffic_generator import TrafficGenerator
from controller import SDNController
from metrics import decisions_to_dataframe, summarize_decisions


def run_all_experiments():
    graph = create_topology()
    controller = SDNController(graph)
    generator = TrafficGenerator()
    decisions = []

    for scenario_name, scenario_cfg in SCENARIOS.items():
        flows = generator.generate(scenario_name)
        failed_edges = scenario_cfg.get("failure_edges", [])
        for algorithm in ALGORITHMS:
            for flow in flows:
                decisions.append(controller.decide(flow, algorithm, failed_edges=failed_edges))

    decisions_df = decisions_to_dataframe(decisions)
    summary_df = summarize_decisions(decisions_df)
    return summary_df, decisions_df
