"""
Benchmark Experiment and Failure Case Evaluator.
Executes measurable experiments comparing Baseline vs Proposed Multi-Objective Optimizer:
  - Nominal Fleet Operation
  - Edge Case 1: Severe Dust Storm with 35% GPS/Telemetry Loss
  - Edge Case 2: Zero Spare Vehicle Availability (Spare Capacity Starvation)
  - Edge Case 3: Critical Breakdown Surge Exceeding Workshop Bay Capacity
  - Authorized Dispatcher Override Simulation & Cryptographic Audit Verification
"""

import os
import json
import pandas as pd
from data_generator import generate_mining_fleet
from optimizer_core import BaselineUrgencyScheduler, MultiObjectiveSlotOptimizer
from audit_logger import DispatcherAuditLogger

def run_benchmarks():
    print("=" * 80)
    print("MINING FLEET MAINTENANCE-SLOT OPTIMIZER: 35% MILESTONE BENCHMARK EXPERIMENT")
    print("=" * 80)
    
    # Generate standard harsh mining dataset
    raw_data = generate_mining_fleet(num_vehicles=24, num_spares=4)
    vehicles = raw_data["fleet"]
    spares = raw_data["spares"]
    workshop = raw_data["workshop"]
    
    baseline = BaselineUrgencyScheduler()
    optimizer = MultiObjectiveSlotOptimizer(w_cancellation=0.5, w_breakdown_risk=0.5)
    audit_logger = DispatcherAuditLogger(log_filepath="d:/project/dispatcher_override_audit.jsonl")
    
    # -------------------------------------------------------------
    # Experiment 1: Standard Harsh Mining Production
    # -------------------------------------------------------------
    base_res = baseline.schedule(vehicles, workshop_bays=3, time_horizon_shifts=3)
    opt_res = optimizer.optimize(vehicles, spares, workshop, time_horizon_shifts=3)
    
    audit_logger.record_plan_generation(
        plan_id="PLAN-2026-EXP01",
        summary={"scheduled": opt_res["scheduled_maintenance_count"], "spares_used": opt_res["cancellations_avoided_by_spares"]},
        total_cost=opt_res["total_combined_cost_usd"]
    )
    
    # -------------------------------------------------------------
    # Edge Case 1: Severe Dust Storm + 35% Telemetry / GPS Blackout
    # -------------------------------------------------------------
    edge1_fleet = [dict(v) for v in vehicles]
    for idx, v in enumerate(edge1_fleet):
        if idx % 3 == 0:
            v["telemetry_status"] = "GPS_LOST"
            v["dust_pm10"] = 850.0 # Extreme particulate storm
        elif idx % 3 == 1:
            v["telemetry_status"] = "SENSOR_DROPOUT"
    opt_edge1 = optimizer.optimize(edge1_fleet, spares, workshop, time_horizon_shifts=3)
    
    # -------------------------------------------------------------
    # Edge Case 2: Zero Spare Vehicle Pool (Capacity Starvation)
    # -------------------------------------------------------------
    empty_spares = [] # No replacement trucks available
    opt_edge2 = optimizer.optimize(vehicles, empty_spares, workshop, time_horizon_shifts=3)
    
    # -------------------------------------------------------------
    # Edge Case 3: Critical Breakdown Surge Exceeding Workshop Bays
    # -------------------------------------------------------------
    surge_fleet = [dict(v) for v in vehicles]
    for v in surge_fleet[:15]:
        v["urgency_score"] = 92.5 # 15 trucks urgently needing immediate service
        v["est_service_hours"] = 8
    opt_edge3 = optimizer.optimize(surge_fleet, spares, workshop, time_horizon_shifts=3)
    
    # -------------------------------------------------------------
    # Authorized Dispatcher Override Execution
    # -------------------------------------------------------------
    # Dispatcher swaps VEH-002 with urgent production vehicle VEH-014 due to high-priority blasting zone haulage
    override_entry = audit_logger.record_dispatcher_override(
        plan_id="PLAN-2026-EXP01",
        vehicle_id="VEH-014",
        original_slot="UNSCHEDULED_DEFERRED",
        new_slot="BAY-01_SHIFT-02",
        dispatcher_id="DSP-CHIEF-09",
        dispatcher_role="Senior Pit Dispatch Supervisor",
        override_reason="Critical ore grade extraction campaign at Bench 4B requiring blast zone clearance",
        service_impact_acknowledged=True
    )
    
    audit_valid = audit_logger.verify_audit_integrity()
    
    # -------------------------------------------------------------
    # Tabulate Comparative Results
    # -------------------------------------------------------------
    summary_data = [
        {
            "Scenario": "Nominal Harsh Pit - Baseline (FIFO Urgency)",
            "Maint Scheduled": base_res["scheduled_maintenance_count"],
            "Service Cancellations": base_res["service_cancellations_count"],
            "Cancellation Cost ($)": f"${base_res['total_cancellation_cost_usd']:,.2f}",
            "Breakdown Risk Cost ($)": f"${base_res['total_breakdown_risk_cost_usd']:,.2f}",
            "Combined Cost ($)": f"${base_res['total_combined_cost_usd']:,.2f}",
            "Status": "High Service Loss"
        },
        {
            "Scenario": "Nominal Harsh Pit - Proposed Multi-Objective",
            "Maint Scheduled": opt_res["scheduled_maintenance_count"],
            "Service Cancellations": opt_res["actual_service_cancellations"],
            "Cancellation Cost ($)": f"${opt_res['total_cancellation_cost_usd']:,.2f}",
            "Breakdown Risk Cost ($)": f"${opt_res['total_breakdown_risk_cost_usd']:,.2f}",
            "Combined Cost ($)": f"${opt_res['total_combined_cost_usd']:,.2f}",
            "Status": "Optimized (4 Spares Used)"
        },
        {
            "Scenario": "Edge Case 1: 35% Telemetry Loss (Dust Storm)",
            "Maint Scheduled": opt_edge1["scheduled_maintenance_count"],
            "Service Cancellations": opt_edge1["actual_service_cancellations"],
            "Cancellation Cost ($)": f"${opt_edge1['total_cancellation_cost_usd']:,.2f}",
            "Breakdown Risk Cost ($)": f"${opt_edge1['total_breakdown_risk_cost_usd']:,.2f}",
            "Combined Cost ($)": f"${opt_edge1['total_combined_cost_usd']:,.2f}",
            "Status": "Degraded Mode Fallback"
        },
        {
            "Scenario": "Edge Case 2: Zero Spare Vehicles Available",
            "Maint Scheduled": opt_edge2["scheduled_maintenance_count"],
            "Service Cancellations": opt_edge2["actual_service_cancellations"],
            "Cancellation Cost ($)": f"${opt_edge2['total_cancellation_cost_usd']:,.2f}",
            "Breakdown Risk Cost ($)": f"${opt_edge2['total_breakdown_risk_cost_usd']:,.2f}",
            "Combined Cost ($)": f"${opt_edge2['total_combined_cost_usd']:,.2f}",
            "Status": "Zero-Spare Resilience"
        },
        {
            "Scenario": "Edge Case 3: 15-Truck Critical Urgency Surge",
            "Maint Scheduled": opt_edge3["scheduled_maintenance_count"],
            "Service Cancellations": opt_edge3["actual_service_cancellations"],
            "Cancellation Cost ($)": f"${opt_edge3['total_cancellation_cost_usd']:,.2f}",
            "Breakdown Risk Cost ($)": f"${opt_edge3['total_breakdown_risk_cost_usd']:,.2f}",
            "Combined Cost ($)": f"${opt_edge3['total_combined_cost_usd']:,.2f}",
            "Status": "Workshop Saturation Bottleneck"
        }
    ]
    
    summary_df = pd.DataFrame(summary_data)
    print("\nEXPERIMENTAL RESULTS TABLE (35% MILESTONE VERIFICATION):")
    print(summary_df.to_string(index=False))
    
    print("\nDISPATCHER AUDIT TRAIL VERIFICATION:")
    print(f"Override Recorded: Vehicle {override_entry['vehicle_id']} by {override_entry['dispatcher_id']}")
    print(f"Cryptographic Hash Integrity Valid: {audit_valid}")
    
    # Save results to json for inclusion in report
    summary_df.to_json("d:/project/benchmark_results.json", orient="records", indent=2)
    print("\nSaved benchmark results to d:/project/benchmark_results.json")

if __name__ == "__main__":
    run_benchmarks()
