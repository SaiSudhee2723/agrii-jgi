/**
 * Geosense LiteRT-LM Web Worker
 * Executes Gemma 4 E2B on-device inference using WebGPU acceleration in a background thread.
 * Prevents main thread UI freezing and handles token streaming.
 */

/* global self, Blob, performance, navigator */

let engine = null;
let conversation = null;
let isModelLoaded = false;
let webGpuSupported = false;
let webGpuAdapterInfo = null;

// Test WebGPU in Worker context
async function checkWebGpuSupport() {
  if (typeof navigator !== 'undefined' && navigator.gpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter) {
        webGpuSupported = true;
        try {
          const info = await adapter.requestAdapterInfo();
          webGpuAdapterInfo = {
            vendor: info.vendor || 'Unknown GPU Vendor',
            architecture: info.architecture || 'WebGPU Compatible',
            device: info.device || 'Default Graphics Device',
            description: info.description || ''
          };
        } catch {
          webGpuAdapterInfo = { vendor: 'WebGPU Adapter', device: 'Supported' };
        }
        return { supported: true, adapter: webGpuAdapterInfo };
      }
    } catch (err) {
      console.warn('[LiteRtWorker] WebGPU check failed:', err);
    }
  }
  webGpuSupported = false;
  return { supported: false, error: 'WebGPU is not supported or disabled in this browser environment.' };
}

self.onmessage = async (event) => {
  const { type, payload } = event.data || {};

  // 1. CHECK ENVIRONMENT SUPPORT
  if (type === 'CHECK_SUPPORT') {
    const gpuStatus = await checkWebGpuSupport();
    self.postMessage({
      type: 'SUPPORT_STATUS',
      webGpu: gpuStatus.supported,
      adapter: gpuStatus.adapter || null,
      error: gpuStatus.error || null
    });
    return;
  }

  // 2. LOAD LITERTLM MODEL & INITIALIZE ENGINE
  if (type === 'INIT_ENGINE') {
    try {
      self.postMessage({ type: 'STATUS', status: 'LOADING_RUNTIME', message: 'Verifying WebGPU hardware acceleration...' });
      const gpuCheck = await checkWebGpuSupport();
      if (!gpuCheck.supported) {
        throw new Error(gpuCheck.error || 'WebGPU is required for LiteRT Gemma 4 E2B execution.');
      }

      self.postMessage({ type: 'STATUS', status: 'IMPORTING_RUNTIME', message: 'Loading @litert-lm/core WebGPU engine...' });
      
      let LiteRtCore;
      try {
        LiteRtCore = await import('https://cdn.jsdelivr.net/npm/@litert-lm/core/+esm');
      } catch (importErr) {
        throw new Error(`Failed to load LiteRT-LM runtime library: ${importErr.message}`);
      }

      const { Engine } = LiteRtCore;
      if (!Engine) {
        throw new Error('LiteRT Engine constructor not found in runtime module.');
      }

      self.postMessage({ type: 'STATUS', status: 'INITIALIZING_MODEL', message: 'Compiling Gemma 4 E2B shaders and loading weights...' });
      
      const { modelBlob, modelUrl, systemPrompt } = payload;
      const modelSource = modelBlob || modelUrl;

      if (!modelSource) {
        throw new Error('No model binary blob or valid URL provided.');
      }

      // Initialize LiteRT Engine with max context tokens
      engine = await Engine.create({
        model: modelSource,
        mainExecutorSettings: {
          maxNumTokens: 4096,
        }
      });

      const defaultSystem = systemPrompt || (
        "You are Geo, an expert agronomic AI assistant running directly in the browser via Gemma 4 E2B with LiteRT WebGPU acceleration. " +
        "You provide grounded, scientifically verified guidance on soil NPK health, crop phenology, and FAO-56 irrigation standards. Keep answers actionable."
      );

      conversation = await engine.createConversation({
        preface: {
          messages: [
            { role: 'system', content: defaultSystem }
          ]
        }
      });

      isModelLoaded = true;
      self.postMessage({
        type: 'STATUS',
        status: 'READY',
        message: 'Gemma 4 E2B initialized successfully on WebGPU.',
        adapter: webGpuAdapterInfo
      });

    } catch (err) {
      isModelLoaded = false;
      engine = null;
      conversation = null;
      self.postMessage({
        type: 'STATUS',
        status: 'ERROR',
        error: err.message || 'Model initialization failed.',
        unsupported: !webGpuSupported
      });
    }
    return;
  }

  // 3. GENERATE TEXT (OFFLINE INFERENCE)
  if (type === 'GENERATE') {
    const { prompt, context } = payload;

    if (!isModelLoaded || !conversation) {
      self.postMessage({
        type: 'GENERATE_ERROR',
        error: 'Gemma 4 E2B engine is not loaded. Please initialize the model first.'
      });
      return;
    }

    try {
      const startTime = performance.now();
      let fullText = '';
      let tokenCount = 0;

      // Construct prompt with local context (latest soil test, crop, weather)
      let augmentedPrompt = prompt;
      if (context && (context.soil || context.crop || context.weather)) {
        augmentedPrompt = `[Context: Soil=${JSON.stringify(context.soil || {})}, Crop=${JSON.stringify(context.crop || {})}, Weather=${JSON.stringify(context.weather || {})}]\nFarmer Question: ${prompt}`;
      }

      // LiteRT conversation streaming
      const stream = conversation.sendMessageStreaming
        ? await conversation.sendMessageStreaming(augmentedPrompt)
        : await conversation.sendMessage({ role: 'user', content: augmentedPrompt });

      // Handle async iterable stream
      if (stream && typeof stream[Symbol.asyncIterator] === 'function') {
        for await (const chunk of stream) {
          const chunkText = (chunk && chunk.content && chunk.content[0] && chunk.content[0].text) 
            ? chunk.content[0].text 
            : (typeof chunk === 'string' ? chunk : (chunk.text || ''));
          
          if (chunkText) {
            fullText += chunkText;
            tokenCount++;
            self.postMessage({
              type: 'TOKEN_CHUNK',
              chunk: chunkText,
              tokenCount
            });
          }
        }
      } else {
        // Fallback for non-streaming response object
        const resultText = (stream && stream.content && stream.content[0] && stream.content[0].text)
          ? stream.content[0].text
          : (typeof stream === 'string' ? stream : JSON.stringify(stream));
        fullText = resultText;
      }

      const elapsedMs = Math.round(performance.now() - startTime);
      const tokensPerSec = elapsedMs > 0 ? ((tokenCount / elapsedMs) * 1000).toFixed(1) : '0';

      self.postMessage({
        type: 'GENERATE_COMPLETE',
        text: fullText,
        tokenCount,
        elapsedMs,
        tokensPerSec,
        engine: 'Gemma 4 E2B (LiteRT-LM WebGPU On-Device)'
      });

    } catch (err) {
      console.error('[LiteRtWorker] Generation error:', err);
      self.postMessage({
        type: 'GENERATE_ERROR',
        error: `Inference failed: ${err.message}`
      });
    }
  }

  // 4. RESET CONVERSATION
  if (type === 'RESET_CONVERSATION') {
    if (engine) {
      try {
        conversation = await engine.createConversation({
          preface: {
            messages: [{ role: 'system', content: payload.systemPrompt || 'You are Geo, an on-device agronomic assistant.' }]
          }
        });
        self.postMessage({ type: 'STATUS', status: 'CONVERSATION_RESET' });
      } catch (e) {
        self.postMessage({ type: 'STATUS', status: 'ERROR', error: e.message });
      }
    }
  }
};
