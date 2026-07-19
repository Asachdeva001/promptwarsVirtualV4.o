import React, { useState } from "react";
import { API_BASE_URL } from "../config";
import { Clock, User, CheckCircle2, AlertCircle } from "lucide-react";

export default function HelpRequestForm() {
  const [formData, setFormData] = useState({
    name: "",
    contact_number: "",
    assistance_type: "",
    location: ""
  });
  const [status, setStatus] = useState("idle"); // idle, submitting, success, error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("submitting");
    try {
      const res = await fetch(`${API_BASE_URL}/api/help/request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await res.json();

      if (res.ok && data.success) {
        setResult(data);
        setStatus("success");
      } else {
        throw new Error(data.detail || data.message || "Failed to submit request.");
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message);
      setStatus("error");
    }
  };

  if (status === "success" && result) {
    return (
      <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "16px", background: "rgba(0,0,0,0.2)", borderRadius: "12px", border: "1px solid var(--border-glass)", marginTop: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--accent-green)" }}>
          <CheckCircle2 size={24} />
          <h3 style={{ margin: 0 }}>Request Received!</h3>
        </div>
        
        <div style={{ background: "rgba(255,255,255,0.05)", padding: "16px", borderRadius: "8px" }}>
          <p style={{ margin: "0 0 12px 0", fontSize: "14px", color: "var(--text-secondary)" }}>A volunteer has been dispatched to your location.</p>
          
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
            <User size={16} color="var(--accent-blue)" />
            <span style={{ fontWeight: "600", fontSize: "15px" }}>{result.assigned_volunteer.name}</span>
            <span style={{ fontSize: "12px", padding: "2px 6px", background: "rgba(255,255,255,0.1)", borderRadius: "4px" }}>{result.assigned_volunteer.specialty}</span>
          </div>
          
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Clock size={16} color="var(--accent-purple)" />
            <span style={{ fontWeight: "500" }}>ETA: {result.eta_minutes} minutes</span>
          </div>
        </div>

        <button 
          onClick={() => { setStatus("idle"); setFormData({ name: "", contact_number: "", assistance_type: "", location: "" }); }}
          style={{ padding: "10px", background: "transparent", border: "1px solid var(--border-glass)", borderRadius: "6px", color: "white", cursor: "pointer", marginTop: "8px" }}
        >
          Submit Another Request
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "16px 10px" }}>
      <h3 style={{ marginBottom: "16px", fontSize: "16px" }}>Request Assistance</h3>
      
      {status === "error" && (
        <div style={{ padding: "10px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.4)", borderRadius: "6px", color: "#ef4444", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px", fontSize: "13px" }}>
          <AlertCircle size={14} />
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <div>
          <label style={{ display: "block", fontSize: "12px", marginBottom: "4px", color: "var(--text-secondary)" }}>Full Name</label>
          <input 
            type="text" 
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "10px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-glass)", borderRadius: "6px", color: "white" }}
          />
        </div>
        
        <div>
          <label style={{ display: "block", fontSize: "12px", marginBottom: "4px", color: "var(--text-secondary)" }}>Contact Number</label>
          <input 
            type="tel" 
            name="contact_number"
            value={formData.contact_number}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "10px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-glass)", borderRadius: "6px", color: "white" }}
          />
        </div>
        
        <div>
          <label style={{ display: "block", fontSize: "12px", marginBottom: "4px", color: "var(--text-secondary)" }}>Type of Assistance</label>
          <select 
            name="assistance_type"
            value={formData.assistance_type}
            onChange={handleChange}
            required
            style={{ width: "100%", padding: "10px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-glass)", borderRadius: "6px", color: "white" }}
          >
            <option value="" disabled>Select an option</option>
            <option value="Medical">Medical / First Aid</option>
            <option value="Directions">Directions / Escort</option>
            <option value="Security">Security Issue</option>
            <option value="Accessibility">Accessibility / Wheelchair</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontSize: "12px", marginBottom: "4px", color: "var(--text-secondary)" }}>Location (Section / Landmark)</label>
          <input 
            type="text" 
            name="location"
            value={formData.location}
            onChange={handleChange}
            required
            placeholder="e.g. Gate A, Section 112"
            style={{ width: "100%", padding: "10px", background: "rgba(0,0,0,0.3)", border: "1px solid var(--border-glass)", borderRadius: "6px", color: "white" }}
          />
        </div>

        <button 
          type="submit" 
          disabled={status === "submitting"}
          style={{ width: "100%", padding: "12px", background: "var(--accent-blue)", border: "none", borderRadius: "6px", color: "white", fontWeight: "600", marginTop: "8px", cursor: status === "submitting" ? "not-allowed" : "pointer" }}
        >
          {status === "submitting" ? "Submitting..." : "Request Help Now"}
        </button>
      </form>
    </div>
  );
}
