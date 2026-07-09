import React, { useState, useEffect } from "react";
import { Train, Bus, Info, Zap } from "lucide-react";

export default function TransitPanel({ stadiumId, matchMinute, onUpdateNeeded }) {
  const [transitLines, setTransitLines] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTransit = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/transit");
      const data = await res.json();
      setTransitLines(data);
    } catch (err) {
      console.error("Failed to fetch local transit:", err);
      // Local mock state checks
      if (stadiumId === "metlife") {
        setTransitLines([
          { id: "train", name: "NJ Transit Train (Secaucus)", type: "Train", wait_time: 15, status: "Delayed" },
          { id: "bus", name: "Coach USA Bus (Route 351)", type: "Bus", wait_time: 8, status: "Normal" },
          { id: "rideshare", name: "Uber/Lyft Lot G", type: "Rideshare", wait_time: 20, status: "Congested" }
        ]);
      } else {
        setTransitLines([
          { id: "train", name: "SkyTrain (Expo Line)", type: "Train", wait_time: 5, status: "Normal" },
          { id: "bus", name: "TransLink Bus Hub", type: "Bus", wait_time: 12, status: "Busy" }
        ]);
      }
    }
  };

  useEffect(() => {
    fetchTransit();
  }, [stadiumId, matchMinute]);

  const handleBalance = async (transitId) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/transit/balance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transit_id: transitId })
      });
      const data = await res.json();
      if (data.success) {
        setTransitLines(data.transit);
        if (onUpdateNeeded) onUpdateNeeded();
      }
    } catch (err) {
      console.error("Failed to execute transit balance:", err);
      // Hardcoded fallback updates
      const updated = transitLines.map(t => {
        if (t.id === transitId) {
          return { ...t, wait_time: Math.max(5, t.wait_time - 10), status: "Normal" };
        }
        return t;
      });
      setTransitLines(updated);
      if (onUpdateNeeded) onUpdateNeeded();
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status === "Delayed" || status === "Congested") return "var(--accent-red)";
    if (status === "Busy") return "var(--accent-orange)";
    return "var(--accent-green)";
  };

  return (
    <div className="transit-panel-container" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div className="panel-header">
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-blue)" }}></span>
          <Train size={18} style={{ marginRight: 6 }} />
          Local Transit & Egress
        </h2>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10, overflowY: "auto", flex: 1 }}>
        {transitLines.map((line) => {
          const color = getStatusColor(line.status);
          const needsBalancing = line.wait_time > 12;

          return (
            <div 
              key={line.id} 
              style={{
                background: "rgba(255, 255, 255, 0.02)",
                border: "1px solid var(--border-glass)",
                borderRadius: "8px",
                padding: "10px 12px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <span style={{ fontSize: "12px", fontWeight: "700" }}>{line.name}</span>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span style={{ fontSize: "10px", color: "var(--text-secondary)" }}>Wait: {line.wait_time} mins</span>
                  <span 
                    style={{ 
                      fontSize: "9px", 
                      fontWeight: "700", 
                      color: color, 
                      backgroundColor: `${color}15`, 
                      padding: "1px 5px", 
                      borderRadius: "4px" 
                    }}
                  >
                    {line.status.toUpperCase()}
                  </span>
                </div>
              </div>

              {needsBalancing && (
                <button 
                  className="crowd-alert-action-btn"
                  onClick={() => handleBalance(line.id)}
                  disabled={loading}
                  style={{
                    padding: "4px 8px",
                    fontSize: "10px",
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                    borderColor: "var(--accent-blue)",
                    color: "var(--text-primary)",
                    marginTop: 0
                  }}
                >
                  <Zap size={10} style={{ color: "var(--accent-blue)" }} />
                  Inject Shuttle
                </button>
              )}
            </div>
          );
        })}
      </div>

      {matchMinute >= 75 && (
        <div style={{
          marginTop: 10,
          background: "rgba(255,145,0,0.05)",
          border: "1px solid rgba(255,145,0,0.15)",
          padding: "8px 10px",
          borderRadius: "6px",
          display: "flex",
          gap: 6,
          alignItems: "flex-start"
        }}>
          <Info size={14} style={{ color: "var(--accent-orange)", flexShrink: 0, marginTop: 1 }} />
          <p style={{ fontSize: "10px", color: "var(--text-secondary)", lineHeight: "1.4" }}>
            Egress Peak Active: Fans are leaving the stadium. Expect transit queues to rise. Consider staggering concessions exit notices.
          </p>
        </div>
      )}
    </div>
  );
}
