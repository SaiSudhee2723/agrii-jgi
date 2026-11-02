/**
 * Geosense LiteRT-LM Persistent Cache Manager
 * Manages IndexedDB & Cache Storage for browser-compatible Gemma 4 E2B .litertlm models.
 * Ensures zero repeated downloads and manages browser disk quotas.
 */

(function (window) {
  'use strict';

  const DB_NAME = 'geosense_litert_models';
  const DB_VERSION = 1;
  const STORE_NAME = 'models';
  const DEFAULT_MODEL_ID = 'gemma-4-e2b-litertlm';

  class LiteRtCacheManager {
    constructor() {
      this.db = null;
    }

    async initDb() {
      if (this.db) return this.db;
      return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onupgradeneeded = (e) => {
          const db = e.target.result;
          if (!db.objectStoreNames.contains(STORE_NAME)) {
            db.createObjectStore(STORE_NAME, { keyPath: 'id' });
          }
        };
        req.onsuccess = (e) => {
          this.db = e.target.result;
          resolve(this.db);
        };
        req.onerror = (e) => {
          console.error('[LiteRtCache] IndexedDB open error:', e);
          reject(e);
        };
      });
    }

    /**
     * Request persistent storage permission so browser doesn't evict the model blob.
     */
    async requestPersistence() {
      if (navigator.storage && navigator.storage.persist) {
        const isPersisted = await navigator.storage.persist();
        console.log(`[LiteRtCache] Persistent storage granted: ${isPersisted}`);
        return isPersisted;
      }
      return false;
    }

    /**
     * Get storage estimate (usage and quota in MB / GB).
     */
    async getStorageStats() {
      if (navigator.storage && navigator.storage.estimate) {
        const estimate = await navigator.storage.estimate();
        const usageMB = (estimate.usage / (1024 * 1024)).toFixed(1);
        const quotaMB = (estimate.quota / (1024 * 1024)).toFixed(1);
        const usagePct = ((estimate.usage / estimate.quota) * 100).toFixed(1);
        return {
          usageBytes: estimate.usage,
          quotaBytes: estimate.quota,
          usageMB: parseFloat(usageMB),
          quotaMB: parseFloat(quotaMB),
          usagePct: parseFloat(usagePct)
        };
      }
      return { usageMB: 0, quotaMB: 0, usagePct: 0 };
    }

    /**
     * Checks if model is already stored in persistent IndexedDB.
     */
    async isModelCached(modelId = DEFAULT_MODEL_ID) {
      try {
        const db = await this.initDb();
        return new Promise((resolve) => {
          const tx = db.transaction(STORE_NAME, 'readonly');
          const store = tx.objectStore(STORE_NAME);
          const req = store.get(modelId);
          req.onsuccess = () => {
            const result = req.result;
            resolve(!!(result && result.blob && result.blob.size > 0));
          };
          req.onerror = () => resolve(false);
        });
      } catch (err) {
        console.warn('[LiteRtCache] Error checking cache:', err);
        return false;
      }
    }

    /**
     * Retrieves cached model blob and metadata.
     */
    async getCachedModel(modelId = DEFAULT_MODEL_ID) {
      const db = await this.initDb();
      return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readonly');
        const store = tx.objectStore(STORE_NAME);
        const req = store.get(modelId);
        req.onsuccess = () => resolve(req.result || null);
        req.onerror = (e) => reject(e);
      });
    }

    /**
     * Downloads model from URL with streaming progress, storing into IndexedDB.
     * @param {string} url - Model binary endpoint (.litertlm)
     * @param {string} modelId - Identifier
     * @param {Function} onProgress - Callback: { percent, downloadedMB, totalMB, speedMBs, etaSec }
     * @param {AbortSignal} signal - Optional abort signal
     */
    async downloadAndCacheModel(url, modelId = DEFAULT_MODEL_ID, onProgress = null, signal = null) {
      await this.requestPersistence();

      const startTime = performance.now();
      const response = await fetch(url, { signal });
      if (!response.ok) {
        throw new Error(`Failed to fetch model from ${url} (HTTP ${response.status}: ${response.statusText})`);
      }

      const contentLength = response.headers.get('Content-Length');
      const totalBytes = contentLength ? parseInt(contentLength, 10) : 1250000000; // ~1.25 GB fallback estimate
      const reader = response.body.getReader();

      const chunks = [];
      let receivedBytes = 0;
      let lastReportTime = startTime;
      let lastReportBytes = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        chunks.push(value);
        receivedBytes += value.length;

        const now = performance.now();
        if (now - lastReportTime > 200 || receivedBytes === totalBytes) {
          const deltaSec = (now - lastReportTime) / 1000;
          const deltaBytes = receivedBytes - lastReportBytes;
          const speedMBs = deltaSec > 0 ? ((deltaBytes / (1024 * 1024)) / deltaSec).toFixed(1) : '0.0';

          const remainingBytes = Math.max(0, totalBytes - receivedBytes);
          const speedBytesPerSec = deltaSec > 0 ? (deltaBytes / deltaSec) : 1;
          const etaSec = Math.round(remainingBytes / Math.max(speedBytesPerSec, 1));

          const percent = Math.min(100, parseFloat(((receivedBytes / totalBytes) * 100).toFixed(1)));
          const downloadedMB = (receivedBytes / (1024 * 1024)).toFixed(1);
          const totalMB = (totalBytes / (1024 * 1024)).toFixed(1);

          if (onProgress) {
            onProgress({
              percent,
              downloadedMB,
              totalMB,
              speedMBs,
              etaSec
            });
          }

          lastReportTime = now;
          lastReportBytes = receivedBytes;
        }
      }

      const modelBlob = new Blob(chunks, { type: 'application/octet-stream' });
      const record = {
        id: modelId,
        url,
        sizeBytes: modelBlob.size,
        sizeMB: (modelBlob.size / (1024 * 1024)).toFixed(1),
        blob: modelBlob,
        downloadedAt: new Date().toISOString()
      };

      // Persist to IndexedDB
      const db = await this.initDb();
      await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        const putReq = store.put(record);
        putReq.onsuccess = () => resolve(record);
        putReq.onerror = (e) => reject(e);
      });

      console.log(`[LiteRtCache] Model ${modelId} cached successfully (${record.sizeMB} MB).`);
      return record;
    }

    /**
     * Deletes cached model from IndexedDB.
     */
    async clearCachedModel(modelId = DEFAULT_MODEL_ID) {
      const db = await this.initDb();
      return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        const delReq = store.delete(modelId);
        delReq.onsuccess = () => {
          console.log(`[LiteRtCache] Model ${modelId} cleared from cache.`);
          resolve(true);
        };
        delReq.onerror = (e) => reject(e);
      });
    }
  }

  window.LiteRtCacheManager = new LiteRtCacheManager();
})(window);
