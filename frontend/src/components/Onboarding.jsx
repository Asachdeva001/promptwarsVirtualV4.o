import { useState, useEffect } from "react";
import { ArrowRight, MapPin, AlertCircle } from "lucide-react";
import { API_BASE_URL } from "../config";
import "./Onboarding.css";

export default function Onboarding({ onStadiumSelect }) {
  const [stadiums, setStadiums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStadiums() {
      try {
        setError(null);
        const res = await fetch(`${API_BASE_URL}/api/stadiums`);
        if (!res.ok) {
          throw new Error(`Failed to fetch stadiums (Status: ${res.status})`);
        }
        const data = await res.json();
        setStadiums(data);
      } catch (e) {
        console.error("Failed to fetch stadiums for onboarding:", e);
        setError("Failed to load host venues. Please check your connection and try again.");
      } finally {
        setLoading(false);
      }
    }
    fetchStadiums();
  }, []);

  if (loading) {
    return (
      <div className="onboarding-container loading-state" role="status" aria-live="polite">
        <div className="spinner" aria-hidden="true"></div>
        <p>Loading Host Venues...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="onboarding-container error-state" role="alert">
        <AlertCircle size={48} color="#ef4444" style={{ marginBottom: "16px" }} />
        <h2>Error Loading Venues</h2>
        <p>{error}</p>
        <button className="retry-btn" onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="onboarding-container">
      <div className="onboarding-glass">
        <div className="onboarding-header">
          <div className="nav-logo-icon" aria-hidden="true" style={{ width: 48, height: 48, fontSize: 24, margin: "0 auto 16px" }}>S</div>
          <h1>StadiumOS</h1>
          <p>Select your host venue to initialize the AI Copilot.</p>
        </div>
        
        <div className="stadium-list" role="list">
          {stadiums.map((stadium) => (
            <button 
              key={stadium.id} 
              className="stadium-card"
              onClick={() => onStadiumSelect(stadium.id)}
              aria-label={`Select ${stadium.name} located in ${stadium.location}`}
              role="listitem"
            >
              <div className="stadium-info">
                <h3>{stadium.name}</h3>
                <span className="stadium-loc">
                  <MapPin size={12} aria-hidden="true" /> {stadium.location}
                </span>
              </div>
              <ArrowRight size={20} className="stadium-arrow" aria-hidden="true" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
