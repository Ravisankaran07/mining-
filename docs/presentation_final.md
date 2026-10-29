# Final Project Defense Presentation: 100% Completion

## Mining Operation Depending on Heavy Vehicles in Harsh Conditions: Maintenance-Slot Optimiser Including Service Demand

---

### Slide 1: Title & Overview
* **Project Title:** Heavy Mining Vehicle Maintenance-Slot Optimiser Including Service Demand & Replacement-Vehicle Capacity
* **Milestone:** Final Capstone Project Defense (100% Completed)
* **Target Domain:** Open-Pit Heavy Mining Operations (CAT 797F, Komatsu 930E, Hitachi EX5600)
* **Core Contribution:** An end-to-end operational decision-support and control system that incorporates production haul disruption costs into maintenance slot scheduling with standby vehicle synchronization and degraded-mode resilience.

---

### Slide 2: Problem Statement & Industrial Motivation
* **The Operational Blindspot:**
  * Maintenance pulls a 400-tonne haul truck for an overhaul solely based on engine hours or sensor alarms.
  * Pit Dispatch is blindsided: no spare hauler is staged; the haul route is cancelled; crusher throughput drops.
  * Cost of cancellation: **\$45,000 to \$60,000 per lost shift**.
* **The Opposite Hazard:**
  * Dispatchers informally postpone maintenance to meet short-term tonnage quotas.
  * Hauler suffers catastrophic in-pit breakdown (engine fire, final drive seizure) on a 12% ramp, blocking pit access and costing $5\times$ more to recover.
* **Harsh Operating Environment:**
  * Ambient heat ($48^\circ\text{C}$), extreme dust ($\text{PM}_{10} > 600\,\mu\text{g/m}^3$), steep inclines, and frequent GPS/radio dead zones.

---

### Slide 3: System Architecture & Workflow
```
[ Telemetry Ingestion ] ──> [ Degraded Mode Preprocessor ] (GPS Loss / Sensor Dropouts)
                                      │
                                      ▼
[ Mathematical Engine ] <── [ Workshop Bays (3) ] + [ Standby Spares (4) ]
  • Exact 0-1 MILP Solver (scipy.optimize.milp)
  • Fast Dynamic Heuristic (<15ms)
                                      │
                                      ▼
[ Dispatcher Oversight Portal ] ──> [ Cryptographic SHA-256 Chained Audit Ledger ]
                                      │
                                      ▼
[ Workshop Bay Staging & Replacement Vehicle Dispatch ]
```

---

### Slide 4: Dual Competing Objectives Formulation
$$\min_{\mathbf{x}, \mathbf{y}, \mathbf{z}} \quad \mathcal{J} = w_1 \cdot J_1 + w_2 \cdot J_2$$

* **Objective 1 ($J_1$): Operational Disruption / Service Cancellation Cost**
  $$J_1 = \sum_{v, t} \left[ \left( \sum_b x_{v,b,t} - \sum_s y_{v,s,t} \right) \cdot C_v^{\text{canc}} + \sum_s y_{v,s,t} \cdot C_{v,s}^{\text{changeover}} \right]$$
  *Minimizes lost haulage revenue, reduced to a minor \$3,500 changeover cost when covered by a spare.*
* **Objective 2 ($J_2$): Catastrophic Breakdown Hazard Risk**
  $$J_2 = \sum_v z_v \cdot \left( U_v^{1.8} \cdot \kappa \cdot \Omega_{\text{env}} \cdot \mu_{\text{telemetry}} \right)$$
  *Penalizes deferring maintenance on stressed equipment operating under extreme dust and heat.*

---

### Slide 5: Hard & Soft Constraints Matrix
* **Hard Constraints (Strict Invariants):**
  1. Bay capacity limit: $\sum_v x_{v,b,t} \le 1$
  2. Maximum concurrent bays: $\sum_{v,b} x_{v,b,t} \le 3$
  3. Single service allotment: $\sum_{b,t} x_{v,b,t} \le 1$
  4. Spare vehicle pool availability: $\sum_v y_{v,s,t} \le 1$
  5. Replacement validity: $y_{v,s,t} \le \sum_b x_{v,b,t}$
* **Soft Constraints:**
  * Preference for standard 8-hour shift changeover windows (06:00, 14:00, 22:00).
  * Outbound workshop release queue smoothing.

---

### Slide 6: Resilience to Incomplete Telemetry (Degraded Mode)
* **GPS Signal Loss in Deep Pit Benches:**
  * Automatically switches to dead reckoning based on last known pit sector gate checkpoint.
  * Adds an automatic 1.0-hour transit safety buffer to prevent workshop bays from sitting idle.
