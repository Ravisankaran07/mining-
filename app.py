"""
Full-Featured Production Application: Mining Fleet Maintenance-Slot Optimiser Dashboard.
Can be executed as:
  1. Streamlit Interactive Web Application: streamlit run app.py
  2. Standalone CLI Application: python app.py --cli
Features:
  - Telemetry Health & Environmental Harshness Monitor (GPS/Sensor degraded mode)
  - Solver Engine Selection: Real-Time Fast Heuristic vs Exact Global MILP (scipy.optimize.milp)
  - Pareto Frontier Trade-Off Curve (J1 Service Disruption vs J2 Breakdown Risk)
  - Interactive Workshop Bay Gantt Visualizer & Standby Spare Fleet Pairing
  - 7-Day (21 Shifts) Rolling-Horizon Simulation Monitor
  - Authorized Dispatcher Override Portal with Mandatory Rationale Capture
  - SHA-256 Tamper-Proof Cryptographic Audit Ledger Inspector
"""

import sys
import os
import argparse
import json
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure local imports work cleanly
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from data_generator import generate_mining_fleet
from optimizer_core import TelemetryResilientPreprocessor, BaselineUrgencyScheduler, MultiObjectiveSlotOptimizer
from milp_optimizer import ExactMILPSlotOptimizer
from audit_logger import DispatcherAuditLogger

