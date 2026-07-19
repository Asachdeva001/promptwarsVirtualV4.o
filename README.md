# StadiumOS — AI Operations Platform for FIFA World Cup 2026

StadiumOS is an intelligent, real-time Fan Experience Platform designed to streamline tournament operations, provide multilingual assistance, and facilitate on-demand fan support during the **FIFA World Cup 2026**. 

This repository implements a production-ready, modular system containing a **FastAPI backend** (representing the agent coordination layer) and a **Vite React frontend** styled with **premium vanilla CSS** (utilizing dark mode, glassmorphic surfaces, and micro-animations).

---

## 1. Chosen Vertical & Persona

- **Vertical**: Smart Stadiums & Fan Experience
- **System Persona**: A localized mobile assistant (Fan Copilot) for event attendees. It allows fans to quickly query for directions, food wait times, restrooms, accessibility options, and request immediate physical assistance (such as medical help or wheelchair escorts).

---

## 2. Solution Overview & Architecture

StadiumOS is built as a microservice-oriented dashboard:
```
                                  [Fan Mobile App]
                      (Multilingual Chat, Help Requests)
                                             │
                                             ▼
                                   [FastAPI Backend]
                                             │
                                             ▼
                                        [Fan Agent]
                                   (Gemini-powered NLP)
```

---

## 3. How the Solution Works (Core Features)

### 1. Fan Copilot (Multilingual Support)
- **Logic**: Implements a simulated smartphone app frame that supports 5 languages (English, Spanish, French, German, Arabic).
- **Capabilities**: Localized concession recommendations (pointing fans to the food court with the shortest queue), wheelchair accessibility guidance, and step-by-step indoor routing directions.

### 2. Live Help Request Dispatcher
- **Logic**: Fans can fill out a simple "Request Help" form containing their location, contact info, and assistance type (or ask directly in the Copilot Chat). 
- **Action**: The system processes the request, selects an available idle volunteer from the live telemetry database, and instantly dispatches them, providing the fan with the volunteer's name, specialty, and a live ETA.

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
