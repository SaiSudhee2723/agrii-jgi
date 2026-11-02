/**
 * Geosense Frontend Controller
 * Integrates all 7 software modules into the existing UI without altering styles, animations, or DOM layout.
 * Connects directly to FastAPI backend on http://127.0.0.1:8001/api/v1
 */

(function () {
  'use strict';

  let currentCapturedBlob = null;
  let activeTab = 'soil';

  const Geosense = {
    init() {
      console.log('🌱 Geosense Smart Agriculture System Initializing...');
      this.injectStyles();
      this.buildModalDOM();
      this.bindExistingTriggers();
      this.loadInitialData();
    },

    injectStyles() {
      if (!document.getElementById('geosense-css')) {
        const link = document.createElement('link');
        link.id = 'geosense-css';
        link.rel = 'stylesheet';
        link.href = 'js/geosense.css';
        document.head.appendChild(link);
      }
    },

    bindExistingTriggers() {
      // 1. Wire navbar Login button
      const loginLinks = document.querySelectorAll('.login, [href*="login"]');
      loginLinks.forEach((el) => {
        el.addEventListener('click', (e) => {
          e.preventDefault();
          this.openAuthModal();
        });
      });

      // 2. Wire "Get a demo" buttons to open the Geosense Hub
      const ctaButtons = document.querySelectorAll('.navcta a, .hero .btn.lg, a.btn');
      ctaButtons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          this.openHubModal('soil');
        });
      });

      // 3. Wire navigation links (Platform -> Crop, Solutions -> Irrigation, Resources -> Weather)
      const navLinks = document.querySelectorAll('.nav-links a');
      navLinks.forEach((link) => {
        const text = link.textContent.trim().toLowerCase();
        link.addEventListener('click', (e) => {
          e.preventDefault();
          if (text === 'platform') this.openHubModal('soil');
          else if (text === 'solutions') this.openHubModal('crop');
          else if (text === 'security') this.openHubModal('irrigation');
          else if (text === 'resources') this.openHubModal('weather');
          else this.openHubModal('market');
        });
      });
    },

    buildModalDOM() {
      if (document.getElementById('geosense-hub-overlay')) return;

      const overlay = document.createElement('div');
      overlay.id = 'geosense-hub-overlay';
      overlay.className = 'geosense-overlay';
      overlay.innerHTML = `
        <div class="geosense-modal" role="dialog" aria-modal="true">
          <!-- Header -->
          <div class="geosense-modal-header">
            <div class="geosense-modal-title">
              <span>🌾 Geosense Intelligent System</span>
              <span class="badge"><span class="dot-ind"></span> Live Backend Connected</span>
            </div>
            <button class="geosense-close-btn" id="geosense-modal-close" aria-label="Close">&times;</button>
          </div>

          <!-- Tabs -->
          <div class="geosense-tabs">
            <button class="geosense-tab-btn active" data-tab="soil">1. Soil AI Analysis</button>
            <button class="geosense-tab-btn" data-tab="crop">2. Crop Recommendation</button>
            <button class="geosense-tab-btn" data-tab="irrigation">3. Smart Irrigation</button>
            <button class="geosense-tab-btn" data-tab="weather">4. Weather Intelligence</button>
            <button class="geosense-tab-btn" data-tab="market">5. Mandi Market</button>
            <button class="geosense-tab-btn" data-tab="community">6. Community</button>
            <button class="geosense-tab-btn" data-tab="auth">7. Account & Profile</button>
          </div>

          <!-- Body -->
          <div class="geosense-modal-body">
            <!-- 1. SOIL ANALYSIS TAB -->
            <div class="geosense-tab-pane active" id="pane-soil">
              <h3 style="margin-bottom: 8px; font-size: 1.2rem;">AI-Assisted Soil Physical & Quality Analysis</h3>
              <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">
                Capture soil using your device camera or upload from gallery. The computer-vision pipeline validates blur, glare, lighting, and observable physical characteristics.
              </p>

              <div class="soil-capture-container">
                <video id="soil-video" class="soil-video-preview" autoplay playsinline muted></video>
                <img id="soil-preview" class="soil-image-preview" alt="Soil Preview" />

                <div id="soil-placeholder">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="13" r="4"></circle>
                  </svg>
                  <div style="font-weight: 500; color: #475569;">No soil image selected</div>
                  <small style="color: #94a3b8;">Use your camera or choose a file</small>
                </div>

                <input type="file" id="soil-file-input" accept="image/jpeg,image/png,image/webp" style="display: none;" />
              </div>

              <div class="soil-capture-controls">
                <button type="button" class="geosense-btn-secondary" id="btn-camera-start">
                  📷 Open Camera
                </button>
                <button type="button" class="geosense-btn-secondary" id="btn-camera-snap" style="display: none;">
                  ⚡ Capture Photo
                </button>
                <button type="button" class="geosense-btn-secondary" id="btn-upload-file">
                  📁 Upload Photo
                </button>
                <button type="button" class="geosense-btn-secondary" id="btn-retake" style="display: none;">
                  🔄 Retake / Reset
                </button>
                <button type="button" class="geosense-btn-primary" id="btn-analyze-soil" disabled>
                  <span class="btn-dot"></span> Run AI Quality & Analysis
                </button>
              </div>

              <div id="soil-result-container"></div>
            </div>

            <!-- 2. CROP RECOMMENDATION TAB -->
            <div class="geosense-tab-pane" id="pane-crop">
              <h3 style="margin-bottom: 8px; font-size: 1.2rem;">Machine Learning Crop Recommendation</h3>
              <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">
                Trained Random Forest algorithm predicting optimum crops based on soil nutrients and climatic parameters.
              </p>

              <form id="geosense-crop-form">
                <div class="geosense-grid">
                  <div class="geosense-field">
                    <label>Nitrogen (N) [kg/ha]</label>
                    <input type="number" name="nitrogen" value="85" min="0" max="300" required />
                  </div>
                  <div class="geosense-field">
                    <label>Phosphorus (P) [kg/ha]</label>
                    <input type="number" name="phosphorus" value="45" min="0" max="300" required />
                  </div>
                  <div class="geosense-field">
                    <label>Potassium (K) [kg/ha]</label>
                    <input type="number" name="potassium" value="42" min="0" max="300" required />
                  </div>
                  <div class="geosense-field">
                    <label>Soil pH (0 - 14)</label>
                    <input type="number" name="ph" step="0.1" value="6.5" min="0" max="14" required />
                  </div>
                  <div class="geosense-field">
                    <label>Temperature (°C)</label>
                    <input type="number" name="temperature" step="0.1" value="26.0" required />
                  </div>
                  <div class="geosense-field">
                    <label>Relative Humidity (%)</label>
                    <input type="number" name="humidity" step="0.1" value="78" min="0" max="100" required />
                  </div>
                  <div class="geosense-field">
                    <label>Annual Rainfall (mm)</label>
                    <input type="number" name="rainfall" value="1150" min="0" max="2500" required />
                  </div>
                </div>

                <button type="submit" class="geosense-btn-primary">
                  <span class="btn-dot"></span> Get ML Recommendation
                </button>
              </form>

              <div id="crop-result-container"></div>
            </div>

            <!-- 3. SMART IRRIGATION TAB -->
            <div class="geosense-tab-pane" id="pane-irrigation">
              <h3 style="margin-bottom: 8px; font-size: 1.2rem;">Smart Irrigation Advisor</h3>
              <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">
                Software-based evapotranspiration (FAO-56) and soil moisture deficit calculation.
              </p>

              <form id="geosense-irrigation-form">
                <div class="geosense-grid">
                  <div class="geosense-field">
                    <label>Target Crop</label>
                    <select name="crop_name">
                      <option value="Wheat">Wheat</option>
                      <option value="Rice" selected>Rice</option>
                      <option value="Maize">Maize</option>
                      <option value="Cotton">Cotton</option>
                      <option value="Tomato">Tomato</option>
                      <option value="Sugarcane">Sugarcane</option>
                    </select>
                  </div>
                  <div class="geosense-field">
                    <label>Growth Stage</label>
                    <select name="growth_stage">
                      <option value="initial">Initial</option>
                      <option value="vegetative" selected>Vegetative</option>
                      <option value="flowering">Flowering</option>
                      <option value="yield_formation">Yield Formation</option>
                      <option value="ripening">Ripening</option>
                    </select>
                  </div>
                  <div class="geosense-field">
                    <label>Current Soil Moisture (%)</label>
                    <input type="number" name="soil_moisture" value="42" min="0" max="100" required />
                  </div>
                  <div class="geosense-field">
                    <label>Field Area (Acres)</label>
                    <input type="number" name="area_acres" step="0.1" value="2.0" min="0.1" required />
                  </div>
                  <div class="geosense-field">
                    <label>Rainfall Forecast (mm)</label>
                    <input type="number" name="forecast_rain" step="0.1" value="0.0" />
                  </div>
                </div>

                <button type="submit" class="geosense-btn-primary">
                  <span class="btn-dot"></span> Calculate Water Requirement
                </button>
              </form>

              <div id="irrigation-result-container"></div>
            </div>

            <!-- 4. WEATHER TAB -->
            <div class="geosense-tab-pane" id="pane-weather">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                  <h3 style="font-size: 1.2rem;">Live Agricultural Weather Intelligence</h3>
                  <p style="color: #64748b; font-size: 0.9rem;">Real-time weather parameters and agro-hazard warnings</p>
                </div>
                <button type="button" class="geosense-btn-secondary" id="btn-refresh-weather">🔄 Refresh</button>
              </div>
              <div id="weather-content-area">Loading live weather data...</div>
            </div>

            <!-- 5. MARKET TAB -->
            <div class="geosense-tab-pane" id="pane-market">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                  <h3 style="font-size: 1.2rem;">APMC Mandi Commodity Prices & Trends</h3>
                  <p style="color: #64748b; font-size: 0.9rem;">Modal rates, minimum/maximum values and 7-day trajectories</p>
                </div>
                <div style="display: flex; gap: 8px;">
                  <select id="market-commodity-select" style="padding: 6px 12px; border-radius: 6px; border: 1px solid #cbd5e1;">
                    <option value="Wheat">Wheat</option>
                    <option value="Rice" selected>Rice</option>
                    <option value="Cotton">Cotton</option>
                    <option value="Maize">Maize</option>
                    <option value="Tomato">Tomato</option>
                    <option value="Chickpea">Chickpea</option>
                  </select>
                </div>
              </div>
              <div id="market-content-area">Loading market data...</div>
            </div>

            <!-- 6. COMMUNITY TAB -->
            <div class="geosense-tab-pane" id="pane-community">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                  <h3 style="font-size: 1.2rem;">Farmer Community & Knowledge Exchange</h3>
                  <p style="color: #64748b; font-size: 0.9rem;">Discuss practices, pest management, and regional insights</p>
                </div>
                <button type="button" class="geosense-btn-primary" id="btn-open-create-post">
                  <span class="btn-dot"></span> New Post
                </button>
              </div>
              <div id="community-create-box" style="display: none; padding: 16px; background: #f8fafc; border-radius: 10px; margin-bottom: 20px;">
                <input type="text" id="post-title-input" placeholder="Post title..." style="width: 100%; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; border: 1px solid #cbd5e1;" />
                <textarea id="post-content-input" placeholder="Share your experience or question..." rows="3" style="width: 100%; padding: 8px 12px; margin-bottom: 8px; border-radius: 6px; border: 1px solid #cbd5e1;"></textarea>
                <div style="display: flex; justify-content: flex-end; gap: 8px;">
                  <button type="button" class="geosense-btn-secondary" id="btn-cancel-post">Cancel</button>
                  <button type="button" class="geosense-btn-primary" id="btn-submit-post">Publish</button>
                </div>
              </div>
              <div id="community-posts-area">Loading discussions...</div>
            </div>

            <!-- 7. AUTH & PROFILE TAB -->
            <div class="geosense-tab-pane" id="pane-auth">
              <div id="auth-unlogged-view">
                <h3 style="margin-bottom: 8px; font-size: 1.2rem;">Farmer Sign In / Registration</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">
                  Access personalized soil history, farm profiles, and saved crop advisories via Supabase.
                </p>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                  <!-- Sign In -->
                  <form id="geosense-login-form" style="padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
                    <h4 style="margin-bottom: 14px; font-weight: 600;">Sign In</h4>
                    <div class="geosense-field" style="margin-bottom: 12px;">
                      <label>Email Address</label>
                      <input type="email" name="email" required placeholder="farmer@example.com" />
                    </div>
                    <div class="geosense-field" style="margin-bottom: 16px;">
                      <label>Password</label>
                      <input type="password" name="password" required />
                    </div>
                    <button type="submit" class="geosense-btn-primary" style="width: 100%;">
                      <span class="btn-dot"></span> Sign In
                    </button>
                  </form>

                  <!-- Register -->
                  <form id="geosense-register-form" style="padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
                    <h4 style="margin-bottom: 14px; font-weight: 600;">Create Account</h4>
                    <div class="geosense-field" style="margin-bottom: 10px;">
                      <label>Full Name</label>
                      <input type="text" name="full_name" required placeholder="Farmer Name" />
                    </div>
                    <div class="geosense-field" style="margin-bottom: 10px;">
                      <label>Email Address</label>
                      <input type="email" name="email" required placeholder="farmer@example.com" />
                    </div>
                    <div class="geosense-field" style="margin-bottom: 10px;">
                      <label>Password</label>
                      <input type="password" name="password" minlength="6" required />
                    </div>
                    <div class="geosense-field" style="margin-bottom: 16px;">
                      <label>Region / State</label>
                      <input type="text" name="region" placeholder="e.g. Punjab, Maharashtra" />
                    </div>
                    <button type="submit" class="geosense-btn-secondary" style="width: 100%;">
                      Register Farmer Profile
                    </button>
                  </form>
                </div>
              </div>

              <!-- Logged In Profile View -->
              <div id="auth-logged-view" style="display: none;">
                <div style="padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #f8fafc;">
                  <h3 id="profile-name" style="font-size: 1.3rem; margin-bottom: 6px;">Farmer Profile</h3>
                  <div id="profile-email" style="color: #64748b; margin-bottom: 16px;">email@domain.com</div>
                  <div style="display: flex; gap: 12px;">
                    <span class="badge" id="profile-role" style="padding: 4px 10px; background: #e0e7ff; color: #4338ca; border-radius: 20px; font-size: 0.85rem;">Farmer</span>
                    <span class="badge" id="profile-region" style="padding: 4px 10px; background: #e2e8f0; border-radius: 20px; font-size: 0.85rem;">Region: Punjab</span>
                  </div>
                  <div style="margin-top: 24px;">
                    <button type="button" class="geosense-btn-secondary" id="btn-logout">Sign Out</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);

      // Wire close triggers
      document.getElementById('geosense-modal-close').addEventListener('click', () => this.closeModal());
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) this.closeModal();
      });

      // Wire tab buttons
      const tabBtns = overlay.querySelectorAll('.geosense-tab-btn');
      tabBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          tabBtns.forEach((b) => b.classList.remove('active'));
          overlay.querySelectorAll('.geosense-tab-pane').forEach((p) => p.classList.remove('active'));

          btn.classList.add('active');
          const tabId = btn.getAttribute('data-tab');
          document.getElementById(`pane-${tabId}`).classList.add('active');
          activeTab = tabId;

          if (tabId === 'weather') this.renderWeather();
          if (tabId === 'market') this.renderMarket();
          if (tabId === 'community') this.renderCommunity();
        });
      });

      this.bindSoilEvents();
      this.bindCropEvents();
      this.bindIrrigationEvents();
      this.bindAuthEvents();
    },

    openHubModal(tab = 'soil') {
      const overlay = document.getElementById('geosense-hub-overlay');
      if (!overlay) return;

      const targetTabBtn = overlay.querySelector(`.geosense-tab-btn[data-tab="${tab}"]`);
      if (targetTabBtn) targetTabBtn.click();

      overlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    },

    openAuthModal() {
      this.openHubModal('auth');
    },

    closeModal() {
      const overlay = document.getElementById('geosense-hub-overlay');
      if (overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
      }
      if (window.GeosenseCamera) {
        window.GeosenseCamera.stopCamera();
      }
    },

    // ------------------------------------------------------------------------
    // MODULE 1: SOIL ANALYSIS
    // ------------------------------------------------------------------------
    bindSoilEvents() {
      const video = document.getElementById('soil-video');
      const preview = document.getElementById('soil-preview');
      const placeholder = document.getElementById('soil-placeholder');
      const fileInput = document.getElementById('soil-file-input');
      const btnCameraStart = document.getElementById('btn-camera-start');
      const btnCameraSnap = document.getElementById('btn-camera-snap');
      const btnUpload = document.getElementById('btn-upload-file');
      const btnRetake = document.getElementById('btn-retake');
      const btnAnalyze = document.getElementById('btn-analyze-soil');

      btnCameraStart.addEventListener('click', async () => {
        try {
          placeholder.style.display = 'none';
          preview.style.display = 'none';
          video.style.display = 'block';
          btnCameraStart.style.display = 'none';
          btnUpload.style.display = 'none';
          btnCameraSnap.style.display = 'inline-flex';
          btnRetake.style.display = 'inline-flex';

          await window.GeosenseCamera.startCamera(video);
        } catch (err) {
          alert(`Camera access failed: ${err.message}`);
          btnRetake.click();
        }
      });

      btnCameraSnap.addEventListener('click', async () => {
        try {
          const blob = await window.GeosenseCamera.captureSnapshot();
          currentCapturedBlob = blob;
          window.GeosenseCamera.stopCamera();

          video.style.display = 'none';
          btnCameraSnap.style.display = 'none';

          preview.src = URL.createObjectURL(blob);
          preview.style.display = 'block';
          btnAnalyze.disabled = false;
        } catch (err) {
          alert(`Snapshot capture error: ${err.message}`);
        }
      });

      btnUpload.addEventListener('click', () => fileInput.click());

      fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        currentCapturedBlob = file;
        placeholder.style.display = 'none';
        video.style.display = 'none';
        btnCameraStart.style.display = 'none';
        btnUpload.style.display = 'none';

        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
        btnRetake.style.display = 'inline-flex';
        btnAnalyze.disabled = false;
      });

      btnRetake.addEventListener('click', () => {
        if (window.GeosenseCamera) window.GeosenseCamera.stopCamera();
        currentCapturedBlob = null;
        fileInput.value = '';

        video.style.display = 'none';
        preview.style.display = 'none';
        placeholder.style.display = 'block';

        btnCameraStart.style.display = 'inline-flex';
        btnUpload.style.display = 'inline-flex';
        btnCameraSnap.style.display = 'none';
        btnRetake.style.display = 'none';
        btnAnalyze.disabled = true;
        document.getElementById('soil-result-container').innerHTML = '';
      });

      btnAnalyze.addEventListener('click', async () => {
        if (!currentCapturedBlob) return;

        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<span class="btn-dot"></span> Processing OpenCV Pipeline...';

        try {
          const report = await window.GeosenseApi.analyzeSoilImage(currentCapturedBlob);
          this.renderSoilReport(report);
        } catch (err) {
          alert(`Soil Analysis Error: ${err.message}`);
        } finally {
          btnAnalyze.disabled = false;
          btnAnalyze.innerHTML = '<span class="btn-dot"></span> Run AI Quality & Analysis';
        }
      });
    },

    renderSoilReport(report) {
      const container = document.getElementById('soil-result-container');
      const isPass = report.quality_status === 'passed';

      container.innerHTML = `
        <div class="geosense-result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h4 style="font-size: 1.1rem; font-weight: 600;">Soil Assessment Diagnostics</h4>
            <span style="padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; background: ${isPass ? '#dcfce7' : '#fef3c7'}; color: ${isPass ? '#15803d' : '#b45309'};">
              Status: ${report.quality_status}
            </span>
          </div>

          <div class="geosense-grid" style="margin-bottom: 16px;">
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Image Blur Score</small>
              <div style="font-weight: 600; font-size: 1.1rem;">${report.quality_metrics.blur_score}</div>
              <small style="color: ${isPass ? '#15803d' : '#b45309'}; font-weight: 500;">${report.quality_metrics.blur_status}</small>
            </div>
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Lighting & Glare</small>
              <div style="font-weight: 600; font-size: 1.1rem;">${report.quality_metrics.lighting_status}</div>
              <small style="color: #64748b;">Glare ratio: ${report.quality_metrics.glare_ratio}%</small>
            </div>
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Observed Soil Texture</small>
              <div style="font-weight: 600; font-size: 1.1rem;">${report.color_analysis.estimated_soil_texture}</div>
              <small style="color: #64748b;">${report.color_analysis.color_description}</small>
            </div>
          </div>

          <div class="geosense-disclaimer-box">
            <strong>⚠️ Scientific Disclosure:</strong> ${report.scientific_disclaimer}
          </div>

          <div style="margin-bottom: 16px;">
            <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">Chemical NPK Status (Non-Fabricated)</h5>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center;">
              <div style="padding: 10px; border: 1px dashed #cbd5e1; border-radius: 8px;">
                <strong>Nitrogen (N)</strong><br><span style="color: #64748b; font-size: 0.85rem;">Laboratory Assay Required</span>
              </div>
              <div style="padding: 10px; border: 1px dashed #cbd5e1; border-radius: 8px;">
                <strong>Phosphorus (P)</strong><br><span style="color: #64748b; font-size: 0.85rem;">Laboratory Assay Required</span>
              </div>
              <div style="padding: 10px; border: 1px dashed #cbd5e1; border-radius: 8px;">
                <strong>Potassium (K)</strong><br><span style="color: #64748b; font-size: 0.85rem;">Laboratory Assay Required</span>
              </div>
            </div>
          </div>

          <div>
            <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">Agronomic Guidance:</h5>
            <ul style="padding-left: 20px; font-size: 0.9rem; color: #334155;">
              ${report.recommendations.map((r) => `<li style="margin-bottom: 6px;">${r}</li>`).join('')}
            </ul>
          </div>
        </div>
      `;
    },

    // ------------------------------------------------------------------------
    // MODULE 2: CROP RECOMMENDATION
    // ------------------------------------------------------------------------
    bindCropEvents() {
      const form = document.getElementById('geosense-crop-form');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const payload = {
          nitrogen: parseFloat(fd.get('nitrogen')),
          phosphorus: parseFloat(fd.get('phosphorus')),
          potassium: parseFloat(fd.get('potassium')),
          temperature: parseFloat(fd.get('temperature')),
          humidity: parseFloat(fd.get('humidity')),
          ph: parseFloat(fd.get('ph')),
          rainfall: parseFloat(fd.get('rainfall'))
        };

        try {
          const res = await window.GeosenseApi.getCropRecommendation(payload);
          this.renderCropResults(res);
        } catch (err) {
          alert(`Crop recommendation failed: ${err.message}`);
        }
      });
    },

    renderCropResults(res) {
      const container = document.getElementById('crop-result-container');
      container.innerHTML = `
        <div class="geosense-result-card">
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
            <div>
              <small style="color: #64748b; text-transform: uppercase; font-weight: 600;">Primary Recommended Crop</small>
              <h3 style="font-size: 1.8rem; font-weight: 700; color: var(--ink, #0b1d3a);">${res.primary_crop}</h3>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 1.4rem; font-weight: 700; color: #15803d;">${(res.confidence_score * 100).toFixed(1)}%</span>
              <br><small style="color: #64748b;">Confidence Match</small>
            </div>
          </div>

          <div style="padding: 12px 16px; background: #f8fafc; border-radius: 8px; margin-bottom: 16px; font-size: 0.9rem;">
            <strong>Optimum Growing Conditions:</strong> ${res.growing_conditions.ideal_temp_range} • ${res.growing_conditions.water_requirement} • pH ${res.growing_conditions.soil_ph_preference}
          </div>

          <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">Tailored Package of Practices:</h5>
          <ul style="padding-left: 20px; font-size: 0.9rem; color: #334155; margin-bottom: 16px;">
            ${res.farming_recommendations.map((a) => `<li style="margin-bottom: 4px;">${a}</li>`).join('')}
          </ul>

          <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">Viable Alternative Crops:</h5>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            ${res.alternative_crops.map((alt) => `
              <span style="padding: 6px 14px; background: #e2e8f0; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                ${alt.crop} (${(alt.confidence * 100).toFixed(0)}%)
              </span>
            `).join('')}
          </div>
        </div>
      `;
    },

    // ------------------------------------------------------------------------
    // MODULE 3: SMART IRRIGATION
    // ------------------------------------------------------------------------
    bindIrrigationEvents() {
      const form = document.getElementById('geosense-irrigation-form');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const payload = {
          crop_name: fd.get('crop_name'),
          growth_stage: fd.get('growth_stage'),
          soil_moisture_percentage: parseFloat(fd.get('soil_moisture')),
          field_area_acres: parseFloat(fd.get('area_acres')),
          forecast_rainfall_mm: parseFloat(fd.get('forecast_rain') || 0.0)
        };

        try {
          const res = await window.GeosenseApi.calculateIrrigation(payload);
          this.renderIrrigationResults(res);
        } catch (err) {
          alert(`Irrigation calculation failed: ${err.message}`);
        }
      });
    },

    renderIrrigationResults(res) {
      const container = document.getElementById('irrigation-result-container');
      const needed = res.irrigation_needed;

      container.innerHTML = `
        <div class="geosense-result-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
              <h4 style="font-size: 1.2rem; font-weight: 600;">${res.crop_name} (${res.growth_stage} stage)</h4>
              <small style="color: #64748b;">Soil Moisture Status: <strong>${res.soil_moisture_status}</strong></small>
            </div>
            <span style="padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; background: ${needed ? '#fee2e2' : '#dcfce7'}; color: ${needed ? '#b91c1c' : '#15803d'};">
              ${needed ? 'Irrigation Needed' : 'No Irrigation Needed'}
            </span>
          </div>

          <div class="geosense-grid" style="margin-bottom: 16px;">
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Water Depth / Acre</small>
              <div style="font-size: 1.2rem; font-weight: 700;">${(res.water_required_liters_per_acre / 4046.86).toFixed(1)} mm</div>
              <small style="color: #64748b;">${res.water_required_liters_per_acre.toLocaleString()} L / acre</small>
            </div>
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Total Water Requirement</small>
              <div style="font-size: 1.2rem; font-weight: 700; color: #1d4ed8;">${res.total_water_liters.toLocaleString()} Liters</div>
              <small style="color: #64748b;">For your total acreage</small>
            </div>
            <div style="padding: 12px; background: #f8fafc; border-radius: 8px;">
              <small style="color: #64748b;">Evapotranspiration Rate</small>
              <div style="font-size: 1.2rem; font-weight: 700;">${res.evapotranspiration_rate_mm_day} mm/day</div>
              <small style="color: #64748b;">Crop ET (FAO-56)</small>
            </div>
          </div>

          <div style="padding: 14px 18px; background: #f1f5f9; border-left: 4px solid var(--accent, #5b7cf0); border-radius: 6px; margin-bottom: 16px;">
            <strong>Scheduling Advisory:</strong> ${res.schedule_recommendation}
          </div>

          <div>
            <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;">Water Conservation Recommendations:</h5>
            <ul style="padding-left: 20px; font-size: 0.9rem; color: #334155;">
              ${res.water_saving_tips.map((tip) => `<li style="margin-bottom: 4px;">${tip}</li>`).join('')}
            </ul>
          </div>
        </div>
      `;
    },

    // ------------------------------------------------------------------------
    // MODULE 4: WEATHER INTELLIGENCE
    // ------------------------------------------------------------------------
    async renderWeather() {
      const container = document.getElementById('weather-content-area');
      container.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">Fetching Open-Meteo agro-meteorology data...</div>';

      try {
        const data = await window.GeosenseApi.getWeather();
        container.innerHTML = `
          <div style="padding: 20px; background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
              <div>
                <span style="font-size: 0.85rem; color: #64748b; text-transform: uppercase;">Location: ${data.location_name}</span>
                <div style="font-size: 2.5rem; font-weight: 700; color: var(--ink, #0b1d3a);">${data.current.temperature}°C</div>
                <div style="font-size: 1rem; font-weight: 500; color: #475569;">${data.current.weather_condition}</div>
              </div>
              <div style="text-align: right; font-size: 0.9rem; color: #475569; line-height: 1.6;">
                <div>💧 Relative Humidity: <strong>${data.current.humidity}%</strong></div>
                <div>💨 Wind Speed: <strong>${data.current.wind_speed} km/h</strong></div>
                <div>🌧️ Precipitation: <strong>${data.current.precipitation_mm} mm</strong></div>
              </div>
            </div>

            ${data.alerts.length > 0 ? `
              <div style="margin-top: 16px; padding: 12px 16px; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 6px;">
                <strong>${data.alerts[0].title}:</strong> ${data.alerts[0].advisory_action}
              </div>
            ` : ''}
          </div>

          <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 10px;">7-Day Agricultural Forecast</h5>
          <div class="weather-forecast-strip">
            ${data.forecast.map((d) => `
              <div class="weather-day-card">
                <div style="font-size: 0.8rem; font-weight: 600; color: #64748b;">${d.date.slice(5)}</div>
                <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">${d.temp_max}°</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">${d.temp_min}°</div>
                <div style="font-size: 0.75rem; color: #3b82f6; margin-top: 4px;">${d.precipitation_probability}% rain</div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (err) {
        container.innerHTML = `<div style="padding: 16px; color: #b91c1c;">Weather error: ${err.message}</div>`;
      }

      document.getElementById('btn-refresh-weather').onclick = () => this.renderWeather();
    },

    // ------------------------------------------------------------------------
    // MODULE 5: MARKET INTELLIGENCE
    // ------------------------------------------------------------------------
    async renderMarket() {
      const select = document.getElementById('market-commodity-select');
      const container = document.getElementById('market-content-area');
      const commodity = select.value;

      container.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">Loading commodity mandi rates...</div>';

      try {
        const analysis = await window.GeosenseApi.getCommodityAnalysis(commodity);
        container.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 16px; padding: 16px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div>
              <span style="font-size: 0.85rem; color: #64748b; text-transform: uppercase;">Average Modal Price</span>
              <div style="font-size: 1.8rem; font-weight: 700; color: var(--ink, #0b1d3a);">
                ₹${analysis.current_modal_price.toLocaleString()} <span style="font-size: 0.9rem; font-weight: 400; color: #64748b;">/ Quintal</span>
              </div>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 1.1rem; font-weight: 600; color: ${analysis.weekly_change_pct >= 0 ? '#15803d' : '#b91c1c'};">
                ${analysis.weekly_change_pct >= 0 ? '+' : ''}${analysis.weekly_change_pct}% this week
              </span>
              <br><small style="color: #64748b;">${analysis.is_live ? '🟢 Live Mandi' : 'ℹ️ Benchmark Reference'}</small>
            </div>
          </div>

          <h5 style="font-size: 0.95rem; font-weight: 600; margin-bottom: 10px;">Regional Mandi Rates</h5>
          <table class="market-table">
            <thead>
              <tr>
                <th>Mandi Market</th>
                <th>District / State</th>
                <th>Min (₹)</th>
                <th>Modal (₹)</th>
                <th>Max (₹)</th>
              </tr>
            </thead>
            <tbody>
              ${analysis.records.map((r) => `
                <tr>
                  <td><strong>${r.mandi_name}</strong><br><small style="color: #64748b;">${r.variety}</small></td>
                  <td>${r.district}, ${r.state}</td>
                  <td>₹${r.min_price}</td>
                  <td><strong style="color: #1d4ed8;">₹${r.modal_price}</strong></td>
                  <td>₹${r.max_price}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      } catch (err) {
        container.innerHTML = `<div style="padding: 16px; color: #b91c1c;">Market error: ${err.message}</div>`;
      }

      select.onchange = () => this.renderMarket();
    },

    // ------------------------------------------------------------------------
    // MODULE 6: COMMUNITY
    // ------------------------------------------------------------------------
    async renderCommunity() {
      const container = document.getElementById('community-posts-area');
      container.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">Loading farmer community posts...</div>';

      try {
        const posts = await window.GeosenseApi.getCommunityPosts();
        container.innerHTML = posts.map((p) => `
          <div class="community-post-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <div style="font-weight: 600; color: var(--ink, #0b1d3a);">${p.author_name}</div>
              <span style="font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; background: #e0e7ff; color: #4338ca;">${p.category}</span>
            </div>
            <h4 style="font-size: 1.05rem; font-weight: 600; margin-bottom: 6px;">${p.title}</h4>
            <p style="font-size: 0.9rem; color: #334155; line-height: 1.5; margin-bottom: 12px;">${p.content}</p>
            <div style="display: flex; gap: 16px; font-size: 0.85rem; color: #64748b;">
              <button type="button" class="btn-like-post" data-id="${p.id}" style="background: none; border: none; cursor: pointer; color: inherit; font-size: inherit;">
                ❤️ <span>${p.likes_count}</span> Likes
              </button>
              <span>💬 ${p.comments_count} Comments</span>
            </div>
          </div>
        `).join('');

        // Wire like buttons
        container.querySelectorAll('.btn-like-post').forEach((btn) => {
          btn.addEventListener('click', async () => {
            const id = btn.getAttribute('data-id');
            try {
              const res = await window.GeosenseApi.togglePostLike(id);
              btn.querySelector('span').textContent = res.likes_count;
            } catch (err) {
              alert('Sign in to like community posts.');
            }
          });
        });
      } catch (err) {
        container.innerHTML = `<div style="padding: 16px; color: #b91c1c;">Community error: ${err.message}</div>`;
      }

      // Wire create post toggle
      const btnOpenCreate = document.getElementById('btn-open-create-post');
      const createBox = document.getElementById('community-create-box');
      const btnCancelPost = document.getElementById('btn-cancel-post');
      const btnSubmitPost = document.getElementById('btn-submit-post');

      btnOpenCreate.onclick = () => { createBox.style.display = 'block'; };
      btnCancelPost.onclick = () => { createBox.style.display = 'none'; };
      btnSubmitPost.onclick = async () => {
        const title = document.getElementById('post-title-input').value.trim();
        const content = document.getElementById('post-content-input').value.trim();
        if (!title || !content) return alert('Please enter both title and content.');

        try {
          await window.GeosenseApi.createCommunityPost({ title, content, category: 'general' });
          createBox.style.display = 'none';
          document.getElementById('post-title-input').value = '';
          document.getElementById('post-content-input').value = '';
          this.renderCommunity();
        } catch (err) {
          alert(`Post submission error: ${err.message}`);
        }
      };
    },

    // ------------------------------------------------------------------------
    // MODULE 7: AUTH & PROFILES
    // ------------------------------------------------------------------------
    bindAuthEvents() {
      const loginForm = document.getElementById('geosense-login-form');
      const registerForm = document.getElementById('geosense-register-form');
      const btnLogout = document.getElementById('btn-logout');

      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(loginForm);
        try {
          const res = await window.GeosenseApi.loginUser(fd.get('email'), fd.get('password'));
          alert('Signed in successfully!');
          this.updateAuthView();
        } catch (err) {
          alert(`Login error: ${err.message}`);
        }
      });

      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(registerForm);
        try {
          await window.GeosenseApi.registerUser({
            full_name: fd.get('full_name'),
            email: fd.get('email'),
            password: fd.get('password'),
            region: fd.get('region')
          });
          alert('Account created! Please sign in with your email and password.');
        } catch (err) {
          alert(`Registration error: ${err.message}`);
        }
      });

      btnLogout.addEventListener('click', () => {
        window.GeosenseApi.clearSession();
        this.updateAuthView();
      });

      this.updateAuthView();
    },

    updateAuthView() {
      const user = window.GeosenseApi.getUser();
      const token = window.GeosenseApi.getToken();
      const unloggedView = document.getElementById('auth-unlogged-view');
      const loggedView = document.getElementById('auth-logged-view');

      if (token) {
        unloggedView.style.display = 'none';
        loggedView.style.display = 'block';
        document.getElementById('profile-name').textContent = user?.user_metadata?.full_name || user?.full_name || 'Farmer Member';
        document.getElementById('profile-email').textContent = user?.email || '';
      } else {
        unloggedView.style.display = 'block';
        loggedView.style.display = 'none';
      }
    },

    loadInitialData() {
      // Pre-warm weather data
    }
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Geosense.init());
  } else {
    Geosense.init();
  }

  window.Geosense = Geosense;
})();
