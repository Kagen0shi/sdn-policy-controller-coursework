from dataclasses import asdict
import pandas as pd


def decisions_to_dataframe(decisions):
    rows = []
    for d in decisions:
        row = asdict(d)
        row["path"] = " -> ".join(d.path)
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_decisions(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scenario, algorithm), part in df.groupby(["scenario", "algorithm"], sort=False):
        total = len(part)
        allowed = int((part["controller_decision"] == "allow").sum())
        denied = int((part["controller_decision"] == "deny").sum())
        unreachable = int((part["controller_decision"] == "unreachable").sum())
        violations = int(part["policy_violation"].sum())
        rerouted = int(part["rerouted"].sum())
        avg_path = round(part.loc[part["controller_decision"] == "allow", "path_length"].mean() or 0, 2)
        rules = int(part["generated_rules"].sum())
        policy_denials = int(((part["allowed_by_policy"] == False) & (part["controller_decision"] == "deny")).sum())
        compliance = round(100 * (1 - violations / total), 2)
        availability = round(100 * allowed / max(allowed + unreachable, 1), 2)
        recovery_success = round(100 * rerouted / max(rerouted + unreachable, 1), 2) if (rerouted + unreachable) else 100.0
        # Integrated score rewards policy compliance and availability, penalizes path length and excessive rules.
        score = 0.42 * compliance + 0.26 * availability + 0.18 * recovery_success
        score += 0.08 * max(0, 100 - avg_path * 12)
        score += 0.06 * max(0, 100 - rules / max(total, 1) * 9)
        rows.append({
            "scenario": scenario,
            "algorithm": algorithm,
            "total_flows": total,
            "allowed_flows": allowed,
            "denied_flows": denied,
            "unreachable_flows": unreachable,
            "policy_denials": policy_denials,
            "policy_violations": violations,
            "rerouted_flows": rerouted,
            "avg_path_length": avg_path,
            "generated_rules": rules,
            "compliance_percent": compliance,
            "availability_percent": availability,
            "recovery_success_percent": recovery_success,
            "efficiency_index": round(score, 2),
        })
    return pd.DataFrame(rows)
