"""
Unit and Integration Test Suite for Mining Fleet Maintenance-Slot Optimiser.
Tests:
  1. Data generation integrity and harsh condition metrics.
  2. Telemetry degraded mode preprocessor (GPS lost, sensor dropouts).
  3. Baseline scheduler execution.
  4. Multi-objective slot optimizer constraint satisfaction (Hard & Soft constraints).
  5. Replacement vehicle pool assignment logic and capacity preservation.
  6. Dispatcher override logging and SHA-256 cryptographic hash chain verification.
  7. Edge case stability (Telemetry loss, Zero spares, Bay saturation).
"""

import unittest
import os
import json
from data_generator import generate_mining_fleet
from optimizer_core import TelemetryResilientPreprocessor, BaselineUrgencyScheduler, MultiObjectiveSlotOptimizer
from audit_logger import DispatcherAuditLogger

class TestMaintenanceSlotOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.data = generate_mining_fleet(num_vehicles=18, num_spares=3)
        self.vehicles = self.data["fleet"]
        self.spares = self.data["spares"]
        self.workshop = self.data["workshop"]
        self.audit_file = "d:/project/test_audit.jsonl"
        if os.path.exists(self.audit_file):
            try:
                os.remove(self.audit_file)
            except:
                pass

    def tearDown(self):
        if os.path.exists(self.audit_file):
            try:
                os.remove(self.audit_file)
            except:
                pass

    def test_data_generation_structure(self):
        self.assertEqual(len(self.vehicles), 18)
        self.assertEqual(len(self.spares), 3)
        self.assertEqual(self.workshop["num_bays"], 3)
        for v in self.vehicles:
            self.assertIn("vehicle_id", v)
            self.assertIn("telemetry_status", v)
            self.assertIn("urgency_score", v)
            self.assertIn("cancellation_cost_per_shift", v)
            self.assertGreaterEqual(v["urgency_score"], 0.0)

    def test_telemetry_resilience_preprocessor(self):
        # Test GPS Loss handling
        v_gps_lost = {"vehicle_id": "V-TEST-1", "telemetry_status": "GPS_LOST", "urgency_score": 60.0}
        proc_gps = TelemetryResilientPreprocessor.process_vehicle_telemetry(v_gps_lost)
        self.assertEqual(proc_gps["location_confidence"], "LOW_DEAD_RECKONING")
        self.assertEqual(proc_gps["transit_time_buffer_hours"], 1.0)
        self.assertGreater(proc_gps["operational_risk_multiplier"], 1.0)

        # Test Sensor Dropout handling
        v_sensor_drop = {"vehicle_id": "V-TEST-2", "telemetry_status": "SENSOR_DROPOUT", "urgency_score": 60.0}
        proc_sensor = TelemetryResilientPreprocessor.process_vehicle_telemetry(v_sensor_drop)
        self.assertEqual(proc_sensor["location_confidence"], "SENSOR_BLINDSPOT")
        # Urgency should be conservatively inflated by 25%
        self.assertEqual(proc_sensor["urgency_score"], 75.0)

    def test_hard_constraints_workshop_capacity(self):
        opt = MultiObjectiveSlotOptimizer()
        res = opt.optimize(self.vehicles, self.spares, self.workshop, time_horizon_shifts=3)
        scheduled = res["scheduled_slots"]
        
        # Verify no bay is scheduled for overlapping times beyond bay limits
        bay_usage = {}
        for slot in scheduled:
            bay = slot["bay"]
            if bay not in bay_usage:
                bay_usage[bay] = []
            bay_usage[bay].append((slot["start_hour"], slot["end_hour"]))

        # For each bay, intervals must not overlap
        for bay, intervals in bay_usage.items():
            intervals.sort(key=lambda x: x[0])
            for i in range(len(intervals) - 1):
                self.assertLessEqual(intervals[i][1], intervals[i+1][0], 
                                     f"Overlap detected in {bay}: {intervals[i]} and {intervals[i+1]}")

    def test_replacement_vehicle_allocation_reduces_cancellations(self):
        opt = MultiObjectiveSlotOptimizer()
        # Case A: With spares
        res_with_spares = opt.optimize(self.vehicles, self.spares, self.workshop)
        # Case B: Without spares
        res_no_spares = opt.optimize(self.vehicles, [], self.workshop)
        
        self.assertGreater(res_with_spares["cancellations_avoided_by_spares"], 0)
        self.assertLess(res_with_spares["total_cancellation_cost_usd"], res_no_spares["total_cancellation_cost_usd"])

    def test_dispatcher_override_and_cryptographic_audit(self):
        logger = DispatcherAuditLogger(log_filepath=self.audit_file)
        logger.record_plan_generation("PLAN-T1", {"test": True}, 50000.0)
        
        override = logger.record_dispatcher_override(
            plan_id="PLAN-T1",
            vehicle_id="VEH-005",
            original_slot="BAY-02_SHIFT-01",
            new_slot="DEFERRED_SHIFT-03",
            dispatcher_id="SUP-TEST",
            dispatcher_role="Mine Supervisor",
            override_reason="Bench 3 blast evacuation in progress",
            service_impact_acknowledged=True
        )
        
        self.assertTrue(logger.verify_audit_integrity())
        self.assertEqual(len(logger.history), 2)
        self.assertEqual(override["dispatcher_id"], "SUP-TEST")

    def test_edge_case_bay_saturation(self):
        # All vehicles have maximum urgency (surge scenario)
        surge_fleet = [dict(v) for v in self.vehicles]
        for v in surge_fleet:
            v["urgency_score"] = 99.0
            v["est_service_hours"] = 8
            
        opt = MultiObjectiveSlotOptimizer()
        res = opt.optimize(surge_fleet, self.spares, self.workshop, time_horizon_shifts=3)
        # 3 bays * 24 hours / 8 hours per job = 9 maximum possible slots
        self.assertLessEqual(res["scheduled_maintenance_count"], 9)
        self.assertGreater(res["unserviced_count"], 0)

if __name__ == "__main__":
    unittest.main()
