from pathlib import Path
from experiments import run_all_experiments
from visualization import build_all_charts


def main():
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    summary_df, decisions_df = run_all_experiments()
    summary_path = results_dir / "summary_results.csv"
    decisions_path = results_dir / "flow_decisions.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    decisions_df.to_csv(decisions_path, index=False, encoding="utf-8-sig")
    build_all_charts(summary_df, decisions_df, results_dir)
    print("Моделювання SDN-контролера завершено.")
    print(f"Зведені результати: {summary_path}")
    print(f"Рішення за потоками: {decisions_path}")
    print("Графіки збережено у папці results.")
    best = summary_df[(summary_df["scenario"] == "link_failure") & (summary_df["algorithm"] == "sdn_resilient_policy")].iloc[0]
    print("Ключовий результат для link_failure:")
    print(f"sdn_resilient_policy: violations={best.policy_violations}; recovery={best.recovery_success_percent}%; index={best.efficiency_index}")


if __name__ == "__main__":
    main()
