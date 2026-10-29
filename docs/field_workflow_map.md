# End-to-End Field Workflow Map & Architecture

## Heavy Mining Fleet Maintenance-Slot Optimisation under Harsh Conditions

```mermaid
flowchart TD
    subgraph MiningPit["Open-Pit Mine Operations (Harsh Environment)"]
        HT["Haul Trucks (CAT 797F / Komatsu 930E)<br/>High Dust, Extreme Temps, Steep Grade"]
        EX["Hydraulic Excavators (Hitachi EX5600)"]
        PitDispatch["Pit Dispatch Controller / Fleet Management System (FMS)"]
        HT -->|Haul Tonnage Cycles| PitDispatch
        EX -->|Ore Loading Schedules| PitDispatch
    end

    subgraph TelemetryLayer["Telemetry & Ingestion Layer"]
        Sensors["Onboard Sensors (Engine Temp, Vibration, Oil Pressure)"]
        GPS["GPS Position & Grade Tracking"]
        Network["Private LTE / Mesh Radio"]
        Sensors --> Network
        GPS --> Network
        Network -->|Real-time Packet Stream| DegradedHandler
        
        subgraph DegradedHandler["Degraded Mode Preprocessor"]
            D1{"Telemetry Drop?"}
            D1 -- Yes: GPS Lost --> DeadReck["Dead Reckoning & Sector Buffer (+1.0h transit)"]
            D1 -- Yes: Sensor Drop --> ConsRisk["Conservative Risk Inflation (Urgency x 1.25)"]
            D1 -- No: Healthy --> RawNorm["Pass Clean Telemetry"]
        end
    end

    subgraph OptimEngine["Maintenance-Slot Optimizer Engine"]
        MultiObj["Multi-Objective Optimization Formulation<br/>Min J = w1 * J_cancellation + w2 * J_breakdown"]
        HardCons["Hard Constraints:<br/>- Workshop Bay Concurrency <= 3<br/>- No Overlapping Vehicle Servicing<br/>- Spare Fleet Allocation Limits"]
        SoftCons["Soft Constraints:<br/>- Shift Change Alignment (06:00/18:00)<br/>- High-Risk Queue Buffer"]
        
        DegradedHandler --> MultiObj
        HardCons --> MultiObj
        SoftCons --> MultiObj
    end

    subgraph CapacityResources["Resource & Capacity Feeds"]
        WorkshopBays["Workshop Capacity (3 Heavy Bays, Certified Techs)"]
        SparePool["Standby Replacement Fleet (CAT/Komatsu Pool)"]
        DemandSchedules["Tonnage Haul Quotas & Blasting Schedules"]
        WorkshopBays --> MultiObj
        SparePool --> MultiObj
        DemandSchedules --> MultiObj
    end

    subgraph DecisionExecution["Execution & Control Loop"]
        OptPlan["Generated Optimal Maintenance Plan<br/>(Slots, Bays, Replacement Matchings)"]
        MultiObj --> OptPlan
        
        DispReview{"Dispatcher Intervention Required?"}
        OptPlan --> DispReview
        
        DispReview -- No --> AutoDispatch["Auto-Dispatch to Workshop & Deploy Replacement"]
        DispReview -- Yes: Critical Blast/Grade Override --> ManOverride["Authorized Dispatcher Override<br/>(Cryptographic Reason & Identity Logging)"]
        
        ManOverride --> AuditLog["Immutable Audit Trail Ledger (SHA-256 Chained)"]
        ManOverride --> AutoDispatch
    end

    subgraph WorkshopFloor["Maintenance Workshop Execution"]
        Bay1["Bay 01: Heavy Mechanical"]
        Bay2["Bay 02: Hydraulic & Structural"]
        Bay3["Bay 03: General Preventative"]
        AutoDispatch --> Bay1
        AutoDispatch --> Bay2
        AutoDispatch --> Bay3
        Bay1 & Bay2 & Bay3 -->|Service Complete Telemetry| PitDispatch
    end
```

## Detailed Field Workflow Stages

### Stage 1: Mine Pit Operation & Harsh Environmental Stress Monitoring
- Heavy vehicles operate under sustained harsh conditions: ambient temperatures reaching 49°C, dust particulate concentration $>600\,\mu\text{g/m}^3$, haul road inclines up to $14\%$, and heavy vibration.
- Traditional systems monitor only component operating hours. Our workflow ingests real-time stress telemetry to dynamically compute urgency scores.

### Stage 2: Telemetry Ingestion & Degraded State Resilience
- Heavy mining pits suffer frequent wireless blackouts, deep pit shading (GPS loss), and dust-fouled sensor dropouts.
- When GPS is lost, the preprocessor triggers **Dead Reckoning & Sector Defaulting**, adding safety transit buffers.
- When sensor telemetry drops, a **Conservative Risk Multiplier (1.25×)** is applied to avoid catastrophic failure in the haul cycle.

### Stage 3: Multi-Objective Slot Optimization
- Concurrently evaluates:
  1. **Operational Cancellation Impact ($J_1$)**: Cost of taking high-payload trucks out of production during critical haulage cycles, mitigated by dynamically dispatching standby replacement vehicles.
  2. **Catastrophic Breakdown Risk ($J_2$)**: Exponential risk cost of operating deteriorated equipment in high-stress pit zones.
- Enforces strict hard constraints on physical bay capacity and crew availability while honoring soft shift preferences.

### Stage 4: Dispatcher Override & Immutable Audit Governance
- Mining superintendents retain the authority to override automated slotting (e.g., deferring service during mandatory blast clearance).
- All overrides require formal credentials and operational justifications, recorded in a tamper-proof SHA-256 chained audit ledger.
