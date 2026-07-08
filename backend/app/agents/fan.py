from typing import Dict, List, Any
from app.mock_data import db

# Local translation dictionaries for key fan assistance concepts to ensure premium multilingual UX
TRANSLATIONS = {
    "es": {
        "welcome": "¡Hola! Soy tu Copiloto del Estadio. ¿Cómo te puedo ayudar hoy?",
        "food_recommendation": "Te recomiendo **{name}** en la Concurrencia {side}. El tiempo de espera es de solo **{wait} minutos**. Oferta: {offer}",
        "nav_directions": "Para llegar a la **{dest}** desde tu ubicación actual:\n1. Camina hacia el concourse principal.\n2. Sigue los letreros hacia el sector {sector}.\n3. Tu destino estará a la derecha.",
        "accessibility_info": "Las facilidades de accesibilidad están disponibles en **{name}**. Hay ascensores y rampas de acceso en el sector {sector}. Los voluntarios con chaleco amarillo pueden ayudarte.",
        "restroom_info": "El baño más cercano con menor espera es **{name}** (tiempo de espera: **{wait} min**). Cuenta con acceso para sillas de ruedas: {access}.",
        "unknown": "Lo siento, no entendí tu pregunta. Puedes preguntar sobre puestos de comida, baños, navegación a secciones o accesibilidad.",
        "yes": "Sí",
        "no": "No"
    },
    "fr": {
        "welcome": "Bonjour! Je suis votre Copilote du Stade. Comment puis-je vous aider aujourd'hui?",
        "food_recommendation": "Je recommande **{name}** sur le Concourse {side}. Le temps d'attente est de seulement **{wait} minutes**. Offre: {offer}",
        "nav_directions": "Pour vous rendre à la **{dest}** depuis votre position actuelle:\n1. Marchez vers le hall principal.\n2. Suivez les panneaux vers la section {sector}.\n3. Votre destination sera sur votre droite.",
        "accessibility_info": "Des installations adaptées sont disponibles à **{name}**. Des ascenseurs et rampes d'accès se trouvent à la section {sector}. Les bénévoles en gilet jaune sont là pour vous aider.",
        "restroom_info": "Les toilettes les plus proches avec le moins d'attente sont **{name}** (temps d'attente: **{wait} min**). Accessible en fauteuil roulant: {access}.",
        "unknown": "Désolé, je n'ai pas compris votre question. Vous pouvez poser des questions sur les stands de nourriture, les toilettes, la navigation ou l'accessibilité.",
        "yes": "Oui",
        "no": "Non"
    },
    "de": {
        "welcome": "Hallo! Ich bin Ihr Stadion-Copilot. Wie kann ich Ihnen heute helfen?",
        "food_recommendation": "Ich empfehle **{name}** auf der {side}-Promenade. Die Wartezeit beträgt nur **{wait} Minuten**. Angebot: {offer}",
        "nav_directions": "So gelangen Sie von Ihrem aktuellen Standort zu **{dest}**:\n1. Gehen Sie in Richtung der Hauptpromenade.\n2. Folgen Sie den Schildern zur Sektion {sector}.\n3. Ihr Ziel befindet sich auf der rechten Seite.",
        "accessibility_info": "Barrierefreie Einrichtungen finden Sie bei **{name}**. Aufzüge und Rampen befinden sich in Sektion {sector}. Volunteers in gelben Westen helfen Ihnen gerne weiter.",
        "restroom_info": "Die nächste Toilette mit der kürzesten Wartezeit ist **{name}** (Wartezeit: **{wait} Min**). Rollstuhlgerecht: {access}.",
        "unknown": "Entschuldigung, das habe ich nicht verstanden. Sie können nach Essensständen, WCs, Navigation zu Sektoren oder Barrierefreiheit fragen.",
        "yes": "Ja",
        "no": "Nein"
    },
    "ar": {
        "welcome": "مرحباً! أنا مساعدك الذكي في الملعب. كيف يمكنني مساعدتك اليوم؟",
        "food_recommendation": "أوصي بـ **{name}** في الممر {side}. وقت الانتظار **{wait} دقائق** فقط. العرض: {offer}",
        "nav_directions": "للوصول إلى **{dest}** من موقعك الحالي:\n1. توجه نحو الممر الرئيسي.\n2. اتبع اللوحات الإرشادية نحو القسم {sector}.\n3. ستجد وجهتك على اليمين.",
        "accessibility_info": "تتوفر مرافق سهولة الوصول في **{name}**. توجد مصاعد وممرات منحدرة في القسم {sector}. يمكن للمتطوعين بالسترات الصفراء مساعدتك.",
        "restroom_info": "أقرب دورة مياه بأقل وقت انتظار هي **{name}** (وقت الانتظار: **{wait} دقائق**). مجهزة لذوي الاحتياجات الخاصة: {access}.",
        "unknown": "عذراً، لم أفهم سؤالك. يمكنك الاستفسار عن مطاعم الأطعمة، دورات المياه، الملاحة، أو خدمات ذوي الاحتياجات الخاصة.",
        "yes": "نعم",
        "no": "لا"
    },
    "en": {
        "welcome": "Hello! I am your Stadium Copilot. How can I help you today?",
        "food_recommendation": "I recommend **{name}** on the {side} Concourse. The wait time is only **{wait} minutes**. Offer: {offer}",
        "nav_directions": "To get to **{dest}** from your current location:\n1. Walk toward the main concourse corridor.\n2. Follow signage directed toward Section {sector}.\n3. Your destination will be on the right.",
        "accessibility_info": "Accessibility accommodations are active at **{name}**. Ramps and elevators are positioned at Section {sector}. Volunteers in yellow vests are available to assist.",
        "restroom_info": "Nearest restroom with shortest wait is **{name}** (wait time: **{wait} mins**). Wheelchair access: {access}.",
        "unknown": "I'm sorry, I didn't quite catch that. You can ask about food stalls, restrooms, section navigation, or accessibility support.",
        "yes": "Yes",
        "no": "No"
    }
}

