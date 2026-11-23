# SmartLPG - Mini Project Review 1 Package (40% Implementation Milestone)

**Course:** 24CSE57 - Societal Based Mini Project (Semester V)  
**Department:** Computer Science & Engineering, New Horizon College of Engineering  
**Project Guide:** Prof. Ashwini G B (Assistant Professor, Dept of CSE)  
**Team Members:**
- **Mohammed Huzaifa Khan** (USN: `1NH24CS126`, 5th Sem, Sec 'C')
- **Mohammad Aftab Ahmed** (USN: `1NH24CS125`, 5th Sem, Sec 'C')

---

## 1. Project Implementation Plan (40% Milestone Portrayal)

In accordance with Review 1 academic evaluation guidelines, the project is strictly framed as **40% implementation functional**, with the remaining **60% scheduled for Review 2**.

### Hardware Removal Rationale (100% Data-Driven Software Solution)
- **Removal of IoT Sensors:** Fragile and costly physical weighing hardware (load cells, HX711 ADCs, strain gauges) have been completely eliminated.
- **Data-Driven Modeling:** Cylinder weight and consumption monitoring are performed purely through synthetic domestic energy datasets ($N=600$ Indian household profiles) and a Scikit-Learn **Random Forest Regressor** ($R^2 \approx 0.9634$).
- **Cost & Reliability Benefit:** Eliminates hardware retrofitting costs (~₹1,500/unit), tare drift, and physical maintenance.

---

## 2. Deliverables Included in this Folder (`first review/`)

| File / Folder | Purpose & Details |
| :--- | :--- |
| **`SmartLPG - Mini Project Review 1.pptx`** | The official 11-slide presentation strictly matching the department template and the uploaded contents outline (Times New Roman, crimson headers, embedded flowchart, zero hardware mentions). |
| **`implementation_flowchart.png`** | High-resolution visual flowchart illustrating Phase 1 (40% Completed Baseline) vs Phase 2 (60% Deployment Roadmap). Embedded directly on Slide 8. |
| **`generate_review1_ppt.py`** | Reproducible automation script that creates the 11-slide PPT from the template. |
| **`generate_flowchart.py`** | Script used to generate the high-resolution architecture and milestone flowchart. |
| **`prototype/`** | The functional 40% software prototype (Flask backend, ML engine, interactive glassmorphic UI). |
| **`start_prototype.py`** | Quick launcher for the Review 1 Prototype server running on `http://127.0.0.1:5001`. |

---

## 3. Milestone Comparison: 40% Achieved vs 60% Planned

### Phase 1: Review 1 Functional Scope (40% COMPLETED)
- [x] **Household Profiling:** Captures family size (1–8), daily meals (1–4), stove burn hours (0.5–6.0h), flame intensity (Low/Med/High), and refill date.
- [x] **Domestic Energy Dataset:** Modeled synthetic energy dataset ($N=600$) reflecting real Indian kitchen consumption patterns.
- [x] **Random Forest ML Engine:** Predicts daily burn rate ($\text{kg/day}$) with $R^2 \approx 0.9634$ and $\text{MAE} \approx 0.021\text{ kg/day}$.
- [x] **Depletion Timeline Formulation:** Computes gas consumed, remaining gas (kg, %), days-to-empty, and projected empty date.
- [x] **Proactive Lead-Time Buffer Alert:** Real-time alert ribbon triggering `CRITICAL` or `WARNING` status when remaining days approach delivery lead times.
- [x] **Review 1 Evaluation Web Dashboard:** Interactive dashboard running on port 5001 with live SVG radial gauge.

### Phase 2: Review 2 Deployment Scope (60% PLANNED ROADMAP)
- [ ] **One-Click OMC Distributor Booking:** API integration with Indane, Bharatgas, and HP Gas portals.
- [ ] **5-Stage Delivery Tracking Stepper:** Real-time order progress stepper with doorstep OTP delivery verification.
- [ ] **Cellular SMS & WhatsApp Gateways:** Twilio-powered automated multi-channel alert dispatcher.
- [ ] **Household Energy Audit PDF Generator:** Downloadable monthly consumption analytics and budgeting reports.
- [ ] **Final Thesis Documentation:** Bound report, plagiarism clearance, and viva presentation.

---

## 4. How to Launch and Test the Review 1 Prototype

```bash
# Navigate to project root or first review folder
cd "first review"

# Run the prototype server
python start_prototype.py
```

Open your browser at:  
👉 **`http://127.0.0.1:5001`**

### Key Interactive Features to Demonstrate to the Guide:
1. **Dynamic Demographic Recalibration:** Drag the "Family Members" or "Daily Cooking Hours" sliders; watch the depletion gauge, remaining gas, and days-to-empty update in real time ($<30\text{ms}$).
2. **Buffer Advisory Ribbon:** Change the "Last Refill Date" to test `OPTIMAL`, `WARNING`, and `CRITICAL` alert triggers.
3. **Review 1 Scope Modal:** Click the top-right button **"Review 1 Scope"** to display the formal 40% vs 60% project plan.
4. **Locked Review 2 Modules:** Scroll down to show the grayed-out/badged module cards clearly communicating the planned 60% engineering milestones for Review 2.
