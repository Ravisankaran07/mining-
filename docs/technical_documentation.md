# Technical Documentation & Architecture Specification

## Project Title: Mining Operation Maintenance-Slot Optimiser Including Service Demand
**Milestone Version:** 1.0 (Review 1 — 35% Project Completion)  
**Programming Environment:** Python 3.13 (Numpy, Pandas, SciPy, Streamlit)  
**System Architecture:** Modular Microservice Architecture (Telemetry Preprocessing -> Optimization Solver -> Dispatch Control & Cryptographic Audit Ledger)

---

## 1. Directory Structure

```
d:/project/
├── Review_1_Report.md                 # Formal Review 1 Milestone Report
├── benchmark_results.json             # Experimental output data (Baseline vs Proposed)
├── dispatcher_override_audit.jsonl    # Cryptographically hash-chained override ledger
├── app.py                             # Functional application (Streamlit & CLI modes)
├── src/
│   ├── data_generator.py              # Harsh environment & fleet simulation engine
│   ├── optimizer_core.py              # Telemetry preprocessor, baseline & multi-objective solver
│   └── audit_logger.py                # SHA-256 tamper-proof dispatcher override logger
├── docs/
│   ├── field_workflow_map.md          # End-to-end field process sequence & Mermaid diagram
│   ├── failure_mode_analysis.md       # Full FMEA matrix & edge-case evaluations
│   ├── user_feedback_summary.md       # Stakeholder validation sessions & persona reviews
│   ├── technical_documentation.md     # System architecture, API specs & execution guide
│   └── presentation_review_1.md       # Slide deck presentation for Review 1
├── notebooks/
│   └── experiment_and_benchmarks.ipynb# Jupyter notebook demonstrating experiments
└── tests/
    └── test_optimizer.py              # Automated unit and integration test suite
```

---

## 2. API Specification & Core Classes

### 2.1 `TelemetryResilientPreprocessor` (`src/optimizer_core.py`)
Provides fail-safe telemetry ingestion when open-pit conditions degrade wireless transmission.

* **Method:** `process_vehicle_telemetry(v: Dict[str, Any]) -> Dict[str, Any]`
  * **Input:** Raw vehicle dictionary containing `telemetry_status` (`HEALTHY`, `GPS_LOST`, `NETWORK_INTERMITTENT`, `SENSOR_DROPOUT`), `urgency_score`, etc.
  * **Returns:** Processed vehicle dictionary with injected `location_confidence`, `transit_time_buffer_hours`, and `operational_risk_multiplier`.
  * **Logic:**
    * `GPS_LOST`: Injects `transit_time_buffer_hours = 1.0`, `operational_risk_multiplier = 1.15`.
    * `SENSOR_DROPOUT`: Applies conservative penalty $U_{\text{adj}} = \min(100.0, U \times 1.25)$, `operational_risk_multiplier = 1.30`.

### 2.2 `MultiObjectiveSlotOptimizer` (`src/optimizer_core.py`)
Computes Pareto-efficient maintenance schedules balancing production disruption against machine breakdown hazard.

* **Constructor:** `__init__(w_cancellation: float = 0.5, w_breakdown_risk: float = 0.5)`
  * **Parameters:** Weights satisfying $w_1 + w_2 = 1.0$.
* **Method:** `optimize(vehicles: List[Dict], spares: List[Dict], workshop: Dict, time_horizon_shifts: int = 3) -> Dict[str, Any]`
  * **Returns:** Dictionary containing scheduled slots, replacement assignments, avoided cancellations, and net financial impact.
  * **Constraints Enforced:**
    * Hard bay capacity limit ($\sum x_{v,b,t} \le 1$).
    * Hard spare vehicle fleet availability limit ($\sum y_{v,s,t} \le 1$).
    * Non-overlapping bay servicing.

### 2.3 `DispatcherAuditLogger` (`src/audit_logger.py`)
Implements an append-only JSONL cryptographic ledger for authorized supervisory overrides.

* **Method:** `record_dispatcher_override(...) -> Dict[str, Any]`
  * **Cryptographic Formula:**
    $$H_k = \text{SHA-256}\left(\text{JSON}(\text{Payload}_k) \parallel H_{k-1}\right)$$
* **Method:** `verify_audit_integrity() -> bool`
  * Recalculates the entire hash chain from the genesis block to detect any unauthorized data modifications.

---

## 3. How to Run & Verify the System

### 3.1 Running the Automated Test Suite
```powershell
$env:PYTHONPATH = "d:\project\src"
& "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" -m unittest "d:\project\tests\test_optimizer.py"
```

### 3.2 Running the Functional Application (CLI Mode)
```powershell
& "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" "d:\project\app.py" --cli
```

### 3.3 Launching the Interactive Web Dashboard (Streamlit)
```powershell
& "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" -m streamlit run "d:\project\app.py"
```

### 3.4 Running the Benchmark Experiments
```powershell
& "C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" "d:\project\src\benchmark_experiment.py"
```
