import React, { useState, useEffect } from "react";
import "./App.css";

// Components
import OpsConsole from "./components/OpsConsole";
import CrowdMap from "./components/CrowdMap";
import VolunteerList from "./components/VolunteerList";
import FanMobile from "./components/FanMobile";
import TransitPanel from "./components/TransitPanel";
import CctvVision from "./components/CctvVision";

// Icons
import { Shield, Sparkles, RefreshCw, Activity, Users, AlertTriangle, Play, Pause } from "lucide-react";

export default function App() {
  const [timeline, setTimeline] = useState(0);
  const [stadiums, setStadiums] = useState([]);
  const [stadiumId, setStadiumId] = useState("metlife");
  const [matchMinute, setMatchMinute] = useState(68);
  const [matchScore, setMatchScore] = useState("2 - 1");
  const [matchTeams, setMatchTeams] = useState("USA vs England");
  const [playClock, setPlayClock] = useState(true);

  const [status, setStatus] = useState({
    active_stadium_id: "metlife",
    stadium_name: "MetLife Stadium",
    stadium_location: "NY/NJ",
    match_teams: "USA vs England",
    match_score: "2 - 1",
    match_minute: 68,
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

  // Fetch available stadiums list
  const fetchStadiums = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/stadiums");
      const data = await res.json();
      setStadiums(data);
      
      const active = data.find(s => s.id === stadiumId);
      if (active) {
        setMatchMinute(active.match_minute);
        setMatchScore(active.match_score);
        setMatchTeams(active.match_teams);
      }
    } catch (err) {
      console.error("Failed to fetch stadiums (offline fallback):", err);
      setStadiums([
        { id: "metlife", name: "MetLife Stadium", location: "NY/NJ", capacity: 82500, match_teams: "USA vs England", match_score: "2 - 1", match_minute: 68 },
        { id: "azteca", name: "Estadio Azteca", location: "Mexico City", capacity: 87500, match_teams: "Mexico vs Argentina", match_score: "0 - 0", match_minute: 14 },
        { id: "bc_place", name: "BC Place", location: "Vancouver", capacity: 54500, match_teams: "Canada vs France", match_score: "1 - 1", match_minute: 41 }
      ]);
    }
  };

  // Fetch live operational statuses
  const fetchTelemetry = async () => {
    try {
      const statusRes = await fetch("http://localhost:8000/api/status");
      const statusData = await statusRes.json();
      setStatus(statusData);
      setMatchMinute(statusData.match_minute);
      setMatchScore(statusData.match_score);
      setMatchTeams(statusData.match_teams);
      if (statusData.logs) {
        setLogs(statusData.logs);
      }

      const incRes = await fetch("http://localhost:8000/api/incidents");
      const incData = await incRes.json();
      setIncidents(incData);

      const volRes = await fetch("http://localhost:8000/api/volunteers");
      const volData = await volRes.json();
      setVolunteers(volData);
    } catch (err) {
      console.error("Telemetry fetch error:", err);
    }
  };

  // Fetch prediction maps
  const fetchCrowdPredictions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/gates?timeline=${timeline}`);
      const data = await res.json();
      setGates(data.gates);
      setAlerts(data.alerts);
    } catch (err) {
      console.error("Crowd prediction fetch error:", err);
    }
  };

  // Handle active stadium switch
  const handleStadiumChange = async (newId) => {
    try {
      const res = await fetch("http://localhost:8000/api/stadiums/select", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stadium_id: newId })
      });
      const data = await res.json();
      if (data.success) {
        setStadiumId(newId);
        setTimeline(0);
        await fetchStadiums();
        await fetchTelemetry();
        await fetchCrowdPredictions();
      }
    } catch (err) {
      console.error("Error changing stadium context:", err);
      setStadiumId(newId);
    }
  };

  // Reset simulator
  const handleResetSimulation = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/reset", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        setTimeline(0);
        setStadiumId("metlife");
        await fetchStadiums();
        await fetchTelemetry();
        await fetchCrowdPredictions();
        alert("Simulation state reset successfully.");
      }
    } catch (err) {
      console.error("Reset error:", err);
      setTimeline(0);
      alert("Local reload triggered.");
    }
  };

  // Match clock ticker handler
  useEffect(() => {
    let tickInterval = null;
    if (playClock) {
      tickInterval = setInterval(async () => {
        try {
          const res = await fetch("http://localhost:8000/api/match/tick", { method: "POST" });
          const data = await res.json();
          setMatchMinute(data.match_minute);
          setMatchScore(data.match_score);
          fetchTelemetry();
        } catch (err) {
          // local fallback tick
          setMatchMinute(m => {
            const nextM = m + 1;
            if (nextM > 90) return 0;
            return nextM;
          });
        }
      }, 3000); // clock ticks every 3 seconds
    }
    return () => {
      if (tickInterval) clearInterval(tickInterval);
    };
  }, [playClock]);

  // Initial load
  useEffect(() => {
    fetchStadiums();
    fetchTelemetry();
  }, [stadiumId]);

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

        {/* Stadium Selector and Live Score Timeline Ticker */}
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
          >
            {stadiums.map(s => (
              <option key={s.id} value={s.id}>{s.name} ({s.location})</option>
            ))}
          </select>

          <div style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid var(--border-glass)",
            padding: "5px 12px",
            borderRadius: "8px",
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontSize: "13px"
          }}>
            <span style={{ fontWeight: 700, color: "var(--accent-green)" }}>LIVE SCORE:</span>
            <span style={{ fontWeight: 500 }}>{matchTeams}</span>
            <strong style={{ letterSpacing: "0.05em", color: "#fff" }}>{matchScore}</strong>
            <span style={{ color: "var(--text-secondary)" }}>Time: {matchMinute}'</span>
            <button 
              onClick={() => setPlayClock(!playClock)} 
              style={{
                background: "transparent",
                border: "none",
                cursor: "pointer",
                color: playClock ? "var(--accent-green)" : "var(--text-secondary)",
                display: "flex",
                alignItems: "center"
              }}
              title={playClock ? "Pause Match Timer" : "Play Match Timer"}
            >
              {playClock ? <Pause size={12} fill="var(--accent-green)" /> : <Play size={12} fill="var(--text-secondary)" />}
            </button>
          </div>
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
        {/* Row 2 */}
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

        {/* Row 3 */}
        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <TransitPanel 
            stadiumId={stadiumId} 
            matchMinute={matchMinute} 
            onUpdateNeeded={fetchTelemetry} 
          />
        </section>

        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <CctvVision />
        </section>

        {/* Row 4 */}
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
