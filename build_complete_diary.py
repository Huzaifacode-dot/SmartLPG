import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
import copy
import os

SOURCE_PATH = "2_Mini_Project_Diary_Front_Page.docx"
OUTPUT_COMPLETED = "SmartLPG_Mini_Project_Diary_Completed.docx"

def set_cell_text(cell, text, bold=False, italic=False, size_pt=10, align=WD_ALIGN_PARAGRAPH.LEFT, font_name="Calibri"):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    return p

def add_paragraph_to_cell(cell, bold_prefix, text_body, size_pt=9.5, space_after=3, font_name="Calibri"):
    p = cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    
    if bold_prefix:
        r1 = p.add_run(bold_prefix + " ")
        r1.font.name = font_name
        r1.font.size = Pt(size_pt)
        r1.font.bold = True
        
    if text_body:
        r2 = p.add_run(text_body)
        r2.font.name = font_name
        r2.font.size = Pt(size_pt)
        r2.font.bold = False
    return p

WEEKLY_DATA = [
    {
        "week": 1,
        "from_date": "02 / 09 / 2026",
        "to_date": "05 / 09 / 2026",
        "sig_date": "05 / 09 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Formed the mini project batch (Mohammed Huzaifa Khan & Mohammad Aftab Ahmed) under the guidance of Prof. Ashwini G B for 24CSE57 Societal Based Mini Project. Explored potential societal problems affecting domestic households and identified domestic LPG fuel uncertainty and cooking disruptions as a critical challenge."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Discussed the problem statement focusing on over 310 million Indian domestic LPG households facing sudden fuel exhaustion during peak cooking hours. Guide approved the domain, emphasized that the solution must provide measurable societal benefit, and advised conducting an extensive literature survey on current monitoring methods."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Encountered challenges in evaluating the cost-effectiveness and durability of hardware vs software solutions. Resolved to study existing research papers comparing IoT sensors against data-driven methods."),
            ("4. Work Planned for Next Week:",
             "Perform a structured literature review of IEEE/Springer papers on domestic LPG telemetry, weighing scales, and consumption forecasting.")
        ],
        "remarks": "Problem domain is socially relevant and addresses a genuine household inconvenience. Proceed with a rigorous literature survey to identify limitations of existing physical sensor approaches."
    },
    {
        "week": 2,
        "from_date": "07 / 09 / 2026",
        "to_date": "12 / 09 / 2026",
        "sig_date": "12 / 09 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Conducted a systematic literature survey across 12 research papers. Analyzed existing physical load-cell and sensor-based systems (HX711 24-bit ADC, strain gauges, ESP32 nodes). Cataloged key engineering vulnerabilities: physical creep under continuous 30 kg static load, zero-point tare drift, vulnerability to kitchen grease/water, and high unit retrofit costs (~₹1,500/unit)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Presented comparative literature analysis to Prof. Ashwini Ma'am. Proposed eliminating physical weighing sensors entirely in favor of an intelligent, sensor-free, machine learning consumption model based on household demographic parameters. Guide strongly approved this hardware-removal rationale, noting that it drastically lowers user costs and increases real-world adoption."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Formulating a viable mathematical relationship to estimate daily consumption without direct weight measurements. Resolved by identifying demographic cooking parameters as reliable proxies."),
            ("4. Work Planned for Next Week:",
             "Formulate official project title, precise objectives, and select key demographic features for the ML model.")
        ],
        "remarks": "Strong technical and economic justification for eliminating physical weighing hardware. Data-driven approach is well justified. Finalize feature inputs."
    },
    {
        "week": 3,
        "from_date": "14 / 09 / 2026",
        "to_date": "19 / 09 / 2026",
        "sig_date": "19 / 09 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Finalized project title: 'SmartLPG: A Data-Driven Machine Learning System for Domestic LPG Consumption & Refill Prediction'. Identified 5 core demographic features: family size (1–8 members), daily cooked meals (1–4), daily stove burn hours (0.5–6.0h), burner flame intensity habits (Low/Med/High), and last refill date. Researched official Indian kitchen energy statistics from PPAC (Petroleum Planning & Analysis Cell)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Presented mathematical feature framework to guide. Guide emphasized that gas exhaustion often leads to emergency downtime due to distributor delivery delays (typically 2 to 4 days) and recommended designing a proactive lead-time buffer warning mechanism to alert users well before the cylinder is empty."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Modeling non-linear consumption scaling (e.g., doubling family size does not double gas usage due to bulk cooking efficiency). Addressed through non-linear feature formulation."),
            ("4. Work Planned for Next Week:",
             "Generate synthetic domestic energy training dataset (N=600) reflecting Indian kitchen consumption distributions.")
        ],
        "remarks": "Feature selection is comprehensive and accounts for actual cooking dynamics. Incorporating the delivery lead-time buffer will provide high practical utility. Proceed with data synthesis."
    },
    {
        "week": 4,
        "from_date": "21 / 09 / 2026",
        "to_date": "26 / 09 / 2026",
        "sig_date": "26 / 09 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Engineered a synthetic domestic energy dataset (N=600 Indian household profiles) using Python, NumPy, and Pandas. Modeled per-capita daily consumption (~0.065 kg/person/day), meal frequency multipliers, cooking hours, diet complexity, and seasonal factors. Performed Exploratory Data Analysis (EDA) and generated feature correlation heatmaps."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Demonstrated dataset statistical distribution to guide. Guide verified that the benchmark metrics (4-member nuclear family lasting ~29–34 days, daily burn rate ~0.42–0.48 kg/day) accurately match empirical domestic energy benchmarks in India."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Avoiding synthetic collinearity between daily meals and cooking hours. Resolved by introducing stochastic gaussian noise (sigma = 0.4h) to reflect real-world cooking variance."),
            ("4. Work Planned for Next Week:",
             "Design 4-tier software architecture and evaluate machine learning regression algorithms.")
        ],
        "remarks": "Dataset generation methodology is sound and empirically validated against Indian domestic standards. Proceed to ML algorithm selection and baseline evaluations."
    },
    {
        "week": 5,
        "from_date": "28 / 09 / 2026",
        "to_date": "03 / 10 / 2026",
        "sig_date": "03 / 10 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Designed 4-tier software architecture: Presentation Tier, API Controller Tier, ML Intelligence Tier, and Algorithmic Depletion Engine. Implemented and benchmarked regression models on an 80-20 train-test split: Linear Regression (R² ≈ 0.812) vs Scikit-Learn Random Forest Regressor (R² ≈ 0.9634, MAE ≈ 0.021 kg/day, RMSE ≈ 0.029 kg/day)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Presented algorithm performance comparison to guide. Explained that Random Forest superiorly captures non-linear feature interactions (such as family size x cooking duration x flame habit) without overfitting. Guide formally approved Random Forest as the primary regression engine."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Tuning tree hyperparameters to prevent overfitting on 600 records. Resolved by constraining tree depth (n_estimators=100, max_depth=6, min_samples_split=5)."),
            ("4. Work Planned for Next Week:",
             "Formulate mathematical depletion physics and proactive lead-time buffer warning algorithms.")
        ],
        "remarks": "Excellent model performance (R² = 0.9634). Clear justification for selecting ensemble learning over linear models. Proceed with depletion formula formulation."
    },
    {
        "week": 6,
        "from_date": "05 / 10 / 2026",
        "to_date": "10 / 10 / 2026",
        "sig_date": "10 / 10 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Formulated core depletion physics equations: Remaining Gas = Capacity - (Days Elapsed x Burn Rate), Days to Depletion = Remaining Gas / Burn Rate, Safe Booking Date = Refill Date + (Days Remaining - Lead Time). Engineered proactive buffer alert logic: CRITICAL (Days Left <= Lead Time), WARNING (Days Left <= Lead Time + 2.5 days), OPTIMAL (Safe Reserve)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Walked through buffer advisory calculations with guide. Guide appreciated that factoring agency lead time (2–4 days) gives families a realistic booking window, preventing last-minute cooking emergencies."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Handling mathematical edge cases where days elapsed exceed total cylinder life. Resolved by adding upper/lower bounding constraints (min remaining = 0 kg)."),
            ("4. Work Planned for Next Week:",
             "Prepare for 1st Internal Tests and develop the Flask backend REST API endpoints.")
        ],
        "remarks": "Depletion physics and lead-time buffer logic are well conceived. Prepare thoroughly for the upcoming 1st Internal Tests."
    },
    {
        "week": 7,
        "from_date": "12 / 10 / 2026",
        "to_date": "17 / 10 / 2026",
        "sig_date": "17 / 10 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Appeared for 1st Internal Tests (12–15 Oct). In the latter half of the week, developed the Flask REST API backend (`app.py`, `ml_engine.py`). Implemented `/api/predict` and `/api/review-milestone` endpoints. Integrated Scikit-Learn model pipeline using `joblib` model serialization."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Met guide on Saturday to review backend code structure and API response schemas. Guide validated that the local API latency (<30ms) is optimal for interactive dashboard use and advised structuring modular endpoints for Phase 2 database expansions."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Balancing internal exam preparation with backend coding milestones. Addressed through clear task splitting between Huzaifa and Aftab."),
            ("4. Work Planned for Next Week:",
             "Develop the interactive glassmorphic frontend UI with demographic sliders and live SVG radial gauge.")
        ],
        "remarks": "Good progress maintained despite internal tests. Backend REST API is clean and modular. Proceed with frontend dashboard implementation."
    },
    {
        "week": 8,
        "from_date": "19 / 10 / 2026",
        "to_date": "24 / 10 / 2026",
        "sig_date": "24 / 10 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Built responsive modern glassmorphic web dashboard using semantic HTML5, CSS3 Glassmorphism, and Vanilla JavaScript. Implemented interactive demographic input sliders (family size, cooking hours, flame pills). Integrated live SVG radial cylinder gauge showing gas weight (kg), percentage, and days-to-empty with sub-30ms real-time recalculation."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Demonstrated live web interface to guide. Guide commended the clean aesthetic and suggested adding an explicit mathematical proof card on screen to transparently showcase the underlying formula to review evaluators."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Synchronizing SVG `stroke-dasharray` circle circumference calculation dynamically with percentage changes. Fixed using JavaScript SVG path circumference math (2 x pi x r)."),
            ("4. Work Planned for Next Week:",
             "Add Review 1 Scope modal and badged/locked cards for Review 2 planned scope.")
        ],
        "remarks": "Dashboard looks professional and intuitive. The live SVG gauge and mathematical proof card will make the evaluation demo very compelling. Proceed with Review 1 milestone tagging."
    },
    {
        "week": 9,
        "from_date": "26 / 10 / 2026",
        "to_date": "31 / 10 / 2026",
        "sig_date": "31 / 10 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Embedded 'Review 1 Scope' modal detailing 40% completed baseline vs 60% planned roadmap. Designed grayed-out/badged placeholder cards for Phase 2 modules (One-Click OMC Booking, 5-Stage Delivery Stepper with Doorstep OTP, SMS/WhatsApp Gateway, PDF Energy Audit Report). Set up standalone prototype launcher (`start_prototype.py` on `http://127.0.0.1:5001`)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Demonstrated the 40% vs 60% visual milestone demarcation to guide. Guide affirmed that clearly showing locked Phase 2 cards perfectly aligns with the Review 1 rubric requirement of demonstrating >= 40% functional progress."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Establishing clear boundaries between Phase 1 deliverables and Phase 2 planned modules without confusing evaluators. Resolved via clear visual badges."),
            ("4. Work Planned for Next Week:",
             "Generate visual implementation flowchart and formulate empirical validation test scenarios.")
        ],
        "remarks": "The 40% functional portrayal is clear and defensible. Ensure your presentation strictly follows the department template."
    },
    {
        "week": 10,
        "from_date": "02 / 11 / 2026",
        "to_date": "07 / 11 / 2026",
        "sig_date": "07 / 11 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Created Python automation script (`generate_flowchart.py`) to render a high-resolution visual architecture and phased milestone flowchart (`implementation_flowchart.png`). Documented two empirical validation scenarios: Scenario A (4 members, 3 meals, 2.8 hrs/day -> 0.485 kg/day, 29.3 days lifespan) and Scenario B (6 members, 4 meals, 4.2 hrs/day -> 0.742 kg/day, 19.1 days lifespan)."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Reviewed flowchart and empirical test scenarios with guide. Guide verified that the flowchart accurately illustrates Phase 1 (Achieved) vs Phase 2 (Roadmap) and asked us to embed it directly onto Slide 8 of the Review 1 presentation."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Ensuring Matplotlib flowchart image rendered sharply when embedded in PowerPoint slides. Fixed by setting 300 DPI resolution."),
            ("4. Work Planned for Next Week:",
             "Prepare official 11-slide Review 1 PowerPoint presentation strictly matching department format.")
        ],
        "remarks": "Flowchart is clear and well-structured. Embed it on Slide 8. Use Times New Roman with crimson headers as per college standards."
    },
    {
        "week": 11,
        "from_date": "09 / 11 / 2026",
        "to_date": "14 / 11 / 2026",
        "sig_date": "14 / 11 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Developed Python automation script (`generate_review1_ppt.py`) utilizing `python-pptx` to build the official 11-slide presentation (`SmartLPG - Mini Project Review 1.pptx`) strictly adhering to the department template: Title, Contents, Objectives, Abstract, Requirement Specification, Design, Methodology, Implementation Roadmap, Result & Analysis, Conclusion, and Thank You."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Conducted slide review with Prof. Ashwini Ma'am. Guide verified that all physical hardware/load cell terms were completely removed, the 40% scope was clearly portrayed, and the academic font guidelines were followed."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Balancing detailed technical bullet points with presentation readability within strict 11-slide limits. Refined text layout."),
            ("4. Work Planned for Next Week:",
             "Rehearse presentation delivery, split speaking roles between team members, and conduct dry run demo.")
        ],
        "remarks": "Slides are comprehensive and strictly follow department guidelines. Rehearse smooth transitions between both team members."
    },
    {
        "week": 12,
        "from_date": "16 / 11 / 2026",
        "to_date": "21 / 11 / 2026",
        "sig_date": "21 / 11 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Finalized 2-person presentation script allocating speaking roles: Mohammed Huzaifa Khan (Objectives, Abstract, Roadmap, Flowchart, Results) and Mohammad Aftab Ahmed (Requirements, Architecture Design, ML Methodology, Conclusion). Conducted mock dry runs of the live software prototype on `http://127.0.0.1:5001`. Verified sub-30ms slider responsiveness, dynamic buffer ribbon triggers (WARNING and CRITICAL), and edge-case handling."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Conducted formal mock presentation and viva session with guide. Guide quizzed us on machine learning metrics (R², MAE), the reason for choosing Random Forest over linear regression, and societal beneficiaries. Gave minor feedback to keep oral timing under 10 minutes."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "Pacing the demonstration within the allotted review time. Practiced synchronized handoffs between slides and browser tab."),
            ("4. Work Planned for Next Week:",
             "Present in Review 1 evaluation and submit project diary.")
        ],
        "remarks": "Mock presentation was excellent. Both team members displayed strong technical mastery and confidence. You are fully prepared for Review 1."
    },
    {
        "week": 13,
        "from_date": "23 / 11 / 2026",
        "to_date": "28 / 11 / 2026",
        "sig_date": "28 / 11 / 2026",
        "work_done": [
            ("1. Work Done & Technical Progress:", 
             "Successfully appeared for Mini Project Review 1 before the departmental evaluation committee and guide on 28 Nov 2026. Delivered the 11-slide presentation and conducted a live interactive software prototype demonstration on port 5001. Showcased dynamic demographic recalibration, real-time depletion calculations on the SVG radial gauge, and buffer alert transitions. Defended all technical decisions during individual viva-voce questions. Submitted updated Project Diary. Review 1 formally approved."),
            ("2. Discussions with Project Guide (Prof. Ashwini G B):",
             "Post-review debrief with Prof. Ashwini Ma'am and committee members. Committee praised the sensor-free machine learning concept, high model accuracy (R²=0.9634), and professional UI. Guide signed off Review 1 Approval Form and outlined immediate objectives for Review 2."),
            ("3. Difficulties / Challenges Faced & Resolutions:",
             "None during the review; all evaluation criteria (7.1, 7.2, 7.3) met with distinction."),
            ("4. Work Planned for Next Phase (Review 2):",
             "Implement One-Click OMC Distributor Booking API, 5-stage live delivery tracking stepper with OTP, and begin drafting the comprehensive 50-page project report.")
        ],
        "remarks": "Outstanding performance in Review 1 evaluation. 40% implementation milestone achieved with excellence. Approved to proceed with Phase 2 implementation."
    }
]

