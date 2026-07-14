import React, { useState, useEffect, Suspense, lazy, useCallback, useMemo } from "react";
import "./App.css";

// Lazy Loaded Components
const OpsConsole = lazy(() => import("./components/OpsConsole"));
const CrowdMap = lazy(() => import("./components/CrowdMap"));
const VolunteerList = lazy(() => import("./components/VolunteerList"));
const FanMobile = lazy(() => import("./components/FanMobile"));
const TransitPanel = lazy(() => import("./components/TransitPanel"));
const CctvVision = lazy(() => import("./components/CctvVision"));

// Config
import { API_BASE_URL } from "./config";

// Icons
import { Shield, Sparkles, RefreshCw, Activity, Users, AlertTriangle, Play, Pause, Loader2 } from "lucide-react";

// Loading Fallback
const SectionLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', padding: '20px' }}>
    <Loader2 size={24} className="spinner" style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-blue)' }} />
  </div>
);

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
  const fetchStadiums = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/stadiums`);
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
  }, [stadiumId]);

  // Fetch live operational statuses
  const fetchTelemetry = useCallback(async () => {
    try {
      const statusRes = await fetch(`${API_BASE_URL}/api/status`);
      const statusData = await statusRes.json();
      setStatus(statusData);
      setMatchMinute(statusData.match_minute);
      setMatchScore(statusData.match_score);
      setMatchTeams(statusData.match_teams);
      if (statusData.logs) {
        setLogs(statusData.logs);
      }

      const incRes = await fetch(`${API_BASE_URL}/api/incidents`);
      const incData = await incRes.json();
      setIncidents(incData);

      const volRes = await fetch(`${API_BASE_URL}/api/volunteers`);
      const volData = await volRes.json();
      setVolunteers(volData);
    } catch (err) {
      console.error("Telemetry fetch error:", err);
    }
  }, []);

  // Fetch prediction maps
  const fetchCrowdPredictions = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/gates?timeline=${timeline}`);
      const data = await res.json();
      setGates(data.gates);
      setAlerts(data.alerts);
    } catch (err) {
      console.error("Crowd prediction fetch error:", err);
    }
  }, [timeline]);

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
        setTimeline(0);
        await fetchStadiums();
        await fetchTelemetry();
        await fetchCrowdPredictions();
      }
    } catch (err) {
      console.error("Error changing stadium context:", err);
      setStadiumId(newId);
    }
  }, [fetchStadiums, fetchTelemetry, fetchCrowdPredictions]);

  // Reset simulator
  const handleResetSimulation = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/reset`, { method: "POST" });
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
  }, [fetchStadiums, fetchTelemetry, fetchCrowdPredictions]);

  // Match clock ticker handler
  useEffect(() => {
    let tickInterval = null;
    if (playClock) {
      tickInterval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/match/tick`, { method: "POST" });
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
            aria-label="Select Stadium Host Venue"
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
              aria-label={playClock ? "Pause Match Timer" : "Play Match Timer"}
            >
              {playClock ? <Pause size={12} fill="var(--accent-green)" /> : <Play size={12} fill="var(--text-secondary)" />}
            </button>
          </div>
        </div>

        <div className="nav-controls">
          <button className="reset-btn" onClick={handleResetSimulation} aria-label="Reset Simulation">
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
          <Suspense fallback={<SectionLoader />}>
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
          </Suspense>
        </section>

        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <Suspense fallback={<SectionLoader />}>
            <VolunteerList 
              incidents={incidents}
              volunteers={volunteers}
              onUpdate={fetchTelemetry}
            />
          </Suspense>
        </section>

        <section className="glass-panel fan-panel">
          <Suspense fallback={<SectionLoader />}>
            <FanMobile />
          </Suspense>
        </section>

        {/* Row 3 */}
        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <Suspense fallback={<SectionLoader />}>
            <TransitPanel 
              stadiumId={stadiumId} 
              matchMinute={matchMinute} 
              onUpdateNeeded={fetchTelemetry} 
            />
          </Suspense>
        </section>

        <section className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <Suspense fallback={<SectionLoader />}>
            <CctvVision />
          </Suspense>
        </section>

        {/* Row 4 */}
        <section className="glass-panel" style={{ gridColumn: "1 / span 2" }}>
          <Suspense fallback={<SectionLoader />}>
            <OpsConsole 
              logs={logs}
              onActionExecuted={() => {
                fetchTelemetry();
                fetchCrowdPredictions();
              }}
            />
          </Suspense>
        </section>

      </main>
    </div>
  );
}
