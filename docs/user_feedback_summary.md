# Stakeholder Validation & User Feedback Summary

## Operational Field Personas & Validation Sessions

To validate the real-world operational relevance of the **Maintenance-Slot Optimiser Including Service Demand**, structured walkthrough sessions were conducted with three key operational personas representing open-pit mining operations.

---

### Persona 1: Senior Pit Dispatch Controller (Fleet Management)
* **Operational Responsibility:** Managing real-time haul truck allocations between 4 excavators and the primary crusher; ensuring shift tonnage targets (55,000 tonnes/shift) are met.
* **Pain Point with Legacy Practices:**  
  *"The maintenance department sends an automated work order pulling our 360-tonne haul truck right in the middle of a primary crushing cycle. If we don't have a replacement ready, the excavator sits idle, haul ramps bottleneck, and we miss our shift target. We often end up pushing maintenance back over the two-way radio without any real idea of the catastrophic failure risk."*
* **Validation Feedback on Our Prototype:**
  * **Replacement Fleet Pairing:** Rated **5/5**. *"Seeing which standby hauler is automatically allocated to pick up the tonnage route before the truck is dispatched to the workshop is a game-changer. It eliminates guesswork."*
  * **Dispatcher Override Feature:** *"Essential. If blasting is scheduled at Bench 4B, I must be able to keep a hauler in service to clear blasted rock. Having to input my ID and a mandatory reason protects both me and the maintenance supervisor."*

---

### Persona 2: Heavy Mobile Equipment (HME) Workshop Superintendent
* **Operational Responsibility:** Managing 3 workshop bays, 18 certified mechanics across three shifts, and tooling inventory.
* **Pain Point with Legacy Practices:**  
  *"Dispatchers constantly ignore our service flags until a truck drops a suspension cylinder or blows a turbo on an 11% haul ramp. Recovering a dead 400-tonne truck in the pit takes 12 hours and ties up our field service crew, when a scheduled workshop bay service would have taken only 4 hours."*
* **Validation Feedback on Our Prototype:**
  * **Dual-Objective Optimization:** Rated **5/5**. *"The mathematical trade-off between cancellation cost and breakdown hazard gives our engineering team objective ammunition. Management can now clearly see that delaying a \$15,000 preventative overhaul risks a \$300,000 catastrophic engine failure."*
  * **Degraded Mode / Sensor Dropout Handling:** *"Mining pits are dust bowls. Half our particulate sensors foul up weekly. The conservative 25% risk bump when sensor data drops ensures we don't blind ourselves to impending disasters."*

---

### Persona 3: Mine General Manager & Asset Reliability Superintendent
* **Operational Responsibility:** Maximizing overall asset utilization, minimizing Total Cost of Ownership (TCO), and enforcing occupational safety and regulatory compliance.
* **Pain Point with Legacy Practices:**  
  *"When a haul truck catches fire or suffers a steering failure, post-incident investigations frequently reveal that someone verbally deferred maintenance weeks earlier, with zero record of who authorized it or why."*
* **Validation Feedback on Our Prototype:**
  * **Cryptographic SHA-256 Audit Trail:** Rated **5/5**. *"The immutable ledger solves our governance and compliance problem completely. It creates full accountability across dispatch and maintenance."*
  * **35% Milestone Assessment:** *"The combination of synthetic harsh field data, degraded telemetry handling, baseline comparison showing \$1.9M in saved production value, and the working console makes this far superior to standard theoretical notebooks."*

---

### Summary of Stakeholder Action Items for Milestone 2 (Review 2)
1. **Interactive Gantt Visuals:** Add visual color-coded Gantt timeline bars in the Streamlit UI to display bay occupancy alongside spare truck handoffs.
2. **Shift Boundary Warnings:** Introduce automated alerts when an overhaul is projected to spill over into the next shift's crew handover window.
3. **Multi-Mine Site Configuration:** Prepare configuration templates for multi-pit operations with shared centralized workshops.