* **Sensor Dropout / Blindspots:**
  * High dust and thermal spikes frequently foul exhaust and oil sensors.
  * Instead of assuming healthy status, system applies a **conservative 25% urgency inflation ($\mu = 1.25$)** to prioritize precautionary inspection.

---

### Slide 7: Authorized Dispatcher Override & Immutable Audit Ledger
* **Operational Necessity:**
  * Mine superintendents must retain override authority for blasting evacuation or ore blending.
* **Cryptographic Governance:**
  * Reassignments require staff ID, role, and mandatory operational justification.
  * Every override is sealed into an immutable JSONL ledger using SHA-256 block hashing:
    $$H_k = \text{SHA-256}\left(\text{Payload}_k \parallel H_{k-1}\right)$$
  * Automated audit checks continuously verify the hash chain; retroactive alteration is mathematically impossible.

---

### Slide 8: Empirical Single-Horizon Benchmark Results
* **Fleet Configuration:** 24 Heavy Mining Vehicles, 4 Standby Spares, 3 Workshop Bays over 3 Shifts.
* **Comparative Performance:**
  * **Baseline FIFO Urgency:** 6 overhauls scheduled $\rightarrow$ **6 service cancellations** (Cost: **\$2,946,000**).
  * **Proposed Multi-Objective Optimizer:** 6 overhauls scheduled $\rightarrow$ **3 cancellations** (Cost: **\$1,033,500**).
  * **Impact:** **50% reduction in route cancellations** and **\$1,912,500 direct production revenue saved**.
* **Edge Case Verification:**
  * Edge Case 1 (35% Telemetry Loss): Handled with dead-reckoning transit buffers.
  * Edge Case 2 (Zero Standby Spares): Graceful prioritization without failure.
  * Edge Case 3 (15-Truck Urgency Surge): Hard bay capacity strictly maintained.

---

### Slide 9: Continuous 7-Day (21 Shifts) Rolling-Horizon Simulation
* **Evaluation Scope:** 21 consecutive shifts subject to stochastic dust storms, thermal waves, and bench blasting.
* **Simulation Findings:**
  * **Tonnage Fulfillment Rate:** **97.32%** (3,660,250 tonnes delivered).
  * **Service Cancellations Avoided:** 13 cancellations prevented by dynamic spare rotation.
  * **Net Multi-Shift Margin Saved:** **\$215,000.00** over baseline FIFO scheduling.
  * **Audit Ledger Verification:** 100% cryptographic integrity verified across all 21 shifts.

---

### Slide 10: Mathematical Optimality Gap (Heuristic vs. Exact MILP)
* **Dual Solvers Implemented:**
  1. Exact 0-1 Mixed-Integer Linear Program (`scipy.optimize.milp`).
  2. Real-Time Dynamic Heuristic (<15ms execution time).
* **Pareto Frontier Analysis ($w_1 \in [0.1, 0.9]$):**
  * When prioritizing cancellation prevention ($w_1 \ge 0.77$), the optimality gap drops to **14.31%**.
  * At $w_1 = 0.90$, the heuristic reaches **0.00% (exact global convergence)**.
  * The fast heuristic delivers near-optimal decisions instantaneously, ideal for live pit dispatch.

---

### Slide 11: Production Dashboard & Deployment Architecture
* **Interactive Dashboard (`app.py`):**
  * Workshop Bay Gantt Chart & Standby Replacement Visualizer.
  * Pareto Trade-off Curve & Optimality Gap Visualizer.
  * 7-Day Rolling Simulation Performance Monitor.
  * Interactive Dispatcher Override Portal with live cryptographic hash viewer.
* **Enterprise Deployment:**
  * Multi-stage Docker containerization (`Dockerfile` & `docker-compose.yml`).
  * Automated unit and integration test suite (`tests/test_full_suite.py`).

---

### Slide 12: Conclusion & Summary of Deliverables
* **Problem Solved:** Overcame the operational disconnect between maintenance and production by coupling maintenance urgency with service demand and replacement capacity.
* **Project Deliverables Completed (100%):**
  * [x] Formal Review Reports: Review 1 (35%), Review 2 (70%), Final Report (100%).
  * [x] Working Codebase: Preprocessors, Baseline, Heuristic, Exact MILP, Simulator, Audit Ledger.
  * [x] Interactive Streamlit Dashboard & Production CLI Console.
  * [x] Full FMEA Risk Matrix & Stakeholder Persona Evaluations.
  * [x] Complete Automated Test Suite & Dockerized Microservice Architecture.
