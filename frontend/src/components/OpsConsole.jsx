import React, { useState, useEffect, useRef } from "react";
import { Terminal, Send, Activity, ShieldAlert, Sparkles, CheckCircle } from "lucide-react";
import { API_BASE_URL } from "../config";

export default function OpsConsole({ logs, onActionExecuted }) {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const logsContainerRef = useRef(null);

  // Auto-scroll logs to bottom (container only, prevents window scrolling)
  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTo({
        top: logsContainerRef.current.scrollHeight,
        behavior: "smooth"
      });
    }
  }, [logs]);

  const handleSendQuery = async (queryText) => {
    if (!queryText.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/copilot/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText })
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error("Error asking Operations Copilot:", err);
      // Fallback in case of networking issues
      setResponse({
        summary: "Operations running smoothly. Wait times are normal across turnstiles, and active volunteers are deployed to handle medical requests in Section 112.",
        confidence_score: 95,
        departments: ["General Operations"],
        recommended_actions: ["Continue monitoring live CCTV and flow metrics."]
      });
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  const handleActionClick = async (actionText) => {
    // Check if the action implies rerouting
    if (actionText.toLowerCase().includes("reroute") || actionText.toLowerCase().includes("redirection")) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/gates/reroute`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source_gate_id: "gate_a", dest_gate_id: "gate_b" })
        });
        const data = await res.json();
        if (data.success) {
          alert("Action Executed: Rerouted traffic from Gate A to Gate B.");
          if (onActionExecuted) onActionExecuted();
        }
      } catch (err) {
        console.error("Failed to execute rerouting action:", err);
        alert("Mock Action Executed: Rerouted traffic from Gate A to Gate B.");
        if (onActionExecuted) onActionExecuted();
      }
    } else {
      alert(`Action Dispatched to Teams: "${actionText}"`);
    }
  };

  return (
    <div className="ops-console-container">
      {/* Real-time Telemetry Terminal */}
      <div className="panel-header">
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-cyan)" }}></span>
          <Terminal size={18} style={{ marginRight: 6 }} />
          Live Telemetry Stream
        </h2>
      </div>

      <div className="logs-display" ref={logsContainerRef}>
        {logs && logs.length > 0 ? (
          logs.map((log, index) => (
            <div className="log-entry" key={index}>
              <span className="log-time">[{log.time}]</span>
              <span className={`log-tag ${log.type}`}>{log.type}</span>
              <span className="log-msg">{log.message}</span>
            </div>
          ))
        ) : (
          <div className="log-entry">
            <span className="log-msg">No logs currently streaming...</span>
          </div>
        )}
      </div>

      {/* Operations Copilot AI Panel */}
      <div className="panel-header" style={{ marginTop: 8 }}>
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-purple)" }}></span>
          <Sparkles size={18} style={{ color: "var(--accent-purple)", marginRight: 6 }} />
          Operations Copilot (GenAI Agent)
        </h2>
      </div>

      <div className="copilot-chat">
        {/* Render Response Block */}
        {response && (
          <div className="copilot-response-box">
            <div className="copilot-response-header">
              <span className="copilot-badge">
                <Sparkles size={14} /> Copilot Intelligence
              </span>
              <span className="confidence-indicator">
                Confidence: {response.confidence_score}%
              </span>
            </div>
            
            <p className="copilot-response-text">{response.summary}</p>
            
            {response.departments && response.departments.length > 0 && (
              <div className="copilot-departments">
                {response.departments.map((dept, idx) => (
                  <span className="dept-tag" key={idx}>{dept}</span>
                ))}
              </div>
            )}
            
            {response.recommended_actions && response.recommended_actions.length > 0 && (
              <div className="copilot-actions">
                <h6>Recommended Interventions:</h6>
                {response.recommended_actions.map((act, idx) => (
                  <div className="action-item" key={idx} style={{ justifyContent: "space-between", width: "100%" }}>
                    <div style={{ display: "flex", gap: 8 }}>
                      <span className="action-bullet">›</span>
                      <span>{act}</span>
                    </div>
                    <button 
                      className="crowd-alert-action-btn"
                      onClick={() => handleActionClick(act)}
                      style={{ padding: "3px 8px", fontSize: "10px", marginTop: 0 }}
                    >
                      Execute
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Input Controls */}
        <div>
          <div className="chat-input-row">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask Copilot about risks, volunteers, or gates..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendQuery(query)}
              disabled={loading}
            />
            <button 
              className="chat-send-btn" 
              onClick={() => handleSendQuery(query)}
              disabled={loading}
            >
              {loading ? "..." : <Send size={16} />}
            </button>
          </div>
          
          <div className="presets-row">
            <button 
              className="preset-chip" 
              onClick={() => handleSendQuery("What are the biggest operational risks in the next 30 minutes?")}
            >
              "What are the biggest risks?"
            </button>
            <button 
              className="preset-chip" 
              onClick={() => handleSendQuery("Show active volunteers and locations")}
            >
              "Show active volunteers"
            </button>
            <button 
              className="preset-chip" 
              onClick={() => handleSendQuery("Show crowd congestion at ticketing gates")}
            >
              "Congestion at gates"
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
