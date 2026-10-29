"""
Data Generator for Heavy Mining Vehicle Fleet under Harsh Operating Conditions.
Simulates haul trucks (e.g. CAT 797F, Komatsu 930E) and excavators in open-pit mines.
Generates:
  - Vehicle fleet states (hours, component degradation, harshness exposure)
  - Shift service demand (tonnage haul schedules)
  - Replacement vehicle pool
  - Workshop bay capacity
  - Degraded telemetry flags (GPS lost, packet dropouts, stale sensor data)
"""

import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Fix seed for reproducibility
np.random.seed(42)
random.seed(42)

FLEET_TYPES = ["CAT_797F_HaulTruck", "Komatsu_930E_HaulTruck", "Hitachi_EX5600_Excavator"]
HARSH_SECTORS = ["Sector_A_HighDust_DeepPit", "Sector_B_SteepIncline_HighStress", "Sector_C_ExtremeThermal"]

def generate_mining_fleet(num_vehicles: int = 24, num_spares: int = 4) -> Dict[str, Any]:
    vehicles = []
    
    # Active fleet
    for i in range(1, num_vehicles + 1):
        v_type = FLEET_TYPES[i % len(FLEET_TYPES)]
        operating_hours = int(np.random.normal(4200, 800))
        hours_since_service = int(np.random.uniform(180, 520)) # nominal service interval is ~250-300h
        
        # Harsh environmental stress factors (0.8 to 2.0 multiplier)
        ambient_temp_c = float(np.random.uniform(38.0, 49.5))
        dust_particulate_pm10 = float(np.random.uniform(180.0, 650.0)) # ug/m3
        haul_road_grade_pct = float(np.random.uniform(8.0, 14.5))
        vibration_index = float(np.random.uniform(1.1, 2.5))
        
        # Telemetry health simulation (GPS dropout, network blackout, missing sensor stream)
        telemetry_status = "HEALTHY"
        rand_t = random.random()
        if rand_t < 0.15:
            telemetry_status = "GPS_LOST"
        elif rand_t < 0.25:
            telemetry_status = "NETWORK_INTERMITTENT"
        elif rand_t < 0.32:
            telemetry_status = "SENSOR_DROPOUT"
            
        # Nominal service demand (tonnage per 8h shift)
        if "HaulTruck" in v_type:
            nominal_payload_tons = 360 if "CAT" in v_type else 300
            hourly_target_trips = 2.5
            shift_demand_tons = nominal_payload_tons * hourly_target_trips * 8 # tons per shift
            cancellation_cost_per_shift = shift_demand_tons * 45.0 # $45/ton margin loss
        else: # Excavator
            shift_demand_tons = 9500
            cancellation_cost_per_shift = shift_demand_tons * 38.0
            
        # Estimated urgency score (0-100) based on hours & harsh conditions
        harshness_weight = (ambient_temp_c / 40.0) * (dust_particulate_pm10 / 300.0) * (vibration_index / 1.5)
        raw_urgency = (hours_since_service / 300.0) * 50.0 * harshness_weight
        urgency_score = min(100.0, max(5.0, raw_urgency))
        
        # Required service duration in hours
        est_service_hours = 4 if urgency_score < 60 else (8 if urgency_score < 85 else 12)
        
        vehicles.append({
            "vehicle_id": f"VEH-{i:03d}",
            "model": v_type,
            "role": "ACTIVE_PRODUCTION",
            "operating_hours": operating_hours,
            "hours_since_service": hours_since_service,
            "telemetry_status": telemetry_status,
            "last_known_pit_sector": random.choice(HARSH_SECTORS),
            "ambient_temp_c": round(ambient_temp_c, 1),
            "dust_pm10": round(dust_particulate_pm10, 1),
            "vibration_index": round(vibration_index, 2),
            "urgency_score": round(urgency_score, 1),
            "shift_demand_tons": round(shift_demand_tons, 0),
            "cancellation_cost_per_shift": round(cancellation_cost_per_shift, 2),
            "est_service_hours": est_service_hours
        })
        
    # Spare vehicle pool (ready replacement fleet)
    spares = []
    for s in range(1, num_spares + 1):
        spares.append({
            "spare_id": f"SPARE-{s:02d}",
            "model": "CAT_797F_HaulTruck" if s % 2 == 1 else "Komatsu_930E_HaulTruck",
            "status": "AVAILABLE_STANDBY",
            "capacity_tons": 360 if s % 2 == 1 else 300,
            "changeover_delay_hours": 1.5 # time to reposition and deploy operator
        })
        
    # Workshop configuration
    workshop = {
        "num_bays": 3,
        "shift_hours_per_day": 24,
        "certified_technicians_per_shift": 6,
        "max_concurrent_heavy_services": 3,
        "bays": [
            {"bay_id": "BAY-01", "type": "HEAVY_MECHANICAL", "status": "AVAILABLE"},
            {"bay_id": "BAY-02", "type": "HYDRAULIC_STRUCTURAL", "status": "AVAILABLE"},
            {"bay_id": "BAY-03", "type": "GENERAL_PREVENTATIVE", "status": "AVAILABLE"}
        ]
    }
    
    return {
        "fleet": vehicles,
        "spares": spares,
        "workshop": workshop
    }

if __name__ == "__main__":
    data = generate_mining_fleet()
    df = pd.DataFrame(data["fleet"])
    print(f"Generated {len(df)} vehicles. Summary of Telemetry Status:")
    print(df["telemetry_status"].value_counts())
    print("\nFleet sample:")
    print(df[["vehicle_id", "model", "urgency_score", "telemetry_status", "cancellation_cost_per_shift"]].head(6))
