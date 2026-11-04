/**
 * Geosense Smart Agriculture - Farm Location Intelligence Map
 * Interactive Satellite GIS, Boundary Polygon Drawing, Geodesic Acreage Calculation,
 * Supabase Persistence, and Micro-Climate Weather Integration.
 */

(function () {
  'use strict';

  let map = null;
  let satelliteLayer = null;
  let streetLayer = null;
  let farmMarker = null;
  let boundaryPolygon = null;
  let drawingPoints = [];
  let isDrawingMode = false;
  let tempPolyline = null;
  let activeFarmId = null;
  let currentCoordinates = { lat: 12.9753, lng: 77.5910 };
  let currentAreaAcres = 0.0;
  let savedFarmsCache = [];

  // Custom Agricultural Marker Icon
  const FarmPinIcon = L.divIcon({
    className: 'custom-farm-pin',
    html: `
      <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;">
        <div style="position: absolute; width: 34px; height: 34px; border-radius: 50%; background: radial-gradient(circle, rgba(47, 224, 208, 0.4) 0%, transparent 70%); animation: pulse 2s infinite;"></div>
        <div style="width: 28px; height: 28px; background: #0b1d3a; border: 2.5px solid #2fe0d0; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
          <span style="transform: rotate(45deg); font-size: 13px;">🌾</span>
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 32],
    popupAnchor: [0, -28]
  });

  // Geodesic Area Calculation (Spherical Excess)
  function calculatePolygonArea(latLngs) {
    if (!latLngs || latLngs.length < 3) return { acres: 0, hectares: 0 };
    const R = 6378137; // Earth radius in meters
    let area = 0;
    const len = latLngs.length;
    const rad = Math.PI / 180;

    for (let i = 0; i < len; i++) {
      const p1 = latLngs[i];
      const p2 = latLngs[(i + 1) % len];
      const lat1 = Array.isArray(p1) ? p1[0] : p1.lat;
      const lon1 = Array.isArray(p1) ? p1[1] : p1.lng;
      const lat2 = Array.isArray(p2) ? p2[0] : p2.lat;
      const lon2 = Array.isArray(p2) ? p2[1] : p2.lng;

      area += (lon2 - lon1) * rad * (2 + Math.sin(lat1 * rad) + Math.sin(lat2 * rad));
    }

    area = Math.abs((area * R * R) / 2.0); // m²
    const acres = area * 0.000247105;
    const hectares = area / 10000;
    return {
      acres: parseFloat(acres.toFixed(2)),
      hectares: parseFloat(hectares.toFixed(2))
    };
  }

  // Calculate Reference Evapotranspiration (ET0) using FAO-56 radiation proxy
  function estimateET0(temp, humidity, windSpeed = 8.0) {
    const t = Math.max(0, temp);
    const rh = Math.min(100, Math.max(10, humidity));
    // Simplified Hargreaves / FAO-56 daily approximation
    const et0 = 0.0023 * (t + 17.8) * Math.sqrt(Math.max(1, 30 - t * 0.3)) * (1.1 - rh / 150);
    return Math.max(1.2, parseFloat(et0.toFixed(2)));
  }

  // Initialize Map
  function initFarmMap() {
    const mapContainer = document.getElementById('farm-map-canvas');
    if (!mapContainer || map) return;

    // 1. Satellite Layer (DEFAULT: Esri World Imagery)
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    // 2. Street Layer (OpenStreetMap)
    streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    // Initialize Map with Satellite Layer as default
    map = L.map('farm-map-canvas', {
      center: [currentCoordinates.lat, currentCoordinates.lng],
      zoom: 14,
      layers: [satelliteLayer], // SATELLITE AS DEFAULT
      zoomControl: true,
      scrollWheelZoom: true
    });

    // Initial Marker
    setFarmMarker(currentCoordinates.lat, currentCoordinates.lng);

    // Map Click Handler
    map.on('click', handleMapClick);

    // Layer Switcher Buttons
    const btnSat = document.getElementById('btn-layer-satellite');
    const btnStreet = document.getElementById('btn-layer-street');

    if (btnSat && btnStreet) {
      btnSat.addEventListener('click', () => {
        if (!map.hasLayer(satelliteLayer)) {
          map.removeLayer(streetLayer);
          map.addLayer(satelliteLayer);
          btnSat.classList.add('active');
          btnSat.style.background = '#0b1d3a';
          btnSat.style.color = '#ffffff';
          btnStreet.classList.remove('active');
          btnStreet.style.background = 'transparent';
          btnStreet.style.color = '#475569';
        }
      });

      btnStreet.addEventListener('click', () => {
        if (!map.hasLayer(streetLayer)) {
          map.removeLayer(satelliteLayer);
          map.addLayer(streetLayer);
          btnStreet.classList.add('active');
          btnStreet.style.background = '#0b1d3a';
          btnStreet.style.color = '#ffffff';
          btnSat.classList.remove('active');
          btnSat.style.background = 'transparent';
          btnSat.style.color = '#475569';
        }
      });
    }

    // Boundary Drawing Buttons
    const btnDraw = document.getElementById('btn-draw-boundary');
    const btnClear = document.getElementById('btn-clear-boundary');

    if (btnDraw) {
      btnDraw.addEventListener('click', toggleDrawingMode);
    }

    if (btnClear) {
      btnClear.addEventListener('click', clearBoundary);
    }

    // Save Farm Modal Setup
    bindFarmModal();

    // Load initial weather for starting position
    updateWeatherTelemetry(currentCoordinates.lat, currentCoordinates.lng);

    // Load previously saved farms from Supabase
    loadSavedFarms();
  }

  // Set / Move Farm Marker
  function setFarmMarker(lat, lng) {
    currentCoordinates = { lat: parseFloat(lat.toFixed(5)), lng: parseFloat(lng.toFixed(5)) };

    if (!farmMarker) {
      farmMarker = L.marker([lat, lng], {
        icon: FarmPinIcon,
        draggable: true,
        autoPan: true
      }).addTo(map);

      farmMarker.on('dragend', (e) => {
        const pos = e.target.getLatLng();
        setFarmMarker(pos.lat, pos.lng);
        updateWeatherTelemetry(pos.lat, pos.lng);
      });
    } else {
      farmMarker.setLatLng([lat, lng]);
    }

    updateHudCoords(lat, lng);
  }

  // Handle Map Clicks
  function handleMapClick(e) {
    if (isDrawingMode) {
      // Add vertex to polygon boundary
      const pt = [parseFloat(e.latlng.lat.toFixed(5)), parseFloat(e.latlng.lng.toFixed(5))];
      drawingPoints.push(pt);
      renderTempDrawing();
    } else {
      // Normal click: drop marker & sync weather
      setFarmMarker(e.latlng.lat, e.latlng.lng);
      updateWeatherTelemetry(e.latlng.lat, e.latlng.lng);
    }
  }

  // Toggle Boundary Drawing Mode
  function toggleDrawingMode() {
    const btn = document.getElementById('btn-draw-boundary');
    const hudStatus = document.getElementById('hud-status');

    if (!isDrawingMode) {
      isDrawingMode = true;
      drawingPoints = [];
      if (tempPolyline) map.removeLayer(tempPolyline);
      if (boundaryPolygon) map.removeLayer(boundaryPolygon);
      boundaryPolygon = null;

      if (btn) {
        btn.style.background = '#22c55e';
        btn.style.borderColor = '#16a34a';
        btn.style.color = '#ffffff';
        btn.innerHTML = '<span>✅ Finish Boundary (Click)</span>';
      }
      if (hudStatus) hudStatus.textContent = 'Click map corners to draw';
      map.getContainer().style.cursor = 'crosshair';
    } else {
      // Finalize Polygon
      isDrawingMode = false;
      map.getContainer().style.cursor = '';

      if (btn) {
        btn.style.background = '#eff6ff';
        btn.style.borderColor = '#bfdbfe';
        btn.style.color = '#1d4ed8';
        btn.innerHTML = '<span>✏️ Draw Boundary</span>';
      }
      if (hudStatus) hudStatus.textContent = 'Plot boundary set';

      if (tempPolyline) {
        map.removeLayer(tempPolyline);
        tempPolyline = null;
      }

      if (drawingPoints.length >= 3) {
        createFinalPolygon(drawingPoints);
      } else {
        alert('Please click at least 3 points on the map to define a farm boundary.');
        clearBoundary();
      }
    }
  }

  // Render Intermediate Lines while Drawing
  function renderTempDrawing() {
    if (tempPolyline) map.removeLayer(tempPolyline);
    tempPolyline = L.polyline(drawingPoints, {
      color: '#2fe0d0',
      weight: 3,
      dashArray: '5, 8'
    }).addTo(map);

    const hudArea = document.getElementById('hud-area');
    if (drawingPoints.length >= 3) {
      const calc = calculatePolygonArea(drawingPoints);
      currentAreaAcres = calc.acres;
      if (hudArea) hudArea.textContent = `${calc.acres} Acres (${calc.hectares} Ha)`;
    } else if (hudArea) {
      hudArea.textContent = `${drawingPoints.length} points set...`;
    }
  }

  // Create Finalized Boundary Polygon
  function createFinalPolygon(pts) {
    if (boundaryPolygon) map.removeLayer(boundaryPolygon);

    boundaryPolygon = L.polygon(pts, {
      color: '#2fe0d0',
      weight: 2.5,
      fillColor: '#2fe0d0',
      fillOpacity: 0.28,
      dashArray: '4, 4'
    }).addTo(map);

    const calc = calculatePolygonArea(pts);
    currentAreaAcres = calc.acres;

    boundaryPolygon.bindPopup(`
      <div style="font-family: inherit; font-size: 0.85rem; padding: 2px;">
        <strong style="color: #0b1d3a;">🌾 Farm Boundary Plot</strong><br>
        <strong>Area:</strong> ${calc.acres} Acres (${calc.hectares} Hectares)<br>
        <span style="font-size: 0.78rem; color: #64748b;">${pts.length} boundary vertices</span>
      </div>
    `);

    const hudArea = document.getElementById('hud-area');
    if (hudArea) hudArea.textContent = `${calc.acres} Acres (${calc.hectares} Ha)`;

    // Auto center farm marker in the centroid
    const bounds = boundaryPolygon.getBounds();
    const center = bounds.getCenter();
    setFarmMarker(center.lat, center.lng);
  }

  // Clear Boundary
  function clearBoundary() {
    drawingPoints = [];
    isDrawingMode = false;
    map.getContainer().style.cursor = '';
    if (tempPolyline) {
      map.removeLayer(tempPolyline);
      tempPolyline = null;
    }
    if (boundaryPolygon) {
      map.removeLayer(boundaryPolygon);
      boundaryPolygon = null;
    }
    currentAreaAcres = 0.0;
    const hudArea = document.getElementById('hud-area');
    if (hudArea) hudArea.textContent = '0.00 Acres (0.00 Ha)';
    const btn = document.getElementById('btn-draw-boundary');
    if (btn) {
      btn.style.background = '#eff6ff';
      btn.style.borderColor = '#bfdbfe';
      btn.style.color = '#1d4ed8';
      btn.innerHTML = '<span>✏️ Draw Boundary</span>';
    }
  }

  // Update Coordinates in HUD
  function updateHudCoords(lat, lng) {
    const el = document.getElementById('hud-coords');
    if (el) el.textContent = `${lat.toFixed(4)}° N, ${lng.toFixed(4)}° E`;
  }

  // Fetch Micro-Climate Weather for Coordinates
  async function updateWeatherTelemetry(lat, lng) {
    const hudTemp = document.getElementById('hud-temp');
    const hudHumid = document.getElementById('hud-humidity');
    const hudRain = document.getElementById('hud-rain');
    const hudEt = document.getElementById('hud-et');
    const hudStatus = document.getElementById('hud-status');

    if (hudStatus) hudStatus.textContent = 'Syncing weather...';

    try {
      const data = await window.GeosenseApi.getWeather(lat, lng);
      if (data && data.current) {
        const c = data.current;
        if (hudTemp) hudTemp.textContent = `${Math.round(c.temperature)}°C`;
        if (hudHumid) hudHumid.textContent = `${c.humidity}% RH`;
        if (hudRain) hudRain.textContent = `${c.precipitation_mm || 0} mm`;
        const et0 = estimateET0(c.temperature, c.humidity, c.wind_speed);
        if (hudEt) hudEt.textContent = `${et0} mm ET₀`;
        if (hudStatus) hudStatus.textContent = data.location_name || 'Live telemetry linked';
      }
    } catch (err) {
      if (hudStatus) hudStatus.textContent = 'Weather linked (fallback)';
    }
  }

  // Bind Save / Edit Farm Modal
  function bindFarmModal() {
    const modal = document.getElementById('farm-modal');
    const openBtn = document.getElementById('btn-open-save-farm');
    const closeBtn = document.getElementById('btn-close-farm-modal');
    const cancelBtn = document.getElementById('btn-cancel-modal');
    const submitBtn = document.getElementById('btn-save-farm-submit');
    const drawerBtn = document.getElementById('btn-toggle-saved-farms');
    const closeDrawerBtn = document.getElementById('btn-close-saved-drawer');
    const drawer = document.getElementById('saved-farms-drawer');

    if (openBtn) {
      openBtn.addEventListener('click', () => {
        openFarmModal();
      });
    }

    if (closeBtn) closeBtn.addEventListener('click', () => { if (modal) modal.style.display = 'none'; });
    if (cancelBtn) cancelBtn.addEventListener('click', () => { if (modal) modal.style.display = 'none'; });

    if (submitBtn) {
      submitBtn.addEventListener('click', handleSaveFarmSubmit);
    }

    if (drawerBtn && drawer) {
      drawerBtn.addEventListener('click', () => {
        const isShown = drawer.style.display === 'block';
        drawer.style.display = isShown ? 'none' : 'block';
      });
    }

    if (closeDrawerBtn && drawer) {
      closeDrawerBtn.addEventListener('click', () => {
        drawer.style.display = 'none';
      });
    }
  }

  function openFarmModal(farmToEdit = null) {
    const modal = document.getElementById('farm-modal');
    const title = document.getElementById('farm-modal-title');
    const nameInput = document.getElementById('modal-farm-name');
    const cropSelect = document.getElementById('modal-crop-type');
    const latInput = document.getElementById('modal-lat');
    const lngInput = document.getElementById('modal-lng');
    const areaDisplay = document.getElementById('modal-area-display');
    const editIdInput = document.getElementById('farm-edit-id');

    if (!modal) return;

    if (farmToEdit) {
      if (title) title.textContent = 'Edit Farm Plot';
      if (editIdInput) editIdInput.value = farmToEdit.id;
      if (nameInput) nameInput.value = farmToEdit.farm_name;
      if (cropSelect) cropSelect.value = farmToEdit.crop_type || 'General Crop';
      if (latInput) latInput.value = farmToEdit.latitude;
      if (lngInput) lngInput.value = farmToEdit.longitude;
      if (areaDisplay) areaDisplay.textContent = `${farmToEdit.area_acres || 0} Acres`;
    } else {
      if (title) title.textContent = 'Save Farm Plot Location';
      if (editIdInput) editIdInput.value = '';
      if (nameInput) nameInput.value = '';
      if (cropSelect) cropSelect.value = 'Wheat';
      if (latInput) latInput.value = currentCoordinates.lat;
      if (lngInput) lngInput.value = currentCoordinates.lng;
      if (areaDisplay) areaDisplay.textContent = `${currentAreaAcres} Acres`;
    }

    modal.style.display = 'flex';
  }

  // Handle Save Farm Submit
  async function handleSaveFarmSubmit() {
    const nameInput = document.getElementById('modal-farm-name');
    const cropSelect = document.getElementById('modal-crop-type');
    const editIdInput = document.getElementById('farm-edit-id');
    const modal = document.getElementById('farm-modal');
    const submitBtn = document.getElementById('btn-save-farm-submit');

    const farmName = nameInput ? nameInput.value.trim() : '';
    if (!farmName) {
      alert('Please enter a farm or plot name.');
      return;
    }

    const cropType = cropSelect ? cropSelect.value : 'General Crop';
    const editId = editIdInput ? editIdInput.value : '';

    const payload = {
      farm_name: farmName,
      crop_type: cropType,
      latitude: currentCoordinates.lat,
      longitude: currentCoordinates.lng,
      boundary_coordinates: drawingPoints.length >= 3 ? drawingPoints : [],
      area_acres: currentAreaAcres
    };

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving to Supabase...';
    }

    try {
      if (editId) {
        await window.GeosenseApi.updateFarm(editId, payload);
      } else {
        await window.GeosenseApi.saveFarm(payload);
      }

      if (modal) modal.style.display = 'none';
      await loadSavedFarms();
      alert(`Farm "${farmName}" successfully saved with live satellite coordinates!`);
    } catch (err) {
      alert('Error saving farm: ' + (err.message || 'Please check your connection.'));
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save to Supabase';
      }
    }
  }

  // Load Saved Farms from Supabase / Backend
  async function loadSavedFarms() {
    const listEl = document.getElementById('saved-farms-list');
    const countEl = document.getElementById('saved-farms-count');

    try {
      const farms = await window.GeosenseApi.listFarms();
      savedFarmsCache = farms || [];
      if (countEl) countEl.textContent = savedFarmsCache.length;

      if (!listEl) return;

      if (savedFarmsCache.length === 0) {
        listEl.innerHTML = `
          <div style="grid-column: 1 / -1; padding: 14px; text-align: center; color: #64748b; font-size: 0.86rem; background: #ffffff; border-radius: 8px; border: 1px dashed #cbd5e1;">
            No saved farm plots found yet. Click anywhere on the satellite map or draw a boundary to save your first plot!
          </div>
        `;
        return;
      }

      listEl.innerHTML = savedFarmsCache.map(f => `
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
              <strong style="font-size: 0.92rem; color: #0b1d3a;">${escapeHtml(f.farm_name)}</strong>
              <span class="data-source-badge" style="font-size: 0.7rem; padding: 2px 6px;">${escapeHtml(f.crop_type || 'Crop')}</span>
            </div>
            <div style="font-size: 0.78rem; color: #64748b; margin-bottom: 6px;">
              📍 Lat ${f.latitude}, Lng ${f.longitude}<br>
              🌾 Size: <strong>${f.area_acres || 0} Acres</strong>
            </div>
          </div>
          <div style="display: flex; gap: 6px; margin-top: 8px; border-top: 1px solid #f1f5f9; padding-top: 8px;">
            <button type="button" onclick="window.FarmMap.flyToFarm('${f.id}')" style="flex: 1; padding: 5px 8px; font-size: 0.78rem; font-weight: 600; background: #0b1d3a; color: #ffffff; border: none; border-radius: 6px; cursor: pointer;">
              🗺️ View
            </button>
            <button type="button" onclick="window.FarmMap.editFarm('${f.id}')" style="padding: 5px 8px; font-size: 0.78rem; background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer;">
              ✏️
            </button>
            <button type="button" onclick="window.FarmMap.deleteFarm('${f.id}')" style="padding: 5px 8px; font-size: 0.78rem; background: #fff1f2; color: #e11d48; border: 1px solid #fecdd3; border-radius: 6px; cursor: pointer;">
              🗑️
            </button>
          </div>
        </div>
      `).join('');

      // If user has saved farms and no active polygon, auto-load the most recent farm!
      if (!activeFarmId && savedFarmsCache.length > 0) {
        flyToFarm(savedFarmsCache[0].id, false);
      }
    } catch (err) {
      if (listEl) {
        listEl.innerHTML = `<div style="color: #b91c1c; font-size: 0.84rem; padding: 8px;">Could not load saved farms: ${escapeHtml(err.message)}</div>`;
      }
    }
  }

  // Fly Map to Farm & Restore Polygon
  function flyToFarm(farmId, animate = true) {
    const farm = savedFarmsCache.find(f => f.id === farmId);
    if (!farm || !map) return;

    activeFarmId = farmId;
    currentCoordinates = { lat: farm.latitude, lng: farm.longitude };
    currentAreaAcres = farm.area_acres || 0.0;

    if (animate) {
      map.flyTo([farm.latitude, farm.longitude], 16, { duration: 1.2 });
    } else {
      map.setView([farm.latitude, farm.longitude], 15);
    }

    setFarmMarker(farm.latitude, farm.longitude);

    // Restore boundary polygon if present
    if (farm.boundary_coordinates && farm.boundary_coordinates.length >= 3) {
      drawingPoints = farm.boundary_coordinates;
      createFinalPolygon(farm.boundary_coordinates);
    } else {
      clearBoundary();
    }

    updateWeatherTelemetry(farm.latitude, farm.longitude);
  }

  // Delete Farm
  async function deleteFarm(farmId) {
    if (!confirm('Are you sure you want to delete this saved farm plot?')) return;
    try {
      await window.GeosenseApi.deleteFarm(farmId);
      if (activeFarmId === farmId) {
        activeFarmId = null;
        clearBoundary();
      }
      await loadSavedFarms();
    } catch (err) {
      alert('Error deleting farm: ' + (err.message || 'Please try again.'));
    }
  }

  // Edit Farm
  function editFarm(farmId) {
    const farm = savedFarmsCache.find(f => f.id === farmId);
    if (farm) {
      flyToFarm(farmId);
      openFarmModal(farm);
    }
  }

  // Helper Escape HTML
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Public Interface for Inline Button Calls & Event Listeners
  window.FarmMap = {
    init: initFarmMap,
    flyToFarm,
    editFarm,
    deleteFarm,
    setCoordinates: (lat, lng) => {
      if (map) {
        map.flyTo([lat, lng], 16);
        setFarmMarker(lat, lng);
        updateWeatherTelemetry(lat, lng);
      }
    }
  };

  // Auto-init when tab is opened or DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    // Check if on weather tab
    const weatherNav = document.querySelector('[data-target="weather"]');
    if (weatherNav) {
      weatherNav.addEventListener('click', () => {
        setTimeout(() => {
          if (!map) {
            initFarmMap();
          } else {
            map.invalidateSize();
          }
        }, 150);
      });
    }

    // In case user lands on weather directly
    const pane = document.getElementById('pane-weather');
    if (pane && pane.classList.contains('active')) {
      setTimeout(initFarmMap, 200);
    }
  });

})();
