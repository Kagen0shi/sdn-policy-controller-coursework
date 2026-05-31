import networkx as nx


class RoutingEngine:
    """Shortest-path routing with optional link failures and rerouting."""

    def __init__(self, graph: nx.Graph):
        self.original_graph = graph.copy()

    def graph_with_failures(self, failed_edges=None) -> nx.Graph:
        g = self.original_graph.copy()
        for edge in failed_edges or []:
            if g.has_edge(*edge):
                g.remove_edge(*edge)
        return g

    def shortest_path(self, source: str, target: str, failed_edges=None):
        g = self.graph_with_failures(failed_edges)
        try:
            path = nx.shortest_path(g, source=source, target=target, weight="cost")
            return path, False
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], True

    def static_path(self, source: str, target: str):
        # Static routing knows only the initial topology. It does not react to failed links.
        try:
            path = nx.shortest_path(self.original_graph, source=source, target=target, weight="cost")
            return path, False
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], True

    @staticmethod
    def rules_count_for_path(path):
        if not path:
            return 0
        return max(len(path) - 1, 0)
