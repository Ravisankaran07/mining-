"""
7-Day (21 Shifts) Continuous Rolling-Horizon Mining Operation Simulator.
Directly benchmarks:
  Policy A: Baseline Urgency FIFO (Current Mining Practice)
  Policy B: Proposed Multi-Objective Maintenance-Slot Optimizer with Spare Vehicle Capacity
Tracks across identical stochastic pit events:
  - Tonnage fulfillment rate
  - Actual route cancellations
  - Unscheduled catastrophic in-pit breakdowns
  - Preserved operational margin revenue ($)
  - Cryptographic audit trail of all supervisor overrides
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from data_generator import generate_mining_fleet
from optimizer_core import TelemetryResilientPreprocessor, BaselineUrgencyScheduler, MultiObjectiveSlotOptimizer
from audit_logger import DispatcherAuditLogger

class ComparativeMiningSimulator:
    def __init__(self, num_vehicles: int = 24, num_spares: int = 4, total_shifts: int = 21, seed: int = 42):
        self.num_vehicles = num_vehicles
        self.num_spares = num_spares
        self.total_shifts = total_shifts
        self.seed = seed

    def run_policy(self, policy_type: str = "PROPOSED_OPTIMIZER") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        raw = generate_mining_fleet(num_vehicles=self.num_vehicles, num_spares=self.num_spares)
        fleet = [dict(v) for v in raw["fleet"]]
        spares = [dict(s) for s in raw["spares"]]
        workshop = dict(raw["workshop"])
        
        baseline_solver = BaselineUrgencyScheduler()
        opt_solver = MultiObjectiveSlotOptimizer(w_cancellation=0.5, w_breakdown_risk=0.5)
        audit_logger = DispatcherAuditLogger(log_filepath=f"d:/project/sim_audit_{policy_type.lower()}.jsonl")
        
        total_target_tons = 0.0
        total_delivered_tons = 0.0
        total_cancellations = 0
        total_breakdowns = 0
        total_overhauls = 0
        history = []
        
        for shift in range(1, self.total_shifts + 1):
            shift_target = sum(v["shift_demand_tons"] for v in fleet)
            shift_delivered = shift_target
            
            # Weather & dust storm simulation
            is_dust_storm = shift in [4, 5, 12, 18]
            temp_wave = 43.0 + 5.0 * np.sin(shift * np.pi / 3)
            
            # Wear and telemetry simulation
            for v in fleet:
                v["operating_hours"] += 8
                v["hours_since_service"] += 8
                v["ambient_temp_c"] = round(temp_wave + np.random.uniform(-1, 2), 1)
                
                if is_dust_storm:
                    v["dust_pm10"] = round(np.random.uniform(650.0, 900.0), 1)
                    r = random.random()
                    v["telemetry_status"] = "GPS_LOST" if r < 0.25 else ("SENSOR_DROPOUT" if r < 0.40 else "HEALTHY")
                else:
                    v["dust_pm10"] = round(np.random.uniform(200.0, 420.0), 1)
                    v["telemetry_status"] = "GPS_LOST" if random.random() < 0.08 else "HEALTHY"
                    
                # Dynamic urgency
                harshness = (v["ambient_temp_c"] / 40.0) * (v["dust_pm10"] / 300.0) * (v["vibration_index"] / 1.5)
                v["urgency_score"] = min(100.0, (v["hours_since_service"] / 300.0) * 50.0 * harshness)

            # Check catastrophic breakdown hazard if deferred beyond safe limit (>88 urgency)
            for v in fleet:
                if v["urgency_score"] > 88.0:
                    hazard_prob = 0.12 if not is_dust_storm else 0.25
                    if random.random() < hazard_prob:
                        total_breakdowns += 1
                        shift_delivered -= v["shift_demand_tons"] * 0.75 # Substantial haul loss from ramp blockage
                        # Emergency repair required
                        v["hours_since_service"] = 0
                        v["urgency_score"] = 15.0

            # Execute Selected Policy
            if policy_type == "BASELINE_FIFO":
                plan = baseline_solver.schedule(fleet, workshop_bays=workshop["num_bays"], time_horizon_shifts=1)
                cancellations = plan["service_cancellations_count"]
                spares_used = 0
            else: # PROPOSED_OPTIMIZER
                plan = opt_solver.optimize(fleet, spares, workshop, time_horizon_shifts=1)
                cancellations = plan["actual_service_cancellations"]
                spares_used = plan["cancellations_avoided_by_spares"]
                
                # Record plan and stochastic override on blast shifts
                audit_logger.record_plan_generation(f"PLAN-S{shift:02d}", {"spares": spares_used}, plan["total_combined_cost_usd"])
                if shift in [7, 14] and plan["scheduled_slots"]:
                    audit_logger.record_dispatcher_override(
                        plan_id=f"PLAN-S{shift:02d}",
                        vehicle_id=plan["scheduled_slots"][0]["vehicle_id"],
                        original_slot="BAY-01",
                        new_slot="DEFERRED_BLAST_CLEARANCE",
                        dispatcher_id="SUP-CHIEF-09",
                        dispatcher_role="Mine Superintendent",
                        override_reason="Bench blast evacuation safety zone protocol",
                        service_impact_acknowledged=True
                    )

            total_cancellations += cancellations
            shift_delivered -= (cancellations * 2800.0)
            
            # Rejuvenate serviced trucks
            for slot in plan["scheduled_slots"]:
                vid = slot["vehicle_id"]
                for v in fleet:
                    if v["vehicle_id"] == vid:
                        v["hours_since_service"] = 0
                        v["urgency_score"] = 10.0
                        total_overhauls += 1
                        break
                        
            total_target_tons += shift_target
            total_delivered_tons += max(0.0, shift_delivered)
            
            history.append({
                "shift": shift,
                "policy": policy_type,
                "is_dust_storm": is_dust_storm,
                "scheduled": plan["scheduled_maintenance_count"],
                "cancellations": cancellations,
                "breakdowns": total_breakdowns,
                "shift_delivered_tons": round(max(0.0, shift_delivered), 0)
            })

        summary = {
            "policy": policy_type,
            "total_shifts": self.total_shifts,
            "target_tonnage": round(total_target_tons, 0),
            "delivered_tonnage": round(total_delivered_tons, 0),
            "fulfillment_pct": round((total_delivered_tons / total_target_tons) * 100, 2),
            "total_overhauls": total_overhauls,
            "total_service_cancellations": total_cancellations,
            "catastrophic_breakdowns": total_breakdowns,
            "total_loss_usd": round(total_cancellations * 45000.0 + total_breakdowns * 185000.0, 2),
            "audit_valid": audit_logger.verify_audit_integrity() if policy_type == "PROPOSED_OPTIMIZER" else None
        }
        return summary, history

def run_comparative_7day_experiment():
    sim = ComparativeMiningSimulator(num_vehicles=24, num_spares=4, total_shifts=21, seed=42)
    base_summary, base_hist = sim.run_policy("BASELINE_FIFO")
    opt_summary, opt_hist = sim.run_policy("PROPOSED_OPTIMIZER")
    
    print("\n" + "=" * 80)
    print("7-DAY (21 SHIFTS) CONTINUOUS MINING FLEET BENCHMARK EVALUATION")
    print("=" * 80)
    
    comp_df = pd.DataFrame([base_summary, opt_summary])
    print(comp_df[["policy", "fulfillment_pct", "total_overhauls", "total_service_cancellations", "catastrophic_breakdowns", "total_loss_usd"]].to_string(index=False))
    
    revenue_saved = base_summary["total_loss_usd"] - opt_summary["total_loss_usd"]
    print(f"\n[+] Total Operational Revenue & Maintenance Loss Saved by Proposed Optimizer: ${revenue_saved:,.2f}")
    print(f"[+] Service Cancellations Reduced by: {base_summary['total_service_cancellations'] - opt_summary['total_service_cancellations']} events")
    print(f"[+] Catastrophic In-Pit Breakdowns Reduced by: {base_summary['catastrophic_breakdowns'] - opt_summary['catastrophic_breakdowns']} events")
    
    # Save results
    comp_df.to_json("d:/project/comparative_simulation_results.json", orient="records", indent=2)
    pd.DataFrame(base_hist + opt_hist).to_csv("d:/project/simulation_7day_comparative.csv", index=False)
    print("[+] Results saved to d:/project/comparative_simulation_results.json and simulation_7day_comparative.csv")

if __name__ == "__main__":
    run_comparative_7day_experiment()
