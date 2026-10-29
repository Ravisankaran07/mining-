# Failure Mode and Effects Analysis (FMEA)
## Heavy Mining Vehicle Maintenance-Slot Optimiser

This document establishes the formal FMEA for the Maintenance-Slot Optimiser deployed in open-pit mining operations under extreme environmental conditions (high dust, extreme temperatures, vibration, and steep grades).

---

## 1. FMEA Risk Evaluation Matrix

Severity ($S$), Occurrence ($O$), and Detection ($D$) are scored on a standard 1–10 industrial scale:
$$\text{Risk Priority Number (RPN)} = S \times O \times D$$

| Failure Mode ID | Operational Stage | Potential Failure Mode | Root Cause / Environmental Driver | Potential Effect on Mining Operations | $S$ | $O$ | $D$ | Initial RPN | Engineering Safeguard & Mitigation Strategy | Mitigated $S$ | Mitigated $O$ | Mitigated $D$ | Final RPN |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **FMEA-01** | Telemetry Ingestion | **GPS Signal Loss in Deep Pit Benches** | Deep open-pit rim shielding, steep bench slopes, multipath satellite interference. | Optimizer miscalculates vehicle transit time; workshop bay sits idle or becomes double-booked. | 7 | 6 | 7 | **294** | **Dead-Reckoning & Sector Buffering:** Ingests last known pit sector gate timestamp and injects a 1.0-hour transit safety buffer. | 4 | 2 | 2 | **16** |
| **FMEA-02** | Telemetry Ingestion | **Sensor Dropout & Blindspot (Heat/Dust)** | Engine bay temperature $>48^\circ\text{C}$, dust particulate clogging sensor intake filters. | Equipment with impending component failure appears healthy; maintenance is deferred. | 9 | 5 | 8 | **360** | **Conservative Risk Inflation ($\mu = 1.25$):** Automatically escalates urgency score by 25% upon lost sensor heartbeat to force precautionary workshop inspection. | 5 | 2 | 2 | **20** |
| **FMEA-03** | Replacement Fleet Allocation | **Standby Replacement Capacity Exhaustion** | Heavy haulage surge coinciding with simultaneous maintenance cycles ($N_{\text{down}} > N_{\text{spares}}$). | Unmitigated haul route cancellation; severe tonnage deficit and crusher starvation. | 8 | 5 | 4 | **160** | **Tonnage-Demand Prioritization:** Optimizer matches available spares strictly to highest-tonnage route haulers ($360\text{t}$ CAT 797F before smaller haulers). | 5 | 3 | 2 | **30** |
| **FMEA-04** | Workshop Bay Scheduling | **Bay Saturation / Over-Demand Surge** | Sudden shift-wide component alerts caused by dust storm. | Workshop bays overwhelmed; physical traffic congestion on workshop aprons. | 8 | 4 | 3 | **96** | **Hard Constraint Enforcement ($\sum x_{v,b,t} \le M$):** Physical concurrency capped at 3 bays; excess demand queued strictly by risk score. | 4 | 2 | 2 | **16** |
| **FMEA-05** | Supervisory Control | **Unauthorized Maintenance Deferral (Ghost Overrides)** | Dispatcher skips maintenance informally via radio to chase short-term tonnage quotas. | Catastrophic in-pit failure (engine seizure, wheel motor fire) blocking haul ramps. | 9 | 6 | 6 | **324** | **Cryptographic Audit Ledger:** Enforces mandatory supervisor credentials, reason recording, and SHA-256 tamper-proof hash chaining. | 4 | 1 | 1 | **4** |
| **FMEA-06** | System Computation | **Algorithmic Deadlock / Infeasible Solution** | Incompatible vehicle models and empty spare pool with zero available bays. | System freezes, falling back to manual whiteboard scheduling. | 8 | 3 | 5 | **120** | **Soft-Constraint Relaxation & Fallback Heuristic:** Graceful degradation permitting penalized overtime shift servicing. | 3 | 1 | 2 | **6** |

---

## 2. Deep Dive: Analysis of Tested Edge Cases

### Edge Case 1: 35% Fleet Telemetry Loss (Severe Dust Storm)
* **Trigger:** PM10 particulate levels surge to $>850\,\mu\text{g/m}^3$; LTE private radio drops packets across 8 of 24 vehicles.
* **Observed System Reaction:** The `TelemetryResilientPreprocessor` identified all 8 affected vehicles. Dead reckoning was engaged for 4 vehicles with lost GPS, extending transit buffers by 1.0 hour. The remaining 4 vehicles with dropped sensor packets received a 1.25× risk penalty.
* **Outcome:** No scheduling collisions; workshop bays maintained orderly queuing without idle gaps.

### Edge Case 2: Zero Spare Vehicles Available (Fleet Starvation)
* **Trigger:** Standby fleet pool reduced from 4 to 0 (all spares undergoing depot engine overhauls).
* **Observed System Reaction:** The optimizer recognized that $y_{v,s,t} = 0$ for all $s \in S$. Rather than aborting, the algorithm prioritized workshop slots for trucks whose breakdown hazard cost exceeded the unmitigated cancellation penalty ($J_2 > J_1$).
* **Outcome:** System executed gracefully, delivering a deterministic schedule with transparent reporting of unavoided cancellation costs.

### Edge Case 3: 15-Truck Critical Urgency Surge (Workshop Saturation)
* **Trigger:** 15 haul trucks concurrently reach critical urgency scores ($U_v > 90.0$).
* **Observed System Reaction:** Since workshop capacity is strictly constrained to 3 bays over 3 shifts (maximum 9 theoretical slots), the optimizer rejected 6 overhauls, scheduling exactly 6 highest-urgency jobs and alerting the mine superintendent of residual deferred risk.
* **Outcome:** Physical bay capacity invariants were 100% preserved; zero apron overcrowding.