def run_cli_interactive():
    print("=" * 80)
    print("MINING FLEET MAINTENANCE-SLOT OPTIMISER (PRODUCTION CLI CONSOLE)")
    print("=" * 80)
    
    data = generate_mining_fleet(num_vehicles=24, num_spares=4)
    fleet = data["fleet"]
    spares = data["spares"]
    workshop = data["workshop"]
    
    print(f"\n[+] Ingested {len(fleet)} heavy vehicles under harsh open-pit conditions.")
    print(f"[+] Workshop Bays: {workshop['num_bays']} | Standby Replacement Pool: {len(spares)}")
    
    degraded = [v for v in fleet if v["telemetry_status"] != "HEALTHY"]
    print(f"[!] Alert: {len(degraded)}/{len(fleet)} vehicles operating in degraded telemetry mode (GPS/Sensor loss).")
    
    # Run Baseline, Heuristic, and MILP
    baseline = BaselineUrgencyScheduler()
    heur_opt = MultiObjectiveSlotOptimizer(w_cancellation=0.5, w_breakdown_risk=0.5)
    milp_opt = ExactMILPSlotOptimizer(w_cancellation=0.5, w_breakdown_risk=0.5)
    
    base_res = baseline.schedule(fleet, workshop_bays=3)
    heur_res = heur_opt.optimize(fleet, spares, workshop)
    milp_res = milp_opt.solve(fleet[:12], spares[:3], workshop) # Solve subset for quick CLI output
    
    print("\n" + "=" * 60)
    print("TRIPLE-SOLVER BENCHMARK COMPARISON:")
    print("=" * 60)
    print(f"1. Baseline FIFO Urgency       : {base_res['service_cancellations_count']} Cancellations | Cost: ${base_res['total_cancellation_cost_usd']:,.2f}")
    print(f"2. Multi-Objective Heuristic   : {heur_res['actual_service_cancellations']} Cancellations | Cost: ${heur_res['total_cancellation_cost_usd']:,.2f} | Spares Used: {heur_res['cancellations_avoided_by_spares']}")
    print(f"3. Exact MILP Global Optimum   : {milp_res['actual_service_cancellations']} Cancellations | Status: {milp_res['status']}")
    
    savings = base_res['total_cancellation_cost_usd'] - heur_res['total_cancellation_cost_usd']
    print(f"\n[+] Direct Revenue / Haul Loss Avoided by Optimization: ${savings:,.2f}")
    
    audit = DispatcherAuditLogger(log_filepath="dispatcher_override_audit.jsonl")
    valid = audit.verify_audit_integrity()
    print(f"[+] Cryptographic Audit Chain Integrity: {'VALID (TAMPER-PROOF)' if valid else 'COMPROMISED'}")
    print("\nLaunch with 'streamlit run app.py' to explore the full interactive dashboard.")

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def run_streamlit_app():
    st.set_page_config(page_title="Mining Fleet Maintenance-Slot Optimiser", layout="wide", page_icon="🚜")
    
    st.title("🚜 Heavy Mining Fleet Maintenance-Slot Optimiser (Production Suite)")
    st.markdown("""
    **Operational Decision-Support & Execution System:** Explicitly balances service demand cancellation costs 
    and replacement-vehicle capacity against catastrophic in-pit breakdown risks under harsh environmental duress.
    """)
    
    # Sidebar Controls
    st.sidebar.header("⚙️ Fleet & Optimization Controls")
    solver_choice = st.sidebar.selectbox("Solver Formulation", ["Fast Multi-Objective Heuristic", "Exact MILP Global Solver (scipy.milp)", "Baseline FIFO Urgency"])
    num_vehicles = st.sidebar.slider("Active Mining Fleet", min_value=12, max_value=36, value=24, step=4)
    num_spares = st.sidebar.slider("Standby Spare Hauler Pool", min_value=0, max_value=8, value=4, step=1)
    
    w_cost = st.sidebar.slider("Weight: Service Cancellation Cost (J1)", 0.0, 1.0, 0.5, 0.05)
    w_risk = round(1.0 - w_cost, 2)
    st.sidebar.caption(f"Weight: Breakdown Hazard Risk (J2) = {w_risk}")
    
    # Degraded Mode Simulation Injection
    st.sidebar.subheader("🌪️ Environmental Harshness Controls")
    inject_dust_storm = st.sidebar.checkbox("Trigger Severe Dust Storm (PM10 > 750 µg/m³)", value=False)
    force_gps_drop = st.sidebar.checkbox("Simulate Deep-Pit GPS Outage (30% fleet)", value=False)
    
    # Generate fleet data
    data = generate_mining_fleet(num_vehicles=num_vehicles, num_spares=num_spares)
    fleet = data["fleet"]
    spares = data["spares"]
    workshop = data["workshop"]
    
    if inject_dust_storm:
        for v in fleet:
            v["dust_pm10"] = 820.0
            v["ambient_temp_c"] = 49.0
    if force_gps_drop:
        for idx, v in enumerate(fleet):
            if idx % 3 == 0:
                v["telemetry_status"] = "GPS_LOST"

    # KPI Top Bar
    df_fleet = pd.DataFrame(fleet)
    degraded_count = len(df_fleet[df_fleet["telemetry_status"] != "HEALTHY"])
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active Heavy Fleet", f"{len(fleet)} Units")
    k2.metric("Workshop Capacity", f"{workshop['num_bays']} Bays")
    k3.metric("Standby Replacement Fleet", f"{len(spares)} Trucks")
    k4.metric("Degraded Telemetry (GPS/Sensors)", f"{degraded_count} Units", delta=f"{degraded_count/len(fleet)*100:.0f}% Offline", delta_color="inverse")
    
    # Run Selected Solver
    st.markdown("---")
    if solver_choice == "Baseline FIFO Urgency":
        solver = BaselineUrgencyScheduler()
        res = solver.schedule(fleet, workshop_bays=workshop["num_bays"])
    elif solver_choice == "Exact MILP Global Solver (scipy.milp)":
        solver = ExactMILPSlotOptimizer(w_cancellation=w_cost, w_breakdown_risk=w_risk)
        # Solve subset if fleet is very large to maintain instant interactivity
        solve_fleet = fleet if len(fleet) <= 18 else fleet[:18]
        res = solver.solve(solve_fleet, spares, workshop)
    else:
        solver = MultiObjectiveSlotOptimizer(w_cancellation=w_cost, w_breakdown_risk=w_risk)
        res = solver.optimize(fleet, spares, workshop)
        
    # Performance Metric Comparisons
    baseline_calc = BaselineUrgencyScheduler().schedule(fleet, workshop_bays=workshop["num_bays"])
    
    st.subheader(f"📊 Solver Performance: {solver_choice}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Maintenance Scheduled", f"{res['scheduled_maintenance_count']} Overhauls")
    m2.metric("Service Cancellations", f"{res['actual_service_cancellations']} Routes", 
              delta=f"-{baseline_calc['service_cancellations_count'] - res['actual_service_cancellations']} Avoided" if "actual_service_cancellations" in res else "0", delta_color="normal")
    revenue_protected = max(0.0, baseline_calc['total_cancellation_cost_usd'] - res['total_cancellation_cost_usd'])
    m3.metric("Revenue Loss Avoided", f"${revenue_protected:,.2f}")
    m4.metric("Combined Objective Cost", f"${res['total_combined_cost_usd']:,.2f}")
    
    # Schedule View
    st.subheader("🗓️ Workshop Bay Allocation & Standby Replacement Schedule")
    df_sched = pd.DataFrame(res["scheduled_slots"])
    if not df_sched.empty:
        st.dataframe(df_sched, use_container_width=True)
    else:
        st.info("No vehicles currently require immediate workshop intervention.")
        
    # Tabs for Advanced Capabilities
    tab_pareto, tab_sim, tab_override, tab_audit = st.tabs([
        "📈 Pareto Trade-Off Curve", 
        "🔄 7-Day Rolling Simulation", 
        "🔒 Dispatcher Override Portal", 
        "📜 Immutable Cryptographic Audit Ledger"
    ])
    
    with tab_pareto:
        st.markdown("### Pareto Frontier: Service Cancellation Cost ($J_1$) vs. Breakdown Hazard Risk ($J_2$)")
        if os.path.exists("pareto_frontier_results.json"):
            with open("pareto_frontier_results.json", "r") as f:
                p_data = json.load(f)
            df_p = pd.DataFrame(p_data)
            st.dataframe(df_p[["w1_cancellation", "w2_breakdown", "heur_combined_cost", "milp_combined_cost", "optimality_gap_pct"]], use_container_width=True)
            st.line_chart(df_p.set_index("w1_cancellation")[["heur_combined_cost", "milp_combined_cost"]])
            st.caption("Visualizing the mathematical optimality gap between real-time heuristic and global MILP solutions.")
            
    with tab_sim:
        st.markdown("### 7-Day (21 Shifts) Stochastic Operation Results")
        if os.path.exists("comparative_simulation_results.json"):
            with open("comparative_simulation_results.json", "r") as f:
                s_data = json.load(f)
            st.dataframe(pd.DataFrame(s_data), use_container_width=True)
        if os.path.exists("simulation_7day_comparative.csv"):
            df_sim_comp = pd.read_csv("simulation_7day_comparative.csv")
            st.line_chart(df_sim_comp.pivot(index="shift", columns="policy", values="shift_delivered_tons"))
            st.caption("Shift-by-shift delivered production tonnage comparing Baseline FIFO vs. Proposed Optimizer.")

    with tab_override:
        st.markdown("### Execute Authorized Maintenance Plan Override")
        with st.form("override_form_adv"):
            col_v, col_s = st.columns(2)
            v_select = col_v.selectbox("Target Vehicle ID", [v["vehicle_id"] for v in fleet])
            slot_select = col_s.selectbox("Override Slot", ["BAY-01_SHIFT-01", "BAY-02_SHIFT-02", "BAY-03_SHIFT-03", "DEFERRED_POST_BLAST"])
            
            col_id, col_r = st.columns(2)
            disp_user = col_id.text_input("Supervisor Staff ID", value="SUP-DISPATCH-99")
            disp_role = col_r.selectbox("Authorization Authority", ["Pit Dispatch Superintendent", "Chief Operations Engineer", "Workshop Lead"])
            
            override_reason = st.text_area("Mandatory Operational Justification", value="Emergency blast clearance haulage in Bench 4B")
            ack = st.checkbox("I legally authorize this plan modification and accept the calculated breakdown/cost risk.", value=True)
            
            submit_btn = st.form_submit_button("Commit Cryptographic Override")
            if submit_btn and ack:
                logger = DispatcherAuditLogger(log_filepath="dispatcher_override_audit.jsonl")
                entry = logger.record_dispatcher_override(
                    plan_id="GUI-LIVE-OVERRIDE",
                    vehicle_id=v_select,
                    original_slot="AUTOMATED_PLAN",
                    new_slot=slot_select,
                    dispatcher_id=disp_user,
                    dispatcher_role=disp_role,
                    override_reason=override_reason,
                    service_impact_acknowledged=ack
                )
                st.success(f"Override securely written to immutable ledger! SHA-256 Block Hash: {entry['current_hash']}")

    with tab_audit:
        st.markdown("### Immutable Cryptographic Audit Ledger")
        audit_engine = DispatcherAuditLogger(log_filepath="dispatcher_override_audit.jsonl")
        if os.path.exists("dispatcher_override_audit.jsonl"):
            with open("dispatcher_override_audit.jsonl", "r") as f:
                audit_records = [json.loads(line) for line in f if line.strip()]
            if audit_records:
                st.dataframe(pd.DataFrame(audit_records)[["timestamp", "entry_type", "vehicle_id", "new_slot", "dispatcher_id", "override_reason", "current_hash"]], use_container_width=True)
                valid = audit_engine.verify_audit_integrity()
                if valid:
                    st.success("✅ Audit Ledger Integrity Verified: All SHA-256 Block Hashes Are Intact.")
                else:
                    st.error("❌ Warning: Audit Trail Hash Chain Tampering Detected!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run interactive CLI console")
    args = parser.parse_args()
    
    if args.cli or not HAS_STREAMLIT:
        run_cli_interactive()
    else:
        if "streamlit" in sys.modules and hasattr(st, "runtime") and st.runtime.exists():
            run_streamlit_app()
        else:
            run_cli_interactive()
