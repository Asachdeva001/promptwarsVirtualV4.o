from typing import Dict, List, Any
from app.database import db

class CrowdIntelligenceAgent:
    def __init__(self):
        pass

    def get_predictions(self, timeline_minutes: int) -> Dict[str, Any]:
        """
        Predict queue lengths and wait times for Gates A, B, C, D based on timeline offset.
        At +15m or +20m, simulate high flow rates at certain gates (like Gate A) to show predictions.
        """
        predicted_gates = []
        alerts = []
        
        for gate in db.gates:
            pred_gate = dict(gate)
            
            # Simulate prediction changes based on minutes ahead
            if timeline_minutes == 0:
                # Live state
                pass
            elif timeline_minutes == 10:
                if gate["id"] == "gate_a":
                    pred_gate["current_queue_length"] = int(gate["current_queue_length"] * 1.25)
                    pred_gate["estimated_wait_time"] = int(pred_gate["current_queue_length"] * gate["ticket_scanner_speed"] / 60 / 3.0) # assuming 3 scanners
                elif gate["id"] == "gate_b":
                    pred_gate["current_queue_length"] = int(gate["current_queue_length"] * 1.1)
                    pred_gate["estimated_wait_time"] = int(pred_gate["current_queue_length"] * gate["ticket_scanner_speed"] / 60 / 3.0)
            elif timeline_minutes == 20 or timeline_minutes == 30:
                factor = 1.6 if timeline_minutes == 20 else 2.1
                if gate["id"] == "gate_a":
                    # Major congestion prediction!
                    pred_gate["current_queue_length"] = int(gate["current_queue_length"] * factor)
                    pred_gate["estimated_wait_time"] = int(pred_gate["current_queue_length"] * gate["ticket_scanner_speed"] / 60 / 3.0)
                    if pred_gate["estimated_wait_time"] > 20:
                        alerts.append({
                            "id": "alert_crowd_gate_a",
                            "severity": "Critical",
                            "message": f"Critical bottleneck predicted at Gate A in {timeline_minutes} minutes! Wait time expected to exceed {pred_gate['estimated_wait_time']} mins.",
                            "recommended_action": "Reroute incoming traffic from Gate A parking to Gate B. Update digital banners.",
                            "target_gate": "gate_a",
                            "alternate_gate": "gate_b"
                        })
                elif gate["id"] == "gate_d":
                    pred_gate["current_queue_length"] = int(gate["current_queue_length"] * 1.3)
                    pred_gate["estimated_wait_time"] = int(pred_gate["current_queue_length"] * gate["ticket_scanner_speed"] / 60 / 3.0)
                    if pred_gate["estimated_wait_time"] > 12:
                        alerts.append({
                            "id": "alert_crowd_gate_d",
                            "severity": "Medium",
                            "message": f"Congestion spike predicted at Gate D in {timeline_minutes} minutes.",
                            "recommended_action": "Open secondary turnstiles at Gate D.",
                            "target_gate": "gate_d",
                            "alternate_gate": "gate_c"
                        })
                else:
                    pred_gate["current_queue_length"] = int(gate["current_queue_length"] * 1.15)
                    pred_gate["estimated_wait_time"] = int(pred_gate["current_queue_length"] * gate["ticket_scanner_speed"] / 60 / 3.0)
            
            # Floor wait time to at least 1 minute
            if pred_gate["estimated_wait_time"] <= 0:
                pred_gate["estimated_wait_time"] = 1
                
            predicted_gates.append(pred_gate)
            
        return {
            "timeline_offset": timeline_minutes,
            "gates": predicted_gates,
            "alerts": alerts
        }

    def execute_rerouting(self, source_gate_id: str, dest_gate_id: str) -> Dict[str, Any]:
        """
        Reroute crowd flow from a congested gate to an alternate gate.
        Adjust queue lengths and log action.
        """
        source_gate = None
        dest_gate = None
        
        for gate in db.gates:
            if gate["id"] == source_gate_id:
                source_gate = gate
            if gate["id"] == dest_gate_id:
                dest_gate = gate
                
        if source_gate and dest_gate:
            # Shift 35% of queue to destination
            transfer_qty = int(source_gate["current_queue_length"] * 0.35)
            source_gate["current_queue_length"] -= transfer_qty
            dest_gate["current_queue_length"] += transfer_qty
            
            # Recalculate wait times
            source_gate["estimated_wait_time"] = int(source_gate["current_queue_length"] * source_gate["ticket_scanner_speed"] / 60 / 3.0)
            dest_gate["estimated_wait_time"] = int(dest_gate["current_queue_length"] * dest_gate["ticket_scanner_speed"] / 60 / 3.0)
            
            db.add_log("system", f"Rerouted traffic from {source_gate['name']} to {dest_gate['name']}. Traffic load balanced.")
            
            return {
                "success": True,
                "message": f"Successfully rerouted crowd from {source_gate['name']} to {dest_gate['name']}.",
                "gates": db.gates
            }
            
        return {"success": False, "message": "Gate mapping not found."}

crowd_agent = CrowdIntelligenceAgent()
