# Geosense Smart Agriculture Intelligent System (agrii-jgi)

**Geosense** is an AI-powered smart agriculture software platform providing intelligent soil analysis, machine-learning crop recommendations, weather-adjusted irrigation scheduling, agro-meteorological forecasting, mandi commodity market intelligence, farmer community collaboration, and an AI agronomic assistant.

---

## Two Distinct Application Experiences

Geosense is built with complete architectural separation between the **Public Marketing Experience** and the **Private Authenticated Dashboard**:

```text
Visitor Flow:
[ Public Homepage (/) ] 
       │
       ▼ (Clicks "Login" or "Get Started")
[ Authentication (/login | /register) ] 
       │
       ▼ (Supabase / FastAPI Auth Success)
[ Private SaaS Dashboard (/dashboard) ] 
       │
       ▼ (Clicks "Sign Out")
[ Public Homepage (/) ]
```

---

## 1. Public Marketing Website (`/`)
- **Route**: `http://localhost:8080/`
- **Design System**: Halden-inspired bowl-glow sky-cyan canvas shader, animated pill navigation, and letter-by-letter scroll reveals.
- **Content**:
  - Hero section introducing **Geo**, the AI teammate for smart agriculture.
  - Agricultural trust metrics and certification badges (`AGROTECH`, `TerraCrop`, `BIOHARVEST`, `KISANAI`, etc.).
  - Pinned agronomist scroll statement.
  - Split showcase section with high-resolution aerial agricultural photography.
  - Core agricultural feature modules grid.
  - Tailored solutions for independent farmers, FPOs, and agronomists.
  - Scientific disclosure section regarding optical reflection vs. laboratory chemical assay.
  - Full company footer with navigation and legal disclosures.
  - Nav **Login** and **Get Started** buttons connecting directly to the authentication routes.

---

## 2. Authentication Pages (`/login`, `/register`, `/forgot-password`)
- **Login (`/login`)**:
  - Supabase Auth integration via FastAPI backend.
  - One-click instant demo login button for swift testing.
  - Form validation and error alerts.
  - Automatically redirects authenticated visitors to `/dashboard`.
- **Register (`/register`)**:
  - Collects Full Name, Email, Password, Farm Region/State, and Phone.
  - Creates account, sets session, and redirects to `/dashboard`.
- **Forgot Password (`/forgot-password`)**:
  - Dispatch password recovery link.

---

## 3. Private Agricultural Dashboard (`/dashboard`)
- **Route**: `http://localhost:8080/dashboard`
- **Auth Guard**: Unauthenticated users attempting to access `/dashboard` are immediately redirected to `/login`.
- **Sidebar Modules**:
  1. 📊 **Overview**: Quick stats (Soil Health Index, Active Crop, Next Irrigation Depth, Live Weather), field activity feed, and shortcut cards.
  2. 🧪 **Soil NPK Analysis**: Device rear-camera API stream (`navigator.mediaDevices.getUserMedia`) + gallery upload, snapshot preview, OpenCV quality check (blur score, glare, lighting), physical texture/hue diagnostics, and prominent scientific notice (chemical NPK requires accredited laboratory assay).
  3. 🌾 **Crop Recommendation**: Interactive inputs (N, P, K, pH, temperature, humidity, rainfall) powered by a trained Scikit-Learn Random Forest model returning primary crop, match score %, growing conditions, and farming advice.
  4. 💧 **Smart Irrigation**: Crop coefficient ($K_c$) and evapotranspiration calculations (FAO-56) based on growth stage, current moisture, and rainfall forecast, delivering exact liter requirements per acre.
  5. ⛅ **Weather Intelligence**: Live Open-Meteo telemetry (temp, humidity, wind, UV index), 7-day agricultural forecast strip, and automated agro-hazard alerts.
  6. 📈 **Mandi Market Prices**: APMC market prices across commodities (Wheat, Rice, Cotton, Maize, Tomato, Chickpea) with 7-day price trajectory, weekly percentage changes, and benchmark reference tags.
  7. 👥 **Farmer Community**: Discussion board, post publisher, comment threads, and like counters.
  8. 🤖 **AI Agro Assistant**: Hybrid assistant supporting both Cloud AI (Qwen3) and on-device Offline AI (Gemma 4 E2B via WebGPU / LiteRT-LM).
  9. 👤 **Farmer Profile & Sign Out**: Profile details with secure sign-out clearing session and returning to `/`.

---

## Running the Complete System

### 1. 1-Click Launch (Recommended)
Simply double click `start_servers.bat` in the root folder. Both FastAPI backend (port 8001) and Frontend server (port 8080) will be launched automatically.

### 2. Manual Start

**Backend:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
API Documentation: `http://127.0.0.1:8001/docs`

**Frontend:**
```powershell
powershell -ExecutionPolicy Bypass -File .\server.ps1
```
Open **`http://localhost:8080/`** in your browser.
