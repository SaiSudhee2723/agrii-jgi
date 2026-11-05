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

    /**
     * Primary chat query method.
     * Guaranteed routing:
     *   - If Cloud: sends to Qwen3 backend API.
     *   - If Offline: NEVER sends to cloud. Uses Gemma Web Worker if loaded, else deterministic offline engine.
     */
    async chat(message, context = {}, onTokenCallback = null) {
      const q = (message || '').trim();
      if (!q) throw new Error('Query cannot be empty.');

      // 1. CLOUD MODE (Qwen3 Grounded Backend)
      if (this.mode === 'cloud') {
        if (!window.GeosenseApi || !window.GeosenseApi.chatWithAssistant) {
          throw new Error('GeosenseApi cloud backend client is unavailable.');
        }
        const lang = context.language || (window.GeosenseI18n ? window.GeosenseI18n.getLanguage() : 'en');
        const res = await window.GeosenseApi.chatWithAssistant(q, lang);
        return {
          answer: res.answer,
          contextUsed: res.context_used || [],
          engine: 'Qwen3 (Cloud Agronomy Engine)',
          mode: 'cloud',
          scientificDisclaimer: res.scientific_disclaimer || 'NOTICE: Agronomic decision support.'
        };
      }

      // 2. OFFLINE MODE: STRICT ENFORCEMENT - ZERO CLOUD CALLS
      // 2A. If Gemma 4 E2B WebGPU worker is loaded and ready
      if (this.isWorkerReady && this.worker) {
        return new Promise((resolve, reject) => {
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
                tokensPerSec: data.tokensPerSec,
                tokenCount: data.tokenCount,
                elapsedMs: data.elapsedMs,
                engine: data.engine || 'Gemma 4 E2B (LiteRT-LM WebGPU)',
                mode: 'offline_gemma',
                scientificDisclaimer: 'NOTICE: On-device Gemma 4 E2B AI advisory running locally via WebGPU. Cross-reference critical field interventions with local extension specialists.'
              });
            } else if (data.type === 'GENERATE_ERROR') {
              this.worker.removeEventListener('message', messageHandler);
              console.warn('[AiClient] Gemma inference failed, falling back to deterministic engine:', data.error);
              // Fallback to deterministic offline engine
              const fallbackRes = window.OfflineAgroEngine.generateAdvisory(q, context);
              resolve({
                ...fallbackRes,
                note: `Gemma on-device execution error (${data.error}). Output provided by Offline Deterministic Engine.`
              });
            }
          };

          this.worker.addEventListener('message', messageHandler);
          this.worker.postMessage({
            type: 'GENERATE',
            payload: { prompt: q, context }
          });
        });
      }

      // 2B. OFFLINE DETERMINISTIC FALLBACK (If model not downloaded or WebGPU unsupported)
      if (window.OfflineAgroEngine) {
        return window.OfflineAgroEngine.generateAdvisory(q, context);
      }

      throw new Error('No offline AI engine or fallback knowledge base is available.');
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
