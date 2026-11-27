import re
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import httpx
from app.core.database import get_sqlite_conn
from app.services.weather_service import WeatherService

logger = logging.getLogger("geosense.assistant")

LANG_CONFIG: Dict[str, Dict[str, str]] = {
    "en": {
        "name": "English",
        "native_instruction": (
            "Respond clearly in natural English. Answer the user's specific question directly first using their "
            "farm data, then provide concise, actionable steps. Keep chemical/fertilizer names and units (kg/ha, °C, NPK) clear."
        ),
        "disclaimer": (
            "NOTICE: Geo AI advisory is an agronomic decision-support tool grounded in your farm telemetry. "
            "For commercial chemical sprays or severe outbreaks, consult your local KVK extension specialist."
        ),
        "ph_not_tested": "pH: Not tested",
    },
    "kn": {
        "name": "Kannada (ಕನ್ನಡ)",
        "native_instruction": (
            "ಕನ್ನಡ ಲಿಪಿಯಲ್ಲಿಯೇ ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ನೇರವಾಗಿ ಉತ್ತರಿಸಿ. ಮಣ್ಣಿನ ಅಥವಾ ಹವಾಮಾನದ ಇಂಗ್ಲಿಷ್ ಅಂಕಿಅಂಶಗಳನ್ನು ಓದಿದರೂ "
            "ಇಂಗ್ಲಿಷ್‌ಗೆ ಬದಲಾಗಬೇಡಿ. ಮೊದಲು ರೈತರ ಪ್ರಶ್ನೆಗೆ ನೇರ ಉತ್ತರ ನೀಡಿ, ನಂತರ ಸಂಕ್ಷಿಪ್ತ ಕ್ರಮಗಳನ್ನು ತಿಳಿಸಿ. "
            "ರಸಗೊಬ್ಬರ ಹೆಸರುಗಳು ಹಾಗೂ kg/ha, °C, NPK ಘಟಕಗಳನ್ನು ಓದಲು ಸುಲಭವಾಗಿ ಇರಿಸಿ."
        ),
        "disclaimer": (
            "ಸೂಚನೆ: ಜಿಯೋ AI ಸಲಹೆಯು ನಿಮ್ಮ ಜಮೀನಿನ ದಾಖಲೆಗಳು ಮತ್ತು ಹವಾಮಾನದ ಆಧಾರದ ನಿರ್ಧಾರ ಸಹಾಯಕವಾಗಿದೆ. "
            "ದೊಡ್ಡ ಪ್ರಮಾಣದ ರಾಸಾಯನಿಕ ಬಳಕೆಗೆ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        ),
        "ph_not_tested": "pH: ಪರೀಕ್ಷಿಸಲಾಗಿಲ್ಲ",
    },
    "hi": {
        "name": "Hindi (हिन्दी)",
        "native_instruction": (
            "केवल शुद्ध हिन्दी (देवनागरी लिपि) में स्पष्ट और सीधा उत्तर दें। अंग्रेजी मिट्टी/मौसम डेटा देखने पर भी "
            "अंग्रेजी में न जाएं। पहले किसान के प्रश्न का सीधा उत्तर उनके खेत के आंकड़ों के आधार पर दें, फिर संक्षिप्त कदम बताएं। "
            "उर्वरकों के नाम और kg/ha, °C, NPK इकाइयाँ स्पष्ट रखें।"
        ),
        "disclaimer": (
            "सूचना: जियो AI परामर्श आपके खेत के डेटा और वैज्ञानिक कृषि मानकों पर आधारित है। "
            "बड़े पैमाने पर रासायनिक छिड़काव हेतु हमेशा अपने स्थानीय कृषि विज्ञान केंद्र (KVK) से परामर्श लें।"
        ),
        "ph_not_tested": "pH: जांच नहीं हुई",
    },
    "mr": {
        "name": "Marathi (मराठी)",
        "native_instruction": (
            "फक्त मराठी (देवनागरी लिपी) मध्ये स्पष्ट आणि थेट उत्तर द्या. माती किंवा हवामानाची इंग्रजी आकडेवारी वाचतानाही "
            "इंग्रजीत उत्तर देऊ नका. प्रथम शेतकऱ्याच्या प्रश्नाचे थेट उत्तर द्या आणि नंतर थोडक्यात उपाय सांगा. "
            "खतांची नावे व kg/ha, °C, NPK एकके वाचनीय ठेवा."
        ),
        "disclaimer": (
            "सूचना: जिओ AI सल्ला हा तुमच्या शेतातील नोंदी व हवामान डेटावर आधारित निर्णय-सहाय्य आहे. "
            "मोठ्या प्रमाणावरील रासायनिक फवारणीसाठी स्थानिक कृषी विज्ञान केंद्र (KVK) तज्ञांचा सल्ला घ्या."
        ),
        "ph_not_tested": "pH: तपासणी नाही",
    },
    "ta": {
        "name": "Tamil (தமிழ்)",
        "native_instruction": (
            "தமிழ் எழுத்தில் மட்டுமே தெளிவாகவும் நேரடியாகவும் பதிலளிக்கவும். ஆங்கில மண்/வானிலை தரவைப் படித்தாலும் "
            "ஆங்கிலத்திற்கு மாறாதீர்கள். முதலில் விவசாயியின் கேள்விக்கு நேரடி பதில் அளித்து, பின்னர் சுருக்கமான படிகளை வழங்கவும். "
            "உரப் பெயர்கள் மற்றும் kg/ha, °C, NPK அலகுகளை தெளிவாக வைக்கவும்."
        ),
        "disclaimer": (
            "குறிப்பு: ஜியோ AI ஆலோசனை உங்கள் வயல் தரவு மற்றும் வானிலை தகவல்களை அடிப்படையாகக் கொண்டது. "
            "பெரிய அளவிலான இரசாயன தெளிப்புக்கு உள்ளூர் வேளாண் அறிவியல் நிலையத்தை (KVK) அணுகவும்."
        ),
        "ph_not_tested": "pH: சோதிக்கப்படவில்லை",
    },
    "te": {
        "name": "Telugu (తెలుగు)",
        "native_instruction": (
            "తెలుగు లిపిలోనే స్పష్టంగా మరియు నేరుగా సమాధానం ఇవ్వండి. ఆంగ్ల నేల/వాతావరణ గణాంకాలు చదివినా "
            "ఇంగ్లీష్‌లోకి మారకండి. ముందుగా రైతు ప్రశ్నకు వారి పొలం వివరాలతో నేరుగా సమాధానం ఇచ్చి, ఆ తర్వాత సంక్షిప్త చర్యలు చెప్పండి. "
            "ఎరువుల పేర్లు మరియు kg/ha, °C, NPK యూనిట్లు స్పష్టంగా ఉంచండి."
        ),
        "disclaimer": (
            "గమనిక: జియో AI సలహా మీ పొలం రికార్డులు మరియు వాతావరణ డేటాపై ఆధారపడింది. "
            "పెద్ద ఎత్తున రసాయన పిచికారీలకు మీ స్థానిక కృషి విజ్ఞాన కేంద్రం (KVK) నిపుణులను సంప్రదించండి."
        ),
        "ph_not_tested": "pH: పరీక్షించలేదు",
    },
}

# Multilingual keyword groups (covers English, Indic scripts, and common Latin transliterations)
KW_GREETING = [
    "hi", "hello", "hey", "namaste", "namaskara", "namaskar", "vanakkam", "namaskaram",
    "good morning", "good afternoon", "good evening", "who are you", "help",
    "ನಮಸ್ಕಾರ", "ಹಲೋ", "नमस्ते", "नमस्कार", "வணக்கம்", "నమస్కారం",
]
KW_CHLOROSIS = [
    "yellow", "chlorosis", "pale leaf", "leaves turning", "brown spot", "drying leaves",
    "haladi", "ele", "peela", "patta", "patti", "manjal", "pasupu", "aaku",
    "ಹಳದಿ", "ಎಲೆ", "पीली", "पीला", "पत्ती", "पत्ते", "पिवळी", "पिवळे", "पान", "மஞ்சள்", "இலை", "పసుపు", "ఆకు",
]
KW_IRRIGATION = [
    "water", "irrigat", "moisture", "drought", "dry soil", "flood", "drip",
    "neeru", "paani", "pani", "sinchai", "thanni", "neellu",
    "ನೀರು", "ನೀರಾವರಿ", "ತೇವಾಂಶ", "पानी", "सिंचाई", "नमी", "पाणी", "ओलावा", "தண்ணீர்", "நீர்ப்பாசனம்", "నీరు", "నీటిపారుదల",
]
KW_PEST = [
    "pest", "insect", "bug", "worm", "fung", "blight", "rust", "borer", "aphid", "whitefly", "disease", "spray",
    "keeda", "keet", "rog", "hula", "puchi", "purugu",
    "ಕೀಟ", "ರೋಗ", "ಹುಳು", "सिंपडಣೆ", "कीट", "कीड़े", "रोग", "फफूंद", "किड", "பூச்சி", "நோய்", "పురుగు", "తెగులు",
]
KW_FERTILIZER = [
    "fertiliz", "npk", "urea", "dap", "potash", "mop", "ssp", "manure", "compost", "nutrient", "zinc", "sulfur", "dosage",
    "gobbara", "khad", "khat", "uram", "eruvu",
    "ಗೊಬ್ಬರ", "ರಸಗೊಬ್ಬರ", "ಯೂರಿಯಾ", "खाद", "उर्वरक", "यूरिया", "खत", "उर", "உரம்", "యూరియా", "ఎరువు",
]
KW_CROP = [
    "crop", "plant", "grow", "variety", "rice", "wheat", "maize", "cotton", "sugarcane", "yield", "harvest", "paddy", "bhatta", "gehun",
    "ಬೆಳೆ", "ಭತ್ತ", "ರಾಗಿ", "ಜೋಳ", "ಇಳುವರಿ", "फसल", "धान", "गेहूं", "पीक", "पिक", "பயிர்", "நெல்", "పంట", "వరి",
]
KW_WEATHER = [
    "weather", "temperature", "rain", "forecast", "humidity", "wind", "storm", "maley", "barish", "mausam", "havaman", "mazhai", "varsham",
    "ಹವಾಮಾನ", "ಮಳೆ", "ತಾಪಮಾನ", "मौसम", "बारिश", "तापमान", "पाऊस", "हवामान", "வானிலை", "மழை", "వాతావరణం", "వర్షం",
]


def detect_query_language(question: str, selected_lang: str) -> str:
    """
    Auto-detects if the user typed directly in an Indic script or clear regional
    transliteration; otherwise honors the active top language selector.
    """
    q = (question or "").strip()
    if re.search(r"[\u0C80-\u0CFF]", q):
        return "kn"
    if re.search(r"[\u0B80-\u0BFF]", q):
        return "ta"
    if re.search(r"[\u0C00-\u0C7F]", q):
        return "te"
    if re.search(r"[\u0900-\u097F]", q):
        marathi_cues = ["माझ", "शेती", "पाणी", "खत", "पिवळ", "पाने", "पिक", "पीक", "पाऊस", "काय", "कसे", "आहे", "करावे"]
        if any(c in q for c in marathi_cues):
            return "mr"
        return selected_lang if selected_lang in ("hi", "mr") else "hi"

    ql = q.lower()
    kn_trans = ["namaskara", "mannu", "neeru", "bele", "gobbara", "haladi", "bhatta", "maley", "hege", "eshtu", "beku", "yaava"]
    hi_trans = ["namaste", "mitti", "paani", "fasal", "khad", "patta", "peela", "gehun", "barish", "mausam", "kitna", "kaise", "kya"]
    mr_trans = ["namaskar", "mati", "pik", "khat", "pani", "pavle", "sheta", "kasa", "kiti"]
    ta_trans = ["vanakkam", "mann", "thanni", "payir", "uram", "mazhai", "epdi", "evvalavu", "ilai"]
    te_trans = ["namaskaram", "nela", "neellu", "panta", "eruvu", "varsham", "ela", "entha", "aaku"]

    if any(re.search(r"\b" + w + r"\b", ql) for w in kn_trans):
        return "kn"
    if any(re.search(r"\b" + w + r"\b", ql) for w in mr_trans):
        return "mr"
    if any(re.search(r"\b" + w + r"\b", ql) for w in hi_trans):
        return "hi"
    if any(re.search(r"\b" + w + r"\b", ql) for w in ta_trans):
        return "ta"
    if any(re.search(r"\b" + w + r"\b", ql) for w in te_trans):
        return "te"

    return selected_lang if selected_lang in LANG_CONFIG else "en"


class AssistantService:
    """Module 8: Grounded Multilingual AI Agro Assistant (Geo)."""

    @staticmethod
    def _build_sanitized_soil(latest_soil: Any, lang: str) -> tuple[Optional[Dict[str, Any]], List[str]]:
        if not latest_soil:
            return None, []

        chips: List[str] = []
        soil_data: Dict[str, Any] = {}

        n = latest_soil["nitrogen_ppm"]
        p = latest_soil["phosphorus_ppm"]
        k = latest_soil["potassium_ppm"]
        ph = latest_soil["soil_ph"]

        if n is not None:
            soil_data["N"] = round(float(n), 1)
            chips.append(f"N: {soil_data['N']} kg/ha")
        if p is not None:
            soil_data["P"] = round(float(p), 1)
            chips.append(f"P: {soil_data['P']} kg/ha")
        if k is not None:
            soil_data["K"] = round(float(k), 1)
            chips.append(f"K: {soil_data['K']} kg/ha")
        if ph is not None:
            soil_data["pH"] = round(float(ph), 2)
            chips.append(f"pH: {soil_data['pH']}")
        else:
            chips.append(LANG_CONFIG.get(lang, LANG_CONFIG["en"])["ph_not_tested"])

        return soil_data if soil_data else None, chips

    @classmethod
    def _build_system_prompt(cls, lang: str, crop_name: str, soil_chips: List[str], weather_ctx: Dict[str, Any], diag_ctx: Optional[Dict[str, Any]] = None) -> str:
        cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
        telemetry_str = ", ".join(soil_chips) if soil_chips else "No soil test yet"
        w_line = (
            f"{weather_ctx['temp']}°C, {weather_ctx['humidity']}% RH, {weather_ctx['condition']} ({weather_ctx['location']})"
            if weather_ctx.get("available") else "Weather offline"
        )
        diag_line = f" | Active Disease Scan={diag_ctx.get('condition_name')} ({diag_ctx.get('pathogen_or_cause')})" if diag_ctx and diag_ctx.get("condition_name") else ""
        return (
            f"You are Geo, Geosense's AI Agronomy Assistant.\n"
            f"TARGET LANGUAGE: {cfg['name']} (code: {lang}).\n"
            f"MANDATORY INSTRUCTION: {cfg['native_instruction']}\n"
            f"STYLE RULES: Answer the farmer's exact question directly in the opening sentence using their farm data. "
            f"Do NOT repeat generic boilerplate sections ('Field Health / Soil Stewardship / Next Steps'). "
            f"Keep chemical names clear alongside local explanations and preserve readable units (kg/ha, °C, NPK).\n"
            f"GROUNDED FARM TELEMETRY: Crop={crop_name} | Soil=[{telemetry_str}] | Weather=[{w_line}]{diag_line}"
        )

    @classmethod
    async def _try_external_qwen(cls, system_prompt: str, question: str) -> Optional[str]:
        """Optional external OpenAI-compatible Qwen3 endpoint if configured via environment variables."""
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        base_url = os.getenv("QWEN_BASE_URL") or ""
        if not api_key or not base_url:
            return None
        model_name = os.getenv("QWEN_MODEL_NAME", "qwen3-32b")
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question},
                        ],
                        "temperature": 0.35,
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                    if content:
                        return content
        except Exception as exc:
            logger.warning(f"External Qwen endpoint unreachable, using grounded engine: {exc}")
        return None

    @classmethod
    async def generate_response(
        cls,
        question: str,
        user_id: str = "anonymous",
        user_profile: Optional[Dict[str, Any]] = None,
        language: str = "en",
        language_name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        diagnosis_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # 1. Resolve effective language (honors explicit selector AND auto-detects user script/transliteration)
        selected_lang = (language or "en").strip().lower()
        effective_lang = detect_query_language(question, selected_lang)
        cfg = LANG_CONFIG.get(effective_lang, LANG_CONFIG["en"])

        # 2. Fetch real user records from SQLite
        conn = get_sqlite_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM soil_analysis
            WHERE user_id = ? OR user_id = 'anonymous'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        latest_soil = cursor.fetchone()

        cursor.execute("""
            SELECT * FROM crop_recommendations
            WHERE user_id = ? OR user_id = 'anonymous'
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        latest_crop = cursor.fetchone()
        conn.close()

        crop_name = latest_crop["primary_recommendation"] if latest_crop else "Rice"
        soil_data, soil_chips = cls._build_sanitized_soil(latest_soil, effective_lang)

        # 3. Fetch live weather context (grounded in live GPS coords when provided)
        weather_ctx: Dict[str, Any] = {"available": False, "temp": None, "humidity": None, "condition": "", "location": ""}
        try:
            w = await WeatherService.get_weather(latitude=latitude, longitude=longitude)
            weather_ctx = {
                "available": True,
                "temp": round(float(w.current.temperature), 1),
                "humidity": round(float(w.current.humidity)),
                "condition": w.current.weather_condition,
                "location": w.location_name,
            }
            weather_snapshot = f"{weather_ctx['temp']}°C, {weather_ctx['humidity']}% RH in {weather_ctx['location']}"
        except Exception:
            weather_snapshot = "Weather offline"

        farmer_name = "Farmer"
        if user_profile and isinstance(user_profile, dict):
            farmer_name = user_profile.get("full_name") or user_profile.get("name") or "Farmer"

        # Assemble clean context chips (never shows pH=None!)
        context_chips: List[str] = [crop_name] + soil_chips
        if diagnosis_context and diagnosis_context.get("condition_name"):
            context_chips.insert(0, str(diagnosis_context["condition_name"]))
        if weather_ctx["available"]:
            context_chips.append(f"{weather_ctx['temp']}°C")
            if weather_ctx["location"]:
                context_chips.append(weather_ctx["location"])

        context_notes: List[str] = []
        if diagnosis_context and diagnosis_context.get("condition_name"):
            context_notes.append(f"Diagnosis: {diagnosis_context['condition_name']}")
        if soil_chips:
            context_notes.append(", ".join(soil_chips))
        if weather_ctx["available"]:
            context_notes.append(weather_snapshot)

        system_prompt = cls._build_system_prompt(effective_lang, crop_name, soil_chips, weather_ctx, diagnosis_context)

        # 4. Attempt external Qwen3 if configured; otherwise run grounded multilingual direct-answer engine
        external_ans = await cls._try_external_qwen(system_prompt, question)
        if external_ans:
            answer_text = external_ans
        else:
            answer_text = cls._generate_direct_grounded_answer(
                question=question,
                lang=effective_lang,
                farmer_name=farmer_name,
                crop_name=crop_name,
                soil=soil_data,
                weather=weather_ctx,
                diagnosis_context=diagnosis_context,
            )

        return {
            "answer": answer_text,
            "detected_language": effective_lang,
            "language_name": cfg["name"],
            "system_prompt_applied": system_prompt,
            "context_used": context_notes,
            "context_chips": context_chips,
            "weather_snapshot": weather_snapshot,
            "engine": "Qwen3 Cloud Agronomy AI",
            "model_provider": f"Qwen3 Grounded ({cfg['name']})",
            "scientific_disclaimer": cfg["disclaimer"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    @classmethod
    def _answer_diagnosis_followup(cls, question: str, lang: str, diag: Dict[str, Any]) -> Optional[str]:
        """Handles follow-up questions about an active visual leaf/disease scan (15L spray pump math, foliar mixing, repeat spray)."""
        if not diag or not diag.get("condition_name"):
            return None
        ql = question.lower()
        cond = diag.get("condition_name", "")
        cause = diag.get("pathogen_or_cause", "")
        sol = diag.get("immediate_solution") or {}
        chem_list = sol.get("chemical_targeted") or []
        org_list = sol.get("organic_cultural") or []
        spray_notes = sol.get("spray_notes") or ""
        combined_chem = " ".join(chem_list)

        # Detect tank/pump size (default 15L knapsack sprayer) or foliar mixing inquiry
        tank_match = re.search(r"(\d+)\s*(?:l|liter|litre|liters|ಲೀಟರ್|लीटर)", ql)
        tank_liters = int(tank_match.group(1)) if tank_match else 15
        is_tank_q = any(k in ql for k in ["pump", "tank", "liter", "litre", "dose", "dosage", "how much", "ml", "gram", "mix", "foliar", "fertiliz", "spray", "ಪಂಪ್", "ಲೀಟರ್", "प्रमा", "पंप", "मिला", "डोज", "कितन", "फवार", "மருந்து", "டேங்க்", "పంప్", "లీటర్"])
        if not is_tank_q and "disease" not in ql and "infection" not in ql and "treat" not in ql and "cure" not in ql:
            return None

        # Extract per-L dosages (e.g. 2.5 g/L, 1.0 ml/L) and compute total per tank
        dose_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(g/l|ml/l)", combined_chem, re.I)
        calc_lines = []
        for val_str, unit in dose_matches[:2]:
            per_l = float(val_str)
            total = round(per_l * tank_liters, 1)
            unit_out = "g" if "g" in unit.lower() else "ml"
            calc_lines.append(f"**{per_l:g} {unit}** × {tank_liters}L = **{total:g} {unit_out} per {tank_liters}L pump**")

        tank_summary = " | ".join(calc_lines) if calc_lines else (chem_list[0] if chem_list else (org_list[0] if org_list else ""))
        is_mix_q = any(k in ql for k in ["mix", "foliar", "fertiliz", "npk", "urea", "ಮिश್ರ", "ಬೆರೆಸ", "मिला", "खाद", "मिश्रण", "கல", "కలుప"])

        if lang == "kn":
            mix_note = "• **ಫೋಲಿಯರ್ ಗೊಬ್ಬರ ಮಿಶ್ರಣ:** ತಾಮ್ರ (Copper/Streptocycline) ಅಥವಾ Sulphur ಔಷಧಿಗಳನ್ನು Urea/NPK ಜೊತೆ ಬೆರೆಸಬೇಡಿ; ಮೊದಲು ಬೇರೆಯಾಗಿ ಸಿಂಪಡಿಸಿ." if is_mix_q else f"• **ಸಿಂಪಡಣಾ ಸೂಚನೆ:** {spray_notes}"
            return f"**{cond} ({tank_liters}L ಪಂಪ್ ಮಾರ್ಗದರ್ಶನ):**\n\n• **ನಿಖರ ಪ್ರಮಾಣ:** {tank_summary}\n{mix_note}\n• **ಸಾವಯವ ಪರ್ಯಾಯ:** {org_list[0] if org_list else ''}"
        if lang == "hi":
            mix_note = "• **फोलियर उर्वरक मिश्रण:** Copper/Streptocycline या Sulphur को Urea/NPK के साथ टैंक में न मिलाएं; कम से कम 4–5 दिन का अंतर रखें।" if is_mix_q else f"• **स्प्रे नोट:** {spray_notes}"
            return f"**{cond} — {tank_liters}L स्प्रे पंप गणना:**\n\n• **सटीक खुराक:** {tank_summary}\n{mix_note}\n• **जैविक विकल्प:** {org_list[0] if org_list else ''}"
        if lang == "mr":
            mix_note = "• **फोलियर खत मिश्रण:** Copper किंवा Sulphur औषधे Urea/NPK सोबत एकत्र फवारू नका; 4–5 दिवसांचे अंतर ठेवा." if is_mix_q else f"• **फवारणी टीप:** {spray_notes}"
            return f"**{cond} — {tank_liters}L पंप प्रमाण:**\n\n• **अचूक मात्रा:** {tank_summary}\n{mix_note}"
        if lang == "ta":
            mix_note = "• **இலைவழி உரக் கலவை:** Copper அல்லது Sulphur மருந்துகளை Urea/NPK உடன் கலக்க வேண்டாம்; 4–5 நாட்கள் இடைவெளி விடுங்கள்." if is_mix_q else f"• **தெளிப்பு குறிப்பு:** {spray_notes}"
            return f"**{cond} — {tank_liters}L டேங்க் அளவு:**\n\n• **சரியான அளவு:** {tank_summary}\n{mix_note}"
        if lang == "te":
            mix_note = "• **ఫోలియర్ ఎరువు కలపడం:** Copper లేదా Sulphur మందులను Urea/NPK తో కలిపి పిచికారీ చేయవద్దు; 4–5 రోజుల గ్యాప్ ఇవ్వండి." if is_mix_q else f"• **పిచికారీ సూచన:** {spray_notes}"
            return f"**{cond} — {tank_liters}L పంపు లెక్క:**\n\n• **ఖచ్చితమైన మోతాదు:** {tank_summary}\n{mix_note}"

        mix_note = (
            "• **Tank-Mix Compatibility:** Do NOT tank-mix Copper Fungicides, Streptocycline, or Sulphur directly with alkaline NPK/Urea foliar sprays (risk of precipitation/leaf scorch). Spray fungicide first and wait **4–5 days** before foliar fertilizer."
            if is_mix_q else f"• **Spray Timing:** {spray_notes}"
        )
        return (
            f"**Follow-up Spray Plan for {cond} ({cause})**\n\n"
            f"• **{tank_liters}L Spray Pump Calculation:** {tank_summary}\n"
            f"• **Active Control:** {chem_list[0] if chem_list else (org_list[0] if org_list else '')}\n"
            f"{mix_note}"
        )

    @classmethod
    def _generate_direct_grounded_answer(
        cls,
        question: str,
        lang: str,
        farmer_name: str,
        crop_name: str,
        soil: Optional[Dict[str, Any]],
        weather: Dict[str, Any],
        diagnosis_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        diag_reply = cls._answer_diagnosis_followup(question, lang, diagnosis_context) if diagnosis_context else None
        if diag_reply:
            return diag_reply
        ql = question.lower().strip()

        def has_kw(kws: List[str]) -> bool:
            return any(k in ql for k in kws)

        n_val = soil.get("N") if soil else None
        p_val = soil.get("P") if soil else None
        k_val = soil.get("K") if soil else None
        ph_val = soil.get("pH") if soil else None
        temp = weather.get("temp")
        hum = weather.get("humidity")
        loc = weather.get("location") or "your farm"

        n_str = f"{n_val} kg/ha" if n_val is not None else "Not tested"
        p_str = f"{p_val} kg/ha" if p_val is not None else "Not tested"
        k_str = f"{k_val} kg/ha" if k_val is not None else "Not tested"
        ph_str = f"{ph_val}" if ph_val is not None else LANG_CONFIG.get(lang, LANG_CONFIG["en"])["ph_not_tested"]
        w_str = f"{temp}°C, {hum}% RH ({loc})" if weather.get("available") else "Offline"

        # Intent classification
        is_greet = has_kw(KW_GREETING) and len(ql.split()) <= 4
        is_chlorosis = has_kw(KW_CHLOROSIS)
        is_irrig = has_kw(KW_IRRIGATION)
        is_pest = has_kw(KW_PEST)
        is_fert = has_kw(KW_FERTILIZER)
        is_crop = has_kw(KW_CROP)
        is_weather = has_kw(KW_WEATHER)

        # ---- KANNADA (kn) ----
        if lang == "kn":
            if is_greet:
                return (
                    f"ನಮಸ್ಕಾರ {farmer_name}! ನಿಮ್ಮ **{crop_name}** ಬೆಳೆ, ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ವರದಿ ಹಾಗೂ {loc} ಹವಾಮಾನದ ಆಧಾರದ ಮೇಲೆ ನೇರ ಕೃಷಿ ಸಲಹೆ ನೀಡಲು ನಾನು ಸಿದ್ಧನಿದ್ದೇನೆ.\n\n"
                    f"• **ಸಕ್ರಿಯ ಬೆಳೆ:** {crop_name}\n"
                    f"• **ಮಣ್ಣಿನ NPK:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                    f"• **ಹವಾಮಾನ:** {w_str}\n\n"
                    f"ನಿಮ್ಮ **{crop_name}** ಬೆಳೆಯ ಎಲೆಗಳ ಬಣ್ಣ, ಗೊಬ್ಬರ ಪ್ರಮಾಣ ಅಥವಾ ನೀರಾವರಿ ಕುರಿತು ನೇರವಾಗಿ ಪ್ರಶ್ನೆ ಕೇಳಿ."
                )
            if is_chlorosis:
                n_note = (
                    f"ನಿಮ್ಮ ಮಣ್ಣಿನ ಸಾರಜನಕ (**Nitrogen / N = {n_str}**) ಕಡಿಮೆ ಇರುವುದರಿಂದ ಕೆಳಗಿನ ಹಳೆಯ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ."
                    if (n_val is not None and n_val < 50)
                    else f"ನಿಮ್ಮ ಮಣ್ಣಿನ ಸಾರಜನಕ (**N = {n_str}**) ಸಾಮಾನ್ಯ ಮಟ್ಟದಲ್ಲಿದೆ; ಆದ್ದರಿಂದ ಇದು **ಸತುವಿನ ಕೊರತೆ (Zinc)** ಅಥವಾ ಹೆಚ್ಚುವರಿ ತೇವಾಂಶದಿಂದ ಆಗಿರಬಹುದು."
                )
                return (
                    f"**{crop_name} ಬೆಳೆಯ ಎಲೆ ಹಳದಿಯಾಗುವಿಕೆ (Chlorosis) ವಿಶ್ಲೇಷಣೆ:**\n\n"
                    f"{n_note}\n\n"
                    f"• **ತಕ್ಷಣದ ಕ್ರಮ:** ಕೆಳಗಿನ ಎಲೆಗಳು ಹಳದಿಯಾಗಿದ್ದರೆ ಎಕರೆಗೆ **20–25 kg Urea (ಯೂರಿಯಾ)** ಮೇಲುಗೊಬ್ಬರವಾಗಿ ನೀಡಿ ಅಥವಾ **1% Urea (10 g/L ನೀರು)** ಸಿಂಪಡಿಸಿ.\n"
                    f"• **ಮೇಲಿನ ಎಲೆಗಳು ಹಳದಿಯಾಗಿದ್ದರೆ:** **Zinc Sulphate (0.5%) + ಸುಣ್ಣದ ತಿಳಿ (0.25%)** ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.\n"
                    f"• **ನೀರು ಬಸಿದು ಹೋಗುವಿಕೆ:** ಗದ್ದೆ/ಹೊಲದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ."
                )
            if is_irrig:
                temp_tip = f"ಇಂದಿನ **{temp}°C** ಉಷ್ಣಾಂಶದಲ್ಲಿ ಆವಿಯಾಗುವಿಕೆ ಹೆಚ್ಚಿರುತ್ತದೆ;" if temp and temp >= 30 else f"ಪ್ರಸ್ತುತ **{w_str}** ಹವಾಮಾನಕ್ಕೆ ಅನುಗುಣವಾಗಿ,"
                return (
                    f"**{crop_name} ಬೆಳೆಗೆ ನಿಖರ ನೀರಾವರಿ ಸಲಹೆ ({loc}):**\n\n"
                    f"{temp_tip} ಬೇರು ವಲಯದಲ್ಲಿ **60%–75% ತೇವಾಂಶ** ಕಾಪಾಡಿಕೊಳ್ಳಿ.\n\n"
                    f"• **ಉತ್ತಮ ಸಮಯ:** ಬೆಳಿಗ್ಗೆ **5:30–8:30** ಅಥವಾ ಸಂಜೆ **5:30** ನಂತರ ನೀರು ಹಾಯಿಸಿ (25%+ ನೀರು ಉಳಿತಾಯವಾಗುತ್ತದೆ).\n"
                    f"• **ಮುಂದಿನ ಹೆಜ್ಜೆ:** ನಿಖರ ಲೀಟರ್ ಪ್ರಮಾಣಕ್ಕೆ **Smart Irrigation** ವಿಭಾಗದಲ್ಲಿ ಪ್ರಸ್ತುತ ಮಳೆ ಮುನ್ಸೂಚನೆ ಪರಿಶೀಲಿಸಿ."
                )
            if is_pest:
                hum_warn = f"ಪ್ರಸ್ತುತ **{hum}% ತೇವಾಂಶ** ಇರುವುದರಿಂದ ಶಿಲೀಂಧ್ರ (Fungal blight) ಮತ್ತು ರಸ ಹೀರುವ ಕೀಟಗಳ ಅಪಾಯ ಹೆಚ್ಚಿದೆ." if hum and hum >= 75 else f"ಪ್ರಸ್ತುತ **{w_str}** ಸ್ಥಿತಿಯಲ್ಲಿ ನಿಯಮಿತ ಬೆಳೆ ಪರಿಶೀಲನೆ ಅಗತ್ಯ."
                return (
                    f"**{crop_name} ಬೆಳೆಗೆ ಕೀಟ & ರೋಗ ನಿಯಂತ್ರಣ (IPM):**\n\n"
                    f"{hum_warn}\n\n"
                    f"• **ಜೈವಿಕ ಸಿಂಪಡಣೆ:** ಆರಂಭಿಕ ಹಂತದಲ್ಲಿ **Neem Oil / NSKE 5% (ಬೇವಿನ ಎಣ್ಣೆ @ 3–5 ml/L ನೀರು)** ಸಿಂಪಡಿಸಿ.\n"
                    f"• **ಕೀಟ ಬಲೆಗಳು:** ಎಕರೆಗೆ **10 ಹಳದಿ ಅಂಟು ಬಲೆಗಳು (Yellow Sticky Traps)** ಅಳವಡಿಸಿ.\n"
                    f"• **ಶಿಲೀಂಧ್ರ ನಿಯಂತ್ರಣ:** ಸಂಜೆ ವೇಳೆ ಮೇಲ್ಮುಖ ನೀರಾವರಿ ತಪ್ಪಿಸಿ ಮತ್ತು **Trichoderma viride** ಬಳಸಿ."
                )
            if is_fert:
                return (
                    f"**{crop_name} ಬೆಳೆಗೆ ರಸಗೊಬ್ಬರ (NPK) ವೇಳಾಪಟ್ಟಿ:**\n\n"
                    f"ನಿಮ್ಮ ಮಣ್ಣಿನ ದಾಖಲೆ (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**) ಪ್ರಕಾರ ಸಮತೋಲಿತ ಪೋಷಕಾಂಶ ನೀಡಿ:\n\n"
                    f"| ಪೋಷಕಾಂಶ | ಪ್ರಸ್ತುತ ಮಟ್ಟ | ಶಿಫಾರಸು ಕ್ರಮ |\n"
                    f"|---|---|---|\n"
                    f"| Nitrogen (N) | {n_str} | **Urea (ಯೂರಿಯಾ)** 3 ಕಂತುಗಳಲ್ಲಿ (50% ಆರಂಭ, 25% ಕವಲು, 25% ಹೂವು) |\n"
                    f"| Phosphorus (P) | {p_str} | **DAP / SSP** ಬೇರು ಆಳದಲ್ಲಿ (3–5 cm ಕೆಳಗೆ) ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ |\n"
                    f"| Potassium (K) | {k_str} | **MOP (Potash)** ಬೆಳೆ ದೃಢತೆ ಮತ್ತು ಕಾಳು ತುಂಬಲು |\n\n"
                    f"• ಪ್ರತಿ ಕಂತಿನೊಂದಿಗೆ ಎಕರೆಗೆ **4–5 ಟನ್ ಕಾಂಪೋಸ್ಟ್ / FYM** ಬಳಸಿ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸಿ."
                )
            if is_crop:
                return (
                    f"**{crop_name} ಬೆಳೆ ಹಾಗೂ ಪರ್ಯಾಯ ಬೆಳೆ ಸಲಹೆ:**\n\n"
                    f"ನಿಮ್ಮ ಜಮೀನಿನ ಪ್ರಸ್ತುತ ಮಣ್ಣು (**N={n_str}, P={p_str}, K={k_str}**) ಮತ್ತು ಹವಾಮಾನ (**{w_str}**) **{crop_name}** ಬೆಳೆಗೆ ಪೂರಕವಾಗಿದೆ.\n\n"
                    f"• **ಬೀಜೋಪಚಾರ:** ಬಿತ್ತನೆಗೂ ಮುನ್ನ **Trichoderma** ಅಥವಾ ಪ್ರಮಾಣಿತ ಬೀಜೋಪಚಾರ ಮಾಡಿ.\n"
                    f"• **ಬೆಳೆ ಪರಿವರ್ತನೆ:** ಕಟಾವಿನ ನಂತರ ಮಣ್ಣಿನ ಸಾರಜನಕ ಹೆಚ್ಚಿಸಲು **ಹೆಸರು / ಕಡಲೆ (Pulses)** ಬೆಳೆಯಿರಿ."
                )
            if is_weather:
                return (
                    f"**{loc} ಪ್ರಸ್ತುತ ಕೃಷಿ ಹವಾಮಾನ ವರದಿ:**\n\n"
                    f"ಇಂದಿನ ವಾತಾವರಣ **{w_str}** ಆಗಿದೆ.\n\n"
                    f"• ಗಾಳಿಯ ವೇಗ 12 km/h ಗಿಂತ ಹೆಚ್ಚಿದ್ದರೆ ಅಥವಾ ಮಳೆ ಸಾಧ್ಯತೆ ಇದ್ದರೆ ಔಷಧಿ ಸಿಂಪಡಣೆ ಮುಂದೂಡಿ.\n"
                    f"• ಭಾರೀ ಮಳೆ ಮುನ್ಸೂಚನೆ ಇದ್ದಲ್ಲಿ **{crop_name}** ಹೊಲದ ಬದು ಮತ್ತು ಒಳಚರಂಡಿ ಕಾಲುವೆಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ."
                )
            return (
                f"**{crop_name} ಕುರಿತು ನೇರ ಕೃಷಿ ಸಲಹೆ ({loc}):**\n\n"
                f"ನಿಮ್ಮ ಪ್ರಶ್ನೆ (*'{question}'*) ಹಾಗೂ ಜಮೀನಿನ ದಾಖಲೆ (**N={n_str}, P={p_str}, K={k_str}, {w_str}**) ಪರಿಶೀಲಿಸಿದ ಪ್ರಕಾರ:\n\n"
                f"• **ಪೋಷಕಾಂಶ ಸಮತೋಲನ:** ಶಿಫಾರಸು ಮಾಡಿದ **{crop_name}** ಬೆಳೆಗೆ ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು NPK ಮಟ್ಟವನ್ನು ಗಮನಿಸಿ ಹಂತ-ಹಂತವಾಗಿ **Urea / DAP / MOP** ನೀಡಿ.\n"
                f"• **ತಕ್ಷಣದ ತಪಾಸಣೆ:** ಎಲೆಗಳಲ್ಲಿ ಬಣ್ಣ ಬದಲಾವಣೆ ಅಥವಾ ಕೀಟ ಲಕ್ಷಣಗಳಿದ್ದರೆ ಕ್ಯಾಮೆರಾ ಬಟನ್ (📷) ಬಳಸಿ ತಕ್ಷಣ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ."
            )

        # ---- HINDI (hi) ----
        if lang == "hi":
            if is_greet:
                return (
                    f"नमस्ते {farmer_name}! मैं आपकी **{crop_name}** फसल, मृदा परीक्षण डेटा और {loc} के लाइव मौसम के आधार पर सीधा कृषि परामर्श देने के लिए तैयार हूँ।\n\n"
                    f"• **सक्रिय फसल:** {crop_name}\n"
                    f"• **मिट्टी का NPK:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                    f"• **मौसम:** {w_str}\n\n"
                    f"अपनी **{crop_name}** फसल में खाद, सिंचाई, या पत्तियों की समस्या के बारे में सीधे पूछें।"
                )
            if is_chlorosis:
                n_note = (
                    f"आपकी मिट्टी में नाइट्रोजन (**N = {n_str}**) कम है, इसलिए निचली पुरानी पत्तियां पीली पड़ रही हैं।"
                    if (n_val is not None and n_val < 50)
                    else f"आपकी मिट्टी में नाइट्रोजन (**N = {n_str}**) पर्याप्त है; यह पीलापन **जिंक (Zinc)** की कमी या अधिक नमी के कारण हो सकता है।"
                )
                return (
                    f"**{crop_name} में पत्तियां पीली पड़ने (Chlorosis) का निदान:**\n\n"
                    f"{n_note}\n\n"
                    f"• **नाइट्रोजन पूर्ति:** निचली पत्तियां पीली हों तो **25 kg/acre Urea (यूरिया)** दें या **1% Urea (10 g/L पानी)** का छिड़काव करें।\n"
                    f"• **सूक्ष्म पोषक तत्व:** नई ऊपरी पत्तियों के लिए **Zinc Sulphate (0.5%) + बुझा चूना (0.25%)** स्प्रे करें।\n"
                    f"• **जल निकासी:** खेत में अतिरिक्त पानी न रुकने दें ताकि जड़ें स्वस्थ रहें।"
                )
            if is_irrig:
                return (
                    f"**{crop_name} के लिए सटीक सिंचाई सलाह ({loc}):**\n\n"
                    f"वर्तमान **{w_str}** मौसम में जड़ क्षेत्र की नमी **60%–75%** बनाए रखें।\n\n"
                    f"• **सही समय:** सुबह **5:30–8:30** या शाम **5:30** के बाद सिंचाई करें (25%+ पानी की बचत होती है)।\n"
                    f"• **कटाव/मात्रा:** सटीक लीटर/एकड़ गणना हेतु ऊपर **Smart Irrigation** टैब में वर्तमान वर्षा पूर्वानुमान देखें।"
                )
            if is_pest:
                return (
                    f"**{crop_name} हेतु एकीकृत कीट एवं रोग प्रबंधन (IPM):**\n\n"
                    f"वर्तमान मौसम (**{w_str}**) में रस चूसक कीट व फफूंद संक्रमण से बचाव के लिए:\n\n"
                    f"• **जैविक नियंत्रण:** शुरुआती अवस्था में **Neem Oil / NSKE 5% (@ 3–5 ml/L पानी)** का छिड़काव करें।\n"
                    f"• **ट्रैप लगाएं:** प्रति एकड़ **10 पीले चिपचिपे ट्रैप (Yellow Sticky Traps)** लगाएं।\n"
                    f"• **फफूंद बचाव:** शाम को स्प्रिंकलर सिंचाई टालें और मिट्टी में **Trichoderma viride** का उपयोग करें।"
                )
            if is_fert:
                return (
                    f"**{crop_name} के लिए संतुलित NPK उर्वरक योजना:**\n\n"
                    f"आपके मृदा रिकॉर्ड (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**) के अनुसार:\n\n"
                    f"| पोषक तत्व | वर्तमान स्तर | अनुशंसित उपयोग |\n"
                    f"|---|---|---|\n"
                    f"| Nitrogen (N) | {n_str} | **Urea (यूरिया)** 3 भागों में (50% बुवाई, 25% कल्ले, 25% बाली अवस्था) |\n"
                    f"| Phosphorus (P) | {p_str} | **DAP / SSP** जड़ क्षेत्र में 3–5 cm गहराई पर बुवाई समय |\n"
                    f"| Potassium (K) | {k_str} | **MOP (पोटाश)** दाने भरने व रोग प्रतिरोधकता हेतु |\n\n"
                    f"• इसके साथ 4–5 टन/एकड़ सड़ी गोबर खाद (FYM) डालें।"
                )
            if is_crop:
                return (
                    f"**{crop_name} फसल एवं किस्म मार्गदर्शन:**\n\n"
                    f"आपकी मिट्टी (**N={n_str}, P={p_str}, K={k_str}**) और मौसम (**{w_str}**) **{crop_name}** की खेती के लिए उपयुक्त हैं।\n\n"
                    f"• **बीजोपचार:** बुवाई से पहले **Trichoderma** से बीज उपचार अवश्य करें।\n"
                    f"• **फसल चक्र:** कटाई के बाद **मूंग या चना (दलहन)** उगाने से प्राकृतिक नाइट्रोजन बढ़ता है।"
                )
            if is_weather:
                return (
                    f"**{loc} की वर्तमान कृषि-मौसम स्थिति:**\n\n"
                    f"अभी मौसम **{w_str}** है।\n\n"
                    f"• हवा 12 km/h से तेज हो या बारिश की संभावना हो तो किसी भी रासायनिक स्प्रे को टाल दें।\n"
                    f"• भारी बारिश से पहले **{crop_name}** के खेत में जल निकासी नालियां साफ रखें।"
                )
            return (
                f"**{crop_name} के लिए सीधा कृषि परामर्श ({loc}):**\n\n"
                f"आपके प्रश्न (*'{question}'*) और खेत के आंकड़ों (**N={n_str}, P={p_str}, K={k_str}, {w_str}**) के आधार पर:\n\n"
                f"• अपनी **{crop_name}** फसल में खाद की मात्रा (**Urea / DAP / MOP**) हमेशा मिट्टी की वास्तविक जांच के अनुसार विभाजित खुराक में दें।\n"
                f"• यदि पत्तियों या मिट्टी की तुरंत जांच करनी हो तो नीचे चैट बार में **📷 कैमरा बटन** से फोटो स्कैन करें।"
            )

        # ---- MARATHI (mr) ----
        if lang == "mr":
            if is_greet:
                return (
                    f"नमस्कार {farmer_name}! तुमच्या **{crop_name}** पिकासाठी, माती परीक्षण नोंदी आणि {loc} येथील हवामानानुसार थेट सल्ला देण्यासाठी मी तयार आहे.\n\n"
                    f"• **सक्रिय पीक:** {crop_name}\n"
                    f"• **माती NPK:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                    f"• **हवामान:** {w_str}\n\n"
                    f"खते, पाणी नियोजन किंवा पानावरील लक्षणांबद्दल थेट प्रश्न विचारा."
                )
            if is_chlorosis:
                return (
                    f"**{crop_name} पिकाची पाने पिवळी पडणे (Chlorosis) उपाय:**\n\n"
                    f"तुमच्या नोंदीनुसार **N={n_str}** आहे. जमिनीत नायट्रोजन कमी असल्यास खालची पाने पिवळी पडतात, तर वरच्या पानांसाठी **Zinc** कमतरता कारणीभूत असते.\n\n"
                    f"• खालच्या पानांसाठी एकरी **25 kg Urea (युरिया)** द्या किंवा **1% Urea** फवारणी करा.\n"
                    f"• वरच्या पानांसाठी **Zinc Sulphate (0.5%)** फवारा आणि शेतात पाणी साचू देऊ नका."
                )
            if is_irrig:
                return (
                    f"**{crop_name} पाणी नियोजन ({loc}):**\n\n"
                    f"सध्याच्या **{w_str}** हवामानात मुळांच्या कक्षेत **60%–75% ओलावा** ठेवा.\n\n"
                    f"• सकाळी **5:30–8:30** किंवा संध्याकाळी **5:30** नंतर पाणी द्या (बाष्पीभवन कमी होते)."
                )
            if is_pest:
                return (
                    f"**{crop_name} कीड व रोग नियंत्रण (IPM):**\n\n"
                    f"सध्याच्या **{w_str}** वातावरणात **Neem Oil / NSKE 5% (3–5 ml/L)** ची फवारणी करा, एकरी **10 पिवळे चिकट सापळे** लावा आणि बुरशीसाठी **Trichoderma** वापरा."
                )
            if is_fert:
                return (
                    f"**{crop_name} खत व्यवस्थापन (NPK):**\n\n"
                    f"माती नोंदी (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**) नुसार **Urea** 3 हप्त्यांत, तर **DAP / SSP** आणि **MOP** पेरणीच्या वेळी मुळांजवळ द्या."
                )
            return (
                f"**{crop_name} थेट कृषी सल्ला ({loc}):**\n\n"
                f"तुमच्या प्रश्नानुसार (*'{question}'*) व शेतातील डेटा (**N={n_str}, P={p_str}, K={k_str}, {w_str}**) नुसार पिकाच्या वाढीच्या अवस्थेप्रमाणे **Urea / DAP / MOP** खतांचे नियोजन करा. फोटोद्वारे त्वरित तपासणीसाठी खालील **📷 कॅमेरा बटण** वापरा."
            )

        # ---- TAMIL (ta) ----
        if lang == "ta":
            if is_greet:
                return (
                    f"வணக்கம் {farmer_name}! உங்கள் **{crop_name}** பயிர், மண் பரிசோதனை மற்றும் {loc} வானிலை அடிப்படையில் நேரடி வேளாண் ஆலோசனை வழங்க நான் தயாராக உள்ளேன்.\n\n"
                    f"• **தற்போதைய பயிர்:** {crop_name}\n"
                    f"• **மண் NPK:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                    f"• **வானிலை:** {w_str}"
                )
            if is_chlorosis:
                return (
                    f"**{crop_name} இலை மஞ்சள் நோய் (Chlorosis) தீர்வு:**\n\n"
                    f"உங்கள் மண்ணில் **N={n_str}** உள்ளது. கீழ் இலைகள் மஞ்சளானால் **Nitrogen (Urea)** பற்றாக்குறை; மேல் இலைகள் மஞ்சளானால் **Zinc** குறைபாடு.\n\n"
                    f"• ஏக்கருக்கு **20–25 kg Urea (யூரியா)** இடவும் அல்லது **1% Urea (10 g/L)** தெளிக்கவும்.\n"
                    f"• மேல் இலைகளுக்கு **Zinc Sulphate (0.5%)** தெளிக்கவும் மற்றும் நீர் தேங்காமல் வடிக்கவும்."
                )
            if is_irrig:
                return (
                    f"**{crop_name} நீர்ப்பாசன ஆலோசனை ({loc}):**\n\n"
                    f"**{w_str}** வானிலையில் வேர் பகுதியில் **60%–75% ஈரப்பதம்** பராமரிக்கவும். காலை **5:30–8:30** அல்லது மாலை **5:30**-க்குப் பிறகு நீர் பாய்ச்சவும்."
                )
            if is_pest:
                return (
                    f"**{crop_name} பூச்சி மற்றும் நோய் கட்டுப்பாடு (IPM):**\n\n"
                    f"**Neem Oil / NSKE 5% (3–5 ml/L)** தெளிக்கவும், ஏக்கருக்கு **10 மஞ்சள் ஒட்டும் பொறிகள்** வைக்கவும், பூஞ்சைக்கு **Trichoderma viride** பயன்படுத்தவும்."
                )
            if is_fert:
                return (
                    f"**{crop_name} உர மேலாண்மை (NPK):**\n\n"
                    f"மண் அளவு (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**) அடிப்படையில் **Urea** 3 தவணைகளிலும், **DAP / SSP** மற்றும் **MOP** அடியுரமாகவும் இடவும்."
                )
            return (
                f"**{crop_name} நேரடி வேளாண் ஆலோசனை ({loc}):**\n\n"
                f"உங்கள் கேள்வி (*'{question}'*) மற்றும் வயல் தரவு (**N={n_str}, P={p_str}, K={k_str}, {w_str}**) அடிப்படையில் சரியான அளவு **Urea / DAP / MOP** உரமிடுங்கள். உடனடி மண்/இலை பரிசோதனைக்கு கீழே உள்ள **📷 கேமரா பொத்தானை** அழுத்தவும்."
            )

        # ---- TELUGU (te) ----
        if lang == "te":
            if is_greet:
                return (
                    f"నమస్కారం {farmer_name}! మీ **{crop_name}** పంట, నేల పరీక్ష విలువలు మరియు {loc} వాతావరణం ఆధారంగా నేరుగా వ్యవసాయ సలహా ఇవ్వడానికి నేను సిద్ధంగా ఉన్నాను.\n\n"
                    f"• **ప్రస్తుత పంట:** {crop_name}\n"
                    f"• **నేల NPK:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                    f"• **వాతావరణం:** {w_str}"
                )
            if is_chlorosis:
                return (
                    f"**{crop_name} ఆకులు పసుపు రంగులోకి మారడం (Chlorosis) విశ్లేషణ:**\n\n"
                    f"మీ నేలలో **N={n_str}** ఉంది. కింది పాత ఆకులు పసుపుగా ఉంటే **Nitrogen (Urea)** లోపం; పై కొత్త ఆకులైతే **Zinc** లోపం కావచ్చు.\n\n"
                    f"• ఎకరానికి **20–25 kg Urea (యూరియా)** వేయండి లేదా **1% Urea (10 g/L)** పిచికారీ చేయండి.\n"
                    f"• పై ఆకుల కోసం **Zinc Sulphate (0.5%)** పిచికారీ చేసి, పొలంలో నీరు నిల్వ ఉండకుండా చూడండి."
                )
            if is_irrig:
                return (
                    f"**{crop_name} నీటిపారుదల సలహా ({loc}):**\n\n"
                    f"**{w_str}** పరిస్థితుల్లో వేరు మండలంలో **60%–75% తేమ** ఉండేలా ఉదయం **5:30–8:30** లేదా సాయంత్రం **5:30** తర్వాత నీరు పెట్టండి."
                )
            if is_pest:
                return (
                    f"**{crop_name} పురుగు & తెగులు నివారణ (IPM):**\n\n"
                    f"**Neem Oil / NSKE 5% (3–5 ml/L)** పిచికారీ చేయండి, ఎకరానికి **10 పసుపు అంటు ఉచ్చులు** ఉంచండి మరియు **Trichoderma viride** వాడండి."
                )
            if is_fert:
                return (
                    f"**{crop_name} ఎరువుల ప్రణాళిక (NPK):**\n\n"
                    f"మీ నేల నివేదిక (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**) ప్రకారం **Urea** 3 దఫాలుగా, మరియు **DAP / SSP**, **MOP** దుక్కిలో వేయండి."
                )
            return (
                f"**{crop_name} నేరుగా వ్యవసాయ సలహా ({loc}):**\n\n"
                f"మీ ప్రశ్న (*'{question}'*) మరియు పొలం డేటా (**N={n_str}, P={p_str}, K={k_str}, {w_str}**) ప్రకారం పంట దశకు అనుగుణంగా **Urea / DAP / MOP** వాడండి. ఆకు లేదా మట్టి ఫోటోను పరీక్షించడానికి క్రింద ఉన్న **📷 కెమెరా బటన్** ఉపయోగించండి."
            )

        # ---- ENGLISH (en) ----
        if is_greet:
            return (
                f"Hello {farmer_name}! I'm Geo, ready with direct guidance tailored to your **{crop_name}** crop and {loc} conditions.\n\n"
                f"• **Active Crop:** {crop_name}\n"
                f"• **Soil Profile:** N={n_str}, P={p_str}, K={k_str} ({ph_str})\n"
                f"• **Live Microclimate:** {w_str}\n\n"
                f"Ask me anything about leaf symptoms, fertilizer dosage, irrigation timing, or scan a photo right below."
            )
        if is_chlorosis:
            n_note = (
                f"Your recorded Nitrogen is low (**N = {n_str}**), making primary **Nitrogen deficiency** the top cause of lower-leaf yellowing in {crop_name}."
                if (n_val is not None and n_val < 50)
                else f"With Nitrogen at **{n_str}**, check whether yellowing appears on younger upper leaves (**Iron / Zinc deficiency**) or results from root-zone waterlogging."
            )
            return (
                f"**Direct Diagnosis: Leaf Yellowing in {crop_name}**\n\n"
                f"{n_note}\n\n"
                f"• **Immediate Nitrogen Fix:** Top-dress **20–25 kg/acre Urea** or apply **1% foliar Urea spray (10 g/L)**.\n"
                f"• **Micronutrient Check:** For upper interveinal chlorosis, spray **0.5% Zinc Sulphate + 0.25% slaked lime**.\n"
                f"• **Drainage:** Avoid standing water so roots can actively uptake nutrients."
            )
        if is_irrig:
            return (
                f"**Precision Irrigation Guidance for {crop_name} ({loc})**\n\n"
                f"Under current conditions (**{w_str}**), keep root-zone soil moisture between **60% and 75% of field capacity**.\n\n"
                f"• **Best Window:** Irrigate between **5:30–8:30 AM** or after **5:30 PM** to cut evaporative loss by up to 28%.\n"
                f"• **Exact Volume:** Use the **Smart Irrigation** tab to compute exact Liters/Acre adjusted for your acreage and forecast rain."
            )
        if is_pest:
            risk = f"High ambient humidity (**{hum}% RH**) raises fungal blight and sucking-pest risk in {crop_name}." if hum and hum >= 75 else f"Current weather (**{w_str}**) favors preventative scouting in {crop_name}."
            return (
                f"**Pest & Disease Protocol for {crop_name} (IPM)**\n\n"
                f"{risk}\n\n"
                f"• **Organic Deterrence:** Spray cold-pressed **Neem Oil / NSKE 5% (3–5 ml/L)** early before pest pressure crosses threshold.\n"
                f"• **Trapping:** Place **10 Yellow Sticky Traps/acre** for aphids/whiteflies and avoid late-evening overhead sprinklers."
            )
        if is_fert:
            return (
                f"**Balanced NPK Dosage Plan for {crop_name}**\n\n"
                f"Based on your soil profile (**N={n_str}, P={p_str}, K={k_str}, {ph_str}**):\n\n"
                f"| Nutrient | Measured | Recommended Strategy |\n"
                f"|---|---|---|\n"
                f"| Nitrogen (N) | {n_str} | **Urea** in 3 splits (50% basal, 25% active vegetative, 25% reproductive) |\n"
                f"| Phosphorus (P) | {p_str} | **DAP / SSP** placed 3–5 cm below seed row at planting |\n"
                f"| Potassium (K) | {k_str} | **MOP (Potash)** for stress tolerance and grain weight |\n\n"
                f"• Pair synthetic splits with **4–5 tonnes/acre well-decomposed FYM/compost**."
            )
        if is_crop:
            return (
                f"**Crop & Variety Guidance ({crop_name})**\n\n"
                f"Your soil profile (**N={n_str}, P={p_str}, K={k_str}**) and microclimate (**{w_str}**) support **{crop_name}** cultivation.\n\n"
                f"• Treat seed with *Trichoderma viride* prior to sowing and follow with a pulse rotation (Moong / Chickpea) to restore organic N."
            )
        if is_weather:
            return (
                f"**Weather Action Plan for {loc}**\n\n"
                f"Live reading is **{w_str}**.\n\n"
                f"• Hold foliar sprays if wind exceeds **12 km/h** or rain is imminent.\n"
                f"• Keep drainage channels clear around your **{crop_name}** plot prior to heavy rainfall events."
            )
        return (
            f"**Direct Agronomy Guidance for {crop_name} ({loc})**\n\n"
            f"Looking directly at your question (*'{question}'*) alongside your farm data (**N={n_str}, P={p_str}, K={k_str}, {ph_str}, {w_str}**):\n\n"
            f"• Align fertilizer splits (**Urea / DAP / MOP**) and irrigation timing directly to **{crop_name}**'s active growth stage rather than fixed dates.\n"
            f"• For instant visual NPK or symptom screening, tap the **📷 Camera / Upload Photo** button in the chat bar below."
        )
