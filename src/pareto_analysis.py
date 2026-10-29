"""
Pareto Frontier & Optimality Gap Analysis Engine.
Sweeps multi-objective weights w1 (Service Disruption) vs w2 (Breakdown Hazard Risk).
Compares:
  - Exact MILP Global Optimum (scipy.optimize.milp)
  - Real-Time Multi-Objective Heuristic Optimizer
Calculates the exact Optimality Gap percentage across the Pareto curve.
"""

import numpy as np
import pandas as pd
from data_generator import generate_mining_fleet
from optimizer_core import MultiObjectiveSlotOptimizer
from milp_optimizer import ExactMILPSlotOptimizer

def run_pareto_analysis(steps: int = 7):
    print("=" * 80)
    print("PARETO FRONTIER & MATHEMATICAL OPTIMALITY GAP BENCHMARK")
    print("=" * 80)
    
    data = generate_mining_fleet(num_vehicles=18, num_spares=3)
    fleet = data["fleet"]
    spares = data["spares"]
    workshop = data["workshop"]
    
    weights_w1 = np.linspace(0.1, 0.9, steps)
    pareto_records = []
    
    for w1 in weights_w1:
        w2 = 1.0 - w1
        
        # 1. Solve with Real-Time Heuristic Optimizer
        heur_solver = MultiObjectiveSlotOptimizer(w_cancellation=w1, w_breakdown_risk=w2)
        heur_res = heur_solver.optimize(fleet, spares, workshop, time_horizon_shifts=3)
        
        # 2. Solve with Exact MILP Solver
        milp_solver = ExactMILPSlotOptimizer(w_cancellation=w1, w_breakdown_risk=w2)
        milp_res = milp_solver.solve(fleet, spares, workshop, num_shifts=3)
        
        heur_cost = heur_res["total_combined_cost_usd"]
        milp_cost = milp_res["total_combined_cost_usd"]
        
        # Optimality Gap: (Heuristic - MILP) / MILP
        opt_gap_pct = max(0.0, ((heur_cost - milp_cost) / milp_cost) * 100.0) if milp_cost > 0 else 0.0
        
        pareto_records.append({
            "w1_cancellation": round(float(w1), 2),
            "w2_breakdown": round(float(w2), 2),
            "heur_canc_cost": heur_res["total_cancellation_cost_usd"],
            "heur_risk_cost": heur_res["total_breakdown_risk_cost_usd"],
            "heur_combined_cost": heur_cost,
            "milp_canc_cost": milp_res["total_cancellation_cost_usd"],
            "milp_risk_cost": milp_res["total_breakdown_risk_cost_usd"],
            "milp_combined_cost": milp_cost,
            "optimality_gap_pct": round(opt_gap_pct, 2)
        })
        
    df = pd.DataFrame(pareto_records)
    print("\nPARETO FRONTIER SWEEP RESULTS:")
    print(df[["w1_cancellation", "w2_breakdown", "heur_combined_cost", "milp_combined_cost", "optimality_gap_pct"]].to_string(index=False))
    
    avg_gap = df["optimality_gap_pct"].mean()
    print(f"\n[+] Mean Mathematical Optimality Gap of Heuristic vs Global MILP: {avg_gap:.2f}%")
    
    df.to_json("d:/project/pareto_frontier_results.json", orient="records", indent=2)
    print("[+] Saved Pareto curve data to d:/project/pareto_frontier_results.json")
    return df

if __name__ == "__main__":
    run_pareto_analysis()
