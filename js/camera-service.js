/**
 * Geosense Camera Service
 * Handles mobile rear-camera capture, gallery upload, image preview, and retake functionality.
 */

class CameraService {
  constructor() {
    this.stream = null;
    this.videoElement = null;
    this.canvasElement = document.createElement('canvas');
  }

  /**
   * Check if getUserMedia is supported and in a secure context (HTTPS / localhost).
   */
  static isCameraSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }

  /**
   * Start rear/environment camera stream into provided HTML video element.
   */
  async startCamera(videoElement) {
    if (!CameraService.isCameraSupported()) {
      throw new Error('Camera access API is not supported in this browser. Please use gallery upload.');
    }

    this.videoElement = videoElement;
    this.stopCamera(); // Clean up previous stream if active

    try {
      const constraints = {
        video: {
          facingMode: { ideal: 'environment' },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.videoElement.srcObject = this.stream;
      await this.videoElement.play();
      return true;
    } catch (err) {
      console.warn('Environment camera failed, attempting standard camera fallback:', err);
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        this.videoElement.srcObject = this.stream;
        await this.videoElement.play();
        return true;
      } catch (fallbackErr) {
        throw new Error('Camera permission denied or camera not found. Please enable permissions or upload a photo.');
      }
    }
  }

  /**
   * Capture still snapshot from the running video stream.
   * Returns a Blob.
   */
  captureSnapshot() {
    if (!this.videoElement || !this.stream) {
      throw new Error('Camera is not active.');
    }

    const video = this.videoElement;
    const canvas = this.canvasElement;
    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return new Promise((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to capture frame from camera.'));
        }
      }, 'image/jpeg', 0.92);
    });
  }

  /**
   * Stop camera stream and free hardware resources.
   */
  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }
  }
}

// Expose globally
window.GeosenseCamera = new CameraService();

