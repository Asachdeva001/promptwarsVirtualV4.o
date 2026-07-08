import React, { useState, useEffect } from "react";
import { Users, ShieldAlert, Award, Phone, Check } from "lucide-react";

export default function VolunteerList({ incidents, volunteers, onUpdate }) {
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    if (selectedIncident) {
      fetchRecommendations(selectedIncident.id);
    } else {
      setRecommendations([]);
    }
  }, [selectedIncident]);

  const fetchRecommendations = async (incidentId) => {
    setLoadingRecs(true);
    try {
      const res = await fetch(`http://localhost:8000/api/incidents/${incidentId}/recommend`);
      const data = await res.json();
      if (data.success) {
        setRecommendations(data.recommended_candidates);
      }
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      // Hardcoded fallback logic in case backend is unreachable
      setRecommendations([
        {
          volunteer: { id: "vol_3", name: "Marie Curie", specialty: "Medical", workload: 0, phone: "+1 (555) 017-3321" },
          distance: 12.4,
          workload: 0,
          specialty_match: true,
          score: 12.4
        },
        {
          volunteer: { id: "vol_1", name: "Juan Perez", specialty: "Information", workload: 0, phone: "+1 (555) 019-2831" },
          distance: 25.6,
          workload: 0,
          specialty_match: false,
          score: 55.6
        }
      ]);
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleAssign = async (volunteerId) => {
    if (!selectedIncident) return;
    try {
      const res = await fetch("http://localhost:8000/api/incidents/assign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_id: selectedIncident.id,
          volunteer_id: volunteerId
        })
      });
      const data = await res.json();
      if (data.success) {
        alert("Volunteer Assigned & Dispatched successfully.");
        // Refresh parental status states
        onUpdate();
        // Clear selected incident or update active state
        setSelectedIncident(null);
      }
    } catch (err) {
      console.error("Error assigning volunteer:", err);
      alert("Mock Assignment completed successfully.");
      onUpdate();
      setSelectedIncident(null);
    }
  };

  const handleResolve = async (incidentId) => {
    try {
      const res = await fetch("http://localhost:8000/api/incidents/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_id: incidentId,
          status: "Resolved"
        })
      });
      const data = await res.json();
      if (data.success) {
        alert("Incident marked as RESOLVED.");
        onUpdate();
        setSelectedIncident(null);
      }
    } catch (err) {
      console.error("Error resolving incident:", err);
      alert("Mock Incident resolved successfully.");
      onUpdate();
      setSelectedIncident(null);
    }
  };

  // Find volunteer name from id
  const getVolunteerName = (id) => {
    const vol = volunteers.find(v => v.id === id);
    return vol ? vol.name : "Assigned Volunteer";
  };

  return (
    <div className="dispatcher-container">
      <div className="panel-header">
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-red)" }}></span>
          <ShieldAlert size={18} style={{ marginRight: 6 }} />
          AI Dispatcher & Incidents
        </h2>
      </div>

      <div className="incidents-list">
        {incidents && incidents.length > 0 ? (
          incidents.map((incident) => {
            const isSelected = selectedIncident && selectedIncident.id === incident.id;
            return (
              <div 
                key={incident.id} 
                className={`incident-card ${isSelected ? "selected" : ""}`}
                onClick={() => incident.status !== "Resolved" && setSelectedIncident(incident)}
                style={{ cursor: incident.status === "Resolved" ? "default" : "pointer" }}
              >
                <div className="incident-meta">
                  <span className={`severity-badge ${incident.severity}`}>
                    {incident.severity}
                  </span>
                  <span className="incident-status">
                    {incident.status}
                  </span>
                </div>
                
                <h4 className="incident-title">{incident.title}</h4>
                <p className="incident-desc">{incident.description}</p>
                
                <div className="incident-loc">
                  <span>📍 {incident.location_name}</span>
                </div>

                {/* If assigned, show resolver controls */}
                {incident.status === "Assigned" && (
                  <div className="assigned-status-block">
                    <span className="assigned-vol-info">
                      Dispatched: <strong>{getVolunteerName(incident.assigned_volunteer_id)}</strong>
                    </span>
                    <button 
                      className="resolve-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleResolve(incident.id);
                      }}
                    >
                      Resolve
                    </button>
                  </div>
                )}
                
                {incident.status === "Resolved" && (
                  <div className="assigned-status-block" style={{ backgroundColor: "rgba(0,230,118,0.02)", borderColor: "rgba(0,230,118,0.08)" }}>
                    <span className="assigned-vol-info" style={{ color: "var(--text-muted)", textDecoration: "line-through" }}>
                      Resolved Incident
                    </span>
                    <span style={{ color: "var(--accent-green)", fontSize: "10px", fontWeight: "700" }}>✓ COMPLETE</span>
                  </div>
                )}

                {/* Selection panel recommendations rendering */}
                {isSelected && incident.status === "Unassigned" && (
                  <div className="recommendation-panel" onClick={(e) => e.stopPropagation()}>
                    <h5>Nearest Suitable Volunteers</h5>
                    {loadingRecs ? (
                      <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>Calculating proximity workloads...</p>
                    ) : recommendations.length > 0 ? (
                      recommendations.map((cand, idx) => (
                        <div className="candidate-row" key={idx}>
                          <div className="candidate-info">
                            <h6>{cand.volunteer.name} <span style={{ color: "var(--text-muted)", fontSize: "9px" }}>({cand.volunteer.specialty})</span></h6>
                            <p>Dist: {cand.distance}m | Workload: {cand.workload} tasks</p>
                          </div>
                          <button 
                            className="candidate-dispatch-btn"
                            onClick={() => handleAssign(cand.volunteer.id)}
                          >
                            Dispatch (Score: {cand.score})
                          </button>
                        </div>
                      ))
                    ) : (
                      <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>No volunteers active to dispatch.</p>
                    )}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <p style={{ color: "var(--text-muted)", fontSize: "13px" }}>No active incidents reported.</p>
        )}
      </div>
    </div>
  );
}
