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
        cloud_btn: "☁️ Advanced Cloud AI (Qwen3)",
        offline_btn: "⚡ Offline Browser AI (Gemma 4 E2B)",
        status_cloud: "Cloud AI: Qwen3 Grounded",
        settings_btn: "⚙️ Settings",
        greeting: "Hello! I am Geo, your AI agronomy assistant. I cross-reference your verified soil test records and live local weather to provide agronomic advisories. How can I help with your soil, crops, or irrigation today?",
        placeholder: "e.g., Why are my bottom wheat leaves turning yellow?",
        btn_send: "Send"
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
        label_engine: "अनुमान इंजन:",
        cloud_btn: "☁️ उन्नत क्लाउड AI (Qwen3)",
        offline_btn: "⚡ ऑफलाइन ऑन-डिवाइस AI (Gemma 4)",
        status_cloud: "क्लाउड AI: Qwen3 सक्रिय",
        settings_btn: "⚙️ सेटिंग्स",
        greeting: "नमस्ते! मैं जियो हूँ, आपका AI कृषि सहायक। मैं आपके सत्यापित मृदा परीक्षण और स्थानीय मौसम के आधार पर सटीक कृषि सलाह देता हूँ। आज मैं आपकी मिट्टी, फसल या सिंचाई में क्या सहायता कर सकता हूँ?",
        placeholder: "उदा. मेरी गेहूं की निचली पत्तियां पीली क्यों पड़ रही हैं?",
        btn_send: "भेजें"
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
        cloud_btn: "☁️ ಸುಧಾರಿತ ಕ್ಲೌಡ್ AI (Qwen3)",
        offline_btn: "⚡ ಆಫ್‌ಲೈನ್ ಆನ್-ಡಿವೈಸ್ AI (Gemma 4)",
        status_cloud: "ಕ್ಲೌಡ್ AI: Qwen3 ಸಕ್ರಿಯ",
        settings_btn: "⚙️ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        greeting: "ನಮಸ್ಕಾರ! ನಾನು ಜಿಯೋ, ನಿಮ್ಮ AI ಕೃಷಿ ಸಹಾಯಕ. ನಿಮ್ಮ ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ದಾಖಲೆಗಳು ಮತ್ತು ಸ್ಥಳೀಯ ಹವಾಮಾನವನ್ನು ಪರಿಶೀಲಿಸಿ ನಾನು ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ನೀಡುತ್ತೇನೆ. ಇಂದು ನಿಮ್ಮ ಮಣ್ಣು, ಬೆಳೆಗಳು ಅಥವಾ ನೀರಾವರಿಗೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?",
        placeholder: "ಉದಾ. ನನ್ನ ಗಿಡಗಳ ಕೆಳಗಿನ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ, ಪರಿಹಾರವೇನು?",
        btn_send: "ಕಳುಹಿಸಿ"
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
      }
    }
  };

  function getSavedLanguage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && (saved === 'en' || saved === 'hi' || saved === 'kn')) {
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

    // 1. Text elements: [data-i18n]
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
  }

  function setLanguage(lang) {
    if (lang !== 'en' && lang !== 'hi' && lang !== 'kn') return;
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
      if (e.target && e.target.id === 'global-lang-select') {
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
    setLanguage,
    applyTranslations,
    languages: [
      { code: 'en', name: 'English', label: 'English (EN)' },
      { code: 'hi', name: 'हिन्दी', label: 'हिन्दी (Hindi)' },
      { code: 'kn', name: 'ಕನ್ನಡ', label: 'ಕನ್ನಡ (Kannada)' }
    ]
  };
})(window);
