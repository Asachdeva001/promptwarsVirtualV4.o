import React, { useState, useEffect } from "react";
import "./App.css";

// Components
import OpsConsole from "./components/OpsConsole";
import CrowdMap from "./components/CrowdMap";
import VolunteerList from "./components/VolunteerList";
import FanMobile from "./components/FanMobile";

// Icons
import { Shield, Sparkles, RefreshCw, Activity, Users, AlertTriangle } from "lucide-react";

export default function App() {
  const [timeline, setTimeline] = useState(0);
  const [status, setStatus] = useState({
    occupancy: 68450,
    occupancy_rate: 85.6,
    total_volunteers: 8,
    active_volunteers: 2,
    idle_volunteers: 6,
    total_incidents: 3,
    active_incidents: 3,
    critical_incidents: 1,
    crowd_status: "Green",
    max_gate_wait_time: 15
  });
  const [gates, setGates] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [logs, setLogs] = useState([]);

  // Fetch all live database status info
  const fetchTelemetry = async () => {
    try {
      // 1. General status summary
      const statusRes = await fetch("http://localhost:8000/api/status");
      const statusData = await statusRes.json();
      setStatus(statusData);
      if (statusData.logs) {
        setLogs(statusData.logs);
      }

      // 2. Incident tracker registry
      const incRes = await fetch("http://localhost:8000/api/incidents");
      const incData = await incRes.json();
      setIncidents(incData);

      // 3. Volunteer registry
      const volRes = await fetch("http://localhost:8000/api/volunteers");
      const volData = await volRes.json();
      setVolunteers(volData);
    } catch (err) {
      console.error("Telemetry fetch error (API offline, using fallback):", err);
    }
  };

  // Fetch crowd projections based on timeline offset
  const fetchCrowdPredictions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/gates?timeline=${timeline}`);
      const data = await res.json();
      setGates(data.gates);
      setAlerts(data.alerts);
    } catch (err) {
      console.error("Crowd prediction fetch error:", err);
      // Fail-safe mock data loader
      if (timeline === 0) {
        setGates([
          { id: "gate_a", name: "Gate A", current_queue_length: 620, estimated_wait_time: 15, coordinates: { x: 20, y: 10 } },
          { id: "gate_b", name: "Gate B", current_queue_length: 150, estimated_wait_time: 4, coordinates: { x: 80, y: 10 } },
          { id: "gate_c", name: "Gate C", current_queue_length: 280, estimated_wait_time: 7, coordinates: { x: 80, y: 90 } },
          { id: "gate_d", name: "Gate D", current_queue_length: 340, estimated_wait_time: 9, coordinates: { x: 20, y: 90 } }
        ]);
        setAlerts([]);
      } else if (timeline === 20) {
        setGates([
          { id: "gate_a", name: "Gate A", current_queue_length: 992, estimated_wait_time: 24, coordinates: { x: 20, y: 10 } },
          { id: "gate_b", name: "Gate B", current_queue_length: 165, estimated_wait_time: 4, coordinates: { x: 80, y: 10 } },
          { id: "gate_c", name: "Gate C", current_queue_length: 322, estimated_wait_time: 8, coordinates: { x: 80, y: 90 } },
          { id: "gate_d", name: "Gate D", current_queue_length: 442, estimated_wait_time: 11, coordinates: { x: 20, y: 90 } }
        ]);
        setAlerts([
          {
            severity: "Critical",
            message: "Critical bottleneck predicted at Gate A in 20 minutes! Wait time expected to exceed 24 mins.",
            target_gate: "gate_a",
            alternate_gate: "gate_b"
          }
        ]);
      }
    }
  };

  // Reset simulator
  const handleResetSimulation = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/reset", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        setTimeline(0);
        await fetchTelemetry();
        await fetchCrowdPredictions();
        alert("Simulation state reset successfully.");
      }
    } catch (err) {
      console.error("Reset error:", err);
      // Local reload
      setTimeline(0);
      alert("Local reload triggered.");
    }
  };

  // Initial load
  useEffect(() => {
    fetchTelemetry();
  }, []);

  // Sync predictions whenever timeline or logs update
  useEffect(() => {
    fetchCrowdPredictions();
  }, [timeline]);

  // Periodic polling every 5s to fetch latest changes from backend
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTelemetry();
      fetchCrowdPredictions();
    }, 5000);
    return () => clearInterval(interval);
  }, [timeline]);

  return (
    <div className="app-container">
      {/* Header Navbar */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="nav-logo-icon">S</div>
          <span className="nav-logo-text">StadiumOS</span>
          <span className="nav-badge">FIFA World Cup 2026</span>
        </div>
        <div className="nav-controls">
          <button className="reset-btn" onClick={handleResetSimulation}>
            <RefreshCw size={14} style={{ marginRight: 6 }} />
            Reset Sim
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
              <div className="kpi-sub">{status.occupancy_rate}% capacity</div>
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

          <div className="glass-panel kpi-card">
            <div className="kpi-icon crowd" style={{ color: status.crowd_status === "Red" ? "var(--accent-red)" : (status.crowd_status === "Yellow" ? "var(--accent-orange)" : "var(--accent-green)") }}>
              <Activity size={22} />
            </div>
            <div className="kpi-details">
              <h4>Max Wait Time</h4>
              <p>{status.max_gate_wait_time} min</p>
              <div className="kpi-sub">Turnstile crowd stress: {status.crowd_status}</div>
            </div>
          </div>

        </section>

        {/* Dashboard Panels */}
        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <CrowdMap 
            timeline={timeline} 
            setTimeline={setTimeline} 
            gates={gates} 
            alerts={alerts}
            onRerouteSuccess={() => {
              fetchTelemetry();
              fetchCrowdPredictions();
            }}
          />
        </section>

        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <VolunteerList 
            incidents={incidents}
            volunteers={volunteers}
            onUpdate={fetchTelemetry}
          />
        </section>

        <section className="glass-panel fan-panel">
          <FanMobile />
        </section>

        {/* Operations Terminal Bottom Row */}
        <section className="glass-panel" style={{ gridColumn: "1 / span 2" }}>
          <OpsConsole 
            logs={logs}
            onActionExecuted={() => {
              fetchTelemetry();
              fetchCrowdPredictions();
            }}
          />
        </section>

      </main>
    </div>
  );
}
