import { useState, useEffect } from "react";
import { ArrowRight, MapPin } from "lucide-react";
import { API_BASE_URL } from "../config";
import "./Onboarding.css";

export default function Onboarding({ onStadiumSelect }) {
  const [stadiums, setStadiums] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStadiums() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/stadiums`);
        const data = await res.json();
        setStadiums(data);
      } catch (e) {
        console.error("Failed to fetch stadiums for onboarding:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchStadiums();
  }, []);

  if (loading) {
    return (
      <div className="onboarding-container loading-state">
        <div className="spinner"></div>
        <p>Loading Host Venues...</p>
      </div>
    );
  }

  return (
    <div className="onboarding-container">
      <div className="onboarding-glass">
        <div className="onboarding-header">
          <div className="nav-logo-icon" style={{ width: 48, height: 48, fontSize: 24, margin: "0 auto 16px" }}>S</div>
          <h1>StadiumOS</h1>
          <p>Select your host venue to initialize the AI Copilot.</p>
        </div>
        
        <div className="stadium-list">
          {stadiums.map((stadium) => (
            <button 
              key={stadium.id} 
              className="stadium-card"
              onClick={() => onStadiumSelect(stadium.id)}
            >
              <div className="stadium-info">
                <h3>{stadium.name}</h3>
                <span className="stadium-loc">
                  <MapPin size={12} /> {stadium.location}
                </span>
              </div>
              <ArrowRight size={20} className="stadium-arrow" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
