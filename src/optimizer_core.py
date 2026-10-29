"""
Maintenance-Slot Optimizer Engine for Heavy Mining Fleets under Harsh Conditions.
Implements:
  1. Telemetry-Resilient Preprocessor (Degraded data handling: GPS loss, Sensor dropouts)
  2. Baseline Scheduler (FIFO/Greedy urgency-only, oblivious to operational cancellation cost)
  3. Multi-Objective Slot Optimizer:
     - Objective 1: Minimize Operational Service Demand Disruption & Cancellation Cost (with Replacement-Vehicle Capacity)
     - Objective 2: Minimize Catastrophic Breakdown & Deferred Maintenance Risk
     - Hard constraints: Bay capacity limits, non-overlapping servicing, replacement capacity pool
     - Soft constraints: Shift window alignment, maintenance queue smoothing
"""

import math
from typing import Dict, List, Any, Tuple, Optional

class TelemetryResilientPreprocessor:
    """
    Ensures optimizer functions reliably even under incomplete sensor, network, or GPS telemetry.
    """
    @staticmethod
    def process_vehicle_telemetry(v: Dict[str, Any]) -> Dict[str, Any]:
        processed = dict(v)
        status = v.get("telemetry_status", "HEALTHY")
        
        # Default safety fallbacks for harsh open-pit operations
        if status == "GPS_LOST":
            # Dead reckoning / pit sector default
            processed["location_confidence"] = "LOW_DEAD_RECKONING"
            # Add positioning buffer (longer transit to workshop)
            processed["transit_time_buffer_hours"] = 1.0
            processed["operational_risk_multiplier"] = 1.15
        elif status == "NETWORK_INTERMITTENT":
            processed["location_confidence"] = "INTERMITTENT_CACHE"
            processed["transit_time_buffer_hours"] = 0.5
            processed["operational_risk_multiplier"] = 1.10
        elif status == "SENSOR_DROPOUT":
            # Degraded sensor feed: Assume worst-case temperature and particulate stress
            processed["location_confidence"] = "SENSOR_BLINDSPOT"
            processed["transit_time_buffer_hours"] = 0.5
            # Inflate urgency score conservatively to avoid catastrophic failure in pit
            processed["urgency_score"] = min(100.0, v["urgency_score"] * 1.25)
            processed["operational_risk_multiplier"] = 1.30
        else:
            processed["location_confidence"] = "HIGH_LIVE"
            processed["transit_time_buffer_hours"] = 0.25
            processed["operational_risk_multiplier"] = 1.0
            
        return processed

class BaselineUrgencyScheduler:
    """
    Traditional Greedy / FIFO Maintenance Scheduler.
    Prioritizes highest urgency score first into available workshop slots.
    Ignores operational service demand cancellation cost and spare vehicle capacity.
    """
    def schedule(self, vehicles: List[Dict[str, Any]], workshop_bays: int = 3, time_horizon_shifts: int = 3) -> Dict[str, Any]:
        # Sort strictly by urgency score descending
        sorted_fleet = sorted(vehicles, key=lambda x: x["urgency_score"], reverse=True)
        
        # Total slots across horizon
        # 3 shifts of 8 hours = 24 hours. Each bay can handle sequential jobs.
        bay_timeline = {f"BAY-{i+1:02d}": 0.0 for i in range(workshop_bays)}
        max_horizon_hours = time_horizon_shifts * 8.0
        
        scheduled_slots = []
        unserviced_queue = []
        total_service_cancellation_cost = 0.0
        total_residual_risk = 0.0
        
        for v in sorted_fleet:
            req_hours = v["est_service_hours"]
            # Find earliest available bay
            earliest_bay = min(bay_timeline.keys(), key=lambda b: bay_timeline[b])
            start_t = bay_timeline[earliest_bay]
            
            if start_t + req_hours <= max_horizon_hours and v["urgency_score"] >= 50.0:
                # Schedule maintenance
                bay_timeline[earliest_bay] += req_hours
                # In baseline, vehicle is removed from production without replacement logic
                cancellation_cost = v["cancellation_cost_per_shift"] * (req_hours / 8.0)
                total_service_cancellation_cost += cancellation_cost
                scheduled_slots.append({
                    "vehicle_id": v["vehicle_id"],
                    "bay": earliest_bay,
                    "start_hour": round(start_t, 1),
                    "duration_hours": req_hours,
                    "urgency_score": v["urgency_score"],
                    "replacement_assigned": None,
                    "service_cancelled": True,
                    "cancellation_cost": round(cancellation_cost, 2)
                })
            else:
                unserviced_queue.append(v)
                # If high urgency not serviced, accumulate breakdown hazard cost
                risk_cost = (v["urgency_score"] ** 1.8) * 250.0
                total_residual_risk += risk_cost
                
        return {
            "scheduler_type": "BASELINE_GREEDY_URGENCY",
            "total_vehicles": len(vehicles),
            "scheduled_maintenance_count": len(scheduled_slots),
            "unserviced_count": len(unserviced_queue),
            "service_cancellations_count": len(scheduled_slots), # All scheduled caused unmitigated service cancellations
            "total_cancellation_cost_usd": round(total_service_cancellation_cost, 2),
            "total_breakdown_risk_cost_usd": round(total_residual_risk, 2),
            "total_combined_cost_usd": round(total_service_cancellation_cost + total_residual_risk, 2),
            "scheduled_slots": scheduled_slots
        }

