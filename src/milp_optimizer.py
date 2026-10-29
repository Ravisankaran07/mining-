"""
Exact Mixed-Integer Linear Programming (MILP) Maintenance-Slot Optimizer.
Solves the global optimal assignment of heavy mining vehicles to workshop bays
and replacement-vehicle capacity over multi-shift planning horizons.
Uses scipy.optimize.milp with exact binary constraint matrix formulation.
"""

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from typing import Dict, List, Any, Tuple

class ExactMILPSlotOptimizer:
    """
    Exact Mathematical Optimizer for Mining Fleet Maintenance Slots.
    Formulates the problem as a 0-1 Mixed-Integer Linear Program.
    """
    def __init__(self, w_cancellation: float = 0.5, w_breakdown_risk: float = 0.5):
        self.w1 = w_cancellation
        self.w2 = w_breakdown_risk

    def solve(
        self,
        vehicles: List[Dict[str, Any]],
        spares: List[Dict[str, Any]],
        workshop: Dict[str, Any],
        num_shifts: int = 3
    ) -> Dict[str, Any]:
        """
        Solves the exact MILP optimization problem.
        Decision variables:
          - x[v, b, t]: binary, 1 if vehicle v is assigned to bay b during shift t
          - y[v, s, t]: binary, 1 if spare s replaces vehicle v during shift t
          - z[v]: binary, 1 if vehicle v is deferred (not serviced across all shifts)
        """
        nV = len(vehicles)
        nB = workshop["num_bays"]
        nT = num_shifts
        nS = len(spares)

        # Index offsets for flat variable vector
        # Total variables:
        # x: nV * nB * nT
        # y: nV * nS * nT
        # z: nV
        num_x = nV * nB * nT
        num_y = nV * nS * nT
        num_z = nV
        total_vars = num_x + num_y + num_z

        def idx_x(v, b, t):
            return v * (nB * nT) + b * nT + t

        def idx_y(v, s, t):
            return num_x + v * (nS * nT) + s * nT + t

        def idx_z(v):
            return num_x + num_y + v

        # Objective Function Coefficients: c^T * [x, y, z]
        c = np.zeros(total_vars)

        # Objective 1: Operational Disruption / Service Cancellation Cost
        # If x[v, b, t] is active and NOT replaced, cost is C_v^canc.
        # If replaced by y[v, s, t], cost is reduced to C_changeover ($3,500).
        for v_i, v in enumerate(vehicles):
            canc_cost = v["cancellation_cost_per_shift"]
            changeover_cost = 3500.0
            for t in range(nT):
                for b in range(nB):
                    # Base cost for scheduling maintenance without spare
                    c[idx_x(v_i, b, t)] += self.w1 * (canc_cost / 1000.0)
                for s in range(nS):
                    # Spare replacement reduces cost by (canc_cost - changeover_cost)
                    saving = canc_cost - changeover_cost
                    c[idx_y(v_i, s, t)] -= self.w1 * (saving / 1000.0)

        # Objective 2: Cumulative Machine Breakdown Hazard Cost
        # If vehicle is deferred (z[v] = 1), penalty proportional to urgency^1.8
        for v_i, v in enumerate(vehicles):
            urgency = v["urgency_score"]
            risk_mult = v.get("operational_risk_multiplier", 1.0)
            hazard_penalty = ((urgency ** 1.8) * 250.0 * risk_mult) / 1000.0
            c[idx_z(v_i)] += self.w2 * hazard_penalty

        # Constraints
        # 1. Bay Capacity: For each bay b and shift t, at most 1 vehicle: sum_v x[v, b, t] <= 1
        # 2. Single Service: Each vehicle serviced at most once: sum_b sum_t x[v, b, t] <= 1
        # 3. Spare Availability: Each spare s used at most once per shift t: sum_v y[v, s, t] <= 1
        # 4. Replacement Linking: Spare only active if vehicle is being serviced:
        #    y[v, s, t] <= sum_b x[v, b, t]  ==>  y[v, s, t] - sum_b x[v, b, t] <= 0
        # 5. Deferral Linking: If vehicle is not serviced in any bay/shift, z[v] = 1:
        #    z[v] + sum_b sum_t x[v, b, t] >= 1

        rows = []
        lhs = []
        rhs = []

        # Constraint 1: Bay capacity per shift
        for b in range(nB):
            for t in range(nT):
                row = np.zeros(total_vars)
                for v in range(nV):
                    row[idx_x(v, b, t)] = 1.0
                rows.append(row)
                lhs.append(0.0)
                rhs.append(1.0)

        # Constraint 2: Vehicle at most one service slot
        for v in range(nV):
            row = np.zeros(total_vars)
            for b in range(nB):
                for t in range(nT):
                    row[idx_x(v, b, t)] = 1.0
            rows.append(row)
            lhs.append(0.0)
            rhs.append(1.0)

        # Constraint 3: Spare fleet capacity per shift
        for s in range(nS):
            for t in range(nT):
                row = np.zeros(total_vars)
                for v in range(nV):
                    row[idx_y(v, s, t)] = 1.0
                rows.append(row)
                lhs.append(0.0)
                rhs.append(1.0)

        # Constraint 4: Spare can only cover actively serviced vehicle
        for v in range(nV):
            for s in range(nS):
                for t in range(nT):
                    row = np.zeros(total_vars)
                    row[idx_y(v, s, t)] = 1.0
                    for b in range(nB):
                        row[idx_x(v, b, t)] -= 1.0
                    rows.append(row)
                    lhs.append(-np.inf)
                    rhs.append(0.0)

        # Constraint 5: Deferral linking
        for v in range(nV):
            row = np.zeros(total_vars)
            row[idx_z(v)] = 1.0
            for b in range(nB):
                for t in range(nT):
                    row[idx_x(v, b, t)] = 1.0
            rows.append(row)
            lhs.append(1.0)
            rhs.append(1.0)

        A = np.array(rows)
        constraints = LinearConstraint(A, lhs, rhs)
        integrality = np.ones(total_vars) # All variables are binary integers
        bounds = Bounds(np.zeros(total_vars), np.ones(total_vars))

        # Solve MILP
        res = milp(c=c, integrality=integrality, constraints=constraints, bounds=bounds)

        scheduled_slots = []
        cancellations_avoided = 0
        actual_cancellations = 0
        total_canc_cost = 0.0
        total_risk_cost = 0.0

        if res.success:
            sol = np.round(res.x)
            for v_i, v in enumerate(vehicles):
                # Check if scheduled
                serviced = False
                for b in range(nB):
                    for t in range(nT):
                        if sol[idx_x(v_i, b, t)] == 1:
                            serviced = True
                            # Check if spare assigned
                            spare_id = None
                            for s in range(nS):
                                if sol[idx_y(v_i, s, t)] == 1:
                                    spare_id = spares[s]["spare_id"]
                                    cancellations_avoided += 1
                                    break
                            
                            if spare_id:
                                financial_impact = 3500.0
                                is_canc = False
                            else:
                                financial_impact = v["cancellation_cost_per_shift"]
                                is_canc = True
                                actual_cancellations += 1
                                
                            total_canc_cost += financial_impact
                            scheduled_slots.append({
                                "vehicle_id": v["vehicle_id"],
                                "model": v["model"],
                                "bay": f"BAY-{b+1:02d}",
                                "shift": f"SHIFT-{t+1:02d}",
                                "start_hour": t * 8.0,
                                "end_hour": (t + 1) * 8.0,
                                "duration_hours": 8.0,
                                "urgency_score": v["urgency_score"],
                                "telemetry_status": v["telemetry_status"],
                                "replacement_assigned": spare_id,
                                "service_cancelled": is_canc,
                                "financial_impact_usd": round(financial_impact, 2)
                            })
                            
                if not serviced:
                    risk_cost = (v["urgency_score"] ** 1.8) * 250.0 * v.get("operational_risk_multiplier", 1.0)
                    total_risk_cost += risk_cost

            status = "OPTIMAL_SOLVED"
            opt_val = res.fun * 1000.0
        else:
            status = "FALLBACK_FAILED"
            opt_val = 0.0

        return {
            "solver_type": "EXACT_MILP_GLOBAL_OPTIMUM",
            "status": status,
            "success": bool(res.success),
            "scheduled_maintenance_count": len(scheduled_slots),
            "unserviced_count": nV - len(scheduled_slots),
            "cancellations_avoided_by_spares": cancellations_avoided,
            "actual_service_cancellations": actual_cancellations,
            "total_cancellation_cost_usd": round(total_canc_cost, 2),
            "total_breakdown_risk_cost_usd": round(total_risk_cost, 2),
            "total_combined_cost_usd": round(total_canc_cost + total_risk_cost, 2),
            "scheduled_slots": scheduled_slots
        }