class FanExperienceAgent:
    def __init__(self):
        pass

    def handle_query(self, query: str, lang: str = "en") -> Dict[str, Any]:
        """
        Processes a fan's question and returns a localized helpful response.
        Translates text or yields structured recommendations for concessions, queues, restrooms, or directions.
        """
        q = query.lower()
        lang = lang.lower() if lang in TRANSLATIONS else "en"
        t = TRANSLATIONS[lang]
        
        # 1. Food / Concessions / queue check
        if any(w in q for w in ["food", "eat", "hungry", "beer", "drink", "burger", "taco", "churro", "queue", "line", "comida", "hambre", "nourriture", "manger", "essen", "أكل", "طعام"]):
            # Recommend food B (shorter wait time: 4m vs 18m)
            food_b = db.concessions[1]  # Tacos & Churros
            side_str = "East" if lang == "en" else ("Este" if lang == "es" else ("Est" if lang == "fr" else ("Ost" if lang == "de" else "الشرقي")))
            response = t["food_recommendation"].format(
                name=food_b["name"],
                side=side_str,
                wait=food_b["current_wait_time"],
                offer=food_b["special_offer"]
            )
            return {"response": response, "category": "Food"}
            
        # 2. Restrooms
        elif any(w in q for w in ["restroom", "toilet", "bathroom", "wc", "baño", "toilette", "toiletten", "حمام", "دورة مياه"]):
            restroom_b = db.concessions[3] # Restroom Hub 2 (wait time: 2 min)
            access_str = t["yes"] if restroom_b.get("accessibility_friendly", True) else t["no"]
            response = t["restroom_info"].format(
                name=restroom_b["name"],
                wait=restroom_b["current_wait_time"],
                access=access_str
            )
            return {"response": response, "category": "Restroom"}

        # 3. Accessibility
        elif any(w in q for w in ["accessible", "wheelchair", "disabled", "elevator", "ramp", "discapacidad", "rampa", "ascensor", "handicap", "fauteuil", "rampe", "barrierefrei", "rollstuhl", "ذوي الاحتياجات", "كرسي"]):
            response = t["accessibility_info"].format(
                name="Section 104 ADA Gate",
                sector="104"
            )
            return {"response": response, "category": "Accessibility"}

        # 4. Navigation
        elif any(w in q for w in ["navigate", "direction", "how to get", "go to", "section", "find my seat", "gate", "cómo llegar", "sección", "aller à", "wie komme ich", "كيف أصل", "طريق"]):
            # Parse target destination if mentioned
            dest = "Section 104"
            if "112" in q:
                dest = "Section 112"
            elif "gate b" in q:
                dest = "Gate B (North-East)"
            elif "gate a" in q:
                dest = "Gate A (North-West)"
                
            response = t["nav_directions"].format(
                dest=dest,
                sector="104 to 112"
            )
            return {"response": response, "category": "Navigation"}
            
        # Default fallback
        else:
            return {"response": t["unknown"], "category": "General"}

fan_agent = FanExperienceAgent()
