import React, { useState, useEffect, Suspense, lazy, useCallback } from "react";
import "./App.css";
import Onboarding from "./components/Onboarding";
import { API_BASE_URL } from "./config";
import { Shield, Sparkles, RefreshCw, Activity, Users, AlertTriangle, Play, Pause, Loader2 } from "lucide-react";

const FanMobile = lazy(() => import("./components/FanMobile"));

const SectionLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', padding: '20px' }}>
    <Loader2 size={24} className="spinner" style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-blue)' }} />
  </div>
);

export default function App() {
  const [stadiumId, setStadiumId] = useState(null); // null means onboarding mode
  const [stadiums, setStadiums] = useState([]);

  const [status, setStatus] = useState({
    active_stadium_id: "",
    stadium_name: "",
    stadium_location: "",
    occupancy: 0,
    occupancy_rate: 0,
    total_volunteers: 0,
    active_volunteers: 0,
    idle_volunteers: 0,
    total_incidents: 0,
    active_incidents: 0,
    critical_incidents: 0,
    crowd_status: "Green",
    max_gate_wait_time: 0
  });

  const [volunteers, setVolunteers] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [logs, setLogs] = useState([]);

  // Fetch available stadiums list
  const fetchStadiums = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/stadiums`);
      const data = await res.json();
      setStadiums(data);
    } catch (err) {
      console.error("Failed to fetch stadiums (offline fallback):", err);
    }
  }, []);

  // Fetch live operational statuses
  const fetchTelemetry = useCallback(async () => {
    if (!stadiumId) return;
    try {
      const statusRes = await fetch(`${API_BASE_URL}/api/status`);
      const statusData = await statusRes.json();
      setStatus(statusData);
      if (statusData.logs) setLogs(statusData.logs);

      const incRes = await fetch(`${API_BASE_URL}/api/incidents`);
      const incData = await incRes.json();
      setIncidents(incData);

      const volRes = await fetch(`${API_BASE_URL}/api/volunteers`);
      const volData = await volRes.json();
      setVolunteers(volData);
    } catch (err) {
      console.error("Telemetry fetch error:", err);
    }
  }, [stadiumId]);

  // Handle active stadium switch
  const handleStadiumChange = useCallback(async (newId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/stadiums/select`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stadium_id: newId })
      });
      const data = await res.json();
      if (data.success) {
        setStadiumId(newId);
      }
    } catch (err) {
      console.error("Error changing stadium context:", err);
      setStadiumId(newId);
    }
  }, []);

  // Reset simulator
  const handleResetSimulation = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/reset`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        setStadiumId(null); // Go back to onboarding
        alert("Simulation state reset successfully.");
      }
    } catch (err) {
      console.error("Reset error:", err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchStadiums();
  }, []);

  useEffect(() => {
    if (stadiumId) fetchTelemetry();
  }, [stadiumId]);

  // Periodic polling every 5s to fetch latest changes from backend
  useEffect(() => {
    if (!stadiumId) return;
    const interval = setInterval(() => {
      fetchTelemetry();
    }, 5000);
    return () => clearInterval(interval);
  }, [stadiumId]);

  if (!stadiumId) {
    return <Onboarding onStadiumSelect={handleStadiumChange} />;
  }

  return (
    <div className="app-container">
      {/* Header Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="nav-logo-icon">S</div>
          <span className="nav-logo-text">StadiumOS</span>
          <span className="nav-badge">AI Assistant Hub</span>
        </div>

        {/* Stadium Selector */}
        <div className="nav-middle" style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <select 
            className="lang-selector" 
            style={{ 
              fontSize: "12px", 
              padding: "6px 12px", 
              borderRadius: "8px", 
              border: "1px solid rgba(255,255,255,0.15)", 
              backgroundColor: "rgba(0,0,0,0.45)",
              color: "#fff"
            }}
            value={stadiumId}
            onChange={(e) => handleStadiumChange(e.target.value)}
            aria-label="Select Stadium Host Venue"
          >
            {stadiums.map(s => (
              <option key={s.id} value={s.id}>{s.name} ({s.location})</option>
            ))}
          </select>
        </div>

        <div className="nav-controls">
          <button className="reset-btn" onClick={handleResetSimulation} aria-label="Reset Simulation">
            <RefreshCw size={14} style={{ marginRight: 6 }} />
            Exit Venue
          </button>
        </div>
      </header>

      {/* Main Panel Grid */}
      <main className="dashboard-grid">
        
        {/* KPI Panel Row */}
        <section className="kpi-row">
          <div className="glass-panel kpi-card">
            <div className="kpi-icon occupancy">
              <Users size={22} />
            </div>
            <div className="kpi-details">
              <h4>Stadium Occupancy</h4>
              <p>{status.occupancy.toLocaleString()}</p>
              <div className="kpi-sub">85.5% capacity</div>
            </div>
          </div>

          <div className="glass-panel kpi-card">
            <div className="kpi-icon volunteers">
              <Users size={22} />
            </div>
            <div className="kpi-details">
              <h4>Active Volunteers</h4>
              <p>{status.active_volunteers} / {status.total_volunteers}</p>
              <div className="kpi-sub">{status.idle_volunteers} Idle volunteers</div>
            </div>
          </div>

          <div className="glass-panel kpi-card">
            <div className="kpi-icon incidents" style={{ color: status.critical_incidents > 0 ? "var(--accent-red)" : "inherit" }}>
              <AlertTriangle size={22} />
            </div>
            <div className="kpi-details">
              <h4>Active Incidents</h4>
              <p>{status.active_incidents}</p>
              <div className="kpi-sub">{status.critical_incidents} Critical alerts</div>
            </div>
          </div>
        </section>

        {/* Dashboard Panels */}
        <section className="glass-panel fan-panel" style={{ gridColumn: "1 / span 3" }}>
          <Suspense fallback={<SectionLoader />}>
            <FanMobile />
          </Suspense>
        </section>
      </main>
    </div>
  );
}
