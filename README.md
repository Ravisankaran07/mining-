# Mining Fleet Maintenance-Slot Optimiser

> **Operational Decision-Support System for Heavy Vehicles Operating Under Harsh Mining Conditions**

![Status](https://img.shields.io/badge/Status-100%25%20Completed-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue)
![Solvers](https://img.shields.io/badge/Solvers-Exact%20MILP%20%2B%20Fast%20Heuristic-orange)
![Resilience](https://img.shields.io/badge/Resilience-GPS%20%26%20Sensor%20Degraded%20Mode-red)
![Audit](https://img.shields.io/badge/Audit-SHA--256%20Blockchain--Style-purple)

---

## 📌 Problem Overview
In large open-pit mining operations, heavy mobile equipment (e.g., Ultra-Class haul trucks like CAT 797F and Komatsu 930E, hydraulic excavators like Hitachi EX5600) operates under severe environmental duress: ambient heat (38°C–50°C), dense dust ($\text{PM}_{10} > 600\,\mu\text{g/m}^3$), high-vibration duty cycles, and steep haul ramps ($>10\%$).

Historically, maintenance scheduling has been isolated from pit dispatching:
- **The Operational Blindspot:** When a 400-tonne haul truck is pulled for an 8-hour service during peak production without a coordinated replacement, operations suffer sudden haul route cancellations costing **\$45,000–\$60,000 per lost shift**.
- **The Deferral Hazard:** If dispatchers informally postpone maintenance to meet short-term tonnage quotas, vehicles suffer catastrophic in-pit breakdowns, blocking ramps and costing $5\times$ more to recover.

This project delivers an integrated **Maintenance-Slot Optimiser Including Service Demand and Replacement-Vehicle Capacity**—an operational decision-support and control system rather than an isolated predictive notebook.

---

## 🚀 Key Features

1. **Dual Competing Objectives Formulation:**
   - **$J_1$ (Operational Service Cancellation Cost):** Minimizes lost production tonnage, actively mitigated by dynamic assignment from a standby replacement fleet.
   - **$J_2$ (Catastrophic Pit Breakdown Hazard Risk):** Penalizes deferring maintenance on stressed equipment operating under extreme dust and heat.
2. **Standby Replacement Capacity Synchronization:** Matches taken-down production haulers with available standby replacement trucks.
3. **Telemetry Degraded-Mode Resilience:** Remains fully operational during GPS blackouts (dead-reckoning + 1.0h transit buffer) and dust-fouled sensor dropouts (conservative 25% urgency inflation).
4. **Dual Optimization Engines:**
   - **Exact 0-1 MILP Solver:** Global mathematical optimum formulated via binary constraint matrices with `scipy.optimize.milp`.
   - **Fast Dynamic Heuristic:** Sub-15ms execution time for live real-time dispatch environments.
5. **Authorized Dispatcher Override & Immutable Audit Ledger:**
   - Authenticated supervisory override portal requiring credentials and mandatory operational justifications.
   - Every override is cryptographically sealed into an append-only ledger using **SHA-256 blockchain-style hash chaining** ($H_k = \text{SHA-256}(\text{Data}_k \parallel H_{k-1})$).
6. **Continuous 7-Day (21 Shifts) Rolling-Horizon Simulator:**
   - 97.32% tonnage fulfillment rate across stochastic dust storms, thermal waves, and emergency blasting evacuations.
   - Preserves **\$1.91M in single-horizon production revenue** and **\$215k in net multi-shift margins**.
7. **Production Web Dashboard & CLI:**
   - Interactive Streamlit dashboard featuring workshop bay Gantt charts, live telemetry monitors, Pareto curve plots, and live cryptographic audit verification.

---

## 📊 Benchmark Summary

```
Scenario                                      Maint Scheduled  Cancellations  Cancellation Cost ($)  Breakdown Risk Cost ($)  Total Combined Cost ($)
-----------------------------------------------------------------------------------------------------------------------------------------------------
Nominal Pit - Baseline (FIFO Urgency)                6               6            $2,946,000.00          $10,415,436.01           $13,361,436.01
Nominal Pit - Proposed Multi-Objective               6               3            $1,033,500.00          $12,184,416.64           $13,217,916.64
Edge Case 1: 35% Telemetry Loss (Dust Storm)         6               5            $2,462,812.50          $13,616,697.78           $16,079,510.28
Edge Case 2: Zero Spare Vehicles Available           6               6            $2,410,125.00          $12,184,416.64           $14,594,541.64
Edge Case 3: 15-Truck Critical Urgency Surge         6               3            $1,204,625.00          $13,833,111.83           $15,037,736.83
```

---

## 🛠️ Quick Start

### 1. Installation
```bash
git clone <your-repository-url>
cd mining-maintenance-slot-optimizer
pip install -r requirements.txt
```

### 2. Run Automated System Tests
```bash
python -m unittest tests/test_full_suite.py
```

### 3. Launch Interactive Web Dashboard
```bash
streamlit run app.py
```

### 4. Run CLI Interactive Console
```bash
python app.py --cli
```

### 5. Docker Deployment
```bash
docker-compose up -d --build
```

---

## 📁 Repository Structure

```
├── Final_Project_Report.md           # Comprehensive 100% Final Report
├── Review_1_Report.md                # 35% Milestone Submission Report
├── Review_2_Report.md                # 70% Milestone Technical Report
├── app.py                            # Production Streamlit GUI & CLI Console
├── requirements.txt                  # Python Dependencies
├── Dockerfile & docker-compose.yml   # Production Containerization
├── benchmark_results.json            # Benchmark Experimental Data
├── pareto_frontier_results.json      # Pareto Frontier & Optimality Gap Data
├── comparative_simulation_results.json# 7-Day Rolling Simulation Metrics
├── dispatcher_override_audit.jsonl   # Cryptographic SHA-256 Audit Ledger
├── src/                              # Core Optimization Engines
│   ├── data_generator.py             # Harsh fleet & environmental simulator
│   ├── optimizer_core.py             # Preprocessor, baseline, & heuristic
│   ├── milp_optimizer.py             # Exact 0-1 MILP global mathematical solver
│   ├── simulation_engine.py          # 21-shift stochastic rolling simulator
│   ├── pareto_analysis.py            # Multi-objective Pareto frontier engine
│   └── audit_logger.py               # Cryptographic hash-chained audit logger
├── docs/                             # Documentation Suite
│   ├── field_workflow_map.md         # Operational Architecture Map & Mermaid flow
│   ├── failure_mode_analysis.md      # Industrial FMEA Risk Matrix
│   ├── user_feedback_summary.md      # Persona Interviews
│   ├── technical_documentation.md    # API Specs & Runbooks
│   ├── presentation_final.md         # Final 12-Slide Project Defense Deck
│   └── presentation_review_1.md      # Review 1 Slide Deck
├── notebooks/
│   └── experiment_and_benchmarks.ipynb # Jupyter Notebook
└── tests/
    ├── test_optimizer.py             # Core mathematical tests (6/6 passing)
    └── test_full_suite.py            # System integration tests (5/5 passing)
```
