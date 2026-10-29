"""
Dispatcher Override & Immutable Audit Logger Module.
Preserves complete history of maintenance plan changes, slot overrides,
authorizing supervisor identity, and formal operational justification.
Includes cryptographic integrity check to prevent tampering.
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

class DispatcherAuditLogger:
    def __init__(self, log_filepath: str = "dispatcher_override_audit.jsonl"):
        self.log_filepath = log_filepath
        self.history: List[Dict[str, Any]] = []
        
    def _calculate_entry_hash(self, entry: Dict[str, Any], previous_hash: str) -> str:
        serialized = json.dumps(entry, sort_keys=True) + previous_hash
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def record_plan_generation(self, plan_id: str, summary: Dict[str, Any], total_cost: float) -> Dict[str, Any]:
        previous_hash = self.history[-1]["current_hash"] if self.history else "GENESIS_BLOCK"
        entry = {
            "entry_type": "INITIAL_OPTIMIZED_PLAN",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": plan_id,
            "summary": summary,
            "total_estimated_disruption_cost": total_cost,
            "authorized_by": "SYSTEM_OPTIMIZER",
            "override_reason": "Automated Multi-Objective Optimization Schedule"
        }
        entry_hash = self._calculate_entry_hash(entry, previous_hash)
        entry["prev_hash"] = previous_hash
        entry["current_hash"] = entry_hash
        
        self.history.append(entry)
        self._append_to_file(entry)
        return entry

    def record_dispatcher_override(
        self,
        plan_id: str,
        vehicle_id: str,
        original_slot: Optional[str],
        new_slot: str,
        dispatcher_id: str,
        dispatcher_role: str,
        override_reason: str,
        service_impact_acknowledged: bool
    ) -> Dict[str, Any]:
        """
        Records an authorized dispatcher override with explicit operational justification.
        """
        previous_hash = self.history[-1]["current_hash"] if self.history else "GENESIS_BLOCK"
        entry = {
            "entry_type": "DISPATCHER_OVERRIDE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": plan_id,
            "vehicle_id": vehicle_id,
            "original_slot": original_slot,
            "new_slot": new_slot,
            "dispatcher_id": dispatcher_id,
            "dispatcher_role": dispatcher_role,
            "override_reason": override_reason,
            "service_impact_acknowledged": service_impact_acknowledged
        }
        entry_hash = self._calculate_entry_hash(entry, previous_hash)
        entry["prev_hash"] = previous_hash
        entry["current_hash"] = entry_hash
        
        self.history.append(entry)
        self._append_to_file(entry)
        return entry

    def _append_to_file(self, entry: Dict[str, Any]):
        try:
            with open(self.log_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Warning: could not write to {self.log_filepath}: {e}")

    def verify_audit_integrity(self) -> bool:
        """
        Validates hash chaining across all log entries to prove zero history tampering.
        """
        if not self.history:
            return True
        prev = "GENESIS_BLOCK"
        for item in self.history:
            stored_hash = item["current_hash"]
            raw_item = {k: v for k, v in item.items() if k not in ("prev_hash", "current_hash")}
            computed = self._calculate_entry_hash(raw_item, prev)
            if computed != stored_hash:
                return False
            prev = stored_hash
        return True
