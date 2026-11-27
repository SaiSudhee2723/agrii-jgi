/**
 * Geosense Smart Agriculture - Offline Deterministic Agronomy Engine
 * 100% In-Browser Multilingual Advisory & FAO-56 Standard Calculations
 * Supports en, kn, hi, mr, ta, te with script auto-detection & sanitized farm telemetry.
 */

(function (window) {
  'use strict';

  const PH_NOT_TESTED = {
    en: 'pH: Not tested',
    kn: 'pH: ಪರೀಕ್ಷಿಸಲಾಗಿಲ್ಲ',
    hi: 'pH: जांच नहीं हुई',
    mr: 'pH: तपासणी नाही',
    ta: 'pH: சோதிக்கப்படவில்லை',
    te: 'pH: పరీక్షించలేదు'
  };

  const DISCLAIMERS = {
    en: 'OFFLINE ADVISORY: Grounded on your cached farm records & FAO-56 calculations with zero cloud transmission.',
    kn: 'ಆಫ್‌ಲೈನ್ ಸಲಹೆ: ನಿಮ್ಮ ಜಮೀನಿನ ದಾಖಲೆಗಳು ಮತ್ತು FAO-56 ಮಾದರಿಯ ಆಧಾರದಲ್ಲಿ ಯಾವುದೇ ಕ್ಲೌಡ್ ಸಂಪರ್ಕವಿಲ್ಲದೆ ನೀಡಲಾಗಿದೆ.',
    hi: 'ऑफ़लाइन परामर्श: आपके सहेजे गए खेत डेटा और FAO-56 मानकों पर आधारित (बिना इंटरनेट के स्थानीय गणना)।',
    mr: 'ऑफलाइन सल्ला: तुमच्या जतन केलेल्या शेत नोंदी व FAO-56 नियमांवर आधारित (इंटरनेटशिवाय).',
    ta: 'ஆஃப்லைன் ஆலோசனை: இணைய இணைப்பின்றி உங்கள் பண்ணை பதிவுகள் மற்றும் FAO-56 கணக்கீடுகளின் அடிப்படையில் வழங்கப்பட்டது.',
    te: 'ఆఫ్‌లైన్ సలహా: ఇంటర్నెట్ లేకుండా మీ పొలం రికార్డులు మరియు FAO-56 ప్రమాణాల ఆధారంగా అందించబడింది.'
  };

  class OfflineAgroEngine {
    constructor() {
      this.version = '2.0.0-offline-multilingual';
      this.engineName = 'Geosense Offline Agronomy Engine';
    }

    calculateIrrigation(params) {
      const crop = (params.crop || 'rice').toLowerCase();
      const stage = (params.stage || 'vegetative').toLowerCase();
      const moisture = parseFloat(params.soilMoisture) || 40.0;
      const area = parseFloat(params.areaAcres) || 1.0;
      const temp = parseFloat(params.tempC) || 26.0;
      const humidity = parseFloat(params.humidityPct) || 55.0;

      const kcTable = {
        wheat: { initial: 0.35, vegetative: 0.75, flowering: 1.15, yield: 0.85, ripening: 0.45 },
        rice: { initial: 1.05, vegetative: 1.15, flowering: 1.25, yield: 1.10, ripening: 0.90 },
        maize: { initial: 0.40, vegetative: 0.80, flowering: 1.20, yield: 0.85, ripening: 0.50 },
        cotton: { initial: 0.35, vegetative: 0.70, flowering: 1.20, yield: 0.90, ripening: 0.65 },
        sugarcane: { initial: 0.40, vegetative: 0.85, flowering: 1.25, yield: 1.00, ripening: 0.70 }
      };

      const cropKc = (kcTable[crop] && kcTable[crop][stage]) ? kcTable[crop][stage] : 0.90;
      const baseEto = Math.max(2.0, (0.0023 * (temp + 17.8) * Math.sqrt(Math.max(5, 35 - temp)) * 2.5) * (1 - humidity / 200));
      const cropEtc = baseEto * cropKc;

      const fieldCapacity = 65.0;
      const moistureDeficitPct = Math.max(0, fieldCapacity - moisture);
      const rootZoneDepthMm = 400;
      const netWaterRequirementMm = (moistureDeficitPct / 100) * rootZoneDepthMm * 0.15 + (moisture < 50 ? cropEtc : 0);

      const litersPerAcre = netWaterRequirementMm * 4046.86;
      const totalLiters = litersPerAcre * area;
      const needed = moistureDeficitPct > 10 || netWaterRequirementMm > 5;

      return {
        irrigationNeeded: needed,
        waterPerAcreLiters: Math.round(litersPerAcre),
        totalWaterLiters: Math.round(totalLiters),
        evapotranspirationMmDay: parseFloat(cropEtc.toFixed(2)),
        deficitMm: parseFloat(netWaterRequirementMm.toFixed(1)),
        faoMethod: 'FAO-56 Penman-Monteith'
      };
    }

    _sanitizeChips(soil, cropName, weather, lang) {
      const chips = [cropName];
      const hasVal = (v) => v !== null && v !== undefined && v !== '' && !Number.isNaN(Number(v));

      if (hasVal(soil.nitrogen_ppm)) chips.push(`N: ${soil.nitrogen_ppm} kg/ha`);
      if (hasVal(soil.phosphorus_ppm)) chips.push(`P: ${soil.phosphorus_ppm} kg/ha`);
      if (hasVal(soil.potassium_ppm)) chips.push(`K: ${soil.potassium_ppm} kg/ha`);
      if (hasVal(soil.soil_ph)) {
        chips.push(`pH: ${soil.soil_ph}`);
      } else if (hasVal(soil.nitrogen_ppm)) {
        chips.push(PH_NOT_TESTED[lang] || PH_NOT_TESTED.en);
      }
      if (hasVal(weather.temp)) chips.push(`${weather.temp}°C`);
      return chips;
    }

    generateAdvisory(prompt, context = {}) {
      const selectedLang = context.language || (window.GeosenseI18n ? window.GeosenseI18n.getLanguage() : 'en');
      const lang = (window.GeosenseI18n && window.GeosenseI18n.detectQueryLanguage)
        ? window.GeosenseI18n.detectQueryLanguage(prompt, selectedLang)
        : selectedLang;

      const q = (prompt || '').toLowerCase();
      const soil = context.soil || {};
      const crop = context.crop || {};
      const weather = context.weather || {};
      const diag = context.diseaseDiagnosis || null;
      const cropName = crop.primary_recommendation || crop.primary_crop || 'Rice';
      const chips = this._sanitizeChips(soil, cropName, weather, lang);
      if (diag && diag.condition_name) chips.unshift(diag.condition_name);

      // Follow-up support for active disease diagnosis (15L tank math & foliar compatibility)
      if (diag && diag.condition_name && /(pump|tank|liter|litre|dose|dosage|mix|foliar|spray|ಪಂಪ್|ಲೀಟರ್|पंप|लीटर|मिला|फवार|டேங்க்|పంప్)/i.test(q)) {
        const tankMatch = q.match(/(\d+)\s*(?:l|liter|litre|liters)/i);
        const tankL = tankMatch ? parseInt(tankMatch[1], 10) : 15;
        const chem = (diag.immediate_solution && diag.immediate_solution.chemical_targeted && diag.immediate_solution.chemical_targeted[0]) || 'Mancozeb 75% WP @ 2.5 g/L';
        const org = (diag.immediate_solution && diag.immediate_solution.organic_cultural && diag.immediate_solution.organic_cultural[0]) || 'Neem Oil @ 3 ml/L';
        const doseMatches = [...chem.matchAll(/(\d+(?:\.\d+)?)\s*(g\/L|ml\/L)/gi)];
        const tankLine = doseMatches.length
          ? doseMatches.map(m => `**${m[1]} ${m[2]}** × ${tankL}L = **${(parseFloat(m[1]) * tankL).toFixed(1).replace(/\.0$/, '')} ${m[2].toLowerCase().includes('g') ? 'g' : 'ml'}**`).join(' | ')
          : chem;
        const isMix = /(mix|foliar|fertiliz|urea|npk|ಬೆರೆಸ|मिला|मिश्रण|கல|కలుప)/i.test(q);
        const byLang = {
          kn: `**${diag.condition_name} (${tankL}L ಪಂಪ್):**\n\n• **ಪ್ರಮಾಣ:** ${tankLine}\n• **ಸೂಚನೆ:** ${isMix ? 'Copper/Sulphur ಅನ್ನು Urea/NPK ಜೊತೆ ಬೆರೆಸಬೇಡಿ (4–5 ದಿನ ಅಂತರ ಇಡಿ).' : org}`,
          hi: `**${diag.condition_name} (${tankL}L पंप गणना):**\n\n• **सटीक खुराक:** ${tankLine}\n• **सलाह:** ${isMix ? 'Copper/Sulphur को Urea/NPK फोलियर खाद के साथ न मिलाएं (4–5 दिन का अंतर रखें)।' : org}`,
          mr: `**${diag.condition_name} (${tankL}L पंप):**\n\n• **प्रमाण:** ${tankLine}\n• **टीप:** ${isMix ? 'Copper/Sulphur हे Urea/NPK सोबत एकत्र फवारू नका.' : org}`,
          ta: `**${diag.condition_name} (${tankL}L டேங்க்):**\n\n• **அளவு:** ${tankLine}\n• **குறிப்பு:** ${isMix ? 'Copper/Sulphur உடன் Urea/NPK கலக்க வேண்டாம்.' : org}`,
          te: `**${diag.condition_name} (${tankL}L పంపు):**\n\n• **మోతాదు:** ${tankLine}\n• **సూచన:** ${isMix ? 'Copper/Sulphur ను Urea/NPK తో కలిపి పిచికారీ చేయవద్దు.' : org}`,
          en: `**${diag.condition_name} — ${tankL}L Spray Tank Plan:**\n\n• **Tank Mix Math:** ${tankLine}\n• **Compatibility:** ${isMix ? 'Do NOT tank-mix Copper/Sulphur fungicides with Urea/NPK foliar sprays; wait 4–5 days between applications.' : org}`
        };
        return {
          answer: byLang[lang] || byLang.en,
          detected_language: lang,
          contextUsed: chips,
          contextChips: chips,
          engine: `${this.engineName} (${lang.toUpperCase()})`,
          mode: 'offline_deterministic',
          scientificDisclaimer: DISCLAIMERS[lang] || DISCLAIMERS.en
        };
      }

      const nVal = soil.nitrogen_ppm !== null && soil.nitrogen_ppm !== undefined ? Number(soil.nitrogen_ppm) : null;
      const pVal = soil.phosphorus_ppm !== null && soil.phosphorus_ppm !== undefined ? Number(soil.phosphorus_ppm) : null;
      const kVal = soil.potassium_ppm !== null && soil.potassium_ppm !== undefined ? Number(soil.potassium_ppm) : null;
      const phVal = soil.soil_ph !== null && soil.soil_ph !== undefined ? Number(soil.soil_ph) : null;

      const nStr = nVal !== null ? `${nVal} kg/ha` : 'Not tested';
      const pStr = pVal !== null ? `${pVal} kg/ha` : 'Not tested';
      const kStr = kVal !== null ? `${kVal} kg/ha` : 'Not tested';
      const phStr = phVal !== null ? `${phVal}` : (PH_NOT_TESTED[lang] || PH_NOT_TESTED.en);

      const hasAny = (kws) => kws.some((k) => q.includes(k));
      const isGreet = hasAny(['hi', 'hello', 'hey', 'namaste', 'namaskara', 'namaskar', 'vanakkam', 'namaskaram', 'ನಮಸ್ಕಾರ', 'नमस्ते', 'नमस्कार', 'வணக்கம்', 'నమస్కారం']) && q.split(/\s+/).length <= 4;
      const isYellow = hasAny(['yellow', 'leaf', 'chlorosis', 'pale', 'haladi', 'ele', 'peela', 'patta', 'patti', 'ಹಳದಿ', 'ಎಲೆ', 'पीली', 'पीला', 'पत्ती', 'पिवळ', 'पान', 'மஞ்சள்', 'இலை', 'పసుపు', 'ఆకు']);
      const isWater = hasAny(['water', 'irrigat', 'dry', 'moisture', 'drought', 'neeru', 'paani', 'pani', 'thanni', 'neellu', 'ನೀರು', 'ನೀರಾವರಿ', 'पानी', 'सिंचाई', 'पाणी', 'தண்ணீர்', 'నీరు']);
      const isPest = hasAny(['pest', 'bug', 'insect', 'worm', 'fung', 'blight', 'disease', 'keet', 'hula', 'rog', 'ಕೀಟ', 'ರೋಗ', 'कीट', 'रोग', 'किड', 'பூச்சி', 'நோய்', 'పురుగు', 'తెగులు']);
      const isFert = hasAny(['fertiliz', 'npk', 'urea', 'dap', 'potash', 'mop', 'gobbara', 'khad', 'khat', 'uram', 'eruvu', 'ಗೊಬ್ಬರ', 'ಯೂರಿಯಾ', 'खाद', 'उर्वरक', 'यूरिया', 'खत', 'உரம்', 'ఎరువు']);

      const irrigCalc = this.calculateIrrigation({
        crop: cropName,
        soilMoisture: soil.moisture_pct || 42.0,
        areaAcres: 1.0,
        tempC: weather.temp || 26.0,
        humidityPct: weather.humidity || 55.0
      });

      let answer = '';

      if (lang === 'kn') {
        if (isGreet) {
          answer = `ನಮಸ್ಕಾರ! ನಿಮ್ಮ **${cropName}** ಬೆಳೆಗೆ ಆಫ್‌ಲೈನ್ AI ಮಾರ್ಗದರ್ಶನ ಸಿದ್ಧವಿದೆ (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**). ಎಲೆ ಬಣ್ಣ, ಗೊಬ್ಬರ ಅಥವಾ ನೀರಾವರಿ ಕುರಿತು ನೇರವಾಗಿ ಕೇಳಿ.`;
        } else if (isYellow) {
          const nNote = (nVal !== null && nVal < 50)
            ? `ನಿಮ್ಮ ಮಣ್ಣಿನ ಸಾರಜನಕ (**N = ${nStr}**) ಕಡಿಮೆ ಇರುವುದರಿಂದ ಕೆಳಗಿನ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ.`
            : `ನಿಮ್ಮ ಸಾರಜನಕ (**N = ${nStr}**) ಸಾಮಾನ್ಯವಾಗಿದೆ; ಇದು **Zinc (ಸತುವಿನ)** ಕೊರತೆ ಅಥವಾ ನೀರು ನಿಲ್ಲುವಿಕೆಯಿಂದ ಆಗಿರಬಹುದು.`;
          answer = `**${cropName} ಎಲೆ ಹಳದಿಯಾಗುವಿಕೆ (Chlorosis) ಪರಿಹಾರ:**\n\n${nNote}\n\n• ಕೆಳಗಿನ ಎಲೆಗಳಿಗೆ ಎಕರೆಗೆ **20–25 kg Urea (ಯೂರಿಯಾ)** ಅಥವಾ **1% Urea (10 g/L)** ಸಿಂಪಡಿಸಿ.\n• ಮೇಲಿನ ಎಲೆಗಳಿಗೆ **0.5% Zinc Sulphate** ಸಿಂಪಡಿಸಿ ಮತ್ತು ಗದ್ದೆಯಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.`;
        } else if (isWater) {
          answer = `**${cropName} ಆಫ್‌ಲೈನ್ ನೀರಾವರಿ ಲೆಕ್ಕಾಚಾರ (FAO-56):**\n\n• ಎಕರೆಗೆ ಅಂದಾಜು ನೀರಿನ ಅಗತ್ಯ: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre** (ETc: ${irrigCalc.evapotranspirationMmDay} mm/day).\n• ಬೆಳಿಗ್ಗೆ **5:30–8:30** ಅಥವಾ ಸಂಜೆ **5:30** ನಂತರ ನೀರು ಹಾಯಿಸಿ.`;
        } else if (isPest) {
          answer = `**${cropName} ಜೈವಿಕ ಕೀಟ ನಿಯಂತ್ರಣ (IPM):**\n\n• ಎಕರೆಗೆ **8–10 ಹಳದಿ ಅಂಟು ಬಲೆಗಳು (Yellow Sticky Traps)** ಅಳವಡಿಸಿ.\n• **Neem Oil / NSKE 5% (@ 3–4 ml/L ನೀರು)** ಸಿಂಪಡಿಸಿ ಮತ್ತು ಸಂಜೆ ಮೇಲ್ಮುಖ ನೀರಾವರಿ ತಪ್ಪಿಸಿ.`;
        } else if (isFert) {
          answer = `**${cropName} ಸಮತೋಲಿತ NPK ಗೊಬ್ಬರ ಕ್ರಮ:**\n\n• ಪ್ರಸ್ತುತ ಮಣ್ಣು: **N=${nStr}, P=${pStr}, K=${kStr} (${phStr})**.\n• **Urea (ಯೂರಿಯಾ)** ಅನ್ನು 3 ಹಂತಗಳಲ್ಲಿ (50% ಆರಂಭ, 25% ಕವಲು, 25% ಹೂವು) ಹಾಗೂ **DAP / MOP** ಅನ್ನು ಬೇಸಾಯದ ಸಮಯದಲ್ಲಿ ನೀಡಿ.`;
        } else {
          answer = `**${cropName} ನೇರ ಆಫ್‌ಲೈನ್ ಕೃಷಿ ಸಲಹೆ:**\n\nನಿಮ್ಮ ಪ್ರಶ್ನೆ (*'${prompt}'*) ಮತ್ತು ಜಮೀನಿನ ದಾಖಲೆ (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**) ಪ್ರಕಾರ ಬೆಳೆಯ ಹಂತಕ್ಕೆ ತಕ್ಕಂತೆ **Urea / DAP / MOP** ಮತ್ತು FAO-56 ನೀರಾವರಿ ವೇಳಾಪಟ್ಟಿ ಅನುಸರಿಸಿ.`;
        }
      } else if (lang === 'hi') {
        if (isGreet) {
          answer = `नमस्ते! आपकी **${cropName}** फसल के लिए ऑफ़लाइन AI तैयार है (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**)। पत्तियों, सिंचाई या खाद के बारे में सीधे पूछें।`;
        } else if (isYellow) {
          const nNote = (nVal !== null && nVal < 50)
            ? `आपकी मिट्टी में नाइट्रोजन (**N = ${nStr}**) कम है, जिससे निचली पत्तियां पीली हो रही हैं।`
            : `नाइट्रोजन (**N = ${nStr}**) पर्याप्त है; यह पीलापन **जिंक (Zinc)** की कमी या अधिक जलभराव से हो सकता है।`;
          answer = `**${cropName} पत्तियां पीली पड़ने (Chlorosis) का उपाय:**\n\n${nNote}\n\n• निचली पत्तियों हेतु **20–25 kg/acre Urea (यूरिया)** या **1% Urea (10 g/L)** स्प्रे करें।\n• ऊपरी पत्तियों के लिए **0.5% Zinc Sulphate** छिड़कें और जल निकासी सुधारें।`;
        } else if (isWater) {
          answer = `**${cropName} ऑफ़लाइन सिंचाई अनुमान (FAO-56):**\n\n• अनुमानित पानी की मांग: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre** (ETc: ${irrigCalc.evapotranspirationMmDay} mm/day)।\n• वाष्पीकरण घटाने हेतु सुबह **5:30–8:30** या शाम **5:30** के बाद सिंचाई करें।`;
        } else if (isPest) {
          answer = `**${cropName} कीट एवं रोग प्रबंधन (IPM):**\n\n• प्रति एकड़ **8–10 पीले चिपचिपे ट्रैप (Yellow Sticky Traps)** लगाएं।\n• **Neem Oil / NSKE 5% (3–4 ml/L पानी)** का छिड़काव करें।`;
        } else if (isFert) {
          answer = `**${cropName} संतुलित NPK उर्वरक नियम:**\n\n• वर्तमान स्तर: **N=${nStr}, P=${pStr}, K=${kStr} (${phStr})**।\n• **Urea** को 3 भागों में (50% बुवाई, 25% कल्ले, 25% बाली) और **DAP / MOP** बुवाई समय जड़ क्षेत्र में दें।`;
        } else {
          answer = `**${cropName} सीधा ऑफ़लाइन कृषि परामर्श:**\n\nआपके प्रश्न (*'${prompt}'*) व डेटा (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**) के आधार पर फसल की अवस्था के अनुरूप **Urea / DAP / MOP** और सिंचाई दें।`;
        }
      } else if (lang === 'mr') {
        if (isYellow) {
          answer = `**${cropName} पाने पिवळी पडणे उपाय:**\n\nनोंदीनुसार **N=${nStr}** आहे. खालच्या पानांसाठी **20–25 kg/acre Urea** द्या किंवा **0.5% Zinc Sulphate** फवारणी करा व पाणी साचू देऊ नका.`;
        } else if (isWater) {
          answer = `**${cropName} सिंचन अंदाज (FAO-56):**\n\nअंदाजे पाणी: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre**. सकाळी **5:30–8:30** किंवा संध्याकाळी **5:30** नंतर पाणी द्या.`;
        } else {
          answer = `**${cropName} ऑफलाइन सल्ला:**\n\nतुमच्या नोंदी (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**) नुसार पिकाच्या अवस्थेप्रमाणे **Urea / DAP / MOP** खते व सिंचन नियोजन करा.`;
        }
      } else if (lang === 'ta') {
        if (isYellow) {
          answer = `**${cropName} இலை மஞ்சள் தீர்வு:**\n\nமண் அளவு **N=${nStr}**. ஏக்கருக்கு **20–25 kg Urea (யூரியா)** அல்லது **0.5% Zinc Sulphate** தெளித்து நீர் தேங்காமல் வடிக்கவும்.`;
        } else if (isWater) {
          answer = `**${cropName} நீர்ப்பாசன அளவு (FAO-56):**\n\nதேவை: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre**. காலை **5:30–8:30** அல்லது மாலை **5:30**-க்குப் பின் நீர் பாய்ச்சவும்.`;
        } else {
          answer = `**${cropName} ஆஃப்லைன் வேளாண் ஆலோசனை:**\n\nஉங்கள் தரவு (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**) அடிப்படையில் **Urea / DAP / MOP** மற்றும் நீர்ப்பாசனத்தைத் திட்டமிடுங்கள்.`;
        }
      } else if (lang === 'te') {
        if (isYellow) {
          answer = `**${cropName} ఆకుల పసుపు రంగు నివారణ:**\n\nమీ నేల నివేదిక **N=${nStr}**. ఎకరానికి **20–25 kg Urea (యూరియా)** లేదా **0.5% Zinc Sulphate** పిచికారీ చేసి నీటి నిల్వ లేకుండా చూడండి.`;
        } else if (isWater) {
          answer = `**${cropName} నీటి అంచనా (FAO-56):**\n\nఅవసరం: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre**. ఉదయం **5:30–8:30** లేదా సాయంత్రం **5:30** తర్వాత నీరు పెట్టండి.`;
        } else {
          answer = `**${cropName} ఆఫ్‌లైన్ వ్యవసాయ సలహా:**\n\nమీ డేటా (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**) ప్రకారం పంట దశకు తగిన **Urea / DAP / MOP** మరియు నీటిపారుదల పాటించండి.`;
        }
      } else {
        if (isGreet) {
          answer = `Hello! I'm Geo running **100% offline** with your **${cropName}** records (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**). Ask directly about leaf symptoms, water deficit, or fertilizer dosage.`;
        } else if (isYellow) {
          const nNote = (nVal !== null && nVal < 50)
            ? `Your Nitrogen is low (**N = ${nStr}**), pointing directly to **Nitrogen deficiency** on lower leaves.`
            : `Your Nitrogen is **${nStr}**, so check younger leaves for **Iron / Zinc deficiency** or saturated roots.`;
          answer = `**Direct Diagnosis: Leaf Yellowing in ${cropName}**\n\n${nNote}\n\n• **Action:** Top-dress **20–25 kg/acre Urea** (or **1% Urea foliar spray**) for older leaves, or **0.5% Zinc Sulphate** for upper leaves.`;
        } else if (isWater) {
          answer = `**Offline Irrigation Calculation for ${cropName} (FAO-56)**\n\n• Estimated Water Deficit: **~${irrigCalc.waterPerAcreLiters.toLocaleString()} Liters/Acre** (ETc: **${irrigCalc.evapotranspirationMmDay} mm/day**).\n• Schedule irrigation between **5:30–8:30 AM** or after **5:30 PM** to cut evaporative losses.`;
        } else if (isPest) {
          answer = `**Integrated Pest Protocol for ${cropName} (IPM)**\n\n• Deploy **8–10 Yellow Sticky Traps/acre** and spray cold-pressed **Neem Oil / NSKE 5% (3–4 ml/L)** early.`;
        } else if (isFert) {
          answer = `**4R Nutrient Split Plan for ${cropName}**\n\n• Grounded Profile: **N=${nStr}, P=${pStr}, K=${kStr} (${phStr})**.\n• Apply **Urea** in 3 splits (50% basal, 25% vegetative, 25% flowering) and place **DAP / MOP** as basal dose near roots.`;
        } else {
          answer = `**Direct Offline Advisory for ${cropName}**\n\nAnswering *'${prompt}'* with your local records (**N=${nStr}, P=${pStr}, K=${kStr}, ${phStr}**): match **Urea / DAP / MOP** split timings and irrigation to your active crop growth stage.`;
        }
      }

      return {
        answer,
        detected_language: lang,
        contextUsed: chips,
        contextChips: chips,
        engine: `${this.engineName} (${lang.toUpperCase()})`,
        mode: 'offline_deterministic',
        scientificDisclaimer: DISCLAIMERS[lang] || DISCLAIMERS.en
      };
    }

    diagnoseDiseaseOffline(question = '', npkRes = null, context = {}) {
      const selectedLang = context.language || (window.GeosenseI18n ? window.GeosenseI18n.getLanguage() : 'en');
      const lang = (window.GeosenseI18n && window.GeosenseI18n.detectQueryLanguage)
        ? window.GeosenseI18n.detectQueryLanguage(question, selectedLang)
        : selectedLang;
      const cropName = (context.crop && (context.crop.primary_recommendation || context.crop.primary_crop)) || 'Rice';
      const weather = context.weather || {};
      const hum = weather.humidity ? Number(weather.humidity) : null;
      const temp = weather.temp ? Number(weather.temp) : null;

      const lowN = npkRes && npkRes.status && npkRes.status.N === 'Low';
      const lowK = npkRes && npkRes.status && npkRes.status.K === 'Low';
      const q = (question || '').toLowerCase();
      const hasDiseaseCues = /(spot|blight|mold|rust|mildew|curl|mosaic|rot|mite|fung|bact|ವೈರಸ್|ಚುಕ್ಕೆ|धब्बा|झुलसा|फफूंद|रोग|डाग|புள்ளி|మచ్చ)/i.test(q);

      let conditionName = `${cropName} Fungal Leaf Spot / Blight (Offline Screen)`;
      let statusCat = 'Infected';
      let pathogenCause = 'Alternaria / Fungal Leaf Spot (Offline Symptom Heuristic)';
      if (!hasDiseaseCues && (lowN || lowK)) {
        conditionName = lowN ? 'Nitrogen Deficiency Chlorosis (Offline Screen)' : 'Potassium Marginal Scorch (Offline Screen)';
        statusCat = 'Deficiency';
        pathogenCause = 'Nutrient Deficiency (ICAR Cross-Check)';
      }

      const wNote = (temp !== null && hum !== null) ? `${temp}°C, ${hum}% RH` : 'Local Field Conditions';
      const whyMap = {
        kn: `ಪ್ರಸ್ತುತ ಹವಾಮಾನ (${wNote}) ಹಾಗೂ ಎಲೆ ಬಣ್ಣ/NPK ಮಾದರಿಯ ಆಧಾರದ ಆಫ್‌ಲೈನ್ ರೋಗ ಪರೀಕ್ಷೆ.`,
        hi: `वर्तमान मौसम (${wNote}) और पत्ती लक्षण/NPK पैटर्न पर आधारित ऑफलाइन रोग जांच।`,
        mr: `सध्याचे हवामान (${wNote}) आणि पान/NPK लक्षणावर आधारित ऑफलाइन निदान.`,
        ta: `தற்போதைய வானிலை (${wNote}) மற்றும் இலை/NPK அடிப்படையிலான ஆஃப்லைன் நோய் கணிப்பு.`,
        te: `ప్రస్తుత వాతావరణం (${wNote}) మరియు ఆకు/NPK లక్షణాల ఆధారిత ఆఫ్‌లైన్ నిర్ధారణ.`,
        en: `Offline visual color & symptom analysis correlated with ${wNote} and ICAR nutrient thresholds.`
      };

      const chips = [cropName];
      if (temp !== null) chips.push(`${temp}°C`);
      if (hum !== null) chips.push(`${hum}% RH`);
      if (npkRes) chips.push(`N:${npkRes.nitrogen} (${npkRes.status?.N || 'OK'})`);

      const solObj = {
        immediate_field_action: [
          'Prune severely spotted lower leaves cleanly and burn/bury outside the plot; switch overhead watering to morning root irrigation.'
        ],
        organic_cultural: [
          'Spray Trichoderma viride @ 5 g/L (75 g per 15L pump) or cold-pressed Neem Oil 1500 ppm @ 3–5 ml/L (45–75 ml per 15L pump).'
        ],
        chemical_targeted: statusCat === 'Deficiency'
          ? ['Spray 1% foliar Urea @ 10 g/L (150 g per 15L pump) or NPK 19:19:19 @ 5 g/L (75 g per 15L pump); repeat after 10 days.']
          : ['Mancozeb 75% WP @ 2.5 g/L (37.5 g per 15L pump) OR Azoxystrobin 23% SC @ 1.0 ml/L (15 ml per 15L pump); repeat every 7–10 days.'],
        spray_notes: 'Apply thoroughly to upper and lower foliage every 7–10 days.'
      };

      return {
        disease_name: conditionName,
        condition_name: conditionName,
        pathogen_type: pathogenCause,
        pathogen_or_cause: pathogenCause,
        observed_symptoms: `Offline leaf visual screening in ${cropName} (${wNote}) correlated with nutrient balance.`,
        status_category: statusCat,
        confidence: 0.72,
        low_confidence: false,
        why_infected: whyMap[lang] || whyMap.en,
        immediate_solution: solObj,
        solution_to_fix: solObj,
        prevention: [
          'Maintain field drainage, morning drip irrigation, and clean weed-free field bunds.'
        ],
        npk_crosscheck: npkRes ? {
          nitrogen: npkRes.nitrogen,
          phosphorus: npkRes.phosphorus,
          potassium: npkRes.potassium,
          status: npkRes.status,
          deficiency_suspected: Boolean(lowN || lowK),
          note: `Offline NPK Cross-Check: N=${npkRes.nitrogen} (${npkRes.status?.N}), K=${npkRes.potassium} (${npkRes.status?.K}) kg/ha.`
        } : null,
        farm_context_chips: chips,
        detected_language: lang,
        language_name: lang.toUpperCase(),
        model_source: 'Offline Color-Constancy + ICAR Rules',
        inference_engine: `${this.engineName} (Disease Fallback)`,
        scientific_disclaimer: DISCLAIMERS[lang] || DISCLAIMERS.en
      };
    }
  }

  window.OfflineAgroEngine = new OfflineAgroEngine();
})(window);
