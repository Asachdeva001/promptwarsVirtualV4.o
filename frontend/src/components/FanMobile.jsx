import React, { useState, memo } from "react";
import { Send, Smartphone, Languages } from "lucide-react";
import { API_BASE_URL } from "../config";

const FanMobile = memo(function FanMobile() {
  const [lang, setLang] = useState("en");
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hello! I am your Stadium Copilot. How can I help you today?"
    }
  ]);
  const [loading, setLoading] = useState(false);

  // Preset prompts mapped to languages for premium localization UX
  const presets = {
    en: [
      { label: "Shortest Queue", text: "Where is the shortest line for food?" },
      { label: "Find Section 112", text: "How do I get to Section 112?" },
      { label: "Restroom Check", text: "Find nearest restroom" },
      { label: "ADA Access", text: "Is there wheelchair access?" }
    ],
    es: [
      { label: "Fila más Corta", text: "¿Dónde está la fila de comida más corta?" },
      { label: "Sección 112", text: "¿Cómo llego a la Sección 112?" },
      { label: "Baño Cercano", text: "Buscar el baño más cercano" },
      { label: "Acceso ADA", text: "¿Hay acceso para silla de ruedas?" }
    ],
    fr: [
      { label: "File d'attente", text: "Où est la file d'attente la plus courte pour manger?" },
      { label: "Section 112", text: "Comment se rendre à la section 112?" },
      { label: "Toilettes proches", text: "Trouver les toilettes les plus proches" },
      { label: "Accès ADA", text: "Y a-t-il un accès en fauteuil roulant?" }
    ],
    de: [
      { label: "Kürzeste Schlange", text: "Wo ist die kürzeste Schlange für Essen?" },
      { label: "Sektion 112", text: "Wie komme ich zu Sektion 112?" },
      { label: "Nächste WC", text: "Finde die nächste Toilette" },
      { label: "Rollstuhlzugang", text: "Gibt es einen Rollstuhlzugang?" }
    ],
    ar: [
      { label: "أقصر طابور", text: "أين أجد أقصر طابور للطعام؟" },
      { label: "القسم 112", text: "كيف أصل إلى القسم 112؟" },
      { label: "أقرب حمام", text: "أين أقرب دورة مياه؟" },
      { label: "كراسي متحركة", text: "هل يتوفر ممر للكراسي المتحركة؟" }
    ]
  };

  const handleLanguageChange = (newLang) => {
    setLang(newLang);
    // Add welcome bubble in selected language
    const welcomes = {
      en: "Hello! I am your Stadium Copilot. How can I help you today?",
      es: "¡Hola! Soy tu Copiloto del Estadio. ¿Cómo te puedo ayudar hoy?",
      fr: "Bonjour! Je suis votre Copilote du Stade. Comment puis-je vous aider aujourd'hui?",
      de: "Hallo! Ich bin Ihr Stadion-Copilot. Wie kann ich Ihnen heute helfen?",
      ar: "مرحباً! أنا مساعدك الذكي في الملعب. كيف يمكنني مساعدتك اليوم؟"
    };
    setMessages([
      { sender: "assistant", text: welcomes[newLang] }
    ]);
  };

  const handleSend = async (textToSend) => {
    if (!textToSend.trim()) return;

    // Append user message
    const newMessages = [...messages, { sender: "user", text: textToSend }];
    setMessages(newMessages);
    setLoading(true);
    setQuery("");

    try {
      const res = await fetch(`${API_BASE_URL}/api/fan/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: textToSend, language: lang })
      });
      const data = await res.json();
      
      setMessages([...newMessages, { sender: "assistant", text: data.response }]);
    } catch (err) {
      console.error("Error talking to Fan Copilot:", err);
      // Fail-safes
      setMessages([...newMessages, { 
        sender: "assistant", 
        text: "I'm sorry, I couldn't reach the server. Please check the network." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fan-panel">
      <div className="panel-header">
        <h2>
          <span className="bullet" style={{ backgroundColor: "var(--accent-purple)" }}></span>
          <Smartphone size={18} style={{ marginRight: 6 }} />
          Fan Copilot App
        </h2>
      </div>

      <div className="mobile-device">
        <div className="mobile-notch"></div>
        
        <div className="mobile-header">
          <span className="mobile-title">StadiumOS Fan</span>
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <Languages size={12} style={{ color: "var(--text-muted)" }} />
            <select 
              className="lang-selector" 
              value={lang} 
              onChange={(e) => handleLanguageChange(e.target.value)}
              aria-label="Select Fan App Language"
            >
              <option value="en">EN</option>
              <option value="es">ES</option>
              <option value="fr">FR</option>
              <option value="de">DE</option>
              <option value="ar">AR</option>
            </select>
          </div>
        </div>

        <div className="mobile-chat-body">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble ${msg.sender}`}>
              {msg.text.split("\n").map((line, lIdx) => (
                <div key={lIdx}>{line}</div>
              ))}
            </div>
          ))}
          {loading && (
            <div className="chat-bubble assistant" style={{ color: "var(--text-muted)" }}>
              Typing...
            </div>
          )}
        </div>

        {/* Dynamic Preset Bubbles based on selected language */}
        <div style={{ padding: "0 10px 8px 10px", background: "#151821" }}>
          <div className="presets-row" style={{ marginTop: 0 }}>
            {presets[lang].map((p, idx) => (
              <button 
                key={idx} 
                className="preset-chip" 
                style={{ fontSize: "10px", padding: "3px 8px", backgroundColor: "#1e2230" }}
                onClick={() => handleSend(p.text)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mobile-input-area">
          <input
            type="text"
            className="mobile-chat-input"
            placeholder={
              lang === "ar" ? "اسأل المساعد..." : 
              lang === "es" ? "Preguntar..." : 
              lang === "fr" ? "Demander..." : 
              lang === "de" ? "Fragen..." : "Ask Copilot..."
            }
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend(query)}
            aria-label="Fan Message Input"
          />
          <button className="mobile-send-btn" onClick={() => handleSend(query)} aria-label="Send Message">
            <Send size={12} />
          </button>
        </div>
      </div>
    </div>
  );
});

export default FanMobile;