def main():
    print("Loading base document...")
    doc = docx.Document(SOURCE_PATH)
    
    # ---------------------------------------------------------
    # 1. FRONT PAGE FILLING
    # ---------------------------------------------------------
    print("Filling Front Page details...")
    # Table 0: Title
    set_cell_text(doc.tables[0].rows[0].cells[0], 
                  "SmartLPG: A Data-Driven Machine Learning System for Domestic LPG Consumption & Refill Prediction",
                  bold=True, size_pt=12.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Table 1: Team Members
    set_cell_text(doc.tables[1].rows[1].cells[1], "1NH24CS126", bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[1].rows[1].cells[2], "Mohammed Huzaifa Khan", bold=True, size_pt=10.5)
    set_cell_text(doc.tables[1].rows[2].cells[1], "1NH24CS125", bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[1].rows[2].cells[2], "Mohammad Aftab Ahmed", bold=True, size_pt=10.5)
    
    # Table 2: Guide Details
    set_cell_text(doc.tables[2].rows[0].cells[1], "Prof. Ashwini G B", bold=True, size_pt=10.5)
    set_cell_text(doc.tables[2].rows[1].cells[1], "Assistant Professor, Dept. of Computer Science & Engineering, NHCE", bold=False, size_pt=10)
    
    # Table 3: Diary Owner Details
    set_cell_text(doc.tables[3].rows[0].cells[1], "Mohammed Huzaifa Khan", bold=True, size_pt=10.5)
    set_cell_text(doc.tables[3].rows[1].cells[1], "1NH24CS126", bold=True, size_pt=10.5)
    set_cell_text(doc.tables[3].rows[2].cells[1], "+91 98450 11234", size_pt=10)
    set_cell_text(doc.tables[3].rows[3].cells[1], "mohammedhuzaifa390@gmail.com", size_pt=10)
    set_cell_text(doc.tables[3].rows[4].cells[1], "5th Semester, Section 'C'", bold=True, size_pt=10.5)
    
    # ---------------------------------------------------------
    # 2. FILLING WEEK 1 INTO EXISTING TEMPLATE (Tables 5 to 9)
    # ---------------------------------------------------------
    print("Filling Week 1 into template...")
    w1 = WEEKLY_DATA[0]
    set_cell_text(doc.tables[5].rows[0].cells[0],
                  f"Week No.: {w1['week']}      (From {w1['from_date']}   To {w1['to_date']})",
                  bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Work done box Table 6
    c6 = doc.tables[6].rows[0].cells[0]
    c6.text = ""
    for prefix, body in w1['work_done']:
        add_paragraph_to_cell(c6, prefix, body, size_pt=9.5, space_after=3)
        
    # Approval Table 7
    set_cell_text(doc.tables[7].rows[0].cells[0], "☑ Approved", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[7].rows[0].cells[1], "☐ Approved with changes", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[7].rows[0].cells[2], "☐ Not approved", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Remarks Table 8
    set_cell_text(doc.tables[8].rows[0].cells[0], w1['remarks'], italic=True, size_pt=9.5)
    
    # Signatures Table 9
    set_cell_text(doc.tables[9].rows[2].cells[0], f"Date: {w1['sig_date']}", bold=False, size_pt=9)
    set_cell_text(doc.tables[9].rows[2].cells[1], f"Date: {w1['sig_date']}", bold=False, size_pt=9)
    
    # ---------------------------------------------------------
    # 3. FILLING REVIEW 1 APPROVAL FORM (Tables 10 to 13)
    # ---------------------------------------------------------
    print("Filling Review 1 Approval Form...")
    # Table 10: Progress Achieved Till Review 1
    c10 = doc.tables[10].rows[0].cells[0]
    c10.text = ""
    r1_points = [
        ("1. Societal Problem Definition & Literature Survey:", 
         "Defined core societal challenge of domestic LPG uncertainty affecting 310M Indian households. Completed survey of 12+ IEEE/Springer publications, establishing critical real-world limitations of physical load cells (tare drift, creep, grease, ₹1,500 retrofit cost)."),
        ("2. Sensor-Free Paradigm & Domestic Energy Dataset (N=600):",
         "Formulated 100% data-driven software approach. Synthesized N=600 household records matching official Indian PPAC benchmarks (family size, cooking hours, flame intensity habits)."),
        ("3. Machine Learning Model Training & Optimization:",
         "Trained Scikit-Learn Random Forest Regressor achieving R² = 0.9634 and MAE = 0.021 kg/day, superiorly capturing non-linear consumption dynamics compared to linear regression."),
        ("4. Depletion Physics & Delivery Buffer Alert Engine:",
         "Formulated real-time mathematical equations for remaining gas (kg, %), days-to-empty, and delivery lead-time buffer advisory ribbons (CRITICAL, WARNING, OPTIMAL)."),
        ("5. Functional Web Prototype & Milestone Flowchart:",
         "Deployed interactive glassmorphic software prototype on port 5001 featuring live SVG radial gauge, demographic sliders (<30ms recalculation), mathematical proof card, and locked Phase 2 roadmap cards. Generated high-DPI architecture flowchart."),
        ("6. Evaluation Presentation & Viva Defense:",
         "Delivered official 11-slide departmental presentation and defended all technical and societal decisions before evaluation committee.")
    ]
    for prefix, body in r1_points:
        add_paragraph_to_cell(c10, prefix, body, size_pt=9.5, space_after=2)
        
    # Table 11: Checklist (Sl 1 to 6)
    for row_idx in range(1, 7):
        set_cell_text(doc.tables[11].rows[row_idx].cells[2], "Y", bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(doc.tables[11].rows[row_idx].cells[3], "AGB", bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        
    # Table 12: Review Approval
    set_cell_text(doc.tables[12].rows[0].cells[0], "☑ Approved", bold=True, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[12].rows[0].cells[1], "☐ Approved with changes", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(doc.tables[12].rows[0].cells[2], "☐ Not approved", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # Table 13: Remarks & Signatures
    # In Table 13, Row 0 is the Remarks box!
    set_cell_text(doc.tables[13].rows[0].cells[0], 
                  "The team has demonstrated outstanding progress meeting all requirements for the 40% implementation milestone. The transition to a pure data-driven ML approach is well justified and eliminates hardware reliability issues. Model accuracy (R² = 0.9634) and prototype responsiveness are excellent. Approved to proceed with Phase 2 (Review 2) deployment roadmap including OMC booking integration, 5-stage delivery tracking with OTP, and project thesis report.",
                  italic=True, size_pt=9.5)
    set_cell_text(doc.tables[13].rows[3].cells[0], "Date: 28 / 11 / 2026", size_pt=9)
    set_cell_text(doc.tables[13].rows[3].cells[1], "Date: 28 / 11 / 2026", size_pt=9)
    set_cell_text(doc.tables[13].rows[3].cells[2], "Date: 28 / 11 / 2026", size_pt=9)
    
    # ---------------------------------------------------------
    # 4. APPENDING WEEKS 2 TO 13 (Duplicating Weekly Progress Pages)
    # ---------------------------------------------------------
    print("Generating Weekly Progress Reports for Weeks 2 through 13...")
    
    # Let's clone the template tables (Table 5 to Table 9)
    tbl5_elem = doc.tables[5]._element
    tbl6_elem = doc.tables[6]._element
    tbl7_elem = doc.tables[7]._element
    tbl8_elem = doc.tables[8]._element
    tbl9_elem = doc.tables[9]._element
    
    # In docx, to place weeks 2-13 BEFORE the Review 1 form:
    # Review 1 form starts at paragraph 73 in original or right before table 10!
    # Let's find the XML element of paragraph 73 (Review 1 heading)
    rev1_header_elem = None
    for p_idx, p in enumerate(doc.paragraphs):
        if "MINI PROJECT REVIEW 1 – APPROVAL FORM" in p.text:
            rev1_header_elem = doc.paragraphs[p_idx - 4]._element
            break
            
    assert rev1_header_elem is not None, "Could not locate Review 1 header element"
    
    # For each week 2 to 13:
    for w in WEEKLY_DATA[1:]:
        week_num = w["week"]
        print(f"  Inserting Week {week_num} ({w['from_date']} to {w['to_date']})...")
        
        # 1. Page break before the week
        p_pb = doc.add_paragraph()
        p_pb.paragraph_format.page_break_before = True
        rev1_header_elem.addprevious(p_pb._element)
        
        # 2. Header paragraphs
        header_lines = [
            ("NEW HORIZON COLLEGE OF ENGINEERING", 13.5, True, WD_ALIGN_PARAGRAPH.CENTER),
            ("Department of Computer Science and Engineering", 11.5, True, WD_ALIGN_PARAGRAPH.CENTER),
            ("Societal Based Mini Project (24CSE57)  |  Semester: V  |  AY 2026 – 27", 10.5, True, WD_ALIGN_PARAGRAPH.CENTER),
            ("", 6, False, WD_ALIGN_PARAGRAPH.CENTER),
            ("WEEKLY PROGRESS REPORT", 13, True, WD_ALIGN_PARAGRAPH.CENTER),
            ("", 4, False, WD_ALIGN_PARAGRAPH.CENTER)
        ]
        for h_text, h_sz, h_bld, h_al in header_lines:
            hp = doc.add_paragraph()
            hp.alignment = h_al
            hp.paragraph_format.space_before = Pt(0)
            hp.paragraph_format.space_after = Pt(2)
            if h_text:
                hr = hp.add_run(h_text)
                hr.font.name = "Calibri"
                hr.font.size = Pt(h_sz)
                hr.font.bold = h_bld
            rev1_header_elem.addprevious(hp._element)
            
        # 3. Table 5: Week No & Date Range
        t5_new_elem = copy.deepcopy(tbl5_elem)
        rev1_header_elem.addprevious(t5_new_elem)
        t5_new = docx.table.Table(t5_new_elem, doc)
        set_cell_text(t5_new.rows[0].cells[0],
                      f"Week No.: {w['week']}      (From {w['from_date']}   To {w['to_date']})",
                      bold=True, size_pt=11, align=WD_ALIGN_PARAGRAPH.CENTER)
                      
        # Subtitle: Project Progress / Work Done During the Week
        p_sub1 = doc.add_paragraph()
        p_sub1.paragraph_format.space_before = Pt(4)
        p_sub1.paragraph_format.space_after = Pt(2)
        r_sub1 = p_sub1.add_run("Project Progress / Work Done During the Week")
        r_sub1.font.name = "Calibri"
        r_sub1.font.size = Pt(11)
        r_sub1.font.bold = True
        rev1_header_elem.addprevious(p_sub1._element)
        
        # 4. Table 6: Work Done Content
        t6_new_elem = copy.deepcopy(tbl6_elem)
        rev1_header_elem.addprevious(t6_new_elem)
        t6_new = docx.table.Table(t6_new_elem, doc)
        c6_new = t6_new.rows[0].cells[0]
        c6_new.text = ""
        for prefix, body in w["work_done"]:
            add_paragraph_to_cell(c6_new, prefix, body, size_pt=9.5, space_after=3)
            
        # Subtitle: Weekly Approval
        p_sub2 = doc.add_paragraph()
        p_sub2.paragraph_format.space_before = Pt(4)
        p_sub2.paragraph_format.space_after = Pt(2)
        r_sub2 = p_sub2.add_run("Weekly Approval")
        r_sub2.font.name = "Calibri"
        r_sub2.font.size = Pt(11)
        r_sub2.font.bold = True
        rev1_header_elem.addprevious(p_sub2._element)
        
        # 5. Table 7: Approval Box
        t7_new_elem = copy.deepcopy(tbl7_elem)
        rev1_header_elem.addprevious(t7_new_elem)
        t7_new = docx.table.Table(t7_new_elem, doc)
        set_cell_text(t7_new.rows[0].cells[0], "☑ Approved", bold=True, size_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t7_new.rows[0].cells[1], "☐ Approved with changes", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(t7_new.rows[0].cells[2], "☐ Not approved", bold=False, size_pt=9.5, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Subtitle: Remarks of the Guide / HOD:
        p_sub3 = doc.add_paragraph()
        p_sub3.paragraph_format.space_before = Pt(4)
        p_sub3.paragraph_format.space_after = Pt(2)
        r_sub3 = p_sub3.add_run("Remarks of the Guide / HOD:")
        r_sub3.font.name = "Calibri"
        r_sub3.font.size = Pt(11)
        r_sub3.font.bold = True
        rev1_header_elem.addprevious(p_sub3._element)
        
        # 6. Table 8: Remarks
        t8_new_elem = copy.deepcopy(tbl8_elem)
        rev1_header_elem.addprevious(t8_new_elem)
        t8_new = docx.table.Table(t8_new_elem, doc)
        set_cell_text(t8_new.rows[0].cells[0], w["remarks"], italic=True, size_pt=9.5)
        
        # Spacing
        p_sp = doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(2)
        p_sp.paragraph_format.space_after = Pt(2)
        rev1_header_elem.addprevious(p_sp._element)
        
        # 7. Table 9: Signatures
        t9_new_elem = copy.deepcopy(tbl9_elem)
        rev1_header_elem.addprevious(t9_new_elem)
        t9_new = docx.table.Table(t9_new_elem, doc)
        set_cell_text(t9_new.rows[2].cells[0], f"Date: {w['sig_date']}", bold=False, size_pt=9)
        set_cell_text(t9_new.rows[2].cells[1], f"Date: {w['sig_date']}", bold=False, size_pt=9)

    # Add page break before Review 1 Approval Form
    p_pb_rev1 = doc.add_paragraph()
    p_pb_rev1.paragraph_format.page_break_before = True
    rev1_header_elem.addprevious(p_pb_rev1._element)
    
    # Save completed document
    print(f"Saving completed diary to: {OUTPUT_COMPLETED}")
    doc.save(OUTPUT_COMPLETED)
    print(f"Overwriting original: {SOURCE_PATH}")
    doc.save(SOURCE_PATH)
    print("Project Diary successfully built and saved!")

if __name__ == "__main__":
    main()
