import React, { useState } from "react";
import { Camera, ShieldAlert, Sparkles, Check } from "lucide-react";

export default function CctvVision() {
  const [selectedCam, setSelectedCam] = useState("cam_104");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);

  const handleInspect = async () => {
    setLoading(true);
    setReport(null);
    try {
      const res = await fetch("http://localhost:8000/api/vision/inspect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ camera_id: selectedCam })
      });
      const data = await res.json();
      if (data.success) {
        setReport(data.report);
      }
    } catch (err) {
      console.error("CCTV inspect error:", err);
      // Local mock fallback
      const mocks = {
        cam_104: {
          hazard_detected: true,
          severity: "Critical",
          hazard_type: "Crowd Bottleneck",
          description: "Crowd congestion exceeding 90% threshold at Gate A entry turnstiles. Scanner bottlenecks observed.",
          action: "Execute Gate A to Gate B traffic redirection. Deploy additional ticketing volunteers.",
          confidence: 96
        },
        cam_202: {
          hazard_detected: true,
          severity: "Critical",
          hazard_type: "Obstruction",
          description: "Safety Hazard: Two large plastic trash containers are blocking the emergency evacuation stairwell in Sector 228.",
          action: "Dispatch nearby volunteer (Juan Perez) to clear obstruction immediately.",
          confidence: 98
        }
      };
      setReport(mocks[selectedCam]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cctv-vision-container" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div className="panel-header">
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-purple)" }}></span>
          <Camera size={18} style={{ marginRight: 6 }} />
          Gemini Vision CCTV Inspector
        </h2>
      </div>

      <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
        <button 
          className={`preset-chip ${selectedCam === "cam_104" ? "active" : ""}`}
          onClick={() => { setSelectedCam("cam_104"); setReport(null); }}
          style={{ backgroundColor: selectedCam === "cam_104" ? "rgba(213, 0, 249, 0.15)" : "", borderColor: selectedCam === "cam_104" ? "var(--accent-purple)" : "" }}
        >
          CAM-104 (Gate A Concourse)
        </button>
        <button 
          className={`preset-chip ${selectedCam === "cam_202" ? "active" : ""}`}
          onClick={() => { setSelectedCam("cam_202"); setReport(null); }}
          style={{ backgroundColor: selectedCam === "cam_202" ? "rgba(213, 0, 249, 0.15)" : "", borderColor: selectedCam === "cam_202" ? "var(--accent-purple)" : "" }}
        >
          CAM-202 (Emergency Stairs)
        </button>
      </div>

      {/* Camera Mock Graphics */}
      <div style={{
        position: "relative",
        height: "160px",
        background: "rgba(0,0,0,0.6)",
        border: "1px solid var(--border-glass)",
        borderRadius: "8px",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}>
        {/* CCTV Grid Lines */}
        <div style={{
          position: "absolute",
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "20px 20px"
        }} />
        
        {/* Rec indicator */}
        <div style={{ position: "absolute", top: 10, left: 10, display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "var(--accent-red)", display: "inline-block", animation: "pulse 1s infinite" }}></span>
          <span style={{ fontSize: "10px", color: "var(--text-muted)", fontWeight: "700" }}>REC [{selectedCam.toUpperCase()}]</span>
        </div>

        {/* Wireframe Graphic overlay */}
        {selectedCam === "cam_104" ? (
          <svg width="100" height="80" viewBox="0 0 100 80" style={{ opacity: 0.35 }}>
            <line x1="10" y1="70" x2="40" y2="10" stroke="#fff" strokeWidth="1.5" />
            <line x1="90" y1="70" x2="60" y2="10" stroke="#fff" strokeWidth="1.5" />
            {/* Queue rows */}
            <circle cx="25" cy="50" r="3" fill="#fff" />
            <circle cx="35" cy="50" r="3" fill="var(--accent-red)" />
            <circle cx="45" cy="55" r="3" fill="var(--accent-red)" />
            <circle cx="55" cy="60" r="3" fill="var(--accent-red)" />
            <circle cx="65" cy="50" r="3" fill="#fff" />
            <circle cx="75" cy="50" r="3" fill="#fff" />
            {/* Scan Area Box */}
            <rect x="30" y="20" width="40" height="30" fill="none" stroke="var(--accent-red)" strokeWidth="1" strokeDasharray="3 3" />
          </svg>
        ) : (
          <svg width="100" height="80" viewBox="0 0 100 80" style={{ opacity: 0.35 }}>
            {/* Stairs */}
            <path d="M 10 70 L 30 70 L 30 50 L 50 50 L 50 30 L 70 30 L 70 10 L 90 10" fill="none" stroke="#fff" strokeWidth="2" />
            {/* Obstacle Box */}
            <rect x="35" y="38" width="10" height="12" fill="var(--accent-red)" opacity="0.6" stroke="var(--accent-red)" strokeWidth="1.5" />
            {/* Target Crosshair */}
            <circle cx="40" cy="44" r="8" fill="none" stroke="var(--accent-red)" strokeWidth="1" strokeDasharray="2 2" />
          </svg>
        )}
        
        {/* Action Button Overlay */}
        {!report && !loading && (
          <button 
            className="crowd-alert-action-btn"
            onClick={handleInspect}
            style={{
              position: "absolute",
              background: "var(--accent-purple)",
              color: "#000",
              fontWeight: 700,
              border: "none",
              boxShadow: "var(--shadow-glow-purple)"
            }}
          >
            Run AI Vision Inspection
          </button>
        )}

        {loading && (
          <div style={{ color: "var(--accent-purple)", fontSize: "11px", fontWeight: "700" }}>
            Analyzing CCTV stream via Gemini Vision...
          </div>
        )}
      </div>

      {/* Vision Inspection Report Card */}
      {report && (
        <div className="copilot-response-box" style={{ 
          marginTop: 10, 
          background: report.hazard_detected ? "rgba(255, 23, 68, 0.03)" : "rgba(0, 230, 118, 0.03)", 
          borderColor: report.hazard_detected ? "rgba(255, 23, 68, 0.15)" : "rgba(0, 230, 118, 0.15)" 
        }}>
          <div className="copilot-response-header" style={{ marginBottom: 6 }}>
            <span className="copilot-badge" style={{ color: report.hazard_detected ? "var(--accent-red)" : "var(--accent-green)" }}>
              <ShieldAlert size={14} /> AI Vision Report
            </span>
            <span className="confidence-indicator" style={{ 
              color: report.hazard_detected ? "var(--accent-red)" : "var(--accent-green)",
              backgroundColor: report.hazard_detected ? "rgba(255, 23, 68, 0.15)" : "rgba(0, 230, 118, 0.15)"
            }}>
              Confidence: {report.confidence}%
            </span>
          </div>

          <p className="copilot-response-text" style={{ fontSize: "12px", marginBottom: 8 }}>
            {report.description}
          </p>

          {report.hazard_detected && (
            <div className="copilot-actions" style={{ padding: 8 }}>
              <span style={{ fontSize: "10px", fontWeight: "700", color: "var(--accent-red)", marginBottom: 2 }}>RECOMMENDED INTERVENTION:</span>
              <p style={{ fontSize: "11px", color: "#ccd6f6" }}>{report.action}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
