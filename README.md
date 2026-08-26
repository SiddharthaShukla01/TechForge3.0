# 🚨 Uttarakhand Disaster Alert & Relief Management System
### उत्तराखंड आपदा चेतावनी एवं राहत प्रबंधन प्रणाली

A high-performance, real-time, bilingual (हिंदी / English) Emergency Command & Public Relief Portal designed for both **non-technical citizens** and **emergency response coordinators (SDRF / District Administration)** across all **13 districts of Uttarakhand**.

---

## 🌟 What's New in this Enhanced & User-Friendly Version

1. **🌐 Full Bilingual Support (हिंदी + English)**:
   - 1-click instant language switcher in the sidebar.
   - All navigation, instructions, form guides, alerts, badges, and metrics are completely translated into simple, everyday language.

2. **⛰️ Complete 13-District Uttarakhand Coverage**:
   - Expanded with rich realistic data covering **Dehradun, Haridwar, Tehri Garhwal, Chamoli, Uttarkashi, Rudraprayag, Pauri Garhwal, Pithoragarh, Bageshwar, Almora, Champawat, Nainital, and Udham Singh Nagar**.
   - Includes real hospitals (AIIMS Rishikesh, Doon Hospital, Sushila Tiwari Haldwani, etc.), district emergency shelters, relief stockpile depots, and active incident coordinates.

3. **👨‍👩‍👧 Designed for Non-Technical Users**:
   - **Emergency SOS Top Banner**: Direct 1-tap 24x7 phone helplines (`1070`, `112`, `1077`, `0135-2710334`).
   - **Simple 3-Step Reporting Guide**: No technical jargon—guided questions (What happened? Where? How urgent?).
   - **Visual Status Badges**: Clear color indicators (🟢 Space/Beds Available, 🟡 Moderate, 🔴 Full/Critical Danger).
   - **Live Interactive Hotspot Map**: Real-time visualization of incidents and relief hubs.

4. **⚡ Bug Fixes & Architectural Enhancements**:
   - Replaced all corrupted box glyphs (`■`) with clean emojis and custom styling.
   - Fixed Streamlit state loss on button clicks and eliminated unwanted full-page re-renders.
   - Thread-safe SQLite context manager with indexed queries for sub-millisecond lookups.
   - Idempotent seed data management.

---

## 📂 Project Architecture

```
disaster_management_system/
│
├── app.py              # Bilingual Streamlit portal with 5 interactive modules
├── database.py         # Thread-safe SQLite database layer & 13-district coordinate lookup
├── translations.py     # English & Hindi translation engine
├── sample_data.py      # Seed data generator across all 13 Uttarakhand districts
├── requirements.txt    # Application dependencies
└── README.md           # Documentation & user guide
```

---

## 🚀 How to Run the Application

### 1. Open Terminal or PowerShell
```powershell
cd C:\Users\siddh\.gemini\antigravity\scratch\disaster_management_system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the 13-District Database (Run Once)
```bash
python sample_data.py
```

### 4. Launch the Streamlit Portal
```bash
streamlit run app.py
```

### 5. Access in Web Browser
Open: **`http://localhost:8501`**

---

## 🧭 Main Sections of the Portal

1. **📊 Overview & Live Map (समग्र स्थिति व लाइव मैप)**:
   - High-level KPIs: Active Emergencies, Urgent Cases, Free Hospital Beds, Shelter Vacancies.
   - Interactive GIS Map of active incident hotspots.
   - Multi-filter incident log table with CSV download.

2. **📝 Report an Emergency (आपदा की सूचना दें)**:
   - **4-Step Guided Reporting**:
     - **Step 1**: What happened? *(बाढ़, भूस्खलन, बादल फटना, भूकंप...)*
     - **Step 2**: Where is it? *(District & Specific Landmark/Road)*
     - **Step 3**: Urgency level *(Critical, High, Medium, Low)*
     - **Step 4 📸 (NEW)**: **Attach Photos & Video Evidence** *(Upload JPG, PNG, MP4, MOV files of the incident site)*
   - Automatic alert dispatch to SDRF and district emergency teams with photo/video preview.

3. **📸 Evidence Gallery in Dashboard**:
   - Responders and officials can view uploaded ground photos and play videos directly inside the Incident Log.


3. **📍 Find Nearest Help (नजदीकी मदद खोजें)**:
   - District-wise lookup for Relief Shelters, Hospital Beds, and Emergency Stockpiles (Food, Water, Oxygen, Rescue Boats).
   - Visual progress gauges showing space availability.

4. **🔔 Live Alerts Feed (लाइव चेतावनी संदेश)**:
   - Real-time priority notifications categorized by urgency level with official SDRF bulletins in Hindi & English.

5. **⚙️ Control Room & Admin (कंट्रोल रूम व अधिकारी पैनल)**:
   - Incident Status Triage (`Active` ➔ `Under Control` ➔ `Resolved`).
   - Live Bed & Shelter Capacity Adjuster.
   - Custom Emergency Alert Broadcast transmitter.
   - 1-click Database Reset & Reseeding tool.