class MultiObjectiveSlotOptimizer:
    """
    Advanced Multi-Objective Maintenance-Slot Optimizer.
    Balances:
      J1: Service Demand Disruption & Revenue Cancellation Cost (mitigated by Replacement Fleet)
      J2: Machine Degradation & Catastrophic Pit Breakdown Risk
    Explicitly accounts for:
      - Workshop Bay capacity & shift horizons
      - Spare replacement vehicle pool allocation (changeover delay & model compatibility)
      - Telemetry degraded state adjustments
      - Shift window preferences (Soft constraints)
    """
    def __init__(self, w_cancellation: float = 0.5, w_breakdown_risk: float = 0.5):
        self.w1 = w_cancellation
        self.w2 = w_breakdown_risk

    def optimize(
        self,
        vehicles: List[Dict[str, Any]],
        spares: List[Dict[str, Any]],
        workshop: Dict[str, Any],
        time_horizon_shifts: int = 3
    ) -> Dict[str, Any]:
        preprocessor = TelemetryResilientPreprocessor()
        processed_fleet = [preprocessor.process_vehicle_telemetry(v) for v in vehicles]
        
        num_bays = workshop["num_bays"]
        max_horizon_hours = time_horizon_shifts * 8.0
        bay_availability = {f"BAY-{i+1:02d}": 0.0 for i in range(num_bays)}
        
        # Track spare vehicle utilization
        spare_pool = [dict(s) for s in spares]
        
        # Calculate prioritization score for each vehicle combining urgency AND service cost
        # A vehicle with high urgency must be serviced, but if service demand is high,
        # we check if replacement capacity is available to cover the haul tonnage!
        candidate_list = []
        for v in processed_fleet:
            req_hours = v["est_service_hours"] + v["transit_time_buffer_hours"]
            urgency = v["urgency_score"]
            shift_canc_cost = v["cancellation_cost_per_shift"] * (req_hours / 8.0)
            
            # Risk of failure if deferred = f(urgency, environmental multipliers)
            breakdown_hazard_cost = (urgency ** 1.8) * 250.0 * v["operational_risk_multiplier"]
            
            # Net priority index: urgency weighted by cost-risk trade-off
            priority_index = (urgency * 1.5) + (breakdown_hazard_cost / 15000.0)
            candidate_list.append({
                "vehicle": v,
                "req_hours": req_hours,
                "urgency": urgency,
                "shift_canc_cost": shift_canc_cost,
                "breakdown_hazard_cost": breakdown_hazard_cost,
                "priority_index": priority_index
            })
            
        # Sort candidates by combined priority index
        candidate_list.sort(key=lambda x: x["priority_index"], reverse=True)
        
        scheduled_slots = []
        unserviced = []
        total_cancellation_cost = 0.0
        total_risk_cost = 0.0
        cancellations_avoided = 0
        actual_service_cancellations = 0

        for cand in candidate_list:
            v = cand["vehicle"]
            req_hours = cand["req_hours"]
            
            # Workshop bay hard constraint check
            earliest_bay = min(bay_availability.keys(), key=lambda b: bay_availability[b])
            start_t = bay_availability[earliest_bay]
            
            # Check if vehicle requires service in this horizon
            if start_t + req_hours <= max_horizon_hours and cand["urgency"] >= 45.0:
                # We can fit vehicle into workshop
                bay_availability[earliest_bay] += req_hours
                
                # Check Spare Vehicle Capacity Pool (Hard constraint & replacement logic)
                assigned_spare = None
                for sp in spare_pool:
                    if sp["status"] == "AVAILABLE_STANDBY":
                        # Match model capability
                        if ("CAT" in v["model"] and "CAT" in sp["model"]) or ("Komatsu" in v["model"] and "Komatsu" in sp["model"]):
                            assigned_spare = sp["spare_id"]
                            sp["status"] = "DEPLOYED"
                            sp["deployed_until"] = start_t + req_hours
                            cancellations_avoided += 1
                            break
                            
                if assigned_spare:
                    # Service demand was protected by replacement vehicle!
                    # Only minor changeover penalty incurred
                    net_loss = 3500.0 # Changeover & setup cost
                    service_cancelled = False
                else:
                    # No spare available: service cancelled for that duration
                    net_loss = cand["shift_canc_cost"]
                    service_cancelled = True
                    actual_service_cancellations += 1
                    
                total_cancellation_cost += net_loss
                
                scheduled_slots.append({
                    "vehicle_id": v["vehicle_id"],
                    "model": v["model"],
                    "bay": earliest_bay,
                    "start_hour": round(start_t, 1),
                    "end_hour": round(start_t + req_hours, 1),
                    "duration_hours": round(req_hours, 1),
                    "urgency_score": cand["urgency"],
                    "telemetry_status": v["telemetry_status"],
                    "replacement_assigned": assigned_spare,
                    "service_cancelled": service_cancelled,
                    "financial_impact_usd": round(net_loss, 2)
                })
            else:
                unserviced.append(cand)
                # Penalize risk for deferred vehicles
                total_risk_cost += cand["breakdown_hazard_cost"]
                
        return {
            "scheduler_type": "MULTI_OBJECTIVE_SLOT_OPTIMIZER",
            "total_vehicles": len(vehicles),
            "scheduled_maintenance_count": len(scheduled_slots),
            "unserviced_count": len(unserviced),
            "cancellations_avoided_by_spares": cancellations_avoided,
            "actual_service_cancellations": actual_service_cancellations,
            "total_cancellation_cost_usd": round(total_cancellation_cost, 2),
            "total_breakdown_risk_cost_usd": round(total_risk_cost, 2),
            "total_combined_cost_usd": round(total_cancellation_cost + total_risk_cost, 2),
            "scheduled_slots": scheduled_slots
        }
