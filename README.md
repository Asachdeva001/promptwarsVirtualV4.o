# StadiumOS — AI Operations Platform for FIFA World Cup 2026

StadiumOS is an intelligent, real-time AI Operations Platform designed to streamline tournament operations, crowd control, volunteer dispatching, and fan assistance during the **FIFA World Cup 2026**. 

This repository implements a production-ready, modular system containing a **FastAPI backend** (representing the agent coordination layer) and a **Vite React frontend** styled with **premium vanilla CSS** (utilizing dark mode, glassmorphic surfaces, and micro-animations).

---

## 1. Chosen Vertical & Persona

- **Vertical**: Smart Stadiums & Tournament Operations
- **System Persona**: The operational command center for stadium organizers combined with a localized mobile assistant for event attendees. It links CCTV analytics, ticketing data, incident reports, and volunteer registries into one intelligent, predictive decision layer.

---

## 2. Solution Overview & Architecture

StadiumOS is built as a microservice-oriented dashboard:
```
                                 [Live Telemetry Inputs]
                     (CCTV feeds, ticket scanner speeds, active incidents)
                                            │
                                            ▼
                                  [FastAPI Backend (8000)]
                                            │
               ┌────────────────────────────┼───────────────────────────┐
               ▼                            ▼                           ▼
      [Crowd Agent]                 [Volunteer Agent]              [Fan Agent]
    (Congestion +15m)            (Distance-Workload Matrix)      (Multilingual FAQ)
               │                            │                           │
               └────────────────────────────┼───────────────────────────┘
                                            ▼
                                [Coordinator Agent (Gemini)]
                                            │
                                            ▼
                                [Vite React Frontend (3000)]
                     (Interactive Maps, Timelines, Mobile Copilot)
```

---

## 3. How the Solution Works (Core Features)

### 1. Operations Copilot
Organizers can query the dashboard in natural language (e.g. *"What are the biggest operational risks in the next 30 minutes?"*).
- **Logic**: The prompt is processed by the **Coordinator Agent**. If a `GEMINI_API_KEY` is present, it uses Gemini to generate response structures. Otherwise, it triggers a semantic rule-matching engine that evaluates current mock state variables.
- **Output**: Returns a risk summary, confidence rating, affected departments, and action cards with "Execute" buttons.

### 2. Predictive Crowd Intelligence
- **Logic**: Reads turnstile ticket scanning rates. If scanner throughput drops (e.g., hardware failure) or ticket density increases, the **Crowd Agent** predicts wait times 15-20 minutes in advance.
- **Action**: Provides alternate gate load-balancing recommendations. Clicking "Apply Reroute" shifts a percentage of incoming traffic from the bottlenecked gate to a free gate, dynamically updating wait times and logs.

### 3. AI Volunteer Coordinator
- **Logic**: When an incident occurs (e.g., Medical Alert in Section 112), the **Volunteer Agent** queries active volunteers.
- **Optimization Algorithm**: Computes a score based on Euclidean grid distance, current workload, and specialty matching:
  $$\text{Score} = \text{Distance} + (\text{Active Tasks} \times 15.0) + (\text{Specialty Mismatch Penalty} \times 30.0)$$
  The volunteer with the lowest score (closest, under-utilized, specialty-qualified) is recommended first.
- **Action**: Supports instant volunteer dispatching and incident status updates (Unassigned -> Assigned -> In Progress -> Resolved).

### 4. Fan Copilot (Multilingual Support)
- **Logic**: Implements a simulated smartphone app frame that supports 5 languages (English, Spanish, French, German, Arabic).
- **Capabilities**: Localized concession recommendations (pointing fans to the food court with the shortest queue), wheelchair accessibility guidance, and step-by-step indoor routing directions.

---

## 4. Tech Stack & Dependencies

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn
- **AI/LLM**: Google Generative AI (`google-generativeai` SDK)
- **Testing**: `pytest`, `httpx`

### Frontend
- **Framework**: Vite + React (JavaScript, React 19)
- **Styling**: Premium Vanilla CSS (custom glassmorphic theme, responsive grid)
- **Icons**: Lucide React

---

## 5. Getting Started & Access

StadiumOS has been deployed to Google Cloud for high availability and scalability.

**Live Frontend Dashboard (React + Vite)**:
- [https://stadiumos-frontend-1076364073843.us-central1.run.app](https://stadiumos-frontend-1076364073843.us-central1.run.app)

**Live Backend API (FastAPI)**:
- [https://stadiumos-backend-1076364073843.us-central1.run.app](https://stadiumos-backend-1076364073843.us-central1.run.app)

The backend is fully equipped with Gemini API integration. If rate limits are exceeded, it seamlessly falls back to a deterministic semantic rule engine, ensuring 100% uptime for operations.

---

## 6. Engineering Assumptions

1. **Stadium Grid Coordinates**: The stadium is mapped onto a simple 100x100 virtual grid representing relative distances. Euclidean distance serves as a proxy for physical walking distance within the stadium concourses.
2. **Real-time Synchronization**: The frontend uses a 5-second polling interval to coordinate data states (such as active incidents and volunteer assignments) from the backend, simulating a WebSocket telemetry flow.
3. **Turnstile Capacity**: Each ticketing gate is assumed to have 3 active scanners. Estimated wait times are derived from: `(queue length * scanning speed) / (60s * 3 turnstiles)`.
