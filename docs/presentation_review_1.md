# Slide Deck: Review 1 Presentation (35% Project Completion)

## Mining Operation Depending on Heavy Vehicles in Harsh Conditions: Maintenance-Slot Optimiser Including Service Demand

---

### Slide 1: Title & Project Metadata
* **Title:** Maintenance-Slot Optimiser Including Service Demand & Replacement-Vehicle Capacity
* **Subtitle:** 35% Completion Milestone — Review 1 Submission
* **Target Domain:** Open-Pit Heavy Mining Operations (CAT 797F, Komatsu 930E, Hitachi EX5600)
* **Date:** October 2026
* **Key Innovation:** Bridging predictive maintenance with real-time pit dispatch schedules and standby replacement capacity under degraded telemetry.

---

### Slide 2: The Core Problem in Open-Pit Mining
* **The Costly Disconnect:**
  * Maintenance pulls a 400-tonne haul truck for an 8-hour service without checking if replacement capacity is available.
  * Result: Sudden route cancellation costing **\$45,000–\$60,000/shift** in lost ore throughput.
* **The Opposite Extreme:**
  * Dispatchers ignore warning flags to meet shift tonnage quotas.
  * Result: Catastrophic in-pit failure (engine fire, seized differential) costing $5\times$ more to recover and blocking haul ramps.
* **Environmental Reality:**
  * Extreme heat ($48^\circ\text{C}$), dense dust ($\text{PM}_{10} > 600\,\mu\text{g/m}^3$), steep ramps ($>10\%$), and frequent GPS/radio blackouts.

---

### Slide 3: What Makes This More Than a Predictive Notebook?
* **Beyond Isolated RUL Predictions:**
  * Traditional notebooks only predict *when* a part might fail.
  * **Our Solution:** A functional decision-support and control system that optimizes **who, when, which bay, and which replacement hauler covers the route**.
* **Key Pillars:**
  1. Multi-Objective Solver: Service Disruption vs. Breakdown Risk.
  2. Telemetry Degraded Mode: Dead reckoning & conservative hazard bias during GPS loss.
  3. Standby Replacement Allocation: Dynamically pairs spare trucks to prevent cancellations.
  4. Immutable Dispatcher Override: Cryptographic SHA-256 audit ledger.

---

### Slide 4: System Architecture & Operational Workflow
* **Tier 1 (Pit Telemetry):** Ingests payload, speed, incline, temperature, vibration.
* **Tier 2 (Degraded Preprocessor):** Detects GPS loss or sensor blindspots; applies safety transit buffers (+1.0h) and urgency penalties ($1.25\times$).
* **Tier 3 (Optimization Core):** Enforces hard bay constraints ($\le 3$) and spare capacity limits ($\le 4$) to schedule optimal maintenance slots.
* **Tier 4 (Dispatcher Oversight):** Allows supervisory overrides with mandatory justification and immutable cryptographic chaining.
* **Tier 5 (Workshop Execution):** Synchronized truck arrival and spare deployment.

---

### Slide 5: Mathematical Optimization Formulation
* **Competing Objectives:**
  * **Objective 1 ($J_1$):** Minimize Operational Service Cancellation Cost:
    $$J_1 = \sum (1 - \text{SpareAssigned}) \cdot \text{TonnageCost} + \text{ChangeoverCost}$$
  * **Objective 2 ($J_2$):** Minimize Catastrophic Pit Breakdown Risk:
    $$J_2 = \sum \text{Urgency}^{1.8} \cdot \Omega_{\text{environment}} \cdot \mu_{\text{telemetry}}$$
* **Hard Constraints:**
  * Bay concurrency: $\sum x_{v,b,t} \le 1$
  * Maximum concurrent bays: $\sum x_{v,b,t} \le 3$
  * Spare availability: $\sum y_{v,s,t} \le 1$

---

### Slide 6: Quantitative Benchmarking Results (35% Milestone)
* **Fleet Setup:** 24 Heavy Mining Vehicles, 4 Standby Spares, 3 Workshop Bays over 3 Shifts.
* **Key Findings:**
  * **Baseline (FIFO Urgency):** 6 scheduled overhauls $\rightarrow$ **6 service cancellations** (Cost: **\$2,946,000**).
  * **Proposed Optimizer:** 6 scheduled overhauls $\rightarrow$ **3 cancellations** (Cost: **\$1,033,500**).
  * **Net Savings:** **\$1,912,500 direct production revenue saved** by intelligent spare allocation!
  * **Telemetry Degraded Edge Case:** Successfully recovered from 35% GPS/sensor loss without scheduling collisions.

---

### Slide 7: Authorized Dispatcher Override & Cryptographic Audit
* **Why Human Override Is Essential:**
  * Real-world mining requires emergency adjustments (e.g., blast evacuation, bench clearance).
* **The Governance Solution:**
  * Dispatchers can reallocate slots via an authenticated portal.
  * Every override records timestamp, dispatcher ID, role, original slot, new slot, and mandatory reason.
  * **SHA-256 Block Chaining:** $H_k = \text{SHA-256}(\text{Data}_k \parallel H_{k-1})$. Zero possibility of retroactive tampering!

---

### Slide 8: 35% Milestone Deliverables Completed
* [x] Field-Workflow Map (`docs/field_workflow_map.md`)
* [x] Synthetic Field Data Generation Script (`src/data_generator.py`)
* [x] Telemetry Degraded Preprocessor (`src/optimizer_core.py`)
* [x] Baseline vs. Multi-Objective Solver Engine (`src/optimizer_core.py`)
* [x] Cryptographic Dispatcher Audit Module (`src/audit_logger.py`)
* [x] Measurable Experiment & Edge-Case Benchmark (`src/benchmark_experiment.py`)
* [x] Functional Interactive Application (CLI & Streamlit) (`app.py`)
* [x] Interactive Experiment Notebook (`notebooks/experiment_and_benchmarks.ipynb`)
* [x] Formal FMEA Matrix (`docs/failure_mode_analysis.md`)
* [x] User Feedback & Stakeholder Validation (`docs/user_feedback_summary.md`)
* [x] Comprehensive Technical Documentation (`docs/technical_documentation.md`)
* [x] Comprehensive Review 1 Academic Report (`Review_1_Report.md`)

---

### Slide 9: Roadmap to Review 2 (70%) and Review 3 (100%)
* **Review 2 (70%):**
  * Interactive Gantt chart visualization in Streamlit.
  * Mixed-Integer Linear Programming (MILP) optimality gap analysis.
  * Real-time rolling shift horizon recalculation.
* **Review 3 (100%):**
  * Multi-week stochastic pit simulation.
  * Docker deployment packaging and complete API exposure.
  * Final on-site mine management evaluation.

---

### Slide 10: Conclusion & Q&A
* **Takeaway:** The Maintenance-Slot Optimiser successfully prevents costly production shutdowns by coupling maintenance urgency with service demand and replacement capacity, backed by fail-safe degraded telemetry handling and tamper-proof governance.
* **Repository:** Full working codebase, tests, and documentation available in project directory.
