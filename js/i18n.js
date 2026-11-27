/**
 * Geosense Internationalization (i18n) Engine
 * Full tri-lingual localization: English (en), हिन्दी (hi), ಕನ್ನಡ (kn)
 * Persisted in localStorage ('geosense_lang'), live DOM scanning,
 * and dynamic module translation.
 */
(function(window) {
  'use strict';

  const STORAGE_KEY = 'geosense_lang';
  const DEFAULT_LANG = 'en';

  const DICTIONARY = {
    en: {
      brand: {
        name: "Geosense",
        tagline: "AI Intelligent System for Smart Agriculture"
      },
      nav: {
        overview: "Overview",
        soil: "Soil NPK Analysis",
        disease: "Infection & Disease Scanner",
        crop: "Crop Recommendation",
        irrigation: "Smart Irrigation",
        weather: "Weather Intelligence",
        market: "Mandi Market",
        community: "Farmer Community",
        assistant: "AI Agro Assistant",
        profile: "Farmer Profile",
        signout: "Sign Out"
      },
      header: {
        title_overview: "Farm Overview",
        title_soil: "Soil NPK Analysis & Diagnostics",
        title_disease: "Crop Infection & Disease Scanner",
        title_crop: "Crop Recommendation Engine",
        title_irrigation: "Precision Irrigation Scheduler",
        title_weather: "Agro-Meteorological Telemetry",
        title_market: "APMC Mandi Commodity Intelligence",
        title_community: "Farmer Discussion & Community",
        title_assistant: "AI Agro Assistant (Geo)",
        title_profile: "Farmer Profile & Settings",
        public_site: "🌐 Public Site",
        fastapi_live: "FastAPI Live: 127.0.0.1:8001"
      },
      overview: {
        metric_soil: "Soil Tests Recorded",
        metric_soil_empty: "No tests submitted yet",
        metric_crop: "Crop Model Status",
        metric_crop_empty: "Run ML model to compute",
        metric_irrigation: "Irrigation Requirement",
        metric_irrigation_empty: "No calculation performed yet",
        metric_weather: "Ambient Weather",
        metric_weather_connecting: "Connecting to Open-Meteo...",
        badge_db: "Database Verified",
        badge_sklearn: "Scikit-Learn Model",
        badge_fao56: "FAO-56 Standard",
        badge_live: "Live Open-Meteo",
        shortcuts_title: "Quick Agricultural Shortcuts",
        shortcut_soil: "Record Soil Test",
        shortcut_soil_desc: "Enter lab NPK or physical scan",
        shortcut_crop: "Run Crop Model",
        shortcut_crop_desc: "Predict suitability from soil NPK",
        shortcut_water: "Water Calculator",
        shortcut_water_desc: "Calculate exact liter deficit",
        recent_activities: "Recent Field Activities",
        badge_activity: "Real Activity Log",
        empty_activities: "No recent field activities recorded. Your actions will appear here as you log soil tests, run crop models, or calculate irrigation."
      },
      soil: {
        sub1_title: "1. Camera Optical Soil Evaluation & Physical Diagnostics",
        sub1_desc: "OpenCV image pipeline verifying surface focus, lighting exposure, and observable physical texture.",
        badge_cv: "Computer Vision",
        ready_photo: "Ready to Evaluate Soil Photo",
        ready_photo_desc: "Capture using mobile camera or upload from your gallery",
        btn_camera: "📷 Open Device Camera",
        btn_snap: "⚡ Capture Frame",
        btn_upload: "📁 Choose from Gallery",
        btn_reset: "🔄 Reset",
        btn_analyze: "Run AI Quality Check",
        btn_predict_npk: "🔬 Predict Vision NPK (ONNX)",
        npk_result_title: "Vision AI Soil / Leaf NPK Prediction",
        npk_apply_btn: "📋 Apply to Crop & Soil Forms",
        sub2_title: "2. Enter Verified Soil Test Measurements (Lab or Sensor)",
        sub2_desc: "Record actual quantitative values from certified soil testing laboratories, sensor kits, or manual test strips.",
        badge_lab: "Certified Assays",
        label_n: "Nitrogen (N) [kg/ha]",
        label_p: "Phosphorus (P) [kg/ha]",
        label_k: "Potassium (K) [kg/ha]",
        label_ph: "Soil pH (0.0 - 14.0)",
        label_ec: "Electrical Conductivity (EC) [dS/m]",
        label_moisture: "Soil Moisture (%)",
        label_source: "Data Source / Equipment",
        source_lab: "Certified Agricultural Laboratory Report",
        source_sensor: "Calibrated Physical Field Sensor Kit",
        source_manual: "Manual Chemical Test Kit",
        label_facility: "Testing Facility / Kit Name",
        btn_save: "Save Verified Soil Test to Database",
        history_title: "Saved Soil Test History",
        badge_db_records: "Database Records",
        history_empty_strong: "No soil tests yet.",
        history_empty_desc: "Add your first soil report or camera scan above to get started."
      },
      crop: {
        title: "Machine Learning Crop Recommendation Model",
        desc: "Calibrated Scikit-Learn Random Forest model predicting optimum crop suitability from 7 agro-climatic parameters.",
        badge_classifier: "Scikit-Learn Classifier",
        label_temp: "Temperature (°C)",
        label_humidity: "Relative Humidity (%)",
        label_rainfall: "Annual Rainfall (mm)",
        btn_compute: "Compute Crop Recommendation",
        history_title: "Saved Crop Recommendations",
        history_empty_strong: "No crop recommendations saved yet.",
        history_empty_desc: "Run your first recommendation above to see results here."
      },
      irrigation: {
        title: "Smart Irrigation Scheduling & Water Requirement",
        desc: "FAO-56 Penman-Monteith Evapotranspiration standard calculating volumetric water demand from soil moisture deficit.",
        badge_fao56: "FAO-56 Methodology",
        label_crop: "Crop",
        label_stage: "Growth Stage",
        stage_initial: "Initial",
        stage_vegetative: "Vegetative",
        stage_flowering: "Flowering",
        stage_yield: "Yield Formation",
        stage_ripening: "Ripening",
        label_moisture: "Current Soil Moisture (%)",
        label_area: "Field Area (Acres)",
        label_rain: "Forecast Rainfall (mm)",
        btn_calc: "Calculate Water Requirement",
        history_title: "Saved Irrigation History",
        history_empty_strong: "No irrigation records yet.",
        history_empty_desc: "Compute your first field requirement above to see records here."
      },
      weather: {
        title: "Live Agro-Meteorological Telemetry",
        desc: "High-precision real-time conditions, satellite agro-telemetry, and multi-day agricultural forecast.",
        placeholder_search: "Search any city, district or village (e.g., Bengaluru, Mandya, Pune, Delhi)...",
        btn_search: "Search Location",
        btn_gps: "📍 Detect My Live GPS",
        map_title: "🛰️ Farm Location Intelligence Map",
        map_badge: "Live Satellite GIS",
        map_desc: "Interactive high-resolution agricultural satellite GIS. Click to drop farm markers, draw field boundaries, calculate acreage, and link telemetry to live micro-climate weather.",
        btn_save_plot: "💾 Save Farm Plot",
        btn_saved_plots: "📂 Saved Farms",
        drawer_title: "Your Saved Agricultural Plots",
        map_search_placeholder: "Search village, town, or farm location...",
        btn_current_gps: "📍 Use My Current Location",
        btn_sat_view: "🛰️ Satellite View (Default)",
        btn_street_view: "🗺️ Street Map",
        btn_draw: "✏️ Draw Boundary",
        btn_clear: "🗑️ Clear Boundary",
        hud_title: "Telemetry HUD",
        hud_status_default: "Click map to pin",
        hud_coord: "Coord:",
        hud_area: "Area:",
        modal_title: "Save Farm Plot Location",
        modal_label_name: "Farm / Plot Name *",
        modal_label_crop: "Primary Crop Type",
        modal_boundary_area: "Boundary Area:",
        btn_cancel: "Cancel",
        btn_save_supabase: "Save to Supabase"
      },
      market: {
        title: "APMC Mandi Commodity Market Intelligence",
        desc: "Verified agricultural commodity transactions from official APMC market bulletins.",
        badge_agmarknet: "Agmarknet GoI",
        label_commodity: "Select Commodity:",
        loading: "Loading verified market data..."
      },
      community: {
        title: "Farmer Discussion & Knowledge Exchange",
        desc: "Direct peer-to-peer discussions, pest advisories, and field observations stored in database.",
        btn_new: "✏️ New Discussion",
        modal_title: "Create Community Post",
        label_cat: "Category",
        cat_general: "General Farming",
        cat_soil: "Soil Health",
        cat_crop: "Crop Advice",
        cat_pest: "Pest & Disease Control",
        cat_market: "Market & Mandi",
        label_post_title: "Post Title",
        placeholder_title: "e.g. Managing yellow rust symptoms in wheat",
        label_content: "Discussion Content",
        placeholder_content: "Share your field observation, question, or technique...",
        btn_publish: "Publish Post",
        empty_strong: "No community discussions yet.",
        empty_desc: "Start the conversation by sharing a farming update above!"
      },
      assistant: {
        label_engine: "Inference Engine:",
        cloud_btn: "☁️ Cloud AI (Qwen3)",
        offline_btn: "⚡ Offline AI (Gemma 4 E2B)",
        status_cloud: "Cloud AI: Qwen3 Grounded",
        settings_btn: "⚙️ Settings",
        greeting: "Hello! I am Geo, your AI agronomy assistant. I cross-reference your verified soil test records and live local weather to give direct field guidance. How can I help your crop today?",
        placeholder: "Ask about Rice leaf symptoms, fertilizer dosage, or irrigation...",
        placeholder_crop: "Ask about {crop} leaf symptoms, NPK dosage, or irrigation...",
        prompt_1: "Why are {crop} leaves turning yellow?",
        prompt_2: "Irrigation need for {crop} today?",
        prompt_3: "Best Urea / NPK split for {crop}?",
        scan_btn_title: "Scan Soil or Leaf Photo (NPK AI)",
        ph_not_tested: "pH: Not tested",
        context_label: "Farm Context",
        btn_send: "Send",
        attach_title: "Attach, Capture or Paste Leaf/Soil Photo",
        mode_disease: "🩺 Infection Scan",
        mode_npk: "🧪 Soil NPK",
        chat_disease_label: "Leaf & Crop Infection Scan",
        chat_npk_label: "Soil & Leaf NPK Scan"
      },
      disease: {
        title: "Crop Infection & Disease Scanner",
        desc: "Two-stage grounded pathology (PlantVillage ONNX + ICAR/UAS Dharwad guidelines + NPK & live weather cross-check).",
        badge_grounded: "ONNX + ICAR Grounded",
        ready_title: "Capture or Upload Leaf / Crop Photo",
        ready_desc: "Focus 15–25 cm from symptomatic foliage in natural daylight for highest confidence.",
        btn_camera: "📷 Capture Photo",
        btn_snap: "⚡ Capture Leaf Frame",
        btn_upload: "📁 Upload Leaf/Crop Photo",
        btn_reset: "🔄 Reset",
        btn_diagnose: "🩺 Run Grounded Diagnosis",
        question_placeholder: "Optional symptom note (e.g., spotted lower leaves, curling shoots)...",
        card_detected: "Detected Infection & Confidence",
        card_why: "Why It Is Infected (Biology & Live Weather Trigger)",
        card_solution: "Recommended Solution & Dosage",
        tab_organic: "🌿 Organic / Cultural Control",
        tab_chemical: "🧪 Targeted Chemical Control (ICAR)",
        card_prevention: "Prevention Measures",
        btn_followup: "🤖 Ask Follow-up in AI Agro Assistant"
      },
      settings: {
        profile_title: "Farmer Profile & Account Settings",
        badge_auth: "Authenticated Account",
        role_farmer: "Role: Farmer",
        region_default: "Farm: Karnataka / Punjab",
        sync_desc: "Your profile is verified and synchronized with Supabase PostgreSQL and Row Level Security. All submitted soil tests, crop recommendations, and irrigation logs are linked directly to your authenticated account ID.",
        language_title: "🌐 Language & Regional Settings",
        badge_active: "Active Preference",
        language_desc: "Choose your primary working language. All dashboard metrics, agronomic analyses, live weather alerts, and AI advisory responses adapt immediately.",
        lang_en: "English",
        lang_en_sub: "Default International",
        lang_hi: "हिन्दी (Hindi)",
        lang_hi_sub: "राष्ट्रीय कृषि संपर्क",
        lang_kn: "ಕನ್ನಡ (Kannada)",
        lang_kn_sub: "ಕರ್ನಾಟಕ ರೈತ ಸಂಪರ್ಕ"
      },
      landing: {
        nav_features: "Features",
        nav_solutions: "Solutions",
        nav_platform: "Platform",
        nav_about: "About",
        nav_login: "Login",
        nav_dashboard: "Dashboard",
        nav_get_started: "Get Started",
        hero_title: 'Meet <span class="hl">Geo</span>, your AI teammate<br>for smart agriculture',
        hero_trust: "Progressive farmers & agronomists trust Geosense",
        hero_cta: "Get Started Free",
        stmt_text: "Geo is an AI agronomist<br>that analyzes soil health, predicts optimum crops,<br>calculates precision irrigation, tracks mandi prices,<br>and guides farmers every step from seed to harvest",
        telemetry_pill: "LIVE FIELD TELEMETRY",
        card_soil_tag: "Soil Bio-Chemistry",
        card_soil_desc: "Volumetric Soil Moisture",
        card_water_tag: "Precision Water",
        card_water_desc: "Crop Evapotranspiration (ET₀)",
        card_canopy_tag: "Canopy Vigor",
        card_canopy_desc: "Vegetative Health & Chlorophyll",
        card_mandi_tag: "Mandi Market APMC",
        card_mandi_desc: "Wheat HD-2967 (Modal Rate)",
        split_title: "AI agronomist that operates<br>like you farm",
        split_sub: "Smart Agriculture",
        split_p: "Yield higher. Irrigate smarter. Eliminate guesswork. Geosense integrates mobile soil diagnostics, ML crop modeling, and real-time agro-meteorology — so your farm maximizes harvest value while conserving resources.",
        feat_tag: "Agricultural Intelligence",
        feat_h2: "Precision farming tools powered by computer vision & machine learning",
        feat_desc: "From soil optical quality assessments to weather-adjusted irrigation scheduling and live Mandi market intelligence, Geosense delivers software-first agronomic decision support.",
        feat_1_title: "AI Soil Optical Diagnostics",
        feat_1_desc: "Capture soil via mobile camera. Our OpenCV pipeline evaluates blur, glare, lighting balance, and visible soil texture/hue with rigorous scientific transparency.",
        feat_2_title: "ML Crop Recommendation",
        feat_2_desc: "Trained Random Forest model correlates soil parameters (N, P, K, pH) with temperature, humidity, and rainfall to predict optimal crop yields and management packages.",
        feat_3_title: "Smart Irrigation Engine",
        feat_3_desc: "Calculates crop evapotranspiration (FAO-56) across growth stages and subtracts local forecast precipitation to provide exact liter demand per acre.",
        feat_4_title: "Agro-Weather Telemetry",
        feat_4_desc: "Live Open-Meteo forecasts combined with automated farming hazard alerts for heat stress, foliar pest risks, and heavy rainfall drainage advisories.",
        feat_5_title: "APMC Mandi Intelligence",
        feat_5_desc: "Track modal, minimum, and maximum commodity prices across regional agricultural markets with 7-day trend trajectories and transparent benchmark labeling.",
        feat_6_title: "Farmer Community",
        feat_6_desc: "Connect with agronomists and peer growers to share bio-fertilizer field results, pest control updates, and regional farming insights.",
        sol_tag: "Tailored Solutions",
        sol_h2: "Engineered for farmers, agronomists, and agricultural enterprises",
        sol_desc: "Whether managing a 2-acre family farm or coordinating an agricultural producer organization, Geosense adapts to your operational scale.",
        sol_1_title: "Independent Farmers",
        sol_1_desc: "Instant mobile camera soil checks, weather alerts, and water-saving irrigation schedules directly on your smartphone without costly proprietary hardware.",
        sol_2_title: "FPOs & Cooperatives",
        sol_2_desc: "Aggregate crop planning, compare regional Mandi commodity prices, and maintain centralized field records for all member farmers.",
        sol_3_title: "Agronomists & Researchers",
        sol_3_desc: "Validated machine learning models, transparent soil optical pipelines, and calibrated agronomic reference data backed by PostgreSQL and Supabase.",
        plat_tag: "Scientific Methodology",
        plat_h2: "Data integrity without fabricated sensor claims",
        plat_desc: "We uphold strict scientific ethics: visible consumer RGB mobile cameras capture surface reflectance and cannot measure chemical NPK concentrations without laboratory chemical assays or calibrated spectroscopy. Geosense provides observable physical diagnostics and clearly directs users to accredited laboratories for soil chemistry.",
        footer_desc: "Software-only intelligent agriculture system integrating computer vision, ML crop modeling, and real-time agro-meteorology.",
        footer_modules: "Modules",
        footer_platform: "Platform",
        footer_account: "Account",
        footer_rights: "© 2026 Geosense Smart Agriculture. All rights reserved."
      }

    },

    // =========================================================================
    // HINDI DICTIONARY (हिन्दी)
    // =========================================================================
    hi: {
      brand: {
        name: "Geosense",
        tagline: "स्मार्ट कृषि हेतु AI आधारित उन्नत प्रणाली"
      },
      nav: {
        overview: "अवलोकन",
        soil: "मृदा NPK विश्लेषण",
        disease: "रोग एवं संक्रमण स्कैनर",
        crop: "फसल अनुशंसा",
        irrigation: "स्मार्ट सिंचाई",
        weather: "मौसम बुद्धिमत्ता",
        market: "मंडी बाज़ार भाव",
        community: "किसान समुदाय",
        assistant: "AI कृषि सहायक",
        profile: "किसान प्रोफ़ाइल",
        signout: "साइन आउट"
      },
      header: {
        title_overview: "फार्म अवलोकन (Dashboard)",
        title_soil: "मृदा NPK विश्लेषण और निदान",
        title_disease: "फसल रोग एवं संक्रमण स्कैनर",
        title_crop: "फसल चयन और अनुशंसा प्रणाली",
        title_irrigation: "सटीक सिंचाई जल निर्धारण",
        title_weather: "कृषि-मौसम टेलीमेट्री",
        title_market: "APMC मंडी कमोडिटी भाव",
        title_community: "किसान चर्चा और समुदाय मंच",
        title_assistant: "AI कृषि सहायक (जियो)",
        title_profile: "किसान प्रोफ़ाइल और सेटिंग्स",
        public_site: "🌐 मुख्य वेबसाइट",
        fastapi_live: "FastAPI लाइव: 127.0.0.1:8001"
      },
      overview: {
        metric_soil: "दर्ज मृदा परीक्षण",
        metric_soil_empty: "अभी तक कोई परीक्षण दर्ज नहीं",
        metric_crop: "फसल मॉडल स्थिति",
        metric_crop_empty: "अनुशंसा हेतु मॉडल चलाएं",
        metric_irrigation: "सिंचाई आवश्यकता",
        metric_irrigation_empty: "अभी गणना नहीं की गई",
        metric_weather: "स्थानीय मौसम",
        metric_weather_connecting: "मौसम डेटा से जुड़ रहा है...",
        badge_db: "डेटाबेस सत्यापित",
        badge_sklearn: "Scikit-Learn मॉडल",
        badge_fao56: "FAO-56 मानक",
        badge_live: "लाइव ओपन-मेटियो",
        shortcuts_title: "त्वरित कृषि शॉर्टकट",
        shortcut_soil: "मृदा परीक्षण दर्ज करें",
        shortcut_soil_desc: "लैब NPK या कैमरा स्कैन दर्ज करें",
        shortcut_crop: "फसल मॉडल चलाएं",
        shortcut_crop_desc: "NPK के आधार पर उपयुक्त फसल जानें",
        shortcut_water: "जल कैलकुलेटर",
        shortcut_water_desc: "सटीक सिंचाई मांग की गणना करें",
        recent_activities: "हालिया कृषि गतिविधियाँ",
        badge_activity: "वास्तविक गतिविधि लॉग",
        empty_activities: "कोई हालिया गतिविधि दर्ज नहीं है। जब आप मृदा परीक्षण, फसल मॉडल या सिंचाई गणना करेंगे तो वे यहाँ दिखाई देंगी।"
      },
      soil: {
        sub1_title: "1. कैमरा आधारित मृदा गुणवत्ता और बनावट परीक्षण",
        sub1_desc: "OpenCV छवि विश्लेषण प्रणाली मिट्टी की सतह, प्रकाश और रंग की बनावट का मूल्यांकन करती है।",
        badge_cv: "कंप्यूटर विज़न",
        ready_photo: "मिट्टी की फोटो जांचने के लिए तैयार",
        ready_photo_desc: "मोबाइल कैमरे से फोटो लें या गैलरी से अपलोड करें",
        btn_camera: "📷 कैमरा खोलें",
        btn_snap: "⚡ फोटो खींचें",
        btn_upload: "📁 गैलरी से चुनें",
        btn_reset: "🔄 रीसेट",
        btn_analyze: "AI गुणवत्ता जांच चलाएं",
        btn_predict_npk: "🔬 विज़न AI से NPK अनुमान (ONNX)",
        npk_result_title: "विज़न AI मृदा / पत्ता NPK अनुमान",
        npk_apply_btn: "📋 फसल व मृदा फॉर्म में भरें",
        sub2_title: "2. सत्यापित मृदा परीक्षण मान दर्ज करें (लैब या सेंसर)",
        sub2_desc: "प्रमाणित मृदा परीक्षण प्रयोगशाला या सेंसर किट से प्राप्त वास्तविक मान यहाँ दर्ज करें।",
        badge_lab: "प्रमाणित परीक्षण",
        label_n: "नाइट्रोजन (N) [किग्रा/हेक्टेयर]",
        label_p: "फास्फोरस (P) [किग्रा/हेक्टेयर]",
        label_k: "पोटैशियम (K) [किग्रा/हेक्टेयर]",
        label_ph: "मृदा पीएच (0.0 - 14.0)",
        label_ec: "विद्युत चालकता (EC) [dS/m]",
        label_moisture: "मृदा नमी (%)",
        label_source: "डेटा स्रोत / उपकरण",
        source_lab: "प्रमाणित कृषि प्रयोगशाला रिपोर्ट",
        source_sensor: "अंशांकित मृदा सेंसर किट",
        source_manual: "रासायनिक परीक्षण किट",
        label_facility: "प्रयोगशाला या किट का नाम",
        btn_save: "सत्यापित मृदा परीक्षण डेटाबेस में सहेजें",
        history_title: "सहेजा गया मृदा परीक्षण इतिहास",
        badge_db_records: "डेटाबेस रिकॉर्ड्स",
        history_empty_strong: "अभी तक कोई परीक्षण नहीं।",
        history_empty_desc: "शुरुआत करने के लिए ऊपर अपनी पहली लैब रिपोर्ट या स्कैन जोड़ें।"
      },
      crop: {
        title: "मशीन लर्निंग फसल अनुशंसा मॉडल",
        desc: "7 कृषि-जलवायु मापदंडों के आधार पर सर्वोत्तम फसल की भविष्यवाणी करने वाला Scikit-Learn मॉडल।",
        badge_classifier: "Scikit-Learn क्लासिफायर",
        label_temp: "तापमान (°C)",
        label_humidity: "सापेक्ष आर्द्रता (%)",
        label_rainfall: "वार्षिक वर्षा (mm)",
        btn_compute: "फसल अनुशंसा की गणना करें",
        history_title: "सहेजी गई फसल अनुशंसाएं",
        history_empty_strong: "अभी तक कोई अनुशंसा सहेजी नहीं गई।",
        history_empty_desc: "परिणाम देखने के लिए ऊपर अपनी पहली फसल अनुशंसा चलाएं।"
      },
      irrigation: {
        title: "स्मार्ट सिंचाई योजना एवं जल आवश्यकता",
        desc: "FAO-56 पेनमैन-मोंटीथ वाष्पोत्सर्जन मानक द्वारा मृदा नमी कमी के आधार पर जल आवश्यकता की गणना।",
        badge_fao56: "FAO-56 कार्यप्रणाली",
        label_crop: "फसल",
        label_stage: "विकास चरण",
        stage_initial: "प्रारंभिक चरण",
        stage_vegetative: "वानस्पतिक विकास",
        stage_flowering: "फूल आने का समय",
        stage_yield: "दाने/फल बनने का समय",
        stage_ripening: "पकने का चरण",
        label_moisture: "वर्तमान मृदा नमी (%)",
        label_area: "खेत का क्षेत्रफल (एकड़)",
        label_rain: "अनुमानित वर्षा (mm)",
        btn_calc: "सिंचाई जल आवश्यकता की गणना करें",
        history_title: "सहेजा गया सिंचाई इतिहास",
        history_empty_strong: "अभी तक कोई सिंचाई रिकॉर्ड नहीं।",
        history_empty_desc: "इतिहास देखने के लिए ऊपर अपने खेत की गणना करें।"
      },
      weather: {
        title: "लाइव कृषि-मौसम टेलीमेट्री",
        desc: "अत्यधिक सटीक वास्तविक समय स्थितियां, उपग्रह टेलीमेट्री और बहु-दिवसीय कृषि पूर्वानुमान।",
        placeholder_search: "शहर, जिला या गाँव खोजें (उदा. बेंगलुरु, मांड्या, पुणे, दिल्ली)...",
        btn_search: "स्थान खोजें",
        btn_gps: "📍 मेरा लाइव GPS पहचानें",
        map_title: "🛰️ कृषि भूमि उपग्रह नक्शा (GIS)",
        map_badge: "लाइव सैटेलाइट GIS",
        map_desc: "उच्च-रिज़ॉल्यूशन उपग्रह नक्शा। खेत को पिन करने, सीमा रेखा खींचने, रकबा नापने और मौसम टेलीमेट्री जोड़ने के लिए क्लिक करें।",
        btn_save_plot: "💾 खेत का भूखंड सहेजें",
        btn_saved_plots: "📂 सहेजे गए खेत",
        drawer_title: "आपके सहेजे गए कृषि भूखंड",
        map_search_placeholder: "गाँव, कस्बा या खेत का स्थान खोजें...",
        btn_current_gps: "📍 मेरे वर्तमान स्थान का उपयोग करें",
        btn_sat_view: "🛰️ उपग्रह दृश्य (डिफ़ॉल्ट)",
        btn_street_view: "🗺️ सड़क नक्शा",
        btn_draw: "✏️ सीमा बनाएं",
        btn_clear: "🗑️ सीमा साफ़ करें",
        hud_title: "टेलीमेट्री HUD",
        hud_status_default: "पिन लगाने हेतु क्लिक करें",
        hud_coord: "निर्देशांक:",
        hud_area: "क्षेत्रफल:",
        modal_title: "खेत का स्थान सहेजें",
        modal_label_name: "खेत / भूखंड का नाम *",
        modal_label_crop: "मुख्य फसल का प्रकार",
        modal_boundary_area: "सीमा क्षेत्रफल:",
        btn_cancel: "रद्द करें",
        btn_save_supabase: "Supabase में सहेजें"
      },
      market: {
        title: "APMC मंडी कमोडिटी बाज़ार भाव",
        desc: "आधिकारिक APMC कृषि उपज मंडी बुलेटिन से सत्यापित दैनिक फसल कीमतें।",
        badge_agmarknet: "Agmarknet भारत सरकार",
        label_commodity: "फसल/कमोडिटी चुनें:",
        loading: "सत्यापित मंडी भाव लोड हो रहे हैं..."
      },
      community: {
        title: "किसान चर्चा एवं ज्ञान विनिमय",
        desc: "किसानों के बीच सीधा संवाद, कीट प्रबंधन सलाह और खेत के अनुभव साझा करने का मंच।",
        btn_new: "✏️ नई चर्चा शुरू करें",
        modal_title: "सामुदायिक पोस्ट बनाएं",
        label_cat: "श्रेणी",
        cat_general: "सामान्य खेती",
        cat_soil: "मृदा स्वास्थ्य",
        cat_crop: "फसल सलाह",
        cat_pest: "कीट एवं रोग नियंत्रण",
        cat_market: "मंडी एवं बाज़ार",
        label_post_title: "पोस्ट का शीर्षक",
        placeholder_title: "उदा. गेहूं में पीला रतुआ रोग की रोकथाम",
        label_content: "चर्चा सामग्री",
        placeholder_content: "अपने खेत का अनुभव, प्रश्न या नई तकनीक साझा करें...",
        btn_publish: "पोस्ट प्रकाशित करें",
        empty_strong: "अभी तक कोई सामुदायिक चर्चा नहीं।",
        empty_desc: "ऊपर अपनी खेती से जुड़ी जानकारी साझा करके पहली चर्चा शुरू करें!"
      },
      assistant: {
        label_engine: "मॉडल इंजन:",
        cloud_btn: "☁️ क्लाउड AI (Qwen3)",
        offline_btn: "⚡ ऑफ़लाइन AI (Gemma 4 E2B)",
        status_cloud: "क्लाउड AI: Qwen3 सक्रिय",
        settings_btn: "⚙️ सेटिंग्स",
        greeting: "नमस्ते! मैं जियो हूँ, आपका AI कृषि सहायक। मैं आपके मिट्टी परीक्षण और लाइव मौसम के आधार पर सीधी सलाह देता हूँ। आज मैं आपकी फसल की क्या सहायता करूँ?",
        placeholder: "अपनी फसल के पत्तों, खाद या सिंचाई के बारे में पूछें...",
        placeholder_crop: "{crop} की पत्तियों, NPK खाद मात्रा या सिंचाई के बारे में पूछें...",
        prompt_1: "{crop} की पत्तियां पीली क्यों पड़ रही हैं?",
        prompt_2: "आज {crop} के लिए कितनी सिंचाई चाहिए?",
        prompt_3: "{crop} में यूरिया / NPK की सही मात्रा?",
        scan_btn_title: "मिट्टी या पत्ती फोटो स्कैन (NPK AI)",
        ph_not_tested: "pH: जांच नहीं हुई",
        context_label: "खेत संदर्भ",
        btn_send: "भेजें",
        attach_title: "पत्ती/मिट्टी की फोटो जोड़ें या पेस्ट करें",
        mode_disease: "🩺 रोग जांच",
        mode_npk: "🧪 मृदा NPK",
        chat_disease_label: "पत्ती और फसल संक्रमण स्कैन",
        chat_npk_label: "मृदा और पत्ती NPK स्कैन"
      },
      disease: {
        title: "फसल रोग एवं संक्रमण स्कैनर",
        desc: "द्वि-स्तरीय प्रमाणित रोग निदान (PlantVillage ONNX + ICAR/UAS मानक + NPK और लाइव मौसम जांच)।",
        badge_grounded: "ONNX + ICAR प्रमाणित",
        ready_title: "पत्ती या फसल की फोटो लें / अपलोड करें",
        ready_desc: "स्पष्ट निदान के लिए दिन की रोशनी में प्रभावित पत्ती से 15–25 सेमी दूरी पर फोटो लें।",
        btn_camera: "📷 कैमरा खोलें",
        btn_snap: "⚡ पत्ती फोटो कैप्चर करें",
        btn_upload: "📁 पत्ती/फसल फोटो चुनें",
        btn_reset: "🔄 रीसेट",
        btn_diagnose: "🩺 प्रमाणित रोग जांच चलाएं",
        question_placeholder: "वैकल्पिक लक्षण लिखें (जैसे: निचली पत्तियों पर धब्बे, पत्ती मुड़ना)...",
        card_detected: "पाया गया संक्रमण और विश्वास स्तर",
        card_why: "संक्रमण का कारण (जीव विज्ञान और मौसम प्रभाव)",
        card_solution: "सुझाया गया उपचार और मात्रा (Dosage)",
        tab_organic: "🌿 जैविक / सस्य नियंत्रण",
        tab_chemical: "🧪 लक्षित रासायनिक उपचार (ICAR)",
        card_prevention: "रोकथाम के उपाय",
        btn_followup: "🤖 AI कृषि सहायक (Geo) में आगे पूछें"
      },
      settings: {
        profile_title: "किसान प्रोफ़ाइल और खाता सेटिंग्स",
        badge_auth: "सत्यापित खाता",
        role_farmer: "भूमिका: किसान सदस्य",
        region_default: "फार्म: कर्नाटक / पंजाब",
        sync_desc: "आपकी प्रोफ़ाइल सत्यापित है और सीधे आपके सुरक्षित खाते से जुड़ी है। आपके सभी मृदा परीक्षण, फसल रिकॉर्ड और सिंचाई डेटा पूर्णतः सुरक्षित हैं।",
        language_title: "🌐 भाषा और स्थानीयकरण सेटिंग्स",
        badge_active: "सक्रिय प्राथमिकता",
        language_desc: "अपनी प्राथमिक भाषा चुनें। सभी डैशबोर्ड आंकड़े, मृदा विश्लेषण, लाइव मौसम अलर्ट और AI कृषि परामर्श तुरंत चुनी हुई भाषा में रूपांतरित हो जाएंगे।",
        lang_en: "English (अंग्रेज़ी)",
        lang_en_sub: "अंतर्राष्ट्रीय मानक",
        lang_hi: "हिन्दी (Hindi)",
        lang_hi_sub: "राष्ट्रीय कृषि संपर्क",
        lang_kn: "ಕನ್ನಡ (Kannada)",
        lang_kn_sub: "ಕರ್ನಾಟಕ ರೈತ ಸಂಪರ್ಕ"
      },
      landing: {
        nav_features: "विशेषताएं",
        nav_solutions: "समाधान",
        nav_platform: "प्लेटफ़ॉर्म",
        nav_about: "परिचय",
        nav_login: "लॉग इन",
        nav_dashboard: "डैशबोर्ड",
        nav_get_started: "शुरू करें",
        hero_title: 'स्मार्ट कृषि के लिए अपने AI साथी <span class="hl">जियो (Geo)</span> से मिलें',
        hero_trust: "प्रगतिशील किसान और कृषि वैज्ञानिक Geosense पर भरोसा करते हैं",
        hero_cta: "निःशुल्क शुरू करें",
        stmt_text: "जियो एक बुद्धिमान कृषि AI सहायक है<br>जो मिट्टी की जांच का विश्लेषण करता है, उपयुक्त फसल बताता है,<br>सटीक सिंचाई जल की गणना करता है, मंडी भाव ट्रैक करता है,<br>और बुवाई से कटाई तक किसानों का मार्गदर्शन करता है",
        telemetry_pill: "लाइव फार्म टेलीमेट्री",
        card_soil_tag: "मृदा जैव-रसायन",
        card_soil_desc: "मृदा नमी स्तर (VWC)",
        card_water_tag: "सटीक सिंचाई जल",
        card_water_desc: "फसल वाष्पीकरण (ET₀)",
        card_canopy_tag: "फसल स्वास्थ्य स्तर",
        card_canopy_desc: "वानस्पतिक स्वास्थ्य (NDVI)",
        card_mandi_tag: "APMC मंडी बाज़ार",
        card_mandi_desc: "गेहूं HD-2967 (मॉडल भाव)",
        split_title: "आपकी खेती की तरह ही<br>काम करने वाला AI कृषि विशेषज्ञ",
        split_sub: "स्मार्ट कृषि",
        split_p: "अधिक पैदावार प्राप्त करें। समझदारी से सिंचाई करें। अनुमान लगाना बंद करें। Geosense मोबाइल मृदा परीक्षण, ML फसल मॉडल और मौसम टेलीमेट्री को एकीकृत करता है ताकि आपके खेत को अधिकतम लाभ मिले।",
        feat_tag: "कृषि बुद्धिमत्ता",
        feat_h2: "कंप्यूटर विज़न और मशीन लर्निंग आधारित सटीक कृषि उपकरण",
        feat_desc: "मिट्टी की गुणवत्ता जांच से लेकर मौसम आधारित सिंचाई निर्धारण और लाइव मंडी भाव तक, Geosense किसानों को वैज्ञानिक निर्णय लेने में सक्षम बनाता है।",
        feat_1_title: "AI मृदा ऑप्टिकल जांच",
        feat_1_desc: "मोबाइल कैमरे से मिट्टी की तस्वीर लें। हमारी OpenCV प्रणाली वैज्ञानिक पारदर्शिता के साथ फोकस, प्रकाश और सतह की बनावट की जांच करती है।",
        feat_2_title: "ML फसल अनुशंसा",
        feat_2_desc: "प्रशिक्षित रैंडम फॉरेस्ट मॉडल मिट्टी के N, P, K, pH और मौसम के आंकड़ों का विश्लेषण कर सबसे अधिक पैदावार देने वाली फसल की सिफारिश करता है।",
        feat_3_title: "स्मार्ट सिंचाई इंजन",
        feat_3_desc: "FAO-56 मानकों के आधार पर फसल की वृद्धि अवस्था और बारिश के पूर्वानुमान को ध्यान में रखकर प्रति एकड़ पानी की सटीक मात्रा बताता है।",
        feat_4_title: "कृषि-मौसम टेलीमेट्री",
        feat_4_desc: "लाइव मौसम पूर्वानुमान के साथ अत्यधिक गर्मी, कीट प्रकोप के खतरे और भारी बारिश की जल निकासी चेतावनियां समय पर प्राप्त करें।",
        feat_5_title: "APMC मंडी बाज़ार भाव",
        feat_5_desc: "क्षेत्रीय कृषि मंडियों में प्रमुख फसलों के न्यूनतम, अधिकतम और मॉडल भाव 7-दिवसीय रुझानों के साथ देखें।",
        feat_6_title: "किसान समुदाय",
        feat_6_desc: "अन्य किसानों और कृषि वैज्ञानिकों से जुड़ें, जैविक खाद के परिणाम और कीट नियंत्रण तकनीकों को साझा करें।",
        sol_tag: "अनुकूलित समाधान",
        sol_h2: "किसानों, कृषि विशेषज्ञों और किसान उत्पादक संगठनों (FPO) के लिए तैयार",
        sol_desc: "चाहे 2 एकड़ का खेत हो या बड़ी किसान सहकारी समिति, Geosense हर स्तर पर आपकी सहायता करता है।",
        sol_1_title: "स्वतंत्र किसान",
        sol_1_desc: "बिना किसी महंगे उपकरण के सीधे अपने स्मार्टफोन से मिट्टी की जांच, मौसम चेतावनी और सिंचाई गणना प्राप्त करें।",
        sol_2_title: "FPO और सहकारी समितियां",
        sol_2_desc: "सामूहिक फसल योजना बनाएं, क्षेत्रीय मंडी भावों की तुलना करें और सभी सदस्यों का डिजिटल रिकॉर्ड रखें।",
        sol_3_title: "कृषि वैज्ञानिक & शोधकर्ता",
        sol_3_desc: "सत्यापित मशीन लर्निंग मॉडल, पारदर्शी मृदा विश्लेषण और PostgreSQL डेटाबेस के साथ शोध कार्य करें।",
        plat_tag: "वैज्ञानिक पद्धति",
        plat_h2: "बिना किसी भ्रामक दावे के वास्तविक डेटा अखंडता",
        plat_desc: "साधारण मोबाइल कैमरा केवल सतह की बनावट देख सकता है, रासायनिक NPK की सही जांच हेतु प्रयोगशाला परीक्षण आवश्यक है। Geosense सतह की स्थिति का निरीक्षण करता है और रासायनिक जांच हेतु प्रमाणित लैब जाने की सलाह देता है।",
        footer_desc: "कंप्यूटर विज़न, मशीन लर्निंग और मौसम टेलीमेट्री को एकीकृत करने वाली सॉफ्टवेयर प्रणाली।",
        footer_modules: "मॉड्यूल",
        footer_platform: "प्लेटफ़ॉर्म",
        footer_account: "खाता",
        footer_rights: "© 2026 Geosense Smart Agriculture. सर्वाधिकार सुरक्षित।"
      }

    },

    // =========================================================================
    // KANNADA DICTIONARY (ಕನ್ನಡ)
    // =========================================================================
    kn: {
      brand: {
        name: "Geosense",
        tagline: "ಸ್ಮಾರ್ಟ್ ಕೃಷಿಗಾಗಿ AI ಬುದ್ಧಿವಂತ ವ್ಯವಸ್ಥೆ"
      },
      nav: {
        overview: "ಅವಲೋಕನ",
        soil: "ಮಣ್ಣಿನ NPK ವಿಶ್ಲೇಷಣೆ",
        disease: "ಬೆಳೆ ರೋಗ ಮತ್ತು ಸೋಂಕು ಸ್ಕ್ಯಾನರ್",
        crop: "ಬೆಳೆ ಶಿಫಾರಸು",
        irrigation: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ",
        weather: "ಹವಾಮಾನ ಮಾಹಿತಿ",
        market: "ಮಂಡಿ ಮಾರುಕಟ್ಟೆ",
        community: "ರೈತ ಸಮುದಾಯ",
        assistant: "AI ಕೃಷಿ ಸಹಾಯಕ",
        profile: "ರೈತರ ಪ್ರೊಫೈಲ್",
        signout: "ಸೈನ್ ಔಟ್"
      },
      header: {
        title_overview: "ಕೃಷಿ ಅವಲೋಕನ (Dashboard)",
        title_soil: "ಮಣ್ಣಿನ NPK ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ತಪಾಸಣೆ",
        title_disease: "ಬೆಳೆ ರೋಗ ಮತ್ತು ಸೋಂಕು ತಪಾಸಣೆ",
        title_crop: "ಉತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸು ವ್ಯವಸ್ಥೆ",
        title_irrigation: "ನಿಖರ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ",
        title_weather: "ಕೃಷಿ ಹವಾಮಾನ ಟೆಲಿಮೆಟ್ರಿ",
        title_market: "APMC ಮಂಡಿ ಸರಕು ದರಗಳು",
        title_community: "ರೈತರ ಚರ್ಚಾ ವೇದಿಕೆ ಮತ್ತು ಸಮುದಾಯ",
        title_assistant: "AI ಕೃಷಿ ಸಹಾಯಕ (ಜಿಯೋ)",
        title_profile: "ರೈತರ ವಿವರ ಮತ್ತು ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        public_site: "🌐 ಮುಖ್ಯ ಪುಟ",
        fastapi_live: "FastAPI ಲೈವ್: 127.0.0.1:8001"
      },
      overview: {
        metric_soil: "ದಾಖಲಾದ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಗಳು",
        metric_soil_empty: "ಇನ್ನೂ ಯಾವುದೇ ಪರೀಕ್ಷೆ ಸಲ್ಲಿಸಿಲ್ಲ",
        metric_crop: "ಬೆಳೆ ಮಾದರಿ ಸ್ಥಿತಿ",
        metric_crop_empty: "ಶಿಫಾರಸು ಪಡೆಯಲು ಮಾದರಿ ಚಲಾಯಿಸಿ",
        metric_irrigation: "ನೀರಾವರಿ ಅಗತ್ಯತೆ",
        metric_irrigation_empty: "ಇನ್ನೂ ಲೆಕ್ಕಾಚಾರ ಮಾಡಿಲ್ಲ",
        metric_weather: "ಸ್ಥಳೀಯ ಹವಾಮಾನ",
        metric_weather_connecting: "ಹವಾಮಾನ ಕೇಂದ್ರಕ್ಕೆ ಸಂಪರ್ಕಿಸಲಾಗುತ್ತಿದೆ...",
        badge_db: "ಡೇಟಾಬೇಸ್ ದೃಢೀಕರಿಸಲಾಗಿದೆ",
        badge_sklearn: "Scikit-Learn ಮಾದರಿ",
        badge_fao56: "FAO-56 ಗುಣಮಟ್ಟ",
        badge_live: "ಲೈವ್ ಓಪನ್-ಮೆಟಿಯೋ",
        shortcuts_title: "ತ್ವರಿತ ಕೃಷಿ ಸೇವೆಗಳು",
        shortcut_soil: "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ ದಾಖಲಿಸಿ",
        shortcut_soil_desc: "ಲ್ಯಾಬ್ NPK ಅಥವಾ ಕ್ಯಾಮೆರಾ ಸ್ಕ್ಯಾನ್ ನಮೂದಿಸಿ",
        shortcut_crop: "ಬೆಳೆ ಮಾದರಿ ಚಲಾಯಿಸಿ",
        shortcut_crop_desc: "NPK ಆಧಾರದ ಮೇಲೆ ಸೂಕ್ತ ಬೆಳೆ ತಿಳಿಯಿರಿ",
        shortcut_water: "ನೀರಿನ ಕ್ಯಾಲ್ಕುಲೇಟರ್",
        shortcut_water_desc: "ನಿಖರ ಲೀಟರ್ ಕೊರತೆಯನ್ನು ಲೆಕ್ಕಹಾಕಿ",
        recent_activities: "ಇತ್ತೀಚಿನ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳು",
        badge_activity: "ನೈಜ ಚಟುವಟಿಕೆ ದಾಖಲೆ",
        empty_activities: "ಯಾವುದೇ ಇತ್ತೀಚಿನ ಚಟುವಟಿಕೆ ದಾಖಲಾಗಿಲ್ಲ. ನೀವು ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ, ಬೆಳೆ ಮಾದರಿ ಅಥವಾ ನೀರಾವರಿ ಲೆಕ್ಕಹಾಕಿದಾಗ ಅವು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ."
      },
      soil: {
        sub1_title: "1. ಕ್ಯಾಮೆರಾ ಆಪ್ಟಿಕಲ್ ಮಣ್ಣಿನ ತಪಾಸಣೆ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ",
        sub1_desc: "OpenCV ಇಮೇಜ್ ಪ್ರೊಸೆಸಿಂಗ್ ಮೂಲಕ ಮಣ್ಣಿನ ಮೇಲ್ಮೈ, ಬೆಳಕು ಮತ್ತು ಭೌತಿಕ ಗುಣಮಟ್ಟವನ್ನು ಪರೀಕ್ಷಿಸಲಾಗುತ್ತದೆ.",
        badge_cv: "ಕಂಪ್ಯೂಟರ್ ವಿಷನ್",
        ready_photo: "ಮಣ್ಣಿನ ಫೋಟೋ ಪರೀಕ್ಷಿಸಲು ಸಿದ್ಧವಾಗಿದೆ",
        ready_photo_desc: "ಕ್ಯಾಮೆರಾ ಬಳಸಿ ಫೋಟೋ ತೆಗೆಯಿರಿ ಅಥವಾ ಗ್ಯಾಲರಿಯಿಂದ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        btn_camera: "📷 ಮೊಬೈಲ್ ಕ್ಯಾಮೆರಾ ತೆರೆಯಿರಿ",
        btn_snap: "⚡ ಫೋಟೋ ಸೆರೆಹಿಡಿಯಿರಿ",
        btn_upload: "📁 ಗ್ಯಾಲರಿಯಿಂದ ಆಯ್ಕೆಮಾಡಿ",
        btn_reset: "🔄 ಮರುಹೊಂದಿಸಿ",
        btn_analyze: "AI ಗುಣಮಟ್ಟ ತಪಾಸಣೆ ನಡೆಸಿ",
        btn_predict_npk: "🔬 ವಿಷನ್ AI NPK ಅಂದಾಜು (ONNX)",
        npk_result_title: "ವಿಷನ್ AI ಮಣ್ಣು / ಎಲೆ NPK ಮುನ್ಸೂಚನೆ",
        npk_apply_btn: "📋 ಬೆಳೆ ಮತ್ತು ಮಣ್ಣಿನ ಫಾರ್ಮ್‌ಗೆ ಅನ್ವಯಿಸಿ",
        sub2_title: "2. ದೃಢೀಕರಿಸಿದ ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ಮೌಲ್ಯಗಳನ್ನು ನಮೂದಿಸಿ (ಲ್ಯಾಬ್ ಅಥವಾ ಸೆನ್ಸಾರ್)",
        sub2_desc: "ಪ್ರಮಾಣೀಕೃತ ಮಣ್ಣು ಪರೀಕ್ಷಾ ಕೇಂದ್ರ ಅಥವಾ ಡಿಜಿಟಲ್ ಕಿಟ್‌ನಿಂದ ಪಡೆದ ನೈಜ ಮೌಲ್ಯಗಳನ್ನು ದಾಖಲಿಸಿ.",
        badge_lab: "ಪ್ರಮಾಣೀಕೃತ ವರದಿ",
        label_n: "ಸಾರಜನಕ (N) [ಕೆಜಿ/ಹೆಕ್ಟೇರ್]",
        label_p: "ರಂಜಕ (P) [ಕೆಜಿ/ಹೆಕ್ಟೇರ್]",
        label_k: "ಪೊಟ್ಯಾಷ್ (K) [ಕೆಜಿ/ಹೆಕ್ಟೇರ್]",
        label_ph: "ಮಣ್ಣಿನ ಪಿಹೆಚ್ (0.0 - 14.0)",
        label_ec: "ವಿದ್ಯುತ್ ವಾಹಕತೆ (EC) [dS/m]",
        label_moisture: "ಮಣ್ಣಿನ ತೇವಾಂಶ (%)",
        label_source: "ಡೇಟಾ ಮೂಲ / ಉಪಕರಣ",
        source_lab: "ಪ್ರಮಾಣೀಕೃತ ಕೃಷಿ ಪ್ರಯೋಗಾಲಯದ ವರದಿ",
        source_sensor: "ಕ್ಯಾಲಿಬ್ರೇಟ್ ಮಾಡಿದ ಮಣ್ಣಿನ ಸೆನ್ಸಾರ್ ಕಿಟ್",
        source_manual: "ಹ್ಯಾಂಡ್‌ಹೆಲ್ಡ್ ರಾಸಾಯನಿಕ ಕಿಟ್",
        label_facility: "ಲ್ಯಾಬ್ ಅಥವಾ ಕಿಟ್ ಹೆಸರು",
        btn_save: "ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಯನ್ನು ಡೇಟಾಬೇಸ್‌ಗೆ ಉಳಿಸಿ",
        history_title: "ಉಳಿಸಿದ ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ಇತಿಹಾಸ",
        badge_db_records: "ಡೇಟಾಬೇಸ್ ದಾಖಲೆಗಳು",
        history_empty_strong: "ಇನ್ನೂ ಯಾವುದೇ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಗಳಿಲ್ಲ.",
        history_empty_desc: "ಪ್ರಾರಂಭಿಸಲು ಮೇಲೆ ನಿಮ್ಮ ಮೊದಲ ಲ್ಯಾಬ್ ವರದಿ ಅಥವಾ ಸ್ಕ್ಯಾನ್ ಸೇರಿಸಿ."
      },
      crop: {
        title: "ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಬೆಳೆ ಶಿಫಾರಸು ಮಾದರಿ",
        desc: "7 ಕೃಷಿ-ಹವಾಮಾನ ನಿಯತಾಂಕಗಳ ಆಧಾರದ ಮೇಲೆ ಸೂಕ್ತ ಬೆಳೆಯನ್ನು ನಿಖರವಾಗಿ ಊಹಿಸುವ Scikit-Learn ಮಾದರಿ.",
        badge_classifier: "Scikit-Learn ಕ್ಲಾಸಿಫೈಯರ್",
        label_temp: "ತಾಪಮಾನ (°C)",
        label_humidity: "ಸಾಪೇಕ್ಷ ಆರ್ದ್ರತೆ (%)",
        label_rainfall: "ವಾರ್ಷಿಕ ಮಳೆ (ಮಿಮೀ)",
        btn_compute: "ಬೆಳೆ ಶಿಫಾರಸು ಲೆಕ್ಕಹಾಕಿ",
        history_title: "ಉಳಿಸಿದ ಬೆಳೆ ಶಿಫಾರಸುಗಳು",
        history_empty_strong: "ಯಾವುದೇ ಬೆಳೆ ಶಿಫಾರಸು ಇನ್ನೂ ಉಳಿಸಲಾಗಿಲ್ಲ.",
        history_empty_desc: "ಫಲಿತಾಂಶಗಳನ್ನು ನೋಡಲು ಮೇಲೆ ನಿಮ್ಮ ಮೊದಲ ಬೆಳೆ ಶಿಫಾರಸನ್ನು ಚಲಾಯಿಸಿ."
      },
      irrigation: {
        title: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ನೀರಿನ ಬೇಡಿಕೆ",
        desc: "FAO-56 ಪೆನ್‌ಮನ್-ಮಾಂಟೀತ್ ಮಾನದಂಡದ ಪ್ರಕಾರ ಮಣ್ಣಿನ ತೇವಾಂಶದ ಕೊರತೆಯಿಂದ ನೀರಿನ ಅಗತ್ಯತೆಯನ್ನು ಲೆಕ್ಕಹಾಕಲಾಗುತ್ತದೆ.",
        badge_fao56: "FAO-56 ವಿಧಾನ",
        label_crop: "ಬೆಳೆ",
        label_stage: "ಬೆಳವಣಿಗೆಯ ಹಂತ",
        stage_initial: "ಆರಂಭಿಕ ಹಂತ",
        stage_vegetative: "ಸಸ್ಯಕ ಬೆಳವಣಿಗೆ",
        stage_flowering: "ಹೂಬಿಡುವ ಹಂತ",
        stage_yield: "ಕಾಳು/ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ",
        stage_ripening: "ಮಾಗುವ ಹಂತ",
        label_moisture: "ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ತೇವಾಂಶ (%)",
        label_area: "ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣ (ಎಕರೆ)",
        label_rain: "ಮಳೆಯ ಮುನ್ಸೂಚನೆ (ಮಿಮೀ)",
        btn_calc: "ನೀರಿನ ಅಗತ್ಯತೆಯನ್ನು ಲೆಕ್ಕಹಾಕಿ",
        history_title: "ಉಳಿಸಿದ ನೀರಾವರಿ ಇತಿಹಾಸ",
        history_empty_strong: "ಯಾವುದೇ ನೀರಾವರಿ ದಾಖಲೆಗಳಿಲ್ಲ.",
        history_empty_desc: "ದಾಖಲೆಗಳನ್ನು ನೋಡಲು ಮೇಲೆ ನಿಮ್ಮ ಮೊದಲ ಜಮೀನಿನ ಅಗತ್ಯತೆಯನ್ನು ಲೆಕ್ಕಹಾಕಿ."
      },
      weather: {
        title: "ಲೈವ್ ಕೃಷಿ-ಹವಾಮಾನ ಟೆಲಿಮೆಟ್ರಿ",
        desc: "ನೈಜ ಸಮಯದ ನಿಖರ ಹವಾಮಾನ, ಉಪಗ್ರಹ ಟೆಲಿಮೆಟ್ರಿ ಮತ್ತು ಹಲವು ದಿನಗಳ ಕೃಷಿ ಮುನ್ಸೂಚನೆ.",
        placeholder_search: "ಯಾವುದೇ ಊರು, ಜಿಲ್ಲೆ ಅಥವಾ ಗ್ರಾಮವನ್ನು ಹುಡುಕಿ (ಉದಾ: ಬೆಂಗಳೂರು, ಮಂಡ್ಯ, ಪುಣೆ, ಧಾರವಾಡ)...",
        btn_search: "ಸ್ಥಳ ಹುಡುಕಿ",
        btn_gps: "📍 ನನ್ನ ಲೈವ್ ಜಿಪಿಎಸ್ ಗುರುತಿಸಿ",
        map_title: "🛰️ ಕೃಷಿ ಭೂಮಿ ಉಪಗ್ರಹ ನಕ್ಷೆ (GIS)",
        map_badge: "ಲೈವ್ ಉಪಗ್ರಹ GIS",
        map_desc: "ಹೈ-ರೆಸಲ್ಯೂಶನ್ ಉಪಗ್ರಹ ಕೃಷಿ ನಕ್ಷೆ. ಜಮೀನಿನ ಗುರುತು ಹಾಕಲು, ಗಡಿ ರೇಖೆ ಎಳೆಯಲು, ವಿಸ್ತೀರ್ಣ ಲೆಕ್ಕಹಾಕಲು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಲಿಂಕ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ.",
        btn_save_plot: "💾 ಜಮೀನಿನ ಪ್ಲಾಟ್ ಉಳಿಸಿ",
        btn_saved_plots: "📂 ಉಳಿಸಿದ ಜಮೀನುಗಳು",
        drawer_title: "ನಿಮ್ಮ ಉಳಿಸಿದ ಕೃಷಿ ಜಮೀನುಗಳು",
        map_search_placeholder: "ಗ್ರಾಮ, ತಾಲೂಕು ಅಥವಾ ಜಮೀನಿನ ಸ್ಥಳ ಹುಡುಕಿ...",
        btn_current_gps: "📍 ಪ್ರಸ್ತುತ ಸ್ಥಳವನ್ನು ಬಳಸಿ",
        btn_sat_view: "🛰️ ಉಪಗ್ರಹ ನೋಟ (ಡೀಫಾಲ್ಟ್)",
        btn_street_view: "🗺️ ರಸ್ತೆ ನಕ್ಷೆ",
        btn_draw: "✏️ ಗಡಿ ರೇಖೆ ಎಳೆಯಿರಿ",
        btn_clear: "🗑️ ಗಡಿ ರೇಖೆ ಅಳಿಸಿ",
        hud_title: "ಟೆಲಿಮೆಟ್ರಿ HUD",
        hud_status_default: "ಪಿನ್ ಮಾಡಲು ನಕ್ಷೆಯಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ",
        hud_coord: "ಅಕ್ಷಾಂಶ-ರೇಖಾಂಶ:",
        hud_area: "ವಿಸ್ತೀರ್ಣ:",
        modal_title: "ಜಮೀನಿನ ಸ್ಥಳವನ್ನು ಉಳಿಸಿ",
        modal_label_name: "ಜಮೀನು / ಪ್ಲಾಟ್ ಹೆಸರು *",
        modal_label_crop: "ಮುಖ್ಯ ಬೆಳೆಯ ವಿಧ",
        modal_boundary_area: "ಗಡಿಯ ವಿಸ್ತೀರ್ಣ:",
        btn_cancel: "ರದ್ದುಮಾಡಿ",
        btn_save_supabase: "Supabase ಗೆ ಉಳಿಸಿ"
      },
      market: {
        title: "APMC ಮಂಡಿ ಸರಕು ಮಾರುಕಟ್ಟೆ ಮಾಹಿತಿ",
        desc: "ಸರ್ಕಾರಿ APMC ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಬುಲೆಟಿನ್‌ಗಳಿಂದ ಪಡೆದ ಅಧಿಕೃತ ಮತ್ತು ದೃಢೀಕರಿಸಿದ ದರಗಳು.",
        badge_agmarknet: "Agmarknet ಭಾರತ ಸರ್ಕಾರ",
        label_commodity: "ಬೆಳೆ/ಸರಕು ಆಯ್ಕೆಮಾಡಿ:",
        loading: "ದೃಢೀಕರಿಸಿದ ಮಂಡಿ ದರಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..."
      },
      community: {
        title: "ರೈತರ ಚರ್ಚೆ ಮತ್ತು ಜ್ಞಾನ ವಿನಿಮಯ",
        desc: "ರೈತರೊಂದಿಗೆ ನೇರ ಸಂವಾದ, ಕೀಟ ಬಾಧೆ ಪರಿಹಾರಗಳು ಮತ್ತು ಕೃಷಿ ಅನುಭವಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳುವ ವೇದಿಕೆ.",
        btn_new: "✏️ ಹೊಸ ಚರ್ಚೆ ಪ್ರಾರಂಭಿಸಿ",
        modal_title: "ಸಮುದಾಯ ಪೋಸ್ಟ್ ರಚಿಸಿ",
        label_cat: "ವರ್ಗ",
        cat_general: "ಸಾಮಾನ್ಯ ಕೃಷಿ",
        cat_soil: "ಮಣ್ಣಿನ ಆರೋಗ್ಯ",
        cat_crop: "ಬೆಳೆ ಸಲಹೆ",
        cat_pest: "ಕೀಟ ಮತ್ತು ರೋಗ ನಿಯಂತ್ರಣ",
        cat_market: "ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಮಂಡಿ",
        label_post_title: "ಪೋಸ್ಟ್ ಶೀರ್ಷಿಕೆ",
        placeholder_title: "ಉದಾ. ಭತ್ತದಲ್ಲಿ ಕವಡೆ ರೋಗದ ನಿರ್ವಹಣೆ",
        label_content: "ಚರ್ಚಾ ವಿವರ",
        placeholder_content: "ನಿಮ್ಮ ಕೃಷಿ ಅನುಭವ, ಪ್ರಶ್ನೆ ಅಥವಾ ಹೊಸ ಪದ್ಧತಿಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ...",
        btn_publish: "ಪೋಸ್ಟ್ ಪ್ರಕಟಿಸಿ",
        empty_strong: "ಯಾವುದೇ ಸಮುದಾಯ ಚರ್ಚೆಗಳು ಇನ್ನೂ ಇಲ್ಲ.",
        empty_desc: "ಮೇಲೆ ನಿಮ್ಮ ಕೃಷಿ ಅನುಭವವನ್ನು ಹಂಚಿಕೊಳ್ಳುವ ಮೂಲಕ ಮೊದಲ ಚರ್ಚೆಯನ್ನು ಪ್ರಾರಂಭಿಸಿ!"
      },
      assistant: {
        label_engine: "ಮಾಡೆಲ್ ಇಂಜಿನ್:",
        cloud_btn: "☁️ ಕ್ಲೌಡ್ AI (Qwen3)",
        offline_btn: "⚡ ಆಫ್‌ಲೈನ್ AI (Gemma 4 E2B)",
        status_cloud: "ಕ್ಲೌಡ್ AI: Qwen3 ಸಕ್ರಿಯ",
        settings_btn: "⚙️ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        greeting: "ನಮಸ್ಕಾರ! ನಾನು ಜಿಯೋ, ನಿಮ್ಮ AI ಕೃಷಿ ಸಹಾಯಕ. ನಿಮ್ಮ ಮಣ್ಣಿನ ವರದಿ ಮತ್ತು ಲೈವ್ ಹವಾಮಾನದ ಆಧಾರದ ಮೇಲೆ ನೇರ ಸಲಹೆ ನೀಡುತ್ತೇನೆ. ಇಂದು ನಿಮ್ಮ ಬೆಳೆಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
        placeholder: "ಬೆಳೆ ಎಲೆ, ಗೊಬ್ಬರ ಪ್ರಮಾಣ ಅಥವಾ ನೀರಾವರಿ ಕುರಿತು ಕೇಳಿ...",
        placeholder_crop: "{crop} ಎಲೆ ಬಣ್ಣ, NPK ಗೊಬ್ಬರ ಅಥವಾ ನೀರಾವರಿ ಕುರಿತು ಕೇಳಿ...",
        prompt_1: "{crop} ಎಲೆಗಳು ಹಳದಿಯಾಗಲು ಕಾರಣವೇನು?",
        prompt_2: "ಇಂದು {crop} ಬೆಳೆಗೆ ಎಷ್ಟು ನೀರು ಬೇಕು?",
        prompt_3: "{crop} ಗೆ ಯೂರಿಯಾ / NPK ಪ್ರಮಾಣ ಎಷ್ಟು?",
        scan_btn_title: "ಮಣ್ಣು / ಎಲೆ ಫೋಟೋ ಸ್ಕ್ಯಾನ್ (NPK AI)",
        ph_not_tested: "pH: ಪರೀಕ್ಷಿಸಲಾಗಿಲ್ಲ",
        context_label: "ಜಮೀನು ವಿವರ",
        btn_send: "ಕಳುಹಿಸಿ",
        attach_title: "ಎಲೆ / ಮಣ್ಣಿನ ಫೋಟೋ ಲಗತ್ತಿಸಿ ಅಥವಾ ಪೇಸ್ಟ್ ಮಾಡಿ",
        mode_disease: "🩺 ರೋಗ ತಪಾಸಣೆ",
        mode_npk: "🧪 ಮಣ್ಣಿನ NPK",
        chat_disease_label: "ಎಲೆ ಮತ್ತು ಬೆಳೆ ಸೋಂಕು ಸ್ಕ್ಯಾನ್",
        chat_npk_label: "ಮಣ್ಣು ಮತ್ತು ಎಲೆ NPK ಸ್ಕ್ಯಾನ್"
      },
      disease: {
        title: "ಬೆಳೆ ರೋಗ ಮತ್ತು ಸೋಂಕು ಸ್ಕ್ಯಾನರ್",
        desc: "ದ್ವಿ-ಹಂತದ ಪ್ರಮಾಣೀಕೃತ ರೋಗ ಪತ್ತೆ (PlantVillage ONNX + ICAR / UAS ಧಾರವಾಡ ಮಾರ್ಗಸೂಚಿ + NPK ಮತ್ತು ಹವಾಮಾನ ಪರಿಶೀಲನೆ).",
        badge_grounded: "ONNX + ICAR ಪ್ರಮಾಣೀಕೃತ",
        ready_title: "ಎಲೆ ಅಥವಾ ಬೆಳೆ ಫೋಟೋ ತೆಗೆಯಿರಿ / ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        ready_desc: "ಸ್ಪಷ್ಟ ಫಲಿತಾಂಶಕ್ಕಾಗಿ ಹಗಲು ಬೆಳಕಿನಲ್ಲಿ ಎಲೆಯಿಂದ 15–25 ಸೆಂ.ಮೀ ದೂರದಿಂದ ಫೋಟೋ ತೆಗೆಯಿರಿ.",
        btn_camera: "📷 ಕ್ಯಾಮೆರಾ ತೆಗೆಯಿರಿ",
        btn_snap: "⚡ ಎಲೆ ಚಿತ್ರ ಸೆರೆಹಿಡಿಯಿರಿ",
        btn_upload: "📁 ಎಲೆ / ಬೆಳೆ ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ",
        btn_reset: "🔄 ಮರುಹೊಂದಿಸಿ",
        btn_diagnose: "🩺 ರೋಗ ತಪಾಸಣೆ ನಡೆಸಿ",
        question_placeholder: "ಐಚ್ಛಿಕ ಲಕ್ಷಣ ಬರೆಯಿರಿ (ಉದಾ: ಕೆಳಗಿನ ಎಲೆಗಳಲ್ಲಿ ಮಚ್ಚೆ, ಎಲೆ ಸುರುಳಿ)...",
        card_detected: "ಪತ್ತೆಯಾದ ಸೋಂಕು ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹತೆ",
        card_why: "ಸೋಂಕಿಗೆ ಕಾರಣ (ಜೀವಶಾಸ್ತ್ರ ಮತ್ತು ಹವಾಮಾನ ಪ್ರಭಾವ)",
        card_solution: "ಶಿಫಾರಸು ಮಾಡಿದ ಪರಿಹಾರ ಮತ್ತು ಪ್ರಮಾಣ (Dosage)",
        tab_organic: "🌿 ಸಾವಯವ / ಕೃಷಿ ನಿಯಂತ್ರಣ",
        tab_chemical: "🧪 ನಿರ್ದಿಷ್ಟ ರಾಸಾಯನಿಕ ನಿಯಂತ್ರಣ (ICAR)",
        card_prevention: "ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳು",
        btn_followup: "🤖 AI ಕೃಷಿ ಸಹಾಯಕ (Geo) ನಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ"
      },
      settings: {
        profile_title: "ರೈತರ ವಿವರ ಮತ್ತು ಖಾತೆ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        badge_auth: "ದೃಢೀಕರಿಸಿದ ಖಾತೆ",
        role_farmer: "ಪಾತ್ರ: ರೈತ ಸದಸ್ಯ",
        region_default: "ಜಮೀನು: ಕರ್ನಾಟಕ",
        sync_desc: "ನಿಮ್ಮ ಪ್ರೊಫೈಲ್ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟಿದೆ ಮತ್ತು ಸುರಕ್ಷಿತ ಡೇಟಾಬೇಸ್‌ನೊಂದಿಗೆ ಲಿಂಕ್ ಆಗಿದೆ. ನಿಮ್ಮ ಎಲ್ಲಾ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಗಳು, ಬೆಳೆ ದಾಖಲೆಗಳು ಮತ್ತು ನೀರಾವರಿ ಮಾಹಿತಿಯು ಸುರಕ್ಷಿತವಾಗಿರುತ್ತದೆ.",
        language_title: "🌐 ಭಾಷೆ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        badge_active: "ಸಕ್ರಿಯ ಆದ್ಯತೆ",
        language_desc: "ನಿಮ್ಮ ಆದ್ಯತೆಯ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ. ಎಲ್ಲಾ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ಅಂಕಿಅಂಶಗಳು, ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ, ಹವಾಮಾನ ಎಚ್ಚರಿಕೆಗಳು ಮತ್ತು AI ಕೃಷಿ ಸಲಹೆಗಳು ತಕ್ಷಣವೇ ಈ ಭಾಷೆಗೆ ಬದಲಾಗುತ್ತವೆ.",
        lang_en: "English (ಇಂಗ್ಲಿಷ್)",
        lang_en_sub: "ಅಂತಾರಾಷ್ಟ್ರೀಯ ಪ್ರಮಾಣಿತ",
        lang_hi: "हिन्दी (ಹಿಂದಿ)",
        lang_hi_sub: "ರಾಷ್ಟ್ರೀಯ ಸಂಪರ್ಕ",
        lang_kn: "ಕನ್ನಡ (Kannada)",
        lang_kn_sub: "ಕರ್ನಾಟಕ ರೈತ ಸಂಪರ್ಕ"
      },
      landing: {
        nav_features: "ವೈಶಿಷ್ಟ್ಯಗಳು",
        nav_solutions: "ಪರಿಹಾರಗಳು",
        nav_platform: "ಪ್ಲಾಟ್‌ಫಾರ್ಮ್",
        nav_about: "ನಮ್ಮ ಬಗ್ಗೆ",
        nav_login: "ಲಾಗಿನ್",
        nav_dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        nav_get_started: "ಪ್ರಾರಂಭಿಸಿ",
        hero_title: 'ಸ್ಮಾರ್ಟ್ ಕೃಷಿಗಾಗಿ ನಿಮ್ಮ AI ಸಹಾಯಕ <span class="hl">ಜಿಯೋ (Geo)</span> ನೊಂದಿಗೆ ಕೃಷಿ ನಡೆಸಿ',
        hero_trust: "ಪ್ರಗತಿಪರ ರೈತರು ಮತ್ತು ಕೃಷಿ ವಿಜ್ಞಾನಿಗಳು ಜಿಯೋಸೆನ್ಸ್ ಅನ್ನು ನಂಬುತ್ತಾರೆ",
        hero_cta: "ಉಚಿತವಾಗಿ ಪ್ರಾರಂಭಿಸಿ",
        stmt_text: "ಜಿಯೋ ಒಂದು ಬುದ್ಧಿವಂತ ಕೃಷಿ AI ಸಹಾಯಕ<br>ಇದು ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ, ಸೂಕ್ತ ಬೆಳೆಗಳನ್ನು ಸೂಚಿಸುತ್ತದೆ,<br>ನಿಖರವಾದ ನೀರಾವರಿ ನೀರಿನ ಲೆಕ್ಕಾಚಾರ ಮಾಡುತ್ತದೆ, ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ದರಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತದೆ,<br>ಮತ್ತು ಬಿತ್ತನೆಯಿಂದ ಕಟಾವಿನವರೆಗೆ ರೈತರಿಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತದೆ",
        telemetry_pill: "ಲೈವ್ ಫಾರ್ಮ್ ಟೆಲಿಮೆಟ್ರಿ",
        card_soil_tag: "ಮಣ್ಣಿನ ಜೈವಿಕ ರಸಾಯನಶಾಸ್ತ್ರ",
        card_soil_desc: "ಮಣ್ಣಿನ ತೇವಾಂಶ ಮಟ್ಟ (VWC)",
        card_water_tag: "ನಿಖರ ನೀರಾವರಿ ನೀರು",
        card_water_desc: "ಬೆಳೆ ಬಾಷ್ಪೀಕರಣ (ET₀)",
        card_canopy_tag: "ಬೆಳೆ ಆರೋಗ್ಯ ಸ್ಥಿತಿ",
        card_canopy_desc: "ಸಸ್ಯವರ್ಗದ ಆರೋಗ್ಯ ಸೂಚ್ಯಂಕ (NDVI)",
        card_mandi_tag: "APMC ಮಂಡಿ ಮಾರುಕಟ್ಟೆ",
        card_mandi_desc: "ಗೋಧಿ HD-2967 (ಮಾದರಿ ದರ)",
        split_title: "ನಿಮ್ಮ ಕೃಷಿಗೆ ತಕ್ಕಂತೆ ಕೆಲಸ ಮಾಡುವ<br>ಬುದ್ಧಿವಂತ AI ಕೃಷಿ ತಜ್ಞ",
        split_sub: "ಸ್ಮಾರ್ಟ್ ಕೃಷಿ",
        split_p: "ಹೆಚ್ಚು ಇಳುವರಿ ಪಡೆಯಿರಿ. ಜಾಣತನದಿಂದ ನೀರಾವರಿ ಮಾಡಿ. ಊಹೆ ಮಾಡುವುದನ್ನು ನಿಲ್ಲಿಸಿ. Geosense ಮೊಬೈಲ್ ಮಣ್ಣಿನ ವಿಶ್ಲೇಷಣೆ, ML ಬೆಳೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು ಹವಾಮಾನ ಟೆಲಿಮೆಟ್ರಿಯನ್ನು ಒಟ್ಟುಗೂಡಿಸಿ ನಿಮ್ಮ ಕೃಷಿಗೆ ಗರಿಷ್ಠ ಲಾಭ ನೀಡುತ್ತದೆ.",
        feat_tag: "ಕೃಷಿ ಬುದ್ಧಿಮತ್ತೆ",
        feat_h2: "ಕಂಪ್ಯೂಟರ್ ವಿಷನ್ ಮತ್ತು ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಆಧಾರಿತ ನಿಖರ ಕೃಷಿ ಸಾಧನಗಳು",
        feat_desc: "ಮಣ್ಣಿನ ಮೇಲ್ಮೈ ಗುಣಮಟ್ಟದಿಂದ ಹಿಡಿದು ಹವಾಮಾನ ಆಧಾರಿತ ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಮತ್ತು ಲೈವ್ ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ದರಗಳವರೆಗೆ, ರೈತರಿಗೆ ವೈಜ್ಞಾನಿಕ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಲು ಜಿಯೋಸೆನ್ಸ್ ನೆರವಾಗುತ್ತದೆ.",
        feat_1_title: "AI ಮಣ್ಣಿನ ಆಪ್ಟಿಕಲ್ ತಪಾಸಣೆ",
        feat_1_desc: "ಮೊಬೈಲ್ ಕ್ಯಾಮೆರಾದಿಂದ ಮಣ್ಣಿನ ಫೋಟೋ ತೆಗೆಯಿರಿ. ನಮ್ಮ OpenCV ಪೈಪ್‌ಲೈನ್ ಫೋಕಸ್, ಬೆಳಕು ಮತ್ತು ಮೇಲ್ಮೈ ವಿನ್ಯಾಸವನ್ನು ವೈಜ್ಞಾನಿಕ ಪಾರದರ್ಶಕತೆಯೊಂದಿಗೆ ಪರಿಶೀಲಿಸುತ್ತದೆ.",
        feat_2_title: "ML ಬೆಳೆ ಶಿಫಾರಸು ಮಾಡೆಲ್",
        feat_2_desc: "ತರಬೇತಿ ಪಡೆದ ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಕ್ಲಾಸಿಫೈಯರ್ ಮಣ್ಣಿನ ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಶ್, pH ಮತ್ತು ಹವಾಮಾನವನ್ನು ಪರಿಶೀಲಿಸಿ ಹೆಚ್ಚು ಇಳುವರಿ ನೀಡುವ ಬೆಳೆಯನ್ನು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ.",
        feat_3_title: "ಸ್ಮಾರ್ಟ್ ನೀರಾವರಿ ಎಂಜಿನ್",
        feat_3_desc: "FAO-56 ಗುಣಮಟ್ಟದ ಆಧಾರದ ಮೇಲೆ ಬೆಳೆಯ ಬೆಳವಣಿಗೆ ಹಂತ ಮತ್ತು ಮಳೆಯ ಮುನ್ಸೂಚನೆಯನ್ನು ಪರಿಗಣಿಸಿ ಎಕರೆಗೆ ಬೇಕಾಗುವ ನೀರಿನ ಕೊರತೆಯನ್ನು ನಿಖರವಾಗಿ ಲೆಕ್ಕಹಾಕುತ್ತದೆ.",
        feat_4_title: "ಕೃಷಿ-ಹವಾಮಾನ ಟೆಲಿಮೆಟ್ರಿ",
        feat_4_desc: "ಲೈವ್ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆಯೊಂದಿಗೆ ತೀವ್ರ ತಾಪಮಾನದ ಎಚ್ಚರಿಕೆಗಳು, ಕೀಟ ಬಾಧೆಯ ಸಾಧ್ಯತೆಗಳು ಮತ್ತು ಜಮೀನಿನ ಒಳಚರಂಡಿ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ.",
        feat_5_title: "APMC ಮಂಡಿ ಮಾರುಕಟ್ಟೆ ದರಗಳು",
        feat_5_desc: "ಕರ್ನಾಟಕ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಕೃಷಿ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಕನಿಷ್ಠ, ಗರಿಷ್ಠ ಮತ್ತು ಮಾದರಿ ದರಗಳ 7 ದಿನಗಳ ಪ್ರವೃತ್ತಿಗಳನ್ನು ವೀಕ್ಷಿಸಿ.",
        feat_6_title: "ರೈತರ ಸಮುದಾಯ",
        feat_6_desc: "ಪ್ರಗತಿಪರ ರೈತರು ಮತ್ತು ಕೃಷಿ ವಿಜ್ಞಾನಿಗಳೊಂದಿಗೆ ಸಂಪರ್ಕ ಸಾಧಿಸಿ, ನೈಸರ್ಗಿಕ ಕೃಷಿ ಕಷಾಯಗಳು ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಸಲಹೆಗಳನ್ನು ವಿನಿಮಯ ಮಾಡಿಕೊಳ್ಳಿ.",
        sol_tag: "ಕಸ್ಟಮೈಸ್ಡ್ ಪರಿಹಾರಗಳು",
        sol_h2: "ರೈತರು, ಕೃಷಿ ತಜ್ಞರು ಮತ್ತು ರೈತ ಉತ್ಪಾದಕ ಸಂಸ್ಥೆಗಳಿಗೆ (FPO) ರೂಪಿಸಲಾಗಿದೆ",
        sol_desc: "2 ಎಕರೆ ಭೂಮಿಯಿರಲಿ ಅಥವಾ ದೊಡ್ಡ ರೈತ ಉತ್ಪಾದಕ ಸಹಕಾರ ಸಂಘವಿರಲಿ, ಜಿಯೋಸೆನ್ಸ್ ಎಲ್ಲರಿಗೂ ಸುಲಭವಾಗಿ ಹೊಂದಿಕೊಳ್ಳುತ್ತದೆ.",
        sol_1_title: "ಸ್ವತಂತ್ರ ರೈತರು",
        sol_1_desc: "ಯಾವುದೇ ದುಬಾರಿ ಉಪಕರಣಗಳಿಲ್ಲದೆ ನೇರವಾಗಿ ನಿಮ್ಮ ಮೊಬೈಲ್ ಮೂಲಕ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆ, ಹವಾಮಾನ ಎಚ್ಚರಿಕೆ ಮತ್ತು ನೀರಿನ ಲೆಕ್ಕಾಚಾರ ಪಡೆಯಿರಿ.",
        sol_2_title: "FPOಗಳು & ಸಹಕಾರ ಸಂಘಗಳು",
        sol_2_desc: "ಸದಸ್ಯ ರೈತರ ಸಾಮೂಹಿಕ ಬೆಳೆ ಯೋಜನೆ ರೂಪಿಸಿ, ಜಿಲ್ಲಾವಾರು ಮಂಡಿ ದರಗಳನ್ನು ಹೋಲಿಸಿ ಮತ್ತು ಎಲ್ಲಾ ಸದಸ್ಯರ ಡಿಜಿಟಲ್ ದಾಖಲೆಗಳನ್ನು ನಿರ್ವಹಿಸಿ.",
        sol_3_title: "ಕೃಷಿ ವಿಜ್ಞಾನಿಗಳು & ಸಂಶೋಧಕರು",
        sol_3_desc: "ಪರಿಶೀಲಿಸಿದ ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಮಾಡೆಲ್‌ಗಳು, FAO-56 ಲೆಕ್ಕಾಚಾರಗಳು ಮತ್ತು PostgreSQL ಡೇಟಾಬೇಸ್‌ನೊಂದಿಗೆ ಸಂಶೋಧನೆ ನಡೆಸಿ.",
        plat_tag: "ವೈಜ್ಞಾನಿಕ ವಿಧಾನ",
        plat_h2: "ಯಾವುದೇ ಸುಳ್ಳು ಭರವಸೆಗಳಿಲ್ಲದ ಪ್ರಾಮಾಣಿಕ ಡೇಟಾ ನಿಖರತೆ",
        plat_desc: "ಸಾಮಾನ್ಯ ಮೊಬೈಲ್ ಕ್ಯಾಮೆರಾದಿಂದ ಮಣ್ಣಿನಲ್ಲಿರುವ ರಾಸಾಯನಿಕ NPK ಪ್ರಮಾಣವನ್ನು ನಿಖರವಾಗಿ ಅಳೆಯಲು ಸಾಧ್ಯವಿಲ್ಲ. ಜಿಯೋಸೆನ್ಸ್ ಮಣ್ಣಿನ ಮೇಲ್ಮೈ ಭೌತಿಕ ಗುಣಗಳನ್ನು ಪರಿಶೀಲಿಸಿ, ರಾಸಾಯನಿಕ ಪರೀಕ್ಷೆಗಾಗಿ ಮಾನ್ಯತೆ ಪಡೆದ ಲ್ಯಾಬ್‌ಗೆ ಹೋಗಲು ಸಲಹೆ ನೀಡುತ್ತದೆ.",
        footer_desc: "ಕಂಪ್ಯೂಟರ್ ವಿಷನ್, ಮೆಷಿನ್ ಲರ್ನಿಂಗ್ ಮತ್ತು ಹವಾಮಾನ ಟೆಲಿಮೆಟ್ರಿಯನ್ನು ಸಂಯೋಜಿಸುವ ಕೃಷಿ ಸಾಫ್ಟ್‌ವೇರ್ ವ್ಯವಸ್ಥೆ.",
        footer_modules: "ಮಾಡ್ಯೂಲ್‌ಗಳು",
        footer_platform: "ಪ್ಲಾಟ್‌ಫಾರ್ಮ್",
        footer_account: "ಖಾತೆ",
        footer_rights: "© 2026 Geosense Smart Agriculture. ಎಲ್ಲ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ."
      }
    },

    // =========================================================================
    // MARATHI DICTIONARY (मराठी)
    // =========================================================================
    mr: {
      brand: { name: "Geosense", tagline: "स्मार्ट शेतीसाठी AI आधारित प्रणाली" },
      nav: {
        overview: "आढावा", soil: "माती NPK विश्लेषण", disease: "पीक रोग व संसर्ग स्कॅनर", crop: "पीक शिफारस",
        irrigation: "स्मार्ट सिंचन", weather: "हवामान माहिती", market: "मंडी बाजारभाव",
        community: "शेतकरी समुदाय", assistant: "AI कृषी सहाय्यक (Geo)", profile: "शेतकरी प्रोफाइल", signout: "बाहेर पडा"
      },
      header: {
        title_overview: "शेत आढावा", title_soil: "माती NPK विश्लेषण", title_disease: "पीक रोग व संसर्ग स्कॅनर", title_crop: "पीक शिफारस मॉडेल",
        title_irrigation: "अचूक सिंचन वेळापत्रक", title_weather: "हवामान व शेत नकाशा", title_market: "APMC मंडी बाजारभाव",
        title_community: "शेतकरी चर्चासत्र", title_assistant: "AI कृषी सहाय्यक (जियो)", title_profile: "शेतकरी प्रोफाइल आणि भाषा",
        public_site: "🌐 मुख्य पृष्ठ", fastapi_live: "FastAPI लाईव्ह: 127.0.0.1:8001"
      },
      assistant: {
        label_engine: "मॉडेल इंजिन:",
        cloud_btn: "☁️ क्लाउड AI (Qwen3)",
        offline_btn: "⚡ ऑफलाइन AI (Gemma 4 E2B)",
        status_cloud: "क्लाउड AI: Qwen3 सक्रिय",
        settings_btn: "⚙️ सेटिंग्ज",
        greeting: "नमस्कार! मी जियो, तुमचा AI कृषी सहाय्यक. तुमच्या माती परीक्षण व हवामान डेटावर आधारित मी थेट मार्गदर्शन करतो. आज पिकासाठी कशी मदत करू?",
        placeholder: "पिकाची पाने, खत मात्रा किंवा पाण्याबद्दल विचारा...",
        placeholder_crop: "{crop} पिकाची पाने, NPK खत किंवा सिंचनाबद्दल विचारा...",
        prompt_1: "{crop} ची पाने पिवळी का पडत आहेत?",
        prompt_2: "आज {crop} ला किती पाणी द्यावे?",
        prompt_3: "{crop} साठी युरिया / NPK प्रमाण किती?",
        scan_btn_title: "माती किंवा पान फोटो स्कॅन (NPK AI)",
        attach_title: "पान / मातीचा फोटो जोडा किंवा पेस्ट करा",
        mode_disease: "🩺 रोग तपासणी",
        mode_npk: "🧪 माती NPK",
        chat_disease_label: "पान आणि पीक संसर्ग स्कॅन",
        chat_npk_label: "माती आणि पान NPK स्कॅन",
        ph_not_tested: "pH: तपासणी नाही",
        context_label: "शेत संदर्भ",
        btn_send: "पाठवा"
      },
      disease: {
        title: "पीक रोग व संसर्ग स्कॅनर",
        desc: "द्वि-स्तरीय प्रमाणित रोग निदान (PlantVillage ONNX + ICAR मानके + NPK आणि हवामान तपासणी).",
        badge_grounded: "ONNX + ICAR प्रमाणित",
        ready_title: "पान किंवा पिकाचा फोटो घ्या / अपलोड करा",
        ready_desc: "अचूक निदानासाठी दिवसाच्या प्रकाशात पानापासून 15–25 सेमी अंतरावरून फोटो घ्या.",
        btn_camera: "📷 कॅमेरा उघडा",
        btn_snap: "⚡ पानाचा फोटो घ्या",
        btn_upload: "📁 पान / पीक फोटो निवडा",
        btn_reset: "🔄 रीसेट",
        btn_diagnose: "🩺 प्रमाणित रोग निदान करा",
        question_placeholder: "वैकल्पिक लक्षण लिहा (उदा. खालच्या पानांवर डाग, पाने गुंडाळणे)...",
        card_detected: "आढळलेला संसर्ग व विश्वास पातळी",
        card_why: "संसर्ग का झाला (जीवशास्त्र आणि हवामान कारण)",
        card_solution: "सुचवलेला उपाय व फवारणी प्रमाण",
        tab_organic: "🌿 सेंद्रिय / मशागत नियंत्रण",
        tab_chemical: "🧪 रासायनिक उपाय (ICAR)",
        card_prevention: "प्रतिबंधात्मक उपाय",
        btn_followup: "🤖 AI कृषी सहाय्यक (Geo) मध्ये विचारा"
      }
    },

    // =========================================================================
    // TAMIL DICTIONARY (தமிழ்)
    // =========================================================================
    ta: {
      brand: { name: "Geosense", tagline: "ஸ்மார்ட் விவசாயத்திற்கான AI அமைப்பு" },
      nav: {
        overview: "கண்ணோட்டம்", soil: "மண் NPK ஆய்வு", disease: "பயிர் நோய் ஸ்கேனர்", crop: "பயிர் பரிந்துரை",
        irrigation: "ஸ்மார்ட் நீர்ப்பாசனம்", weather: "வானிலை தகவல்", market: "மண்டி சந்தை",
        community: "உழவர் சமூகம்", assistant: "AI வேளாண் உதவியாளர் (Geo)", profile: "விவசாயி சுயவிவரம்", signout: "வெளியேறு"
      },
      header: {
        title_overview: "பண்ணை கண்ணோட்டம்", title_soil: "மண் NPK பகுப்பாய்வு", title_disease: "பயிர் நோய் மற்றும் தொற்று ஸ்கேனர்", title_crop: "பயிர் பரிந்துரை எந்திரம்",
        title_irrigation: "துல்லிய நீர்ப்பாசனம்", title_weather: "வேளாண் வானிலை", title_market: "APMC மண்டி சந்தை",
        title_community: "விவசாயிகள் கலந்துரையாடல்", title_assistant: "AI வேளாண் உதவியாளர் (ஜியோ)", title_profile: "சுயவிவரம் & அமைப்புகள்",
        public_site: "🌐 முகப்பு பக்கம்", fastapi_live: "FastAPI நேரலை: 127.0.0.1:8001"
      },
      assistant: {
        label_engine: "AI எந்திரம்:",
        cloud_btn: "☁️ கிளவுட் AI (Qwen3)",
        offline_btn: "⚡ ஆஃப்லைன் AI (Gemma 4 E2B)",
        status_cloud: "கிளவுட் AI: Qwen3 செயல்பாட்டில்",
        settings_btn: "⚙️ அமைப்புகள்",
        greeting: "வணக்கம்! நான் ஜியோ, உங்கள் AI வேளாண் உதவியாளர். உங்கள் மண் பரிசோதனை மற்றும் நேரலை வானிலை அடிப்படையில் நேரடி ஆலோசனை வழங்குகிறேன். இன்று உங்கள் பயிருக்கு எப்படி உதவட்டும்?",
        placeholder: "பயிர் இலை, உர அளவு அல்லது நீர்ப்பாசனம் பற்றி கேளுங்கள்...",
        placeholder_crop: "{crop} இலை நிறம், NPK உரம் அல்லது நீர்ப்பாசனம் பற்றி கேளுங்கள்...",
        prompt_1: "{crop} இலைகள் ஏன் மஞ்சளாகின்றன?",
        prompt_2: "இன்று {crop} பயிருக்கு எவ்வளவு நீர் தேவை?",
        prompt_3: "{crop} பயிருக்கு யூரியா / NPK அளவு என்ன?",
        scan_btn_title: "மண் / இலை புகைப்பட ஸ்கேன் (NPK AI)",
        attach_title: "இலை / மண் படம் இணைக்கவும் அல்லது ஒட்டவும்",
        mode_disease: "🩺 நோய் ஆய்வு",
        mode_npk: "🧪 மண் NPK",
        chat_disease_label: "இலை & பயிர் நோய் ஸ்கேன்",
        chat_npk_label: "மண் & இலை NPK ஸ்கேன்",
        ph_not_tested: "pH: சோதிக்கப்படவில்லை",
        context_label: "வயல் தரவு",
        btn_send: "அனுப்பு"
      },
      disease: {
        title: "பயிர் நோய் மற்றும் தொற்று ஸ்கேனர்",
        desc: "இரு-நிலை ஆதாரப்பூர்வ நோயறிதல் (PlantVillage ONNX + ICAR வழிகாட்டுதல் + NPK & வானிலை சரிபார்ப்பு).",
        badge_grounded: "ONNX + ICAR சான்று",
        ready_title: "இலை / பயிர் படத்தை எடுக்கவும் அல்லது பதிவேற்றவும்",
        ready_desc: "பகல் வெளிச்சத்தில் பாதிக்கப்பட்ட இலையிலிருந்து 15–25 செ.மீ தூரத்தில் படம் எடுக்கவும்.",
        btn_camera: "📷 கேமரா திறக்கவும்",
        btn_snap: "⚡ இலை படம் பிடிக்கவும்",
        btn_upload: "📁 இலை / பயிர் படம் தேர்வு",
        btn_reset: "🔄 மீட்டமை",
        btn_diagnose: "🩺 நோயறிதல் சோதனை செய்",
        question_placeholder: "விருப்பக் குறிப்பு (எ.கா. கீழ் இலைப் புள்ளிகள், இலை சுருட்டு)...",
        card_detected: "கண்டறியப்பட்ட தொற்று & உறுதி",
        card_why: "ஏன் தொற்று ஏற்பட்டது (உயிரியல் & வானிலை)",
        card_solution: "பரிந்துரைக்கப்பட்ட தீர்வு & அளவு",
        tab_organic: "🌿 இயற்கை / சாகுபடி முறை",
        tab_chemical: "🧪 இரசாயனக் கட்டுப்பாடு (ICAR)",
        card_prevention: "தடுப்பு நடவடிக்கைகள்",
        btn_followup: "🤖 AI உதவியாளர் (Geo) இல் தொடரவும்"
      }
    },

    // =========================================================================
    // TELUGU DICTIONARY (తెలుగు)
    // =========================================================================
    te: {
      brand: { name: "Geosense", tagline: "స్మార్ట్ వ్యవసాయం కోసం AI వ్యవస్థ" },
      nav: {
        overview: "అవలోకనం", soil: "నేల NPK విశ్లేషణ", disease: "పంట వ్యాధి స్కానర్", crop: "పంట సిఫార్సు",
        irrigation: "స్మార్ట్ నీటిపారుదల", weather: "వాతావరణ సమాచారం", market: "మండి మార్కెట్",
        community: "రైతు సంఘం", assistant: "AI వ్యవసాయ సహాయకుడు (Geo)", profile: "రైతు ప్రొఫైల్", signout: "సైన్ అవుట్"
      },
      header: {
        title_overview: "పొలం అవలోకనం", title_soil: "నేల NPK విశ్లేషణ", title_disease: "పంట వ్యాధి మరియు ఇన్ఫెక్షన్ స్కానర్", title_crop: "పంట సిఫార్సు మోడల్",
        title_irrigation: "ఖచ్చితమైన నీటిపారుదల", title_weather: "వ్యవసాయ వాతావరణం", title_market: "APMC మండి ధరలు",
        title_community: "రైతు చర్చా వేదిక", title_assistant: "AI వ్యవసాయ సహాయకుడు (జియో)", title_profile: "ప్రొఫైల్ & సెట్టింగులు",
        public_site: "🌐 పబ్లిక్ సైట్", fastapi_live: "FastAPI లైవ్: 127.0.0.1:8001"
      },
      assistant: {
        label_engine: "మోడల్ ఇంజిన్:",
        cloud_btn: "☁️ క్లౌడ్ AI (Qwen3)",
        offline_btn: "⚡ ఆఫ్‌లైన్ AI (Gemma 4 E2B)",
        status_cloud: "క్లౌడ్ AI: Qwen3 సిద్ధం",
        settings_btn: "⚙️ సెట్టింగులు",
        greeting: "నమస్కారం! నేను జియో, మీ AI వ్యవసాయ సహాయకుడిని. మీ నేల పరీక్ష రికార్డులు మరియు లైవ్ వాతావరణం ఆధారంగా నేరుగా సలహా ఇస్తాను. ఈ రోజు మీ పంటకు ఎలా సహాయం చేయను?",
        placeholder: "పంట ఆకులు, ఎరువుల మోతాదు లేదా నీటిపారుదల గురించి అడగండి...",
        placeholder_crop: "{crop} ఆకుల సమస్య, NPK ఎరువు లేదా నీటి గురించి అడగండి...",
        prompt_1: "{crop} ఆకులు పసుపు రంగులోకి ఎందుకు మారుతున్నాయి?",
        prompt_2: "ఈ రోజు {crop} పంటకు ఎంత నీరు అవసరం?",
        prompt_3: "{crop} పంటకు యూరియా / NPK మోతాదు ఎంత?",
        scan_btn_title: "నేల / ఆకు ఫోటో స్కాన్ (NPK AI)",
        attach_title: "ఆకు / నేల ఫోటో జోడించండి లేదా పేస్ట్ చేయండి",
        mode_disease: "🩺 వ్యాధి పరీక్ష",
        mode_npk: "🧪 నేల NPK",
        chat_disease_label: "ఆకు & పంట ఇన్ఫెక్షన్ స్కాన్",
        chat_npk_label: "నేల & ఆకు NPK స్కాన్",
        ph_not_tested: "pH: పరీక్షించలేదు",
        context_label: "పొలం వివరాలు",
        btn_send: "పంపండి"
      },
      disease: {
        title: "పంట వ్యాధి మరియు ఇన్ఫెక్షన్ స్కానర్",
        desc: "రెండు-దశల ప్రామాణిక వ్యాధి నిర్ధారణ (PlantVillage ONNX + ICAR ప్రమాణాలు + NPK & వాతావరణ తనిఖీ).",
        badge_grounded: "ONNX + ICAR ప్రమాణం",
        ready_title: "ఆకు లేదా పంట ఫోటో తీయండి / అప్‌లోడ్ చేయండి",
        ready_desc: "ఖచ్చితమైన ఫలితం కోసం పగటి వెలుతురులో ఆకు నుండి 15–25 సెం.మీ దూరంలో ఫోటో తీయండి.",
        btn_camera: "📷 కెమెరా తెరవండి",
        btn_snap: "⚡ ఆకు ఫోటో తీయండి",
        btn_upload: "📁 ఆకు / పంట ఫోటో ఎంచుకోండి",
        btn_reset: "🔄 రీసెట్",
        btn_diagnose: "🩺 వ్యాధి నిర్ధారణ చేయండి",
        question_placeholder: "ఐచ్ఛిక లక్షణం (ఉదా. కింది ఆకుల మచ్చలు, ఆకు ముడత)...",
        card_detected: "గుర్తించిన వ్యాధి & విశ్వాసం",
        card_why: "వ్యాధి రావడానికి కారణం (జీవశాస్త్రం & వాతావరణం)",
        card_solution: "సూచించిన పరిష్కారం & మోతాదు",
        tab_organic: "🌿 సేంద్రీయ / సాగు నియంత్రణ",
        tab_chemical: "🧪 రసాయన నియంత్రణ (ICAR)",
        card_prevention: "నివారణ చర్యలు",
        btn_followup: "🤖 AI సహాయకుడిలో (Geo) తదుపరి ప్రశ్న అడగండి"
      }
    }
  };

  const SUPPORTED_LANGS = ['en', 'hi', 'kn', 'mr', 'ta', 'te'];

  const LANG_META = {
    en: {
      code: 'en',
      name: 'English',
      label: 'English (EN)',
      scriptInstruction: 'Answer the farmer directly first in clear natural English using their farm data. Keep chemical names and units (kg/ha, °C, NPK) readable.'
    },
    kn: {
      code: 'kn',
      name: 'Kannada (ಕನ್ನಡ)',
      label: 'ಕನ್ನಡ (Kannada)',
      scriptInstruction: 'ಕನ್ನಡ ಲಿಪಿಯಲ್ಲಿಯೇ ಸ್ಪಷ್ಟವಾಗಿ ಉತ್ತರಿಸಿ. ಇಂಗ್ಲಿಷ್ ಅಂಕಿಅಂಶಗಳನ್ನು ಓದಿದರೂ ಇಂಗ್ಲಿಷ್‌ಗೆ ಬದಲಾಗಬೇಡಿ. ಮೊದಲು ನೇರ ಉತ್ತರ ನೀಡಿ, kg/ha, °C, NPK ಘಟಕಗಳನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಇಡಿ.'
    },
    hi: {
      code: 'hi',
      name: 'Hindi (हिन्दी)',
      label: 'हिन्दी (Hindi)',
      scriptInstruction: 'केवल शुद्ध हिन्दी (देवनागरी लिपि) में उत्तर दें। अंग्रेजी डेटा देखकर अंग्रेजी में न बदलें। पहले प्रश्न का सीधा उत्तर दें और kg/ha, °C, NPK इकाइयाँ स्पष्ट रखें।'
    },
    mr: {
      code: 'mr',
      name: 'Marathi (मराठी)',
      label: 'मराठी (Marathi)',
      scriptInstruction: 'फक्त मराठी (देवनागरी लिपी) मध्ये स्पष्ट उत्तर द्या. इंग्रजी डेटा पाहून इंग्रजीत उत्तर देऊ नका. प्रथम थेट उत्तर द्या व kg/ha, °C, NPK एकके स्पष्ट ठेवा.'
    },
    ta: {
      code: 'ta',
      name: 'Tamil (தமிழ்)',
      label: 'தமிழ் (Tamil)',
      scriptInstruction: 'தமிழ் எழுத்தில் மட்டுமே தெளிவாக பதிலளிக்கவும். ஆங்கிலத் தரவைப் படித்தாலும் ஆங்கிலத்திற்கு மாறாதீர்கள். முதலில் நேரடி பதில் அளித்து kg/ha, °C, NPK அலகுகளைத் தெளிவாக வைக்கவும்.'
    },
    te: {
      code: 'te',
      name: 'Telugu (తెలుగు)',
      label: 'తెలుగు (Telugu)',
      scriptInstruction: 'తెలుగు లిపిలోనే స్పష్టంగా సమాధానం ఇవ్వండి. ఆంగ్ల డేటా చూసి ఇంగ్లీష్‌లోకి మారకండి. ముందుగా నేరుగా సమాధానం ఇచ్చి kg/ha, °C, NPK యూనిట్లు స్పష్టంగా ఉంచండి.'
    }
  };

  function detectQueryLanguage(text, fallbackLang) {
    const q = (text || '').trim();
    if (/[\u0C80-\u0CFF]/.test(q)) return 'kn';
    if (/[\u0B80-\u0BFF]/.test(q)) return 'ta';
    if (/[\u0C00-\u0C7F]/.test(q)) return 'te';
    if (/[\u0900-\u097F]/.test(q)) {
      if (/(माझ|शेती|पाणी|खत|पिवळ|पाने|पीक|पाऊस|काय|कसे|आहे)/.test(q)) return 'mr';
      return (fallbackLang === 'mr' || fallbackLang === 'hi') ? fallbackLang : 'hi';
    }
    const ql = q.toLowerCase();
    if (/\b(namaskara|mannu|neeru|bele|gobbara|haladi|bhatta|maley|eshtu|beku|hege)\b/.test(ql)) return 'kn';
    if (/\b(namaskar|mati|pik|khat|pani|sheta|pavle|kiti|kasa)\b/.test(ql)) return 'mr';
    if (/\b(namaste|mitti|paani|fasal|khad|patta|peela|gehun|barish|kitna|kaise)\b/.test(ql)) return 'hi';
    if (/\b(vanakkam|mann|thanni|payir|uram|mazhai|epdi|evvalavu|ilai)\b/.test(ql)) return 'ta';
    if (/\b(namaskaram|nela|neellu|panta|eruvu|varsham|entha|ela|aaku)\b/.test(ql)) return 'te';
    return SUPPORTED_LANGS.includes(fallbackLang) ? fallbackLang : 'en';
  }

  function getSavedLanguage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && SUPPORTED_LANGS.includes(saved)) {
        return saved;
      }
    } catch (e) {}
    return DEFAULT_LANG;
  }

  let currentLang = getSavedLanguage();

  function t(path, fallback) {
    const keys = path.split('.');
    let cur = DICTIONARY[currentLang] || DICTIONARY.en;
    for (let i = 0; i < keys.length; i++) {
      if (cur && typeof cur === 'object' && keys[i] in cur) {
        cur = cur[keys[i]];
      } else {
        // fallback to english
        let fb = DICTIONARY.en;
        for (let j = 0; j < keys.length; j++) {
          if (fb && typeof fb === 'object' && keys[j] in fb) fb = fb[keys[j]];
          else return fallback || path;
        }
        return fb || fallback || path;
      }
    }
    return cur || fallback || path;
  }

  function applyTranslations() {
    document.documentElement.lang = currentLang;

    // 1. HTML elements: [data-i18n-html]
    const htmlElements = document.querySelectorAll('[data-i18n-html]');
    htmlElements.forEach((el) => {
      const key = el.getAttribute('data-i18n-html');
      if (!key) return;
      const html = t(key);
      if (html) el.innerHTML = html;
    });

    // 2. Text elements: [data-i18n]
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (!key) return;
      const text = t(key);
      if (text) {
        // If element contains child elements (e.g. icon + text), only replace last text node
        const childElements = el.children;
        if (childElements.length === 0) {
          el.textContent = text;
        } else {
          // Check for a dedicated text span or replace text nodes
          let updated = false;
          for (let i = 0; i < el.childNodes.length; i++) {
            const node = el.childNodes[i];
            if (node.nodeType === Node.TEXT_NODE && node.nodeValue.trim()) {
              node.nodeValue = ' ' + text;
              updated = true;
              break;
            }
          }
          if (!updated) {
            el.appendChild(document.createTextNode(' ' + text));
          }
        }
      }
    });

    // 2. Placeholder attributes: [data-i18n-placeholder]
    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        const text = t(key);
        if (text) el.placeholder = text;
      }
    });

    // 3. Title attributes: [data-i18n-title]
    const titles = document.querySelectorAll('[data-i18n-title]');
    titles.forEach((el) => {
      const key = el.getAttribute('data-i18n-title');
      if (key) {
        const text = t(key);
        if (text) el.title = text;
      }
    });

    // 4. Update Header Page Title dynamically according to active module pane
    const activePane = document.querySelector('.module-pane.active');
    const headerTitleEl = document.getElementById('dashboard-page-title');
    if (activePane && headerTitleEl) {
      const paneId = activePane.id.replace('pane-', '');
      const titleKey = 'header.title_' + paneId;
      headerTitleEl.textContent = t(titleKey, t('nav.' + paneId, headerTitleEl.textContent));
    }

    // 5. Update global select dropdowns
    const globalSelect = document.getElementById('global-lang-select');
    if (globalSelect && globalSelect.value !== currentLang) {
      globalSelect.value = currentLang;
    }

    // 5b. Update landing page language dropdown and label
    const landingSelect = document.getElementById('landing-lang-select');
    if (landingSelect && landingSelect.value !== currentLang) {
      landingSelect.value = currentLang;
    }
    const navDisplay = document.getElementById('nav-lang-display');
    if (navDisplay) {
      const meta = LANG_META[currentLang];
      navDisplay.textContent = meta ? (meta.code === 'en' ? 'English' : meta.label) : 'English';
    }

    // 6. Update radio buttons in settings
    const radios = document.querySelectorAll('input[name="dash_lang"]');
    radios.forEach((r) => {
      r.checked = (r.value === currentLang);
      const card = r.closest('.lang-card-option');
      if (card) {
        if (r.checked) {
          card.style.borderColor = '#2563eb';
          card.style.background = '#eff6ff';
        } else {
          card.style.borderColor = '#e2e8f0';
          card.style.background = '#ffffff';
        }
      }
    });

    // 7. Update initial AI assistant greeting if untouched
    const chatMsgs = document.getElementById('dash-chat-messages');
    if (chatMsgs && chatMsgs.children.length === 1) {
      const firstBubble = chatMsgs.firstElementChild;
      if (firstBubble && firstBubble.classList.contains('assistant')) {
        firstBubble.textContent = t('assistant.greeting');
      }
    }

    // 8. Refresh character spans for text reveals on landing page if present
    if (typeof window.refreshTextSpans === 'function') {
      try { window.refreshTextSpans(); } catch (e) {}
    }
  }

  function setLanguage(lang) {
    if (!SUPPORTED_LANGS.includes(lang)) return;
    currentLang = lang;
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {}

    applyTranslations();

    // Fire event for any listening modules
    window.dispatchEvent(new CustomEvent('geosense:languageChanged', {
      detail: { lang: currentLang }
    }));
  }

  // Auto-init on script load and DOM ready
  function init() {
    currentLang = getSavedLanguage();
    applyTranslations();

    // Attach listeners to any global language selectors
    document.addEventListener('change', (e) => {
      if (e.target && (e.target.id === 'global-lang-select' || e.target.id === 'landing-lang-select')) {
        setLanguage(e.target.value);
      }
      if (e.target && e.target.name === 'dash_lang') {
        setLanguage(e.target.value);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export to window
  window.GeosenseI18n = {
    t,
    getLanguage: () => currentLang,
    getLanguageInfo: (code) => LANG_META[code || currentLang] || LANG_META.en,
    detectQueryLanguage,
    setLanguage,
    applyTranslations,
    languages: Object.values(LANG_META)
  };
})(window);
