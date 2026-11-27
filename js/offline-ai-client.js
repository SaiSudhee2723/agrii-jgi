/**
 * Geosense Hybrid AI Client Orchestrator
 * Coordinates:
 *   1. Advanced Cloud AI (Qwen3 Grounded Backend API)
 *   2. Offline On-Device AI (Gemma 4 E2B via LiteRT-LM WebGPU Web Worker)
 *   3. Offline Deterministic Fallback (FAO-56 & Expert Agronomy Rules)
 */

(function (window) {
  'use strict';

  const STORAGE_KEY_MODE = 'geosense_ai_mode';
  const STORAGE_KEY_MODEL_URL = 'geosense_litert_model_url';
  const DEFAULT_MODEL_URL = 'https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/main/model.litertlm';
  const MODEL_ID = 'gemma-4-e2b-litertlm';
  const ESTIMATED_MODEL_MB = 1250; // ~1.25 GB

  class GeosenseAiClient {
    constructor() {
      this.mode = localStorage.getItem(STORAGE_KEY_MODE) || 'cloud'; // 'cloud' | 'offline'
      this.modelUrl = localStorage.getItem(STORAGE_KEY_MODEL_URL) || DEFAULT_MODEL_URL;
      this.modelId = MODEL_ID;

      this.worker = null;
      this.isWorkerReady = false;
      this.isModelDownloading = false;
      this.webGpuSupported = false;
      this.webGpuAdapter = null;
      this.cachedModelInfo = null;

      // Status: 'cloud_ready' | 'offline_unloaded' | 'offline_downloading' | 'offline_initializing' | 'offline_gemma_ready' | 'offline_fallback_ready'
      this.status = 'cloud_ready';
      this.statusMessage = 'Cloud AI Engine (Qwen3 Grounded)';

      this.stateListeners = [];
      this.downloadProgressListeners = [];

      this.init();
    }

    async init() {
      // Check cache status
      if (window.LiteRtCacheManager) {
        try {
          const isCached = await window.LiteRtCacheManager.isModelCached(this.modelId);
          if (isCached) {
            this.cachedModelInfo = await window.LiteRtCacheManager.getCachedModel(this.modelId);
          }
        } catch (e) {
          console.warn('[AiClient] Cache check failed:', e);
        }
      }

      // Check WebGPU capability
      if (typeof navigator !== 'undefined' && navigator.gpu) {
        try {
          const adapter = await navigator.gpu.requestAdapter();
          if (adapter) {
            this.webGpuSupported = true;
            try {
              const info = await adapter.requestAdapterInfo();
              this.webGpuAdapter = {
                vendor: info.vendor || 'Standard GPU',
                architecture: info.architecture || 'WebGPU',
                device: info.device || 'Default Graphics'
              };
            } catch {
              this.webGpuAdapter = { vendor: 'WebGPU Compatible', device: 'Active' };
            }
          }
        } catch {
          this.webGpuSupported = false;
        }
      }

      this.updateStatus();
    }

    onStateChange(callback) {
      if (typeof callback === 'function') this.stateListeners.push(callback);
    }

    onDownloadProgress(callback) {
      if (typeof callback === 'function') this.downloadProgressListeners.push(callback);
    }

    notifyState() {
      const state = this.getState();
      this.stateListeners.forEach((cb) => {
        try { cb(state); } catch (e) { console.error(e); }
      });
    }

    getState() {
      return {
        mode: this.mode,
        status: this.status,
        statusMessage: this.statusMessage,
        isGemmaActive: this.mode === 'offline' && this.isWorkerReady,
        isFallbackActive: this.mode === 'offline' && !this.isWorkerReady,
        webGpuSupported: this.webGpuSupported,
        webGpuAdapter: this.webGpuAdapter,
        isModelCached: !!this.cachedModelInfo,
        cachedSizeMB: this.cachedModelInfo ? this.cachedModelInfo.sizeMB : 0,
        downloadedAt: this.cachedModelInfo ? this.cachedModelInfo.downloadedAt : null,
        estimatedModelMB: ESTIMATED_MODEL_MB,
        modelUrl: this.modelUrl,
        modelId: this.modelId
      };
    }

    setMode(mode) {
      if (mode !== 'cloud' && mode !== 'offline') return;
      this.mode = mode;
      localStorage.setItem(STORAGE_KEY_MODE, mode);

      if (mode === 'offline' && !this.isWorkerReady) {
        // If switching to offline, attempt initialization if cached, or prepare fallback
        if (this.cachedModelInfo && this.webGpuSupported) {
          this.initializeGemmaWorker();
        } else {
          this.updateStatus();
        }
      } else {
        this.updateStatus();
      }
    }

    setModelUrl(url) {
      if (!url || !url.trim()) return;
      this.modelUrl = url.trim();
      localStorage.setItem(STORAGE_KEY_MODEL_URL, this.modelUrl);
      this.notifyState();
    }

    updateStatus() {
      if (this.mode === 'cloud') {
        this.status = 'cloud_ready';
        this.statusMessage = 'Cloud AI (Qwen3 Grounded Agro-Engine)';
      } else {
        if (this.isModelDownloading) {
          this.status = 'offline_downloading';
          this.statusMessage = 'Downloading Gemma 4 E2B (~1.2 GB)...';
        } else if (this.isWorkerReady) {
          this.status = 'offline_gemma_ready';
          this.statusMessage = 'Offline AI (Gemma 4 E2B via WebGPU)';
        } else if (this.cachedModelInfo && this.webGpuSupported) {
          this.status = 'offline_cached_unloaded';
          this.statusMessage = 'Gemma 4 E2B Cached (Click to Load)';
        } else if (!this.webGpuSupported) {
          this.status = 'offline_fallback_ready';
          this.statusMessage = 'Offline AI (Deterministic Agro Engine - WebGPU Unsupported)';
        } else {
          this.status = 'offline_unloaded';
          this.statusMessage = 'Offline AI (Model Download Required)';
        }
      }
      this.notifyState();
    }

    /**
     * Downloads Gemma 4 E2B model and persists into IndexedDB cache.
     */
    async downloadModel() {
      if (this.isModelDownloading) return;
      this.isModelDownloading = true;
      this.updateStatus();

      try {
        if (!window.LiteRtCacheManager) {
          throw new Error('LiteRtCacheManager is not loaded.');
        }

        const cachedRecord = await window.LiteRtCacheManager.downloadAndCacheModel(
          this.modelUrl,
          this.modelId,
          (progress) => {
            this.downloadProgressListeners.forEach((cb) => {
              try { cb(progress); } catch (e) { console.error(e); }
            });
          }
        );

        this.cachedModelInfo = cachedRecord;
        this.isModelDownloading = false;

        // Auto initialize worker if WebGPU is supported
        if (this.webGpuSupported) {
          await this.initializeGemmaWorker();
        } else {
          this.updateStatus();
        }

        return cachedRecord;
      } catch (err) {
        this.isModelDownloading = false;
        this.updateStatus();
        console.error('[AiClient] Model download error:', err);
        throw err;
      }
    }

    /**
     * Initializes the Web Worker and loads the Gemma 4 E2B model.
     */
    async initializeGemmaWorker() {
      if (!this.webGpuSupported) {
        console.warn('[AiClient] Cannot initialize Gemma Web Worker: WebGPU is unsupported. Falling back to deterministic agro engine.');
        this.updateStatus();
        return false;
      }

      if (!this.cachedModelInfo) {
        console.warn('[AiClient] Model is not cached yet.');
        this.updateStatus();
        return false;
      }

      this.status = 'offline_initializing';
      this.statusMessage = 'Compiling Gemma 4 E2B WebGPU Shaders...';
      this.notifyState();

      return new Promise((resolve) => {
        try {
          if (this.worker) {
            this.worker.terminate();
          }

          this.worker = new Worker('js/litert-worker.js', { type: 'module' });

          this.worker.onmessage = (e) => {
            const data = e.data || {};

            if (data.type === 'STATUS') {
              if (data.status === 'READY') {
                this.isWorkerReady = true;
                this.updateStatus();
                resolve(true);
              } else if (data.status === 'ERROR') {
                console.error('[AiClient] Worker initialization failed:', data.error);
                this.isWorkerReady = false;
                this.updateStatus();
                resolve(false);
              } else if (data.message) {
                this.statusMessage = data.message;
                this.notifyState();
              }
            }
          };

          this.worker.onerror = (err) => {
            console.error('[AiClient] Web Worker syntax/execution error:', err);
            this.isWorkerReady = false;
            this.updateStatus();
            resolve(false);
          };

          // Send cached blob to worker
          this.worker.postMessage({
            type: 'INIT_ENGINE',
            payload: {
              modelBlob: this.cachedModelInfo.blob,
              systemPrompt: "You are Geo, an expert agronomy AI running on-device via Gemma 4 E2B with LiteRT WebGPU acceleration. Answer farming, soil health, crop nutrient, and irrigation questions concisely and accurately."
            }
          });

        } catch (err) {
          console.error('[AiClient] Failed to instantiate worker:', err);
          this.isWorkerReady = false;
          this.updateStatus();
          resolve(false);
        }
      });
    }

    buildSanitizedContext(context = {}, lang = 'en') {
      const clean = {};
      const soil = context.soil || {};
      const cleanSoil = {};
      const chips = [];

      const cropName = (context.crop && (context.crop.primary_recommendation || context.crop.primary_crop)) || 'Rice';
      clean.crop = { primary_recommendation: cropName };
      chips.push(cropName);
      if (context.diseaseDiagnosis && context.diseaseDiagnosis.condition_name) {
        clean.diseaseDiagnosis = context.diseaseDiagnosis;
        chips.push(context.diseaseDiagnosis.condition_name);
      }

      const hasVal = (v) => v !== null && v !== undefined && v !== '' && !Number.isNaN(Number(v));
      if (hasVal(soil.nitrogen_ppm)) {
        cleanSoil.nitrogen_ppm = Number(soil.nitrogen_ppm);
        chips.push(`N: ${cleanSoil.nitrogen_ppm} kg/ha`);
      }
      if (hasVal(soil.phosphorus_ppm)) {
        cleanSoil.phosphorus_ppm = Number(soil.phosphorus_ppm);
        chips.push(`P: ${cleanSoil.phosphorus_ppm} kg/ha`);
      }
      if (hasVal(soil.potassium_ppm)) {
        cleanSoil.potassium_ppm = Number(soil.potassium_ppm);
        chips.push(`K: ${cleanSoil.potassium_ppm} kg/ha`);
      }
      if (hasVal(soil.soil_ph)) {
        cleanSoil.soil_ph = Number(soil.soil_ph);
        chips.push(`pH: ${cleanSoil.soil_ph}`);
      } else if (Object.keys(cleanSoil).length > 0) {
        const phLabel = window.GeosenseI18n ? window.GeosenseI18n.t('assistant.ph_not_tested') : 'pH: Not tested';
        chips.push(phLabel);
      }
      if (hasVal(soil.moisture_pct)) cleanSoil.moisture_pct = Number(soil.moisture_pct);
      if (Object.keys(cleanSoil).length > 0) clean.soil = cleanSoil;

      if (context.weather && hasVal(context.weather.temp)) {
        clean.weather = {
          temp: Number(context.weather.temp),
          humidity: hasVal(context.weather.humidity) ? Number(context.weather.humidity) : undefined,
          location: context.weather.location || undefined
        };
        chips.push(`${clean.weather.temp}°C`);
        if (clean.weather.location) chips.push(clean.weather.location);
      }

      return { sanitizedContext: clean, contextChips: chips };
    }

    buildLocalizedSystemPrompt(langCode, cleanContext) {
      const langInfo = (window.GeosenseI18n && window.GeosenseI18n.getLanguageInfo)
        ? window.GeosenseI18n.getLanguageInfo(langCode)
        : { code: 'en', name: 'English', scriptInstruction: 'Answer in clear natural English.' };
      const diagNote = (cleanContext && cleanContext.diseaseDiagnosis && cleanContext.diseaseDiagnosis.condition_name)
        ? `\nACTIVE DISEASE DIAGNOSIS: ${cleanContext.diseaseDiagnosis.condition_name} (${cleanContext.diseaseDiagnosis.pathogen_or_cause || ''}). Use its chemical/organic spray dosages for 15L tank follow-ups.`
        : '';
      return (
        `You are Geo, Geosense's AI Agronomy Assistant running on-device via Gemma 4 E2B.\n` +
        `TARGET LANGUAGE: ${langInfo.name} (${langInfo.code}).\n` +
        `MANDATORY SCRIPT RULE: ${langInfo.scriptInstruction}\n` +
        `Answer the farmer's exact question directly first using their real farm telemetry, followed by concise steps. ` +
        `Never echo null or 'None' values. Keep chemical names and units (kg/ha, ml/L, g/L, °C, NPK) clear.${diagNote}`
      );
    }

    /**
     * Primary chat query method.
     * Guaranteed routing:
     *   - If Cloud: sends to Qwen3 backend API with active language + auto-detection.
     *   - If Offline: NEVER sends to cloud. Uses Gemma Web Worker if loaded, else localized offline engine.
     */
    async chat(message, context = {}, onTokenCallback = null) {
      const q = (message || '').trim();
      if (!q) throw new Error('Query cannot be empty.');

      const selectedLang = context.language || (window.GeosenseI18n ? window.GeosenseI18n.getLanguage() : 'en');
      const effectiveLang = (window.GeosenseI18n && window.GeosenseI18n.detectQueryLanguage)
        ? window.GeosenseI18n.detectQueryLanguage(q, selectedLang)
        : selectedLang;
      const langInfo = (window.GeosenseI18n && window.GeosenseI18n.getLanguageInfo)
        ? window.GeosenseI18n.getLanguageInfo(effectiveLang)
        : { code: effectiveLang, name: effectiveLang };

      const { sanitizedContext, contextChips } = this.buildSanitizedContext(context, effectiveLang);
      const systemPrompt = this.buildLocalizedSystemPrompt(effectiveLang, sanitizedContext);

      // 1. CLOUD MODE (Qwen3 Grounded Backend)
      if (this.mode === 'cloud') {
        if (!window.GeosenseApi || !window.GeosenseApi.chatWithAssistant) {
          throw new Error('GeosenseApi cloud backend client is unavailable.');
        }
        const res = await window.GeosenseApi.chatWithAssistant(
          q,
          selectedLang,
          context.lat ?? null,
          context.lon ?? null,
          langInfo.name,
          context.diseaseDiagnosis || null
        );
        return {
          answer: res.answer,
          contextUsed: res.context_used || contextChips,
          contextChips: res.context_chips || contextChips,
          detectedLanguage: res.detected_language || effectiveLang,
          engine: `Qwen3 Cloud AI (${res.language_name || langInfo.name})`,
          mode: 'cloud',
          scientificDisclaimer: res.scientific_disclaimer || 'NOTICE: Agronomic decision support.'
        };
      }

      // 2. OFFLINE MODE: STRICT ENFORCEMENT - ZERO CLOUD CALLS
      if (this.isWorkerReady && this.worker) {
        return new Promise((resolve) => {
          let accumulatedText = '';

          const messageHandler = (e) => {
            const data = e.data || {};

            if (data.type === 'TOKEN_CHUNK') {
              accumulatedText += data.chunk;
              if (typeof onTokenCallback === 'function') {
                onTokenCallback(data.chunk, accumulatedText);
              }
            } else if (data.type === 'GENERATE_COMPLETE') {
              this.worker.removeEventListener('message', messageHandler);
              resolve({
                answer: data.text || accumulatedText,
                contextChips,
                tokensPerSec: data.tokensPerSec,
                tokenCount: data.tokenCount,
                elapsedMs: data.elapsedMs,
                engine: `${data.engine || 'Gemma 4 E2B'} (${langInfo.name})`,
                mode: 'offline_gemma',
                scientificDisclaimer: `NOTICE: On-device Gemma 4 E2B AI advisory (${langInfo.name}) running locally via WebGPU.`
              });
            } else if (data.type === 'GENERATE_ERROR') {
              this.worker.removeEventListener('message', messageHandler);
              console.warn('[AiClient] Gemma inference failed, falling back to offline engine:', data.error);
              const fallbackRes = window.OfflineAgroEngine.generateAdvisory(q, { ...sanitizedContext, language: effectiveLang });
              resolve({
                ...fallbackRes,
                contextChips: fallbackRes.contextChips || contextChips,
                note: `Gemma on-device execution error (${data.error}). Output provided by Offline Deterministic Engine.`
              });
            }
          };

          this.worker.addEventListener('message', messageHandler);
          this.worker.postMessage({
            type: 'GENERATE',
            payload: {
              prompt: q,
              systemPrompt,
              language: effectiveLang,
              languageName: langInfo.name,
              context: sanitizedContext
            }
          });
        });
      }

      // 2B. OFFLINE DETERMINISTIC FALLBACK
      if (window.OfflineAgroEngine) {
        const res = window.OfflineAgroEngine.generateAdvisory(q, { ...sanitizedContext, language: effectiveLang });
        if (!res.contextChips) res.contextChips = contextChips;
        return res;
      }

      throw new Error('No offline AI engine or fallback knowledge base is available.');
    }

    /**
     * In-browser color-constancy NPK estimator fallback when offline mode is active
     * or the FastAPI ONNX backend is unreachable.
     */
    async estimateNpkOffline(imageBlobOrFile) {
      if (!imageBlobOrFile) throw new Error('No image provided for offline NPK estimation.');

      const img = await new Promise((resolve, reject) => {
        const imageEl = new Image();
        const url = typeof imageBlobOrFile === 'string' ? imageBlobOrFile : URL.createObjectURL(imageBlobOrFile);
        imageEl.onload = () => {
          if (typeof imageBlobOrFile !== 'string') URL.revokeObjectURL(url);
          resolve(imageEl);
        };
        imageEl.onerror = () => reject(new Error('Failed to decode image offline.'));
        imageEl.src = url;
      });

      const canvas = document.createElement('canvas');
      canvas.width = 112;
      canvas.height = 112;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, 112, 112);
      const { data } = ctx.getImageData(0, 0, 112, 112);

      let rSum = 0, gSum = 0, bSum = 0;
      const pxCount = data.length / 4;
      for (let i = 0; i < data.length; i += 4) {
        rSum += data[i];
        gSum += data[i + 1];
        bSum += data[i + 2];
      }
      const rMean = rSum / pxCount;
      const gMean = gSum / pxCount;
      const bMean = bSum / pxCount;
      const grayMean = (rMean + gMean + bMean) / 3 || 1;

      // Gray-World color-balanced normalized channels
      const rBal = Math.min(255, rMean * Math.min(1.35, Math.max(0.75, grayMean / (rMean || 1))));
      const gBal = Math.min(255, gMean * Math.min(1.35, Math.max(0.75, grayMean / (gMean || 1))));
      const bBal = Math.min(255, bMean * Math.min(1.35, Math.max(0.75, grayMean / (bMean || 1))));

      const greenIndex = Math.max(0, Math.min(1, (gBal - rBal * 0.45 + (255 - grayMean) * 0.35) / 180));
      const nitrogen = parseFloat((130 + greenIndex * 290).toFixed(2));
      const phosphorus = parseFloat((5 + ((gBal - bBal + 90) / 220) * 23).toFixed(2));
      const potassium = parseFloat((75 + (grayMean / 255) * 185).toFixed(2));

      const classify = (val, lo, hi) => (val < lo ? 'Low' : val > hi ? 'High' : 'Optimal');
      const status = {
        N: classify(nitrogen, 280, 460),
        P: classify(phosphorus, 10, 30),
        K: classify(potassium, 120, 280)
      };

      return {
        nitrogen,
        phosphorus,
        potassium,
        status,
        model_source: 'offline_heuristic',
        inference_engine: 'Offline Color-Constancy Heuristic (ICAR Scale)',
        recommendations: [
          `Offline N=${nitrogen} (${status.N}), P=${phosphorus} (${status.P}), K=${potassium} (${status.K}) kg/ha.`,
          'Reconnect to FastAPI backend for full real-dataset MobileNetV3 + HSV/LAB ONNX inference, and confirm via certified KVK lab assay.'
        ],
        scientific_disclaimer: 'OFFLINE ESTIMATE: Computed in-browser using Gray-World color-constancy fallback with zero network requests.'
      };
    }

    /**
     * Hybrid Crop Infection & Disease Diagnosis (Online ONNX + ICAR Grounded API, or Offline Fallback).
     */
    async diagnoseDisease(imageBlobOrFile, options = {}) {
      if (!imageBlobOrFile) throw new Error('No leaf or crop image provided.');
      if (this.mode !== 'offline' && window.GeosenseApi && window.GeosenseApi.diagnoseCropDisease) {
        try {
          return await window.GeosenseApi.diagnoseCropDisease(imageBlobOrFile, options);
        } catch (err) {
          console.warn('[AiClient] Cloud diagnose-disease failed, switching to offline fallback:', err.message);
        }
      }

      let npkRes = null;
      try {
        npkRes = await this.estimateNpkOffline(imageBlobOrFile);
      } catch (_) {}

      if (window.OfflineAgroEngine && window.OfflineAgroEngine.diagnoseDiseaseOffline) {
        return window.OfflineAgroEngine.diagnoseDiseaseOffline(
          options.question || '',
          npkRes,
          {
            language: options.lang || 'en',
            crop: options.crop ? { primary_recommendation: options.crop } : undefined,
            weather: options.weather
          }
        );
      }
      throw new Error('Offline disease diagnostic engine is unavailable.');
    }

    /**
     * Clear cached model from browser storage.
     */
    async clearCache() {
      if (this.worker) {
        this.worker.terminate();
        this.worker = null;
      }
      this.isWorkerReady = false;

      if (window.LiteRtCacheManager) {
        await window.LiteRtCacheManager.clearCachedModel(this.modelId);
        this.cachedModelInfo = null;
      }

      this.updateStatus();
      return true;
    }
  }

  window.GeosenseAiClient = new GeosenseAiClient();
})(window);
