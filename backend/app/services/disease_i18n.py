"""
Localized ICAR / UAS Dharwad Plant Pathology Knowledge Base for Disease Diagnosis.
Supports Native Scripts: Kannada (kn), Hindi (hi), Marathi (mr), Tamil (ta), Telugu (te).
Divides treatment cleanly into:
  - immediate_field_action (pruning, sanitation, airflow)
  - organic (Trichoderma viride / Pseudomonas fluorescens / Neem oil)
  - chemical (ICAR active ingredient, per-L dose, exact 15L pump mix, 7-10 day interval)
"""

from typing import Dict, Any, Optional

LOCALIZED_ARCHETYPES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "kn": {
        "late_blight": {
            "cause_type": "ಶಿಲೀಂಧ್ರ / ಓಮೈಸೀಟ್ ಸೋಂಕು (Late Blight / Water-Mold)",
            "bio_cause": "ಮಣ್ಣಿನಿಂದ ಅಥವಾ ಗಾಳಿಯಿಂದ ಬಂದ Phytophthora ಬೀಜಕಗಳು ತಂಪು (15–24°C) ಮತ್ತು ಹೆಚ್ಚಿನ ತೇವಾಂಶದಲ್ಲಿ (>75% RH) ಎಲೆಯ ಮೇಲೆ ನೀರು ತುಂಬಿದ ಕಪ್ಪು-ಕಂದು ಮಚ್ಚೆಗಳನ್ನು ಉಂಟುಮಾಡುತ್ತವೆ.",
            "immediate_field_action": [
                "ರೋಗ ತಗುಲಿದ ಕೆಳಗಿನ ಎಲೆಗಳನ್ನು ತಕ್ಷಣ ಕಿತ್ತು ಹೊಲದಿಂದ ಹೊರಗೆ ಸುಡಿ ಅಥವಾ ಆಳವಾಗಿ ಹೂಳಿ.",
                "ಸಂಜೆ ಸ್ಪ್ರಿಂಕ್ಲರ್ ನೀರಾವರಿ ನಿಲ್ಲಿಸಿ ಗಿಡಗಳ ನಡುವೆ ಗಾಳಿ ಆಡುವಂತೆ ಮಾಡಿ."
            ],
            "organic": [
                "Pseudomonas fluorescens @ 10 g/L ಅಥವಾ Trichoderma viride @ 5 g/L ಬೆಳಗಿನ ಬಿಸಿಲಿನಲ್ಲಿ ಸಿಂಪಡಿಸಿ.",
                "ತಡೆ ಕ್ರಮವಾಗಿ Neem Oil 1500 ppm @ 3–5 ml/L ಬಳಸಿ."
            ],
            "chemical": [
                "Mancozeb 75% WP @ 2.5 g/L (15L ಪಂಪ್‌ಗೆ 37.5 g) ಅಥವಾ Metalaxyl 8% + Mancozeb 64% WP @ 2.0 g/L (15L ಪಂಪ್‌ಗೆ 30 g) — ಪ್ರತಿ 7–10 ದಿನಗಳಿಗೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ."
            ],
            "spray_notes": "ಎಲೆಯ ಕೆಳಭಾಗಕ್ಕೂ ಔಷಧಿ ತಾಗುವಂತೆ ಪ್ರತಿ 7–10 ದಿನಗಳಿಗೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ.",
            "prevention": [
                "ಬಿತ್ತನೆಗೆ ಮುನ್ನ Trichoderma viride (4 g/kg) ಬೀಜೋಪಚಾರ ಮಾಡಿ.",
                "ಹೆಚ್ಚುವರಿ Urea ಹಾಕುವುದನ್ನು ತಪ್ಪಿಸಿ."
            ]
        },
        "early_blight_leaf_spot": {
            "cause_type": "ಶಿಲೀಂಧ್ರ ಎಲೆ ಮಚ್ಚೆ / ಅರ್ಲಿ ಬ್ಲೈಟ್ (Alternaria / Cercospora)",
            "bio_cause": "ಮಣ್ಣಿನಲ್ಲಿ ಉಳಿದ ಶಿಲೀಂಧ್ರ ಬೀಜಕಗಳು ಮಳೆ/ನೀರಾವರಿ ಹನಿಗಳಿಂದ ಕೆಳಗಿನ ಎಲೆಗಳಿಗೆ ಹಾರಿ ಹಳದಿ ಅಂಚಿನ ಕಂದು-ವೃತ್ತಾಕಾರದ ಮಚ್ಚೆಗಳನ್ನು ಉಂಟುಮಾಡುತ್ತವೆ.",
            "immediate_field_action": [
                "ಹಳದಿ ಅಂಚು ಮತ್ತು ಕಂದು ಮಚ್ಚೆಯುಳ್ಳ ಹಳೆಯ ಕೆಳಗಿನ ಎಲೆಗಳನ್ನು ಕತ್ತರಿಸಿ ಹೊಲದಿಂದ ಹೊರಗೆ ನಾಶಪಡಿಸಿ.",
                "ಮೇಲಿನಿಂದ ನೀರು ಸಿಂಪಡಿಸದೆ ಬೇರಿಗೆ ಮಾತ್ರ ಬೆಳಿಗ್ಗೆ ನೀರು ಕೊಡಿ."
            ],
            "organic": [
                "Trichoderma viride @ 5 g/L ಅಥವಾ Pseudomonas fluorescens @ 5 g/L + Neem Oil @ 3–5 ml/L ಪ್ರತಿ 10 ದಿನಕ್ಕೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ."
            ],
            "chemical": [
                "Mancozeb 75% WP @ 2.5 g/L (15L ಪಂಪ್‌ಗೆ 37.5 g) ಅಥವಾ Azoxystrobin 23% SC @ 1.0 ml/L (15L ಪಂಪ್‌ಗೆ 15 ml) — ಪ್ರತಿ 7–10 ದಿನಕ್ಕೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ."
            ],
            "spray_notes": "ಕೆಳಗಿನ ಎಲೆಗಳಿಗೂ ಸಮನಾಗಿ ಸಿಂಪಡಿಸಿ; 7–10 ದಿನಗಳ ನಂತರ ಪುನರಾವರ್ತಿಸಿ.",
            "prevention": [
                "ಬೆಳೆ ಪರಿವರ್ತನೆ (Crop Rotation) ಮತ್ತು ಮಣ್ಣಿನ ಹೊದಿಕೆ (Mulching) ಮಾಡಿ.",
                "Potassium (K) ಕೊರತೆಯಾಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ."
            ]
        },
        "powdery_mildew": {
            "cause_type": "ಬೂದು ರೋಗ ಶಿಲೀಂಧ್ರ (Powdery Mildew)",
            "bio_cause": "ಗಾಳಿಯಲ್ಲಿ ಹರಡುವ ಬಿಳಿ ಬೂದು ಬೀಜಕಗಳು ಬೆಚ್ಚಗಿನ ಹಗಲು ಮತ್ತು ಮುಂಜಾನೆಯ ತೇವಾಂಶದಲ್ಲಿ ಎಲೆಯ ಮೇಲ್ಮೈಯಲ್ಲಿ ವೇಗವಾಗಿ ಬೆಳೆಯುತ್ತವೆ.",
            "immediate_field_action": [
                "ದಟ್ಟವಾಗಿ ಬೆಳೆದ ಒಳ ಕೊಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ ಗಾಳಿ ಬೆಳಕು ಹರಿಯುವಂತೆ ಮಾಡಿ.",
                "ಹೆಚ್ಚು ಬೂದು ಇರುವ ಎಲೆಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ."
            ],
            "organic": [
                "ತಂಪಾದ ಬೆಳಗಿನ ವೇಳೆ Wettable Sulphur 80% WP @ 2.0 g/L (15L ಪಂಪ್‌ಗೆ 30 g) ಅಥವಾ Neem Oil @ 3–5 ml/L ಸಿಂಪಡಿಸಿ."
            ],
            "chemical": [
                "Hexaconazole 5% EC @ 1.0 ml/L (15L ಪಂಪ್‌ಗೆ 15 ml) ಅಥವಾ Azoxystrobin 23% SC @ 1.0 ml/L (15L ಪಂಪ್‌ಗೆ 15 ml) — ಪ್ರತಿ 7–10 ದಿನಕ್ಕೊಮ್ಮೆ."
            ],
            "spray_notes": "Sulphur ಸಿಂಪಡಿಸಿದ 14 ದಿನಗಳೊಳಗೆ Neem Oil ಬಳಸಬೇಡಿ.",
            "prevention": ["ಒಂದೇ ಬಾರಿಗೆ ಹೆಚ್ಚು Urea ಕೊಡುವುದನ್ನು ತಪ್ಪಿಸಿ."]
        },
        "rust": {
            "cause_type": "ತುಕ್ಕು ರೋಗ ಶಿಲೀಂಧ್ರ (Fungal Rust)",
            "bio_cause": "ಗಾಳಿ ಮೂಲಕ ಬಂದ ತುಕ್ಕು ಬೀಜಕಗಳು ಬೆಳಗಿನ ಇಬ್ಬನಿಯೊಂದಿಗೆ ಎಲೆಯ ಮೇಲೆ ಕಿತ್ತಳೆ-ಕಂದು ಗುಳ್ಳೆಗಳನ್ನು ಉಂಟುಮಾಡುತ್ತವೆ.",
            "immediate_field_action": ["ತುಕ್ಕು ಗುಳ್ಳೆ ಇರುವ ಕೆಳಗಿನ ಎಲೆಗಳನ್ನು ಕತ್ತರಿಸಿ ನಾಶಪಡಿಸಿ ಮತ್ತು ಬದುಗಳ ಕಳೆ ತೆಗೆಯಿರಿ."],
            "organic": ["Trichoderma viride @ 5 g/L ಅಥವಾ Neem Oil @ 4 ml/L ಸಿಂಪಡಿಸಿ."],
            "chemical": ["Propiconazole 25% EC @ 1.0 ml/L (15L ಪಂಪ್‌ಗೆ 15 ml) ಅಥವಾ Mancozeb 75% WP @ 2.5 g/L (15L ಪಂಪ್‌ಗೆ 37.5 g) ಪ್ರತಿ 10 ದಿನಕ್ಕೊಮ್ಮೆ."],
            "spray_notes": "ಬೆಳಿಗ್ಗೆ ಬಿಸಿಲಿಗೂ ಮುನ್ನ ಸಿಂಪಡಿಸಿ.",
            "prevention": ["UAS ಧಾರವಾಡ / ICAR ತುಕ್ಕು ನಿರೋಧಕ ತಳಿಗಳನ್ನು ಬೆಳೆಯಿರಿ."]
        },
        "bacterial": {
            "cause_type": "ಬ್ಯಾಕ್ಟೀರಿಯಾ ಎಲೆ ಮಚ್ಚೆ / ಅಂಗಮಾರಿ (Bacterial Blight / Spot)",
            "bio_cause": "ಮಳೆ-ಗಾಳಿ ಹನಿಗಳ ಮೂಲಕ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಎಲೆಯ ರಂಧ್ರಗಳನ್ನು ಪ್ರವೇಶಿಸಿ ಹಳದಿ ಅಂಚಿನ ನೀರು ತುಂಬಿದ ಕಪ್ಪು ಮಚ್ಚೆಗಳನ್ನು ಉಂಟುಮಾಡುತ್ತದೆ.",
            "immediate_field_action": ["ಎಲೆಗಳು ಸಂಪೂರ್ಣ ಒಣಗಿದಾಗ ಮಾತ್ರ ಸೋಂಕಿತ ಎಲೆ ತೆಗೆಯಿರಿ; ಒದ್ದೆ ಹೊಲದಲ್ಲಿ ಓಡಾಡಬೇಡಿ."],
            "organic": ["Pseudomonas fluorescens @ 5–10 g/L (15L ಪಂಪ್‌ಗೆ 75–150 g) + Neem Oil 3 ml/L ಸಿಂಪಡಿಸಿ."],
            "chemical": ["Copper Oxychloride 50% WP @ 3.0 g/L (15L ಪಂಪ್‌ಗೆ 45 g) + Streptocycline @ 0.1 g/L (15L ಪಂಪ್‌ಗೆ 1.5 g) ಪ್ರತಿ 7–10 ದಿನಕ್ಕೊಮ್ಮೆ."],
            "spray_notes": "ತಾಜಾ ದ್ರಾವಣವನ್ನು ಮಾತ್ರ ಸಿಂಪಡಿಸಿ; 7–10 ದಿನಕ್ಕೊಮ್ಮೆ ಪುನರಾವರ್ತಿಸಿ.",
            "prevention": ["ಪ್ರಮಾಣೀಕೃತ ರೋಗಮುಕ್ತ ಸಸಿಗಳನ್ನು ಬಳಸಿ."]
        },
        "viral": {
            "cause_type": "ವೈರಸ್ ಸೋಂಕು (Leaf Curl / Mosaic Virus)",
            "bio_cause": "ಬಿಳಿನೊಣ (Whitefly) ಮತ್ತು ಸಸ್ಯಹೇನು (Aphids) ರಸ ಹೀರುವಾಗ ವೈರಸ್ ಹರಡುತ್ತದೆ.",
            "immediate_field_action": ["ರೋಗ ತಗುಲಿದ ಆರಂಭಿಕ ಗಿಡಗಳನ್ನು ಕಿತ್ತು ಹೂಳಿ; ಎಕರೆಗೆ 12–15 ಹಳದಿ ಅಂಟು ಬಲೆ ಹಾಕಿ."],
            "organic": ["Neem Oil 1500 ppm @ 4–5 ml/L (15L ಪಂಪ್‌ಗೆ 60–75 ml) ಎಲೆಯ ಕೆಳಭಾಗಕ್ಕೆ ಸಿಂಪಡಿಸಿ."],
            "chemical": ["ವಾಹಕ ಕೀಟ ನಿಯಂತ್ರಣಕ್ಕೆ Imidacloprid 17.8% SL @ 0.4 ml/L (15L ಪಂಪ್‌ಗೆ 6 ml) ಅಥವಾ Thiamethoxam 25% WG @ 0.3 g/L (15L ಪಂಪ್‌ಗೆ 4.5 g) 10 ದಿನದ ಅಂತರದಲ್ಲಿ ಸಿಂಪಡಿಸಿ."],
            "spray_notes": "ಗಿಡ ಮುಟ್ಟಿದ ನಂತರ ಕೈಗಳನ್ನು ಸಾಬೂನಿನಿಂದ ತೊಳೆಯಿರಿ.",
            "prevention": ["50-ಮೆಶ್ ಕೀಟ ಪರದೆಯೊಳಗೆ ಸಸಿ ಬೆಳೆಸಿ."]
        },
        "spider_mite": {
            "cause_type": "ನುಸಿ ಕೀಟ ಬಾಧೆ (Two-Spotted Spider Mite)",
            "bio_cause": "ಬಿಸಿ ಮತ್ತು ಒಣ ಹವಾಮಾನದಲ್ಲಿ (<55% RH) ಎಲೆಯ ಕೆಳಭಾಗದಲ್ಲಿ ನುಸಿಗಳು ರಸ ಹೀರಿ ಹಳದಿ ಚುಕ್ಕೆಗಳನ್ನು ಉಂಟುಮಾಡುತ್ತವೆ.",
            "immediate_field_action": ["ಎಲೆಯ ಕೆಳಭಾಗಕ್ಕೆ ಶುದ್ಧ ನೀರು ಸಿಂಪಡಿಸಿ ಬಲೆ ತೊಳೆಯಿರಿ ಮತ್ತು ಬದುಗಳ ಧೂಳು ನಿಯಂತ್ರಿಸಿ."],
            "organic": ["Neem Oil 1500 ppm @ 4–5 ml/L (15L ಪಂಪ್‌ಗೆ 60–75 ml) ಅಥವಾ Wettable Sulphur @ 2 g/L."],
            "chemical": ["Spiromesifen 22.9% SC @ 1.0 ml/L (15L ಪಂಪ್‌ಗೆ 15 ml) ಅಥವಾ Abamectin @ 0.5 ml/L ಎಲೆಯ ಕೆಳಭಾಗಕ್ಕೆ 7–10 ದಿನದ ಅಂತರದಲ್ಲಿ ಸಿಂಪಡಿಸಿ."],
            "spray_notes": "ಎಲೆಯ ಕೆಳಭಾಗ ಪೂರ್ತಿ ತೊಯ್ಯುವಂತೆ ಸಿಂಪಡಿಸಿ.",
            "prevention": ["ನೀರಿನ ಕೊರತೆಯಾಗದಂತೆ ನಿಯಮಿತ ನೀರಾವರಿ ಕೊಡಿ."]
        },
        "nutrient_deficiency": {
            "cause_type": "ಪೋಷಕಾಂಶ ಕೊರತೆ (Nitrogen / Potassium Chlorosis)",
            "bio_cause": "ಯಾವುದೇ ಶಿಲೀಂಧ್ರ/ವೈರಸ್ ಸೋಂಕಿಲ್ಲ; ಮಣ್ಣಿನಲ್ಲಿ ಕಡಿಮೆ ಸಾರಜನಕ (N) ಅಥವಾ ಪೊಟ್ಯಾಶ್ (K) ಕಾರಣದಿಂದ ಎಲೆ ಹಳದಿಯಾಗಿ ಅಂಚು ಒಣಗುತ್ತಿದೆ.",
            "immediate_field_action": ["ಹೊಲದಲ್ಲಿ ನಿಂತ ನೀರನ್ನು ಬಸಿದುಹಾಕಿ ಬೇರು ಉಸಿರಾಟ ಸುಧಾರಿಸಿ; ಒಣಗಿದ ತುದಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ."],
            "organic": ["ಎಕರೆಗೆ 4–5 ಟನ್ ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ/ಕಂಪೋಸ್ಟ್ + Jeevamrutha ಅಥವಾ Vermiwash ಸಿಂಪಡಿಸಿ."],
            "chemical": ["1% Urea (10 g/L — 15L ಪಂಪ್‌ಗೆ 150 g) ಅಥವಾ NPK 19:19:19 @ 5 g/L (15L ಪಂಪ್‌ಗೆ 75 g) 10 ದಿನದ ಅಂತರದಲ್ಲಿ ಫೋಲಿಯರ್ ಸಿಂಪಡಿಸಿ."],
            "spray_notes": "ಮೇಲುಗೊಬ್ಬರದೊಂದಿಗೆ ತಕ್ಷಣ ಎಲೆ ಸಿಂಪಡಣೆ ನೀಡಿದರೆ 5–7 ದಿನದಲ್ಲಿ ಹಸಿರು ಬಣ್ಣ ಮರಳುತ್ತದೆ.",
            "prevention": ["4R ವಿಧಾನದಲ್ಲಿ 3 ಹಂತಗಳಲ್ಲಿ Urea ಹಾಗೂ ಮೂಲಗೊಬ್ಬರವಾಗಿ DAP/MOP ನೀಡಿ."]
        },
        "healthy": {
            "cause_type": "ಆರೋಗ್ಯಕರ ಬೆಳೆ ಎಲೆ",
            "bio_cause": "ಎಲೆಯು ಸಂಪೂರ್ಣ ಹಸಿರಾಗಿದ್ದು ಶಿಲೀಂಧ್ರ ಮಚ್ಚೆ, ಕೀಟ ಅಥವಾ ಬ್ಯಾಕ್ಟೀರಿಯಾ ಸೋಂಕು ಕಂಡುಬಂದಿಲ್ಲ.",
            "immediate_field_action": ["ಯಾವುದೇ ಎಲೆ ಕತ್ತರಿಸುವ ಅವಶ್ಯಕತೆಯಿಲ್ಲ; ನಿಯಮಿತ ಬೆಳೆ ಪರಿಶೀಲನೆ ಮುಂದುವರಿಸಿ."],
            "organic": ["ಮುನ್ನೆಚ್ಚರಿಕೆಯಾಗಿ ಪ್ರತಿ 15 ದಿನಕ್ಕೊಮ್ಮೆ Neem Oil @ 3 ml/L (15L ಪಂಪ್‌ಗೆ 45 ml) ಸಿಂಪಡಿಸಬಹುದು."],
            "chemical": ["ಯಾವುದೇ ರಾಸಾಯನಿಕ ಶಿಲೀಂಧ್ರನಾಶಕ ಬೇಕಿಲ್ಲ — ಹಣ ಉಳಿಸಿ."],
            "spray_notes": "ಮಳೆಯ ನಂತರ ಎಲೆಯ ಕೆಳಭಾಗವನ್ನು ಗಮನಿಸಿ.",
            "prevention": ["ಬೆಳೆ ಹಂತಕ್ಕೆ ತಕ್ಕಂತೆ ಸಮತೋಲಿತ NPK ಗೊಬ್ಬರ ನೀಡಿ."]
        },
    },
    "hi": {
        "late_blight": {
            "cause_type": "फफूंद / ओमीसीट संक्रमण (Late Blight / Water-Mold)",
            "bio_cause": "ठंडे (15–24°C) व अधिक नमी (>75% RH) वाले मौसम में मिट्टी/हवा से आए Phytophthora बीजाणु पत्तियों पर गहरे पानी-भीगे काले धब्बे बनाते हैं।",
            "immediate_field_action": ["संक्रमित निचली पत्तियां तुरंत तोड़कर खेत से बाहर जलाएं या गहरा दबाएं।", "शाम की सिंचाई रोकें और पौधों के बीच हवा का बहाव बढ़ाएं।"],
            "organic": ["Pseudomonas fluorescens @ 10 g/L या Trichoderma viride @ 5 g/L + Neem Oil @ 3–5 ml/L सुबह धूप में छिड़कें।"],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L पंप में 37.5 g) या Metalaxyl 8% + Mancozeb 64% WP @ 2.0 g/L (15L पंप में 30 g) — हर 7–10 दिन में दोहराएं।"],
            "spray_notes": "पत्ती की निचली सतह पर हर 7–10 दिन में छिड़काव करें।",
            "prevention": ["बुवाई से पहले Trichoderma viride (4 g/kg) से बीज उपचार करें और अधिक Urea से बचें।"]
        },
        "early_blight_leaf_spot": {
            "cause_type": "फफूंद पत्ती धब्बा / झुलसा (Alternaria / Cercospora)",
            "bio_cause": "मिट्टी में मौजूद फफूंद के बीजाणु बारिश या सिंचाई के छींटों से निचली पत्तियों पर पहुंचकर पीले घेरे वाले गोल भूरे धब्बे बनाते हैं।",
            "immediate_field_action": ["धब्बे वाली पुरानी निचली पत्तियां हटाकर खेत से बाहर नष्ट करें।", "ऊपरी छिड़काव बंद कर जड़ क्षेत्र में सुबह सिंचाई करें।"],
            "organic": ["Trichoderma viride @ 5 g/L (15L पंप में 75 g) या Neem Oil @ 3–5 ml/L (15L पंप में 45–75 ml) छिड़कें।"],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L पंप में 37.5 g) या Azoxystrobin 23% SC @ 1.0 ml/L (15L पंप में 15 ml) — हर 7–10 दिन पर छिड़कें।"],
            "spray_notes": "निचली पत्तियों तक स्प्रे पहुंचाएं; 7–10 दिन बाद दोहराएं।",
            "prevention": ["फसल चक्र अपनाएं, मल्चिंग करें और पोटाश (K) संतुलित रखें।"]
        },
        "powdery_mildew": {
            "cause_type": "चूर्णिल आसिता फफूंद (Powdery Mildew)",
            "bio_cause": "गर्म दिन और सुबह की हल्की नमी में हवा से उड़ने वाला सफेद पाउडर पत्तियों की सतह ढक लेता है।",
            "immediate_field_action": ["घनी शाखाओं की छंटाई कर धूप-हवा बढ़ाएं और सफेद परत वाली पत्तियां हटाएं।"],
            "organic": ["सुबह Wettable Sulphur 80% WP @ 2.0 g/L (15L पंप में 30 g) या Neem Oil @ 3–5 ml/L छिड़कें।"],
            "chemical": ["Hexaconazole 5% EC @ 1.0 ml/L (15L पंप में 15 ml) या Azoxystrobin 23% SC @ 1.0 ml/L — हर 7–10 दिन में।"],
            "spray_notes": "सल्फर और तेल आधारित स्प्रे 14 दिन के भीतर एक साथ न डालें।",
            "prevention": ["अत्यधिक नाइट्रोजन (Urea) एक बार में न दें।"]
        },
        "rust": {
            "cause_type": "रतुआ / गेरुआ फफूंद (Fungal Rust)",
            "bio_cause": "हवा और सुबह की ओस से पत्तियों पर नारंगी-भूरे पाउडर जैसे फफोले बनते हैं।",
            "immediate_field_action": ["अधिक रतुआ वाली निचली पत्तियां तोड़कर नष्ट करें और मेड़ों की घास साफ करें।"],
            "organic": ["Trichoderma viride @ 5 g/L या Neem Oil @ 4 ml/L का छिड़काव करें।"],
            "chemical": ["Propiconazole 25% EC @ 1.0 ml/L (15L पंप में 15 ml) या Mancozeb 75% WP @ 2.5 g/L (37.5 g / 15L पंप) हर 10 दिन में।"],
            "spray_notes": "फफोले 10% क्षेत्र से अधिक फैलने से पहले छिड़काव करें।",
            "prevention": ["ICAR अनुशंसित रतुआ-रोधी किस्में बोएं।"]
        },
        "bacterial": {
            "cause_type": "जीवाणु पत्ती धब्बा / झुलसा (Bacterial Blight / Spot)",
            "bio_cause": "बारिश के छींटों व तेज हवा से जीवाणु रंध्रों में घुसकर पीले घेरे वाले काले पानी-भीगे धब्बे बनाते हैं।",
            "immediate_field_action": ["पत्ती सूखने पर ही संक्रमित भाग काटें; भीगे खेत में काम न करें।"],
            "organic": ["Pseudomonas fluorescens @ 5–10 g/L (15L पंप में 75–150 g) + Neem Oil 3 ml/L छिड़कें।"],
            "chemical": ["Copper Oxychloride 50% WP @ 3.0 g/L (15L पंप में 45 g) + Streptocycline @ 0.1 g/L (15L पंप में 1.5 g) — हर 7–10 दिन में।"],
            "spray_notes": "ताजा घोल बनाकर पत्तियों के दोनों तरफ छिड़कें।",
            "prevention": ["प्रमाणित रोग-मुक्त बीज एवं पौध उपयोग करें।"]
        },
        "viral": {
            "cause_type": "विषाणु रोग (Leaf Curl / Mosaic Virus)",
            "bio_cause": "सफेद मक्खी (Whitefly) व माहू रस चूसकर वायरस फैलाते हैं।",
            "immediate_field_action": ["प्रारंभिक मुड़ी पत्तियों वाले पौधे उखाड़कर गाड़ दें; एकड़ में 12–15 पीले चिपचिपे ट्रैप लगाएं।"],
            "organic": ["Neem Oil 1500 ppm @ 4–5 ml/L (15L पंप में 60–75 ml) पत्तियों के नीचे छिड़कें।"],
            "chemical": ["वाहक कीट नियंत्रण हेतु Imidacloprid 17.8% SL @ 0.4 ml/L (15L पंप में 6 ml) या Thiamethoxam 25% WG @ 0.3 g/L (4.5 g / 15L पंप) 10 दिन अंतराल पर।"],
            "spray_notes": "पौधों को छूने से पहले हाथ साबुन से धोएं।",
            "prevention": ["50-मेश कीट-रोधी जाली में नर्सरी तैयार करें।"]
        },
        "spider_mite": {
            "cause_type": "मकड़ी माइट कीट (Two-Spotted Spider Mite)",
            "bio_cause": "गर्म और शुष्क हवा (<55% RH) में पत्तियों के नीचे लाल मकड़ी जाले बनाती है।",
            "immediate_field_action": ["पत्ती की निचली सतह पर साफ पानी का स्प्रे करें और धूल कम करें।"],
            "organic": ["Neem Oil 1500 ppm @ 4–5 ml/L (15L पंप में 60–75 ml) या Wettable Sulphur @ 2 g/L।"],
            "chemical": ["Spiromesifen 22.9% SC @ 1.0 ml/L (15L पंप में 15 ml) या Abamectin @ 0.5 ml/L 7–10 दिन पर।"],
            "spray_notes": "फुहार पत्ती की निचली सतह पर डालें।",
            "prevention": ["समय पर सिंचाई कर फसल को सूखे के तनाव से बचाएं।"]
        },
        "nutrient_deficiency": {
            "cause_type": "पोषक तत्व कमी (Nitrogen / Potassium Chlorosis)",
            "bio_cause": "संक्रामक रोग नहीं है; मिट्टी में कम नाइट्रोजन (N) या पोटाश (K) के कारण पत्तियां पीली होकर किनारों से सूख रही हैं।",
            "immediate_field_action": ["खेत से अतिरिक्त पानी निकालकर जड़ों को हवा दें और सूखे पत्ते साफ करें।"],
            "organic": ["प्रति एकड़ 4–5 टन सड़ी गोबर खाद/कम्पोस्ट या Vermiwash @ 5 ml/L का स्प्रे करें।"],
            "chemical": ["1% Urea (10 g/L — 15L पंप में 150 g) या NPK 19:19:19 @ 5 g/L (15L पंप में 75 g) 10 दिन अंतराल पर फोलियर स्प्रे करें।"],
            "spray_notes": "तुरंत पत्तियों पर स्प्रे से 5–7 दिन में हरियाली लौटती है।",
            "prevention": ["4R पद्धति से 3 किस्तों में Urea व बेसल DAP/MOP दें।"]
        },
        "healthy": {
            "cause_type": "स्वस्थ फसल पत्ती",
            "bio_cause": "पत्ती पर फफूंद, जीवाणु या कीट का कोई संक्रमण नहीं है; हरियाली संतुलित है।",
            "immediate_field_action": ["किसी छंटाई की आवश्यकता नहीं है; नियमित खेत निरीक्षण जारी रखें।"],
            "organic": ["बचाव हेतु हर 15 दिन पर Neem Oil @ 3 ml/L (15L पंप में 45 ml) उपयोग कर सकते हैं।"],
            "chemical": ["रासायनिक फफूंदनाशक की कोई जरूरत नहीं — लागत बचाएं।"],
            "spray_notes": "बारिश के बाद निचली पत्तियां जांचते रहें।",
            "prevention": ["संतुलित 4R NPK उर्वरक और समयबद्ध सिंचाई जारी रखें।"]
        },
    },
    "mr": {
        "late_blight": {
            "cause_type": "बुरशी / ओमीसीट संसर्ग (Late Blight)",
            "bio_cause": "थंड (15–24°C) आणि दमट (>75% RH) हवेत Phytophthora बीजाणू काळे पाणथळ डाग पाडतात.",
            "immediate_field_action": ["बाधित खालची पाने तात्काळ तोडून नष्ट करा आणि संध्याकाळचे पाणी बंद करा."],
            "organic": ["Trichoderma viride @ 5 g/L किंवा Neem Oil @ 3–5 ml/L सकाळी फवारा."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L पंपासाठी 37.5 g) किंवा Metalaxyl + Mancozeb @ 2.0 g/L — दर 7–10 दिवसांनी."],
            "spray_notes": "पानांच्या खालच्या बाजूने फवारणी करा (7–10 दिवस अंतर).",
            "prevention": ["पेरणीपूर्वी Trichoderma (4 g/kg) प्रक्रिया करा."]
        },
        "early_blight_leaf_spot": {
            "cause_type": "बुरशीजन्य ठिपके / करपा (Alternaria / Cercospora)",
            "bio_cause": "मातीतील बुरशी पावसाच्या थेंबांनी पानांवर येऊन पिवळ्या कडांचे तपकिरी डाग पाडते.",
            "immediate_field_action": ["डाग असलेली जुनी खालची पाने काढून नष्ट करा आणि थेंब सिंचन वापरा."],
            "organic": ["Trichoderma viride @ 5 g/L (15L पंप 75 g) किंवा Neem Oil @ 3–5 ml/L फवारा."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L पंप 37.5 g) किंवा Azoxystrobin 23% SC @ 1.0 ml/L (15L पंप 15 ml) — दर 7–10 दिवसांनी."],
            "spray_notes": "दर 7–10 दिवसांनी फवारणी करा.",
            "prevention": ["पीक फेरपालट आणि मल्चिंग करा."]
        },
        "powdery_mildew": {
            "cause_type": "भुरी रोग (Powdery Mildew)",
            "bio_cause": "उबदार दिवसात पांढरी भुकटी पानांवर वेगाने पसरते.",
            "immediate_field_action": ["दाट फांद्यांची छाटणी करा."],
            "organic": ["Wettable Sulphur @ 2 g/L (30 g / 15L पंप) किंवा Neem Oil @ 3–5 ml/L."],
            "chemical": ["Hexaconazole 5% EC @ 1.0 ml/L (15 ml / 15L पंप) दर 7–10 दिवसांनी."],
            "spray_notes": "गंधक आणि तेल एकत्र करू नका.",
            "prevention": ["अति युरिया टाळा."]
        },
        "rust": {
            "cause_type": "तांबेरा बुरशी (Fungal Rust)",
            "bio_cause": "दव आणि वाऱ्यामुळे तांबूस पुरळ येतात.",
            "immediate_field_action": ["बाधित खालची पाने काढून टाका."],
            "organic": ["Trichoderma @ 5 g/L किंवा Neem Oil @ 4 ml/L."],
            "chemical": ["Propiconazole 25% EC @ 1.0 ml/L (15 ml / 15L पंप) किंवा Mancozeb @ 2.5 g/L दर 10 दिवसांनी."],
            "spray_notes": "सकाळी फवारा.",
            "prevention": ["रोगप्रतिबंधक वाण वापरा."]
        },
        "bacterial": {
            "cause_type": "जिवाणू करपा (Bacterial Blight)",
            "bio_cause": "वादळी पावसात जिवाणू पानांत प्रवेश करून पिवळसर किनारीचे डाग पाडतात.",
            "immediate_field_action": ["पाने कोरडी असतानाच बाधित पाने कापा."],
            "organic": ["Pseudomonas fluorescens @ 5–10 g/L (75–150 g / 15L पंप)."],
            "chemical": ["Copper Oxychloride 50% WP @ 3.0 g/L (45 g / 15L पंप) + Streptocycline @ 0.1 g/L (1.5 g / 15L पंप) दर 7–10 दिवसांनी."],
            "spray_notes": "ताज्या द्रावणाची फवारणी करा.",
            "prevention": ["निरोगी बियाणे वापरा."]
        },
        "viral": {
            "cause_type": "विषाणू रोग (Leaf Curl / Mosaic)",
            "bio_cause": "पांढरी माशी व मावा किडींद्वारे पसरतो.",
            "immediate_field_action": ["बाधित झाडे उपटून गाडा व पिवळे चिकट सापळे लावा."],
            "organic": ["Neem Oil @ 4–5 ml/L (60–75 ml / 15L पंप)."],
            "chemical": ["Imidacloprid 17.8% SL @ 0.4 ml/L (6 ml / 15L पंप) दर 10 दिवसांनी."],
            "spray_notes": "हात साबणाने स्वच्छ धुवा.",
            "prevention": ["50-मेश जाळीत रोपे तयार करा."]
        },
        "spider_mite": {
            "cause_type": "लाल कोळी (Spider Mites)",
            "bio_cause": "कोरड्या गरम हवेत (<55% RH) पानांखाली जाळी तयार करतात.",
            "immediate_field_action": ["पानांखाली पाण्याचा फवारा मारा."],
            "organic": ["Neem Oil @ 4–5 ml/L किंवा Wettable Sulphur @ 2 g/L."],
            "chemical": ["Spiromesifen @ 1.0 ml/L (15 ml / 15L पंप) दर 7–10 दिवसांनी."],
            "spray_notes": "पानांखाली फवारा.",
            "prevention": ["नियमित पाणी द्या."]
        },
        "nutrient_deficiency": {
            "cause_type": "अन्नद्रव्य कमतरता (N / K Deficiency)",
            "bio_cause": "रोग नसून नत्र (N) किंवा पालाश (K) कमतरतेमुळे पाने पिवळी पडत आहेत.",
            "immediate_field_action": ["जास्त पाणी निचरा करा आणि मुळांना हवा द्या."],
            "organic": ["एकरी 4–5 टन शेणखत आणि Vermiwash @ 5 ml/L फवारा."],
            "chemical": ["1% Urea (10 g/L — 150 g / 15L पंप) किंवा NPK 19:19:19 @ 5 g/L (75 g / 15L पंप) फवारा."],
            "spray_notes": "10 दिवसांनी पुन्हा फवारा.",
            "prevention": ["4R पद्धतीने खतांचे हप्ते द्या."]
        },
        "healthy": {
            "cause_type": "निरोगी पीक पान",
            "bio_cause": "कोणताही रोग किंवा कीड आढळलेली नाही.",
            "immediate_field_action": ["नियमित निरीक्षण सुरू ठेवा."],
            "organic": ["प्रतिबंधात्मक Neem Oil @ 3 ml/L (45 ml / 15L पंप)."],
            "chemical": ["रासायनिक औषधाची गरज नाही."],
            "spray_notes": "पावसानंतर पाने तपासा.",
            "prevention": ["संतुलित NPK वेळापत्रक पाळा."]
        },
    },
    "ta": {
        "late_blight": {
            "cause_type": "பூஞ்சை கருகல் நோய் (Late Blight)",
            "bio_cause": "குளிர் (15–24°C) மற்றும் அதிக ஈரப்பதத்தில் (>75% RH) Phytophthora பூஞ்சை கருமைப் புள்ளிகளை உருவாக்குகிறது.",
            "immediate_field_action": ["பாதிக்கப்பட்ட கீழ் இலைகளை உடனே அகற்றி எரிக்கவும்; மாலை நீர்ப்பாசனத்தை நிறுத்தவும்."],
            "organic": ["Trichoderma viride @ 5 g/L (75 g / 15L டேங்க்) அல்லது Neem Oil @ 3–5 ml/L தெளிக்கவும்."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L டேங்கிற்கு 37.5 g) அல்லது Metalaxyl + Mancozeb @ 2.0 g/L — 7–10 நாட்களுக்கு ஒருமுறை."],
            "spray_notes": "இலையின் அடிப்பகுதியில் 7–10 நாட்கள் இடைவெளியில் தெளிக்கவும்.",
            "prevention": ["விதை நேர்த்திக்கு Trichoderma (4 g/kg) பயன்படுத்தவும்."]
        },
        "early_blight_leaf_spot": {
            "cause_type": "பூஞ்சை இலைப் புள்ளி (Alternaria / Cercospora)",
            "bio_cause": "மண்ணிலிருந்து மழைச் சிதறலால் பரவி மஞ்சள் வளையத்துடன் கூடிய பழுப்புப் புள்ளிகளை உருவாக்குகிறது.",
            "immediate_field_action": ["புள்ளிகள் உள்ள பழைய கீழ் இலைகளை அகற்றி அழிக்கவும்."],
            "organic": ["Trichoderma viride @ 5 g/L (75 g / 15L டேங்க்) + Neem Oil @ 3–5 ml/L தெளிக்கவும்."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (37.5 g / 15L டேங்க்) அல்லது Azoxystrobin 23% SC @ 1.0 ml/L (15 ml / 15L டேங்க்) — 7–10 நாட்கள் இடைவெளியில்."],
            "spray_notes": "7–10 நாட்களுக்குப் பிறகு மீண்டும் தெளிக்கவும்.",
            "prevention": ["பயிர் சுழற்சி மற்றும் நிலப்போர்வை செய்யவும்."]
        },
        "powdery_mildew": {
            "cause_type": "சாம்பல் நோய் (Powdery Mildew)",
            "bio_cause": "வெப்பமான பகலில் வெண்ணிறப் பூஞ்சை இலையின் மேல் படிகிறது.",
            "immediate_field_action": ["கிளைகளைக் கவாத்து செய்து காற்றோட்டத்தை அதிகரிக்கவும்."],
            "organic": ["Wettable Sulphur @ 2 g/L (30 g / 15L டேங்க்) அல்லது Neem Oil @ 3–5 ml/L."],
            "chemical": ["Hexaconazole 5% EC @ 1.0 ml/L (15 ml / 15L டேங்க்) 7–10 நாட்கள் இடைவெளியில்."],
            "spray_notes": "கந்தகம் மற்றும் எண்ணெய் தெளிப்பைக் கலக்காதீர்கள்.",
            "prevention": ["அதிக யூரியா இடாதீர்கள்."]
        },
        "rust": {
            "cause_type": "துரு நோய் (Fungal Rust)",
            "bio_cause": "காலைப் பனியில் பழுப்பு துருப் புள்ளிகள் உருவாகின்றன.",
            "immediate_field_action": ["துருப் புள்ளி இலைகளை அகற்றி அழிக்கவும்."],
            "organic": ["Trichoderma @ 5 g/L அல்லது Neem Oil @ 4 ml/L."],
            "chemical": ["Propiconazole 25% EC @ 1.0 ml/L (15 ml / 15L டேங்க்) அல்லது Mancozeb @ 2.5 g/L 10 நாட்களுக்கு ஒருமுறை."],
            "spray_notes": "காலையில் தெளிக்கவும்.",
            "prevention": ["நோய் எதிர்ப்பு இரகங்களைப் பயிரிடவும்."]
        },
        "bacterial": {
            "cause_type": "பாக்டீரியா கருகல் / புள்ளி (Bacterial Blight)",
            "bio_cause": "மழைக் காற்றில் பாக்டீரியா இலைத் துளைகள் வழியாக நுழைகிறது.",
            "immediate_field_action": ["இலை காய்ந்தவுடன் பாதிக்கப்பட்ட பகுதிகளை வெட்டி அகற்றவும்."],
            "organic": ["Pseudomonas fluorescens @ 5–10 g/L (75–150 g / 15L டேங்க்)."],
            "chemical": ["Copper Oxychloride 50% WP @ 3.0 g/L (45 g / 15L டேங்க்) + Streptocycline @ 0.1 g/L (1.5 g / 15L டேங்க்) 7–10 நாட்களுக்கு ஒருமுறை."],
            "spray_notes": "புதிய கலவையாகத் தெளிக்கவும்.",
            "prevention": ["சான்றளிக்கப்பட்ட நாற்றுகளைப் பயன்படுத்தவும்."]
        },
        "viral": {
            "cause_type": "வைரஸ் நோய் (Leaf Curl / Mosaic)",
            "bio_cause": "வெள்ளை ஈ மற்றும் அசுவினி மூலம் பரவுகிறது.",
            "immediate_field_action": ["பாதிக்கப்பட்ட செடிகளைப் பிடுங்கி புதைத்து மஞ்சள் ஒட்டும் பொறி வைக்கவும்."],
            "organic": ["Neem Oil @ 4–5 ml/L (60–75 ml / 15L டேங்க்)."],
            "chemical": ["Imidacloprid 17.8% SL @ 0.4 ml/L (6 ml / 15L டேங்க்) 10 நாட்கள் இடைவெளியில்."],
            "spray_notes": "கைகளை சோப்பால் கழுவவும்.",
            "prevention": ["50-மெஷ் வலைக்குள் நாற்று வளர்க்கவும்."]
        },
        "spider_mite": {
            "cause_type": "சிலந்திப் பேன் (Spider Mites)",
            "bio_cause": "வெப்பமான வறண்ட வானிலையில் (<55% RH) இலை அடியில் சாறு உறிஞ்சுகிறது.",
            "immediate_field_action": ["இலை அடியில் தண்ணீர் பீய்ச்சி அடித்து வலைகளை அகற்றவும்."],
            "organic": ["Neem Oil @ 4–5 ml/L அல்லது Wettable Sulphur @ 2 g/L."],
            "chemical": ["Spiromesifen @ 1.0 ml/L (15 ml / 15L டேங்க்) 7–10 நாட்களுக்கு ஒருமுறை."],
            "spray_notes": "இலை அடியில் நன்கு தெளிக்கவும்.",
            "prevention": ["சீரான நீர்ப்பாசனம் அளிக்கவும்."]
        },
        "nutrient_deficiency": {
            "cause_type": "சத்துக் குறைபாடு (N / K Deficiency)",
            "bio_cause": "நோயல்ல; மண்ணில் நைட்ரஜன் (N) அல்லது பொட்டாஷ் (K) குறைவால் இலை மஞ்சளாகிறது.",
            "immediate_field_action": ["வயலில் தேங்கிய நீரை வடிக்கவும்."],
            "organic": ["ஏக்கருக்கு 4–5 டன் மக்கிய தொழுஉரம் & Vermiwash @ 5 ml/L தெளிக்கவும்."],
            "chemical": ["1% Urea (10 g/L — 150 g / 15L டேங்க்) அல்லது NPK 19:19:19 @ 5 g/L (75 g / 15L டேங்க்) இலைவழியாகத் தெளிக்கவும்."],
            "spray_notes": "10 நாட்களில் மீண்டும் தெளிக்கவும்.",
            "prevention": ["4R முறையில் 3 தவணை NPK இடவும்."]
        },
        "healthy": {
            "cause_type": "ஆரோக்கியமான இலை",
            "bio_cause": "எந்த நோயும் கண்டறியப்படவில்லை.",
            "immediate_field_action": ["தொடர்ந்து பயிரை கண்காணிக்கவும்."],
            "organic": ["தடுப்பாக Neem Oil @ 3 ml/L (45 ml / 15L டேங்க்)."],
            "chemical": ["இரசாயனத் தெளிப்பு தேவையில்லை."],
            "spray_notes": "மழைக்குப் பின் பரிசோதிக்கவும்.",
            "prevention": ["சமச்சீர் உர மேலாண்மை தொடரவும்."]
        },
    },
    "te": {
        "late_blight": {
            "cause_type": "శిలీంధ్ర మాడు తెగులు (Late Blight)",
            "bio_cause": "చల్లని (15–24°C) మరియు అధిక తేమ (>75% RH) లో Phytophthora బీజాంశాలు నల్లటి తడి మచ్చలను కలిగిస్తాయి.",
            "immediate_field_action": ["సోకిన కింది ఆకులను వెంటనే తుంచి కాల్చివేయండి; సాయంత్రం నీరు పెట్టడం ఆపండి."],
            "organic": ["Trichoderma viride @ 5 g/L (75 g / 15L పంపు) లేదా Neem Oil @ 3–5 ml/L పిచికారీ చేయండి."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (15L పంపుకు 37.5 g) లేదా Metalaxyl + Mancozeb @ 2.0 g/L — ప్రతి 7–10 రోజులకు."],
            "spray_notes": "ఆకుల కింది భాగంలో 7–10 రోజుల తేడాతో పిచికారీ చేయండి.",
            "prevention": ["విత్తన శుద్ధికి Trichoderma (4 g/kg) వాడండి."]
        },
        "early_blight_leaf_spot": {
            "cause_type": "శిలీంధ్ర ఆకు మచ్చ / ఎర్లీ బ్లైట్ (Alternaria / Cercospora)",
            "bio_cause": "నేల నుండి వర్షపు చినుకులతో ఆకులపైకి చేరి పసుపు అంచులతో గోధుమ రంగు వలయాకార మచ్చలను ఏర్పరుస్తుంది.",
            "immediate_field_action": ["మచ్చలు ఉన్న పాత కింది ఆకులను తొలగించి నాశనం చేయండి."],
            "organic": ["Trichoderma viride @ 5 g/L (75 g / 15L పంపు) + Neem Oil @ 3–5 ml/L పిచికారీ చేయండి."],
            "chemical": ["Mancozeb 75% WP @ 2.5 g/L (37.5 g / 15L పంపు) లేదా Azoxystrobin 23% SC @ 1.0 ml/L (15 ml / 15L పంపు) — ప్రతి 7–10 రోజులకు."],
            "spray_notes": "7–10 రోజుల తర్వాత మళ్లీ పిచికారీ చేయండి.",
            "prevention": ["పంట మార్పిడి మరియు మల్చింగ్ చేయండి."]
        },
        "powdery_mildew": {
            "cause_type": "బూడిద తెగులు (Powdery Mildew)",
            "bio_cause": "వెచ్చని వాతావరణంలో ఆకులపై తెల్లటి పొడి వేగంగా పెరుగుతుంది.",
            "immediate_field_action": ["దట్టమైన కొమ్మలను కత్తిరించి గాలి వెలుతురు పెంచండి."],
            "organic": ["Wettable Sulphur @ 2 g/L (30 g / 15L పంపు) లేదా Neem Oil @ 3–5 ml/L."],
            "chemical": ["Hexaconazole 5% EC @ 1.0 ml/L (15 ml / 15L పంపు) 7–10 రోజుల తేడాతో."],
            "spray_notes": "గంధకం మరియు నూనె మందులు కలపవద్దు.",
            "prevention": ["అధిక యూరియా తగ్గించండి."]
        },
        "rust": {
            "cause_type": "తుప్పు తెగులు (Fungal Rust)",
            "bio_cause": "ఉదయపు మంచులో ఆకులపై గోధుమ గుల్లలు వస్తాయి.",
            "immediate_field_action": ["తుప్పు ఆకులను తొలగించి నాశనం చేయండి."],
            "organic": ["Trichoderma @ 5 g/L లేదా Neem Oil @ 4 ml/L."],
            "chemical": ["Propiconazole 25% EC @ 1.0 ml/L (15 ml / 15L పంపు) లేదా Mancozeb @ 2.5 g/L 10 రోజులకు ఒకసారి."],
            "spray_notes": "ఉదయం పిచికారీ చేయండి.",
            "prevention": ["తెగులు నిరోధక రకాలను వేయండి."]
        },
        "bacterial": {
            "cause_type": "బాక్టీరియా ఆకు మచ్చ / ఎండు తెగులు (Bacterial Blight)",
            "bio_cause": "వర్షం మరియు గాలి ద్వారా బాక్టీరియా ఆకు రంధ్రాలలోకి ప్రవేశిస్తుంది.",
            "immediate_field_action": ["ఆకులు ఎండినప్పుడే సోకిన ఆకులు కత్తిరించండి."],
            "organic": ["Pseudomonas fluorescens @ 5–10 g/L (75–150 g / 15L పంపు)."],
            "chemical": ["Copper Oxychloride 50% WP @ 3.0 g/L (45 g / 15L పంపు) + Streptocycline @ 0.1 g/L (1.5 g / 15L పంపు) ప్రతి 7–10 రోజులకు."],
            "spray_notes": "తాజా ద్రావణాన్ని పిచికారీ చేయండి.",
            "prevention": ["ఆరోగ్యకరమైన నారు వాడండి."]
        },
        "viral": {
            "cause_type": "వైరస్ ఆకు ముడత / మొజాయిక్ (Viral)",
            "bio_cause": "తెల్లదోమ మరియు పేనుబంక ద్వారా వ్యాపిస్తుంది.",
            "immediate_field_action": ["సోకిన మొక్కలను పీకి పాతిపెట్టి పసుపు అంటు అట్టలు ఉంచండి."],
            "organic": ["Neem Oil @ 4–5 ml/L (60–75 ml / 15L పంపు)."],
            "chemical": ["Imidacloprid 17.8% SL @ 0.4 ml/L (6 ml / 15L పంపు) 10 రోజుల తేడాతో."],
            "spray_notes": "చేతులు సబ్బుతో కడుక్కోండి.",
            "prevention": ["50-మెష్ నెట్ కింద నారు పెంచండి."]
        },
        "spider_mite": {
            "cause_type": "ఎర్ర నల్లి పురుగు (Spider Mites)",
            "bio_cause": "వేడి, పొడి వాతావరణంలో (<55% RH) ఆకుల కింద రసం పీల్చుతుంది.",
            "immediate_field_action": ["ఆకుల అడుగు భాగంలో నీటితో కడిగి బూజు తొలగించండి."],
            "organic": ["Neem Oil @ 4–5 ml/L లేదా Wettable Sulphur @ 2 g/L."],
            "chemical": ["Spiromesifen @ 1.0 ml/L (15 ml / 15L పంపు) 7–10 రోజుల తేడాతో."],
            "spray_notes": "ఆకుల కింది భాగాన్ని తడపండి.",
            "prevention": ["క్రమం తప్పకుండా నీరు పెట్టండి."]
        },
        "nutrient_deficiency": {
            "cause_type": "పోషక లోపం (N / K Deficiency)",
            "bio_cause": "తెగులు కాదు; నేలలో నత్రజని (N) లేదా పొటాష్ (K) తక్కువగా ఉన్నందున ఆకులు పసుపుగా మారుతున్నాయి.",
            "immediate_field_action": ["పొలంలో నిలిచిన నీటిని బయటకు పంపండి."],
            "organic": ["ఎకరానికి 4–5 టన్నుల పశువుల ఎరువు & Vermiwash @ 5 ml/L పిచికారీ చేయండి."],
            "chemical": ["1% Urea (10 g/L — 150 g / 15L పంపు) లేదా NPK 19:19:19 @ 5 g/L (75 g / 15L పంపు) పిచికారీ చేయండి."],
            "spray_notes": "10 రోజులకు మళ్లీ పిచికారీ చేయండి.",
            "prevention": ["4R పద్ధతిలో 3 దఫాలుగా NPK వేయండి."]
        },
        "healthy": {
            "cause_type": "ఆరోగ్యకరమైన పంట ఆకు",
            "bio_cause": "ఎటువంటి తెగులు గుర్తించబడలేదు.",
            "immediate_field_action": ["పంటను క్రమం తప్పకుండా గమనించండి."],
            "organic": ["ముందుజాగ్రత్తగా Neem Oil @ 3 ml/L (45 ml / 15L పంపు)."],
            "chemical": ["రసాయన మందు అవసరం లేదు."],
            "spray_notes": "వర్షాల తర్వాత పరిశీలించండి.",
            "prevention": ["సమతుల్య NPK ఎరువులు కొనసాగించండి."]
        },
    },
}


def get_localized_protocol(proto_key: str, lang: str) -> Optional[Dict[str, Any]]:
    lang_map = LOCALIZED_ARCHETYPES.get(lang)
    if not lang_map:
        return None
    return lang_map.get(proto_key)
