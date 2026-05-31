from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
from topology import create_topology
from config import POLICIES

ALG_ORDER = ["static_acl", "sdn_shortest_path", "sdn_policy", "sdn_resilient_policy"]
ALG_LABELS = {
    "static_acl": "Static ACL",
    "sdn_shortest_path": "SDN shortest path",
    "sdn_policy": "SDN policy",
    "sdn_resilient_policy": "SDN resilient policy",
}
SCENARIO_LABELS = {
    "normal_access": "Normal",
    "unauthorized_attempts": "Unauthorized",
    "link_failure": "Link failure",
    "role_change": "Role change",
    "high_request_load": "High load",
}
PALETTE = {
    "static_acl": "#6C757D",
    "sdn_shortest_path": "#D95F02",
    "sdn_policy": "#1B9E77",
    "sdn_resilient_policy": "#4B3F72",
    "allow": "#2A9D8F",
    "deny": "#E76F51",
    "controller": "#2D3142",
    "core": "#4F5D75",
    "aggregation": "#577590",
    "access": "#43AA8B",
    "service": "#F9C74F",
    "subscriber": "#F9844A",
}


def _style_axes(ax):
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")
    ax.tick_params(axis="both", labelsize=9)


def _save_grouped_bar(df, metric, title, ylabel, out_path):
    pivot = df.pivot(index="scenario", columns="algorithm", values=metric).reindex(columns=ALG_ORDER)
    pivot.index = [SCENARIO_LABELS.get(x, x) for x in pivot.index]
    colors = [PALETTE[a] for a in ALG_ORDER]
    ax = pivot.plot(kind="bar", figsize=(12, 6.2), rot=22, color=colors, width=0.76, edgecolor="#FFFFFF", linewidth=0.7)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Сценарій", fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    _style_axes(ax)
    legend = ax.legend([ALG_LABELS[a] for a in ALG_ORDER], title="Алгоритм", frameon=True, loc="best")
    legend.get_frame().set_edgecolor("#CCCCCC")
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_topology_chart(out_path):
    g = create_topology()
    pos = {
        "controller": (3.0, 5.4),
        "s1": (1.8, 4.2), "s2": (4.2, 4.2),
        "s3": (1.3, 3.0), "s4": (4.7, 3.0),
        "s5": (0.2, 1.7), "s6": (2.1, 1.7), "s7": (3.9, 1.7), "s9": (5.8, 1.7),
        "s8": (3.0, 3.6),
        "student": (0.2, 0.55), "teacher": (2.1, 0.55), "guest": (3.9, 0.55), "admin_user": (5.8, 0.55),
        "internet": (1.4, 5.95), "lms": (2.4, 6.25), "video": (3.4, 6.25), "file": (4.4, 5.95), "admin_panel": (5.25, 5.45), "database": (0.75, 5.45),
    }
    h = nx.Graph()
    h.add_nodes_from(g.nodes(data=True))
    h.add_edges_from(g.edges(data=True))
    # Logical controller and endpoints are drawn only to make the scheme readable.
    h.add_node("controller", label="SDN\nController", layer="controller")
    h.add_node("student", label="Student", layer="subscriber")
    h.add_node("teacher", label="Teacher", layer="subscriber")
    h.add_node("guest", label="Guest", layer="subscriber")
    h.add_node("admin_user", label="Admin", layer="subscriber")
    h.add_node("internet", label="Internet", layer="service")
    h.add_node("lms", label="LMS", layer="service")
    h.add_node("video", label="Video", layer="service")
    h.add_node("file", label="File", layer="service")
    h.add_node("admin_panel", label="Admin\nPanel", layer="service")
    h.add_node("database", label="Database", layer="service")
    dashed_edges = [("controller", n) for n in ["s1", "s2", "s3", "s4", "s8"]]
    endpoint_edges = [("student", "s5"), ("teacher", "s6"), ("guest", "s7"), ("admin_user", "s9"),
                      ("internet", "s8"), ("lms", "s8"), ("video", "s8"), ("file", "s8"), ("admin_panel", "s8"), ("database", "s8")]
    h.add_edges_from(dashed_edges + endpoint_edges)
    labels = nx.get_node_attributes(h, "label")
    fig, ax = plt.subplots(figsize=(12.8, 8.0))
    physical_edges = [e for e in h.edges() if e not in dashed_edges and (e[1], e[0]) not in dashed_edges and e not in endpoint_edges and (e[1], e[0]) not in endpoint_edges]
    nx.draw_networkx_edges(h, pos, edgelist=physical_edges, width=2.3, edge_color="#596275", ax=ax)
    nx.draw_networkx_edges(h, pos, edgelist=dashed_edges, width=1.2, edge_color="#888888", style="dashed", alpha=0.8, ax=ax)
    nx.draw_networkx_edges(h, pos, edgelist=endpoint_edges, width=1.4, edge_color="#B7B7B7", alpha=0.8, ax=ax)
    layers = {
        "controller": ["controller"],
        "core": ["s1", "s2", "s8"],
        "aggregation": ["s3", "s4"],
        "access": ["s5", "s6", "s7", "s9"],
        "service": ["internet", "lms", "video", "file", "admin_panel", "database"],
        "subscriber": ["student", "teacher", "guest", "admin_user"],
    }
    sizes = {"controller": 2600, "core": 2100, "aggregation": 1900, "access": 1800, "service": 1250, "subscriber": 1250}
    for layer, nodes in layers.items():
        nx.draw_networkx_nodes(h, pos, nodelist=nodes, node_color=PALETTE[layer], edgecolors="#FFFFFF", linewidths=1.8, node_size=sizes[layer], ax=ax)
    nx.draw_networkx_labels(h, pos, labels=labels, font_size=9, font_weight="bold", font_color="#111111", ax=ax)
    ax.set_title("Логічна схема SDN-мережі з контролером, абонентами та сервісами", fontsize=15, fontweight="bold", pad=18)
    ax.text(3.0, -0.1, "Суцільні лінії - фізичні канали; пунктир - логічний канал керування контролера", ha="center", fontsize=9, color="#555555")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_access_by_role(decisions_df, out_path):
    data = decisions_df[decisions_df["algorithm"] == "sdn_resilient_policy"].copy()
    table = data.groupby(["role", "controller_decision"]).size().unstack(fill_value=0)
    table = table.reindex(["student", "teacher", "guest", "admin", "blocked"]).fillna(0)
    cols = [c for c in ["allow", "deny"] if c in table.columns]
    ax = table[cols].plot(kind="bar", figsize=(10.8, 5.6), rot=0, color=[PALETTE.get(c, "#999999") for c in cols], edgecolor="#FFFFFF", linewidth=0.8)
    ax.set_title("Рішення SDN-контролера за ролями абонентів", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Роль абонента", fontsize=11)
    ax.set_ylabel("Кількість потоків", fontsize=11)
    _style_axes(ax)
    ax.legend(title="Рішення", labels=["Дозволено" if c == "allow" else "Заборонено" for c in cols])
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_policy_matrix(out_path):
    roles = ["student", "teacher", "guest", "admin", "blocked"]
    services = ["internet", "lms", "video", "file", "admin", "database"]
    data = np.array([[1 if service in POLICIES.get(role, set()) else 0 for service in services] for role in roles])
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.imshow(data, cmap=plt.matplotlib.colors.ListedColormap(["#F4A261", "#2A9D8F"]), aspect="auto")
    ax.set_xticks(range(len(services)), labels=["Internet", "LMS", "Video", "File", "Admin", "DB"], rotation=0)
    ax.set_yticks(range(len(roles)), labels=roles)
    for i in range(len(roles)):
        for j in range(len(services)):
            ax.text(j, i, "allow" if data[i, j] else "deny", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    ax.set_title("Матриця рольових політик доступу", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Тип сервісу")
    ax.set_ylabel("Роль абонента")
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_service_decisions(decisions_df, out_path):
    data = decisions_df[decisions_df["algorithm"] == "sdn_resilient_policy"].copy()
    table = data.groupby(["service_type", "controller_decision"]).size().unstack(fill_value=0)
    table = table.reindex(["internet", "lms", "video", "file", "admin", "database"]).fillna(0)
    cols = [c for c in ["allow", "deny"] if c in table.columns]
    ax = table[cols].plot(kind="barh", figsize=(10, 5.5), color=[PALETTE.get(c, "#999999") for c in cols], edgecolor="#FFFFFF", linewidth=0.8)
    ax.set_title("Доступ до сервісів за рішеннями контролера", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Кількість потоків", fontsize=11)
    ax.set_ylabel("Тип сервісу", fontsize=11)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.6, alpha=0.75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(title="Рішення", labels=["Дозволено" if c == "allow" else "Заборонено" for c in cols])
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_compliance_heatmap(summary_df, out_path):
    pivot = summary_df.pivot(index="scenario", columns="algorithm", values="compliance_percent").reindex(columns=ALG_ORDER)
    pivot.index = [SCENARIO_LABELS.get(x, x) for x in pivot.index]
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    im = ax.imshow(pivot.values, cmap="YlGn", vmin=50, vmax=100, aspect="auto")
    ax.set_xticks(range(len(ALG_ORDER)), labels=[ALG_LABELS[a] for a in ALG_ORDER], rotation=25, ha="right")
    ax.set_yticks(range(len(pivot.index)), labels=pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i,j]:.1f}%", ha="center", va="center", color="#111111", fontsize=9, fontweight="bold")
    ax.set_title("Відповідність політикам доступу за сценаріями", fontsize=14, fontweight="bold", pad=12)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Відповідність, %")
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=260, bbox_inches="tight")
    plt.close()


def build_all_charts(summary_df, decisions_df, results_dir: Path):
    results_dir.mkdir(parents=True, exist_ok=True)
    build_topology_chart(results_dir / "sdn_topology.png")
    build_policy_matrix(results_dir / "policy_matrix.png")
    build_access_by_role(decisions_df, results_dir / "access_decisions_by_role.png")
    build_service_decisions(decisions_df, results_dir / "service_access_decisions.png")
    build_compliance_heatmap(summary_df, results_dir / "compliance_heatmap.png")
    _save_grouped_bar(summary_df, "policy_violations", "Кількість порушень політик доступу", "Кількість порушень", results_dir / "policy_violations_comparison.png")
    _save_grouped_bar(summary_df, "recovery_success_percent", "Успішність відновлення маршрутів після відмов", "Успішність, %", results_dir / "recovery_success_comparison.png")
    _save_grouped_bar(summary_df, "avg_path_length", "Середня довжина маршруту", "Кількість переходів", results_dir / "avg_path_length_comparison.png")
    _save_grouped_bar(summary_df, "generated_rules", "Кількість згенерованих OpenFlow-подібних правил", "Кількість правил", results_dir / "flow_rules_count.png")
    _save_grouped_bar(summary_df, "efficiency_index", "Інтегральний індекс ефективності алгоритмів", "Індекс", results_dir / "efficiency_index.png")
