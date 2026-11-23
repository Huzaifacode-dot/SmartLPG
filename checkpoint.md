# SmartLPG - Mini Project Checkpoint & Milestone Tracking

**Last Updated:** 2026-10-26 (Review 1 Deliverables Ready)  
**Workspace:** `C:\Users\Afshaan\OneDrive\Desktop\Smart_LPG`  
**Course:** 24CSE57 - Societal Based Mini Project (Semester V), Dept. of CSE, NHCE  
**Students:** Mohammed Huzaifa Khan (`1NH24CS126`) & Mohammad Aftab Ahmed (`1NH24CS125`)  
**Project Guide:** Prof. Ashwini G B  

---

## 📍 1. Current Milestone: Mini Project Review 1 (40% Implementation Scope)

In compliance with the 1st Mini Project Review requirements:
- **Portrayal:** The project is portrayed and structured as **40% implementation functional** (Phase 1 Baseline Achieved).
- **Hardware Removal (100% Data-Driven):** Physical IoT load cells (HX711/strain gauges/ESP32) have been completely removed. Cylinder weight and consumption monitoring are modeled through domestic energy datasets ($N=600$) and Scikit-Learn Random Forest machine learning ($R^2 \approx 0.9634$).
- **Review 1 Folder Created:** All Review 1 deliverables are consolidated inside [`first review/`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review).

---

## 📦 2. Deliverables in `first review/`

| Deliverable | Location | Description & Status |
| :--- | :--- | :--- |
| **Review 1 Presentation** | [`first review/SmartLPG - Mini Project Review 1.pptx`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review/SmartLPG%20-%20Mini%20Project%20Review%201.pptx) | Strict **11-slide presentation** following the NHCE CSE template and the exact contents outline from the user's uploaded picture. All fonts in Times New Roman, crimson headers, flowchart embedded on Slide 8, zero hardware mentions. |
| **Implementation Flowchart** | [`first review/implementation_flowchart.png`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review/implementation_flowchart.png) | High-resolution visual flowchart delineating Phase 1 (40% Achieved Baseline) vs Phase 2 (60% Planned Deployment Roadmap). |
| **Review 1 Prototype (40% Scope)** | [`first review/prototype/`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review/prototype) | Functional prototype web application implementing *only* the 40% features: demographic input profiling, ML burn rate estimation, live depletion gauge, and buffer alert ribbons. Review 2 modules are visibly badged and locked. |
| **Prototype Launcher** | [`first review/start_prototype.py`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review/start_prototype.py) | Standalone launcher running the Review 1 prototype on **`http://127.0.0.1:5001/`**. |
| **Review 1 Documentation** | [`first review/README.md`](file:///c:/Users/Afshaan/OneDrive/Desktop/Smart_LPG/first%20review/README.md) | Comprehensive review guide explaining the 40% vs 60% breakdown and demo script. |

---

## 📊 3. Implementation Plan: 40% Achieved vs 60% Planned

### Phase 1: Review 1 Milestone (40% Implementation - COMPLETED)
- [x] **Household Demographics Profiling:** Capture family size, meal frequency, stove burn hours, flame habit, and last refill date.
- [x] **Sensor-Free Domestic Energy Dataset:** Synthetic dataset ($N=600$ Indian household records) mapping demographic features to daily consumption.
- [x] **Random Forest ML Engine:** Trained regressor achieving $R^2 = 0.9634$ and $\text{MAE} = 0.021\text{ kg/day}$ for daily burn rate ($\text{kg/day}$).
- [x] **Depletion Timeline Formulation:** Real-time computation of remaining LPG (kg, %), days-to-empty, and projected empty timestamp.
- [x] **Delivery Buffer Alert Ribbon:** Dynamic alert engine triggering `WARNING` or `CRITICAL` when remaining days approach distributor lead time (2–4 days).
- [x] **Review 1 Web Prototype:** Interactive glassmorphic dashboard running at `http://127.0.0.1:5001`.

### Phase 2: Review 2 Milestone (Remaining 60% Scope - PLANNED)
- [ ] **One-Click OMC Distributor Booking:** Automated API integration with Indane, Bharatgas, and HP Gas portals.
- [ ] **5-Stage Delivery Tracking Stepper:** Real-time lifecycle stepper (Booked ➔ Confirmed ➔ Dispatched ➔ Out for Delivery ➔ Delivered) with doorstep OTP verification.
- [ ] **Cellular SMS & WhatsApp Gateways:** Twilio-powered automated multi-channel alert dispatch.
- [ ] **Monthly Household Energy Audit Report:** Automated PDF report generator for domestic fuel budgeting.
- [ ] **Final Thesis Documentation:** Bound report, plagiarism check, and final viva presentation.

---

## 🏃 4. Active Local Servers

| Application | Port | Directory / Script | Status |
| :--- | :--- | :--- | :--- |
| **Review 1 Prototype (40% Scope)** | `http://127.0.0.1:5001/` | `first review/start_prototype.py` | **RUNNING** |
| **SmartLPG Main Project** | `http://127.0.0.1:5000/` | Root `run.py` | **RUNNING** |
| **Backup Predictor Demo** | `http://127.0.0.1:8080/` | `working_demo_project/serve.py` | **RUNNING** |

---

## 🎯 5. Verification Checklist
- [x] Slide count strictly equals 11.
- [x] Slide 2 contents matches uploaded image (Objectives, Abstract, Requirement Specification, Design, Methodology, Implementation Roadmap, Result & Analysis, Conclusion).
- [x] Zero hardware/IoT sensor terms in presentation or prototype.
- [x] Visual flowchart embedded on Slide 8.
- [x] Prototype server running and tested on port 5001.
- [x] Review 1 package consolidated inside `first review/`.
