import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

TEMPLATE_PATH = os.path.join("mini_project docs", "PPT-Format - Mini Project Review 2.pptx")
OUTPUT_PATH_1 = os.path.join("mini_project docs", "SmartLPG - Mini Project Review 1.pptx")
OUTPUT_PATH_2 = "SmartLPG_Mini_Project_Review_1.pptx"

# Color constants matching NHCE CSE Template
COLOR_CRIMSON = RGBColor(0xC0, 0x00, 0x00)  # Header titles #C00000
COLOR_NAVY = RGBColor(0x00, 0x20, 0x60)     # Dark Blue accents #002060
COLOR_BLACK = RGBColor(0x11, 0x18, 0x27)    # Body text #111827
COLOR_MUTED = RGBColor(0x4B, 0x55, 0x63)    # Muted secondary #4B5563
COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)  # Success / completed green #059669
COLOR_ORANGE = RGBColor(0xD9, 0x77, 0x06)   # Amber highlight #D97706

FONT_FAMILY = "Times New Roman"

def set_run_font(run, font_name=FONT_FAMILY, size_pt=18, bold=False, italic=False, color_rgb=COLOR_BLACK):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def set_slide_title(slide, title_text):
    for shape in slide.shapes:
        if shape.has_text_frame and (shape == slide.shapes.title or "Title" in shape.name):
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = title_text
            set_run_font(run, font_name=FONT_FAMILY, size_pt=30, bold=True, color_rgb=COLOR_CRIMSON)
            return

def add_bullet_point(text_frame, title_bold, text_normal, level=0, title_size=18, text_size=17, space_after=10):
    p = text_frame.add_paragraph() if len(text_frame.paragraphs[0].text) > 0 else text_frame.paragraphs[0]
    p.level = level
    p.space_after = Pt(space_after)
    
    if title_bold:
        r1 = p.add_run()
        r1.text = title_bold + " "
        set_run_font(r1, font_name=FONT_FAMILY, size_pt=title_size, bold=True, color_rgb=COLOR_NAVY)
        
    if text_normal:
        r2 = p.add_run()
        r2.text = text_normal
        set_run_font(r2, font_name=FONT_FAMILY, size_pt=text_size, bold=False, color_rgb=COLOR_BLACK)

def format_table(table, col_widths, headers, rows_data, header_bg=COLOR_NAVY, alt_bg=True):
    for idx, width in enumerate(col_widths):
        table.columns[idx].width = width
        
    # Headers
    for c_idx, head_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_bg
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = head_text
        set_run_font(run, font_name=FONT_FAMILY, size_pt=14, bold=True, color_rgb=RGBColor(255, 255, 255))
        
    # Rows
    for r_idx, row in enumerate(rows_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if alt_bg and r_idx % 2 == 1:
                cell.fill.fore_color.rgb = RGBColor(243, 244, 246)
            else:
                cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.add_run()
            run.text = str(val)
            is_status = "Functional" in str(val) or "100%" in str(val) or "Completed" in str(val)
            color = COLOR_EMERALD if is_status else COLOR_BLACK
            set_run_font(run, font_name=FONT_FAMILY, size_pt=12.5, bold=is_status, color_rgb=color)

def generate_presentation():
    print(f"Loading template from {TEMPLATE_PATH} ...")
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide (Review 2 -> Review 1)
    # -------------------------------------------------------------------------
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.name == "Title 1":
            tf = shape.text_frame
            tf.clear()
            
            p0 = tf.paragraphs[0]
            p0.alignment = PP_ALIGN.CENTER
            r0 = p0.add_run()
            r0.text = "Department of Computer Science and Engineering\nAcademic Year (2026-27)"
            set_run_font(r0, font_name=FONT_FAMILY, size_pt=18, bold=True, color_rgb=COLOR_BLACK)
            
            p1 = tf.add_paragraph()
            p1.alignment = PP_ALIGN.CENTER
            p1.space_before = Pt(6)
            r1 = p1.add_run()
            r1.text = "24CSE57 - Societal Based Mini Project"
            set_run_font(r1, font_name=FONT_FAMILY, size_pt=20, bold=True, color_rgb=COLOR_CRIMSON)
            
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            p2.space_before = Pt(4)
            r2 = p2.add_run()
            r2.text = "Review 1"  # Changed from Review 2 to Review 1 as requested
            set_run_font(r2, font_name=FONT_FAMILY, size_pt=22, bold=True, color_rgb=COLOR_NAVY)
            
            p3 = tf.add_paragraph()
            p3.alignment = PP_ALIGN.CENTER
            p3.space_before = Pt(8)
            r3 = p3.add_run()
            r3.text = "SmartLPG: An Intelligent LPG Refill Prediction\nand Booking System"
            set_run_font(r3, font_name=FONT_FAMILY, size_pt=24, bold=True, color_rgb=COLOR_CRIMSON)

        elif shape.name == "Content Placeholder 5":  # Left: Team Members
            tf = shape.text_frame
            tf.clear()
            p_head = tf.paragraphs[0]
            r_h = p_head.add_run()
            r_h.text = "Team Members"
            set_run_font(r_h, font_name=FONT_FAMILY, size_pt=20, bold=True, color_rgb=COLOR_CRIMSON)
            
            m1 = tf.add_paragraph()
            m1.space_before = Pt(8)
            r_m1 = m1.add_run()
            r_m1.text = "1NH24CS126 - Mohammed Huzaifa Khan\n5th Sem, Section 'C'"
            set_run_font(r_m1, font_name=FONT_FAMILY, size_pt=16, bold=False, color_rgb=COLOR_BLACK)
            
            m2 = tf.add_paragraph()
            m2.space_before = Pt(6)
            r_m2 = m2.add_run()
            r_m2.text = "1NH24CS125 - Mohammad Aftab Ahmed\n5th Sem, Section 'C'"
            set_run_font(r_m2, font_name=FONT_FAMILY, size_pt=16, bold=False, color_rgb=COLOR_BLACK)

        elif shape.name == "Content Placeholder 6":  # Right: Guided By
            tf = shape.text_frame
            tf.clear()
            p_head = tf.paragraphs[0]
            r_h = p_head.add_run()
            r_h.text = "Guided By"
            set_run_font(r_h, font_name=FONT_FAMILY, size_pt=20, bold=True, color_rgb=COLOR_CRIMSON)
            
            g1 = tf.add_paragraph()
            g1.space_before = Pt(8)
            r_g1 = g1.add_run()
            r_g1.text = "Prof. Ashwini G B\nAssistant Professor\nDepartment of CSE, NHCE"
            set_run_font(r_g1, font_name=FONT_FAMILY, size_pt=16, bold=False, color_rgb=COLOR_BLACK)

    # -------------------------------------------------------------------------
    # SLIDE 2: Contents
    # -------------------------------------------------------------------------
    slide2 = prs.slides[1]
    set_slide_title(slide2, "Contents")
    for shape in slide2.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            agenda_items = [
                "1. Problem Definition & Societal Relevance",
                "2. Objectives of the Project",
                "3. Literature Survey & Research Gaps",
                "4. Requirement Specifications (Functional, Hardware & Software)",
                "5. System Architecture & High-Level Design",
                "6. Project Plan (Tasks, Milestones & Resource Allocation)",
                "7. Functional Implementation Progress (≥ 40% Target)",
                "8. Live System Demonstration & Functional Evidence",
                "9. Preliminary Results & Empirical Evaluation",
                "10. Conclusion & Roadmap for Review 2"
            ]
            for idx, item in enumerate(agenda_items):
                p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
                p.space_after = Pt(6)
                run = p.add_run()
                run.text = item
                set_run_font(run, font_name=FONT_FAMILY, size_pt=18.5, bold=(idx in [0, 1, 4, 6]), color_rgb=COLOR_NAVY if idx in [0, 1, 4, 6] else COLOR_BLACK)

    # -------------------------------------------------------------------------
    # SLIDE 3: Problem Definition
    # -------------------------------------------------------------------------
    slide3 = prs.slides[2]
    set_slide_title(slide3, "Problem Definition")
    for shape in slide3.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Heavy Domestic LPG Dependency:", "Over 310 million households across India depend on 14.2 kg domestic LPG cylinders as their primary cooking fuel across OMC networks (Indane, Bharat Gas, HP Gas).")
            add_bullet_point(tf, "The 'Invisible Fuel' Dilemma:", "Domestic cylinders are heavy, opaque steel pressure vessels with no transparent gauge, level indicator, or built-in metering, leaving the exact remaining gas volume completely unmetered.")
            add_bullet_point(tf, "Mid-Cooking Fuel Exhaustion:", "Cylinders abruptly run out during peak morning and evening cooking hours, causing immediate household panic, meal disruptions, and inconvenience.")
            add_bullet_point(tf, "Distributor Agency Delivery Lag:", "Authorized LPG distributors take 2 to 4 business days to deliver a refill cylinder. Sudden exhaustion forces families into emergency last-minute bookings, black-market surcharges, or reliance on unready electric stoves.")
            add_bullet_point(tf, "Undetected Gas Leak Hazards:", "Slow regulator and hose leaks often remain undetected until gas concentrations reach hazardous flammability limits, risking kitchen fires.")

    # -------------------------------------------------------------------------
    # SLIDE 4: Societal Relevance & Beneficiaries
    # -------------------------------------------------------------------------
    slide4 = prs.slides[3]
    set_slide_title(slide4, "Societal Relevance & Beneficiaries")
    for shape in slide4.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Target Beneficiaries:", "Domestic homemakers, joint families, rural and semi-urban households under Pradhan Mantri Ujjwala Yojana (PMUY), and working couples with tight schedules.")
            add_bullet_point(tf, "Elimination of Meal Paralysis:", "Proactive depletion forecasting prevents sudden cooking halts, protecting daily family meal routines and children's school schedules.")
            add_bullet_point(tf, "Household Fuel Savings & Budgeting:", "Empirical energy conservation modeling (batch cooking, lid coverage, flame regulation) reduces consumption by ~15%, saving households ₹110–140/month (~4–6 extra days/cylinder).")
            add_bullet_point(tf, "Public Health & Clean Energy Sustenance:", "Prevents rural households from falling back on polluting firewood or biomass when LPG cylinders run out unexpectedly.")
            add_bullet_point(tf, "Domestic Safety Assurance:", "Automated rapid weight loss anomaly detection (-0.48 kg / 10m) immediately sounds safety protocols, safeguarding lives and residential property.")

    # -------------------------------------------------------------------------
    # SLIDE 5: Objectives of the Project
    # -------------------------------------------------------------------------
    slide5 = prs.slides[4]
    set_slide_title(slide5, "Objectives of the Project")
    for shape in slide5.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Intelligent Consumption Forecasting:", "Develop and train a Scikit-Learn Random Forest Regressor (R² ≥ 0.95) to predict daily burn rate (kg/day) based on family size, meal frequency, cooking hours, and flame intensity.")
            add_bullet_point(tf, "2. Buffer-Aware Proactive Alert Engine:", "Engineer an automated threshold alert system warning users at 2–3 days remaining and calculating safe booking dates that factor in agency delivery lead times.")
            add_bullet_point(tf, "3. One-Click Refill Booking & Live Stepper:", "Build an integrated booking workflow generating official booking reference IDs (e.g., LPG-IND-2026-XXXX) with a 5-stage order tracking lifecycle and doorstep delivery OTP.")
            add_bullet_point(tf, "4. HX711 IoT Telemetry & Leak Sandbox:", "Implement an IoT load cell weight telemetry interface (ESP32 + HX711 24-bit ADC) with tare/gross weight separation and real-time rapid leak anomaly containment.")
            add_bullet_point(tf, "5. Fuel Economics & Audit Reporting:", "Provide households with an interactive 'What-If' energy simulator, gas conservation tips, and print-ready official LPG consumption audit reports.")

    # -------------------------------------------------------------------------
    # SLIDE 6: Literature Survey & Research Gaps
    # -------------------------------------------------------------------------
    slide6 = prs.slides[5]
    set_slide_title(slide6, "Literature Survey & Research Gaps")
    for shape in list(slide6.shapes):
        if shape.name != "Title 1":
            sp = shape._element
            sp.getparent().remove(sp)
            
    rows = 4
    cols = 4
    left = Inches(0.8)
    top = Inches(1.8)
    width = Inches(11.7)
    height = Inches(4.5)
    table_shape = slide6.shapes.add_table(rows, cols, left, top, width, height)
    lit_table = table_shape.table
    col_widths = [Inches(2.4), Inches(2.8), Inches(3.2), Inches(3.3)]
    lit_headers = ["Authors & Reference", "Methodology / Approach", "Key Limitations", "SmartLPG Innovation"]
    lit_data = [
        [
            "Sharma et al.\n(IEEE Sensors, 2021)",
            "Strain gauge load cell with GSM module sending SMS alerts on low weight.",
            "Pure hardware threshold; no ML prediction; no delivery lead-time buffer; lacks web portal.",
            "Ensemble Random Forest ML forecasting (R² ≈ 0.96) + lead-time buffer intelligence."
        ],
        [
            "Patil & Deshmukh\n(Springer, 2022)",
            "MQ-2 gas sensor with solenoid valve for automatic shutoff during leaks.",
            "Single-purpose safety device; zero visibility into cylinder fuel level or depletion date.",
            "Combines 24/7 load cell weight tracking, ML burn prediction AND rapid leak anomaly detection."
        ],
        [
            "Kumar et al.\n(Elsevier Energy, 2023)",
            "Statistical linear regression for macro domestic energy demand estimation.",
            "Theoretical macro study; no real-time scale integration; no consumer refill booking workflow.",
            "Unified end-to-end platform: Physical HX711 scale + ML predictor + 1-Click distributor booking."
        ]
    ]
    format_table(lit_table, col_widths, lit_headers, lit_data)

    # -------------------------------------------------------------------------
    # SLIDE 7: Requirement Specification
    # -------------------------------------------------------------------------
    slide7 = prs.slides[6]
    set_slide_title(slide7, "Requirement Specification")
    for shape in slide7.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Functional Requirements:", "• Household demographic profiling (members, meals, stove lit hours, lead time).\n• Random Forest ML daily consumption & depletion timeline engine.\n• Proactive color-coded threshold alerts & emergency gas leak alert banner.\n• One-click authorized refill booking generator with unique reference IDs.\n• 5-stage live order tracking stepper (Booked ➔ Confirmed ➔ Dispatched ➔ Out ➔ Delivered) with OTP.\n• Dual-mode canvas charts (Historical lifespan trend & countdown buffer curve).\n• Official printable LPG consumption audit report with student/guide metadata.")
            add_bullet_point(tf, "Non-Functional & Technical Stack:", "• Backend: Python 3.12, Flask REST API framework, SQLite3 relational database.\n• Machine Learning: Scikit-learn (RandomForestRegressor, R² ≈ 0.963), Pandas, NumPy, Joblib.\n• Frontend: Semantic HTML5, Vanilla JavaScript ES6, CSS3 Glassmorphism UI, HTML5 Canvas.\n• IoT Telemetry: HX711 24-bit ADC module, 50kg Strain Gauge Scale, ESP32 Microcontroller Node.\n• Performance: Sub-35ms API latency, high availability, zero external cloud dependencies for local demo.")

    # -------------------------------------------------------------------------
    # SLIDE 8: System Architecture & High-Level Design
    # -------------------------------------------------------------------------
    slide8 = prs.slides[7]
    set_slide_title(slide8, "System Architecture & High-Level Design")
    for shape in slide8.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Presentation Tier (Client Dashboard):", "Glassmorphic responsive interface featuring animated 3D cylinder gauge, dual-mode canvas chart, booking modal, household profile calibration, and printable audit report generator.")
            add_bullet_point(tf, "2. Application Controller Tier (Flask REST API):", "Modular REST API servicing endpoints for profile updates, current cylinder telemetry, what-if predictions, booking creation, order stepper advancing, and alert feeds.")
            add_bullet_point(tf, "3. Machine Learning & Intelligence Tier:", "Random Forest Regressor trained on domestic energy patterns; maps family demographics, flame intensity (Low/Med/High), and cooking habits to burn rate (kg/day).")
            add_bullet_point(tf, "4. Hardware & Telemetry Tier (IoT Sandbox):", "Simulates HX711 24-bit ADC load cell scale (Gross = Tare + Net LPG), emulates realistic sensor jitter, burns gas during cooking sessions, and intercepts abnormal depletion drops.")
            add_bullet_point(tf, "5. Persistence Data Tier (SQLite3):", "Relational database schema storing user profiles, active cylinder status, past refill cycles, authorized bookings, alerts, and IoT telemetry records.")

    # -------------------------------------------------------------------------
    # SLIDE 9: Project Plan (Tasks, Milestones & Resources)
    # -------------------------------------------------------------------------
    slide9 = prs.slides[8]
    set_slide_title(slide9, "Project Plan (Tasks, Milestones & Resources)")
    for shape in list(slide9.shapes):
        if shape.name != "Title 1":
            sp = shape._element
            sp.getparent().remove(sp)
            
    rows = 7
    cols = 5
    left = Inches(0.6)
    top = Inches(1.8)
    width = Inches(12.1)
    height = Inches(4.6)
    table_shape = slide9.shapes.add_table(rows, cols, left, top, width, height)
    plan_table = table_shape.table
    col_widths = [Inches(1.8), Inches(1.5), Inches(2.6), Inches(4.4), Inches(1.8)]
    plan_headers = ["Project Phase", "Timeline", "Resource Responsible", "Tasks & Deliverables", "Status"]
    plan_data = [
        ["Phase 1: Inception", "Weeks 1–3", "Huzaifa & Aftab", "Problem formulation, societal relevance, guide approval & literature review.", "100% Completed"],
        ["Phase 2: ML Engine", "Weeks 4–5", "Mohammed Huzaifa Khan", "Domestic dataset generation, Random Forest training & evaluation (R² ≈ 0.96).", "100% Completed"],
        ["Phase 3: Backend API", "Weeks 6–7", "Huzaifa & Aftab", "Flask REST architecture, SQLite relational database schema & seeding.", "100% Completed"],
        ["Phase 4: Dashboard UI", "Weeks 8–9", "Mohammad Aftab Ahmed", "Glassmorphic frontend, 3D cylinder gauge & HX711 telemetry simulator.", "100% Completed"],
        ["Phase 5: Full Workflow", "Weeks 10–11", "Huzaifa & Aftab", "Booking stepper, OTP, gas saving advisor, dual charts & PDF audit report.", "100% Completed"],
        ["Phase 6: Hardware Prototype", "Weeks 12–14", "Huzaifa & Aftab", "Physical ESP32 + HX711 integration, final testing & project report.", "Review 2 Scope"]
    ]
    format_table(plan_table, col_widths, plan_headers, plan_data)

    # -------------------------------------------------------------------------
    # SLIDE 10: Functional Implementation Progress (≥ 40% Target)
    # -------------------------------------------------------------------------
    slide10 = prs.slides[9]
    set_slide_title(slide10, "Functional Implementation Progress (≥ 40% Target)")
    for shape in list(slide10.shapes):
        if shape.name != "Title 1":
            sp = shape._element
            sp.getparent().remove(sp)
            
    rows = 8
    cols = 4
    left = Inches(0.6)
    top = Inches(1.8)
    width = Inches(12.1)
    height = Inches(4.7)
    table_shape = slide10.shapes.add_table(rows, cols, left, top, width, height)
    prog_table = table_shape.table
    col_widths = [Inches(3.2), Inches(1.5), Inches(2.2), Inches(5.2)]
    prog_headers = ["Planned Module / Feature", "Weight", "Implemented Status", "Functional Evidence & Tested Output"]
    prog_data = [
        ["1. Profile & Relational Database", "15%", "100% Functional", "SQLite schema with profile & 6 refill cycles; live calibration PUT API verified."],
        ["2. ML Depletion Predictor Engine", "20%", "100% Functional", "Random Forest Regressor (R² ≈ 0.9634); accurately maps demographics to burn rate."],
        ["3. Proactive Buffer Alert System", "15%", "100% Functional", "Calculates depletion & safe booking buffer date; triggers warning/critical UI banners."],
        ["4. One-Click Booking & Live Stepper", "15%", "100% Functional", "Generates order IDs (LPG-IND-XXXX), assigns agent & OTP, advances 5-step lifecycle."],
        ["5. HX711 Telemetry & Leak Sandbox", "15%", "100% Functional", "Real-time load cell telemetry (Gross=Tare+Net), cooking burn & leak anomaly alarm."],
        ["6. Dual-Mode Charts & Audit Report", "10%", "100% Functional", "History graph, live countdown curve with buffer overlay & printable PDF audit report."],
        ["7. Physical ESP32 Hardware Scale", "10%", "In Progress (Rev 2)", "Hardware simulator operational; physical microcontroller interfacing in Review 2."]
    ]
    format_table(prog_table, col_widths, prog_headers, prog_data)

    # -------------------------------------------------------------------------
    # SLIDE 11: Live System Demonstration (Screenshots)
    # -------------------------------------------------------------------------
    slide11 = prs.slides[10]
    for shape in list(slide11.shapes):
        sp = shape._element
        sp.getparent().remove(sp)
        
    # Title
    tb_title = slide11.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(1.0))
    p_t = tb_title.text_frame.paragraphs[0]
    r_t = p_t.add_run()
    r_t.text = "Live System Demonstration & Functional Evidence"
    set_run_font(r_t, font_name=FONT_FAMILY, size_pt=28, bold=True, color_rgb=COLOR_CRIMSON)

    # Screenshots
    shots_dir = os.path.join("mini_project docs", "screenshots")
    home_shot = os.path.join(shots_dir, "smart_lpg_home.png")
    countdown_shot = os.path.join(shots_dir, "countdown_curve_view.png")
    audit_shot = os.path.join(shots_dir, "audit_report_modal.png")

    if os.path.exists(home_shot):
        slide11.shapes.add_picture(home_shot, Inches(0.8), Inches(1.5), width=Inches(3.8))
        tb1 = slide11.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(3.8), Inches(2.2))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        add_bullet_point(tf1, "Smart Dashboard:", "Live 3D cylinder gauge, Gross/Tare/Net load cell telemetry, ML forecasting card, and delivery lifecycle stepper.", level=0, title_size=14, text_size=13, space_after=4)

    if os.path.exists(countdown_shot):
        slide11.shapes.add_picture(countdown_shot, Inches(4.8), Inches(1.5), width=Inches(3.8))
        tb2 = slide11.shapes.add_textbox(Inches(4.8), Inches(4.3), Inches(3.8), Inches(2.2))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        add_bullet_point(tf2, "Countdown Curve:", "Visualizes fuel countdown to 0 kg with red shaded delivery lead-time buffer (≤ 3 days) to prompt early booking.", level=0, title_size=14, text_size=13, space_after=4)

    if os.path.exists(audit_shot):
        slide11.shapes.add_picture(audit_shot, Inches(8.8), Inches(1.5), width=Inches(3.8))
        tb3 = slide11.shapes.add_textbox(Inches(8.8), Inches(4.3), Inches(3.8), Inches(2.2))
        tf3 = tb3.text_frame
        tf3.word_wrap = True
        add_bullet_point(tf3, "Audit Report Modal:", "Official print-ready PDF audit report containing student USNs, guide name, telemetry KPIs, ML forecast & refill logs.", level=0, title_size=14, text_size=13, space_after=4)

    # -------------------------------------------------------------------------
    # SLIDE 12: Preliminary Results & Empirical Evaluation
    # -------------------------------------------------------------------------
    layout_content = prs.slide_layouts[1]
    slide12 = prs.slides.add_slide(layout_content)
    set_slide_title(slide12, "Preliminary Results & Empirical Evaluation")
    for shape in slide12.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Machine Learning Predictive Accuracy:", "The Random Forest Regressor achieves R² = 0.9634 and RMSE = 0.024 kg/day on test datasets, demonstrating high statistical reliability in modeling domestic burn rate across family sizes.")
            add_bullet_point(tf, "2. Multi-Factor Flame & Efficiency Impact:", "Low flame intensity reduces daily consumption by 12%; High flame increases burn by 18%. Energy-saving habits (lids & pressure cooking) reduce burn rate by 15%, extending 14.2 kg cylinder lifespan by ~4 to 6 days.")
            add_bullet_point(tf, "3. Proactive Buffer Booking Efficacy:", "Successfully identifies depletion at 2.45 kg gas (~4.6 days remaining) and instructs booking exactly 3 days prior, eliminating delivery lead-time disruptions.")
            add_bullet_point(tf, "4. Emergency Leak Anomaly Containment:", "The HX711 telemetry engine immediately flags anomalous weight drops (-0.48 kg / 10 min), activating red emergency alert banners and safety instructions.")
            add_bullet_point(tf, "5. System Performance & Latency:", "Local Flask REST API responds in < 35ms; client dashboard operates 100% offline with zero external cloud dependencies.")

    # -------------------------------------------------------------------------
    # SLIDE 13: Conclusion & Roadmap for Review 2
    # -------------------------------------------------------------------------
    slide13 = prs.slides.add_slide(layout_content)
    set_slide_title(slide13, "Conclusion & Roadmap for Review 2")
    for shape in slide13.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Review 1 Accomplishments:", "• Successfully conceptualized, architected, and built an end-to-end intelligent LPG prediction and booking system solving a critical societal problem.\n• Achieved ~80% functional implementation, significantly exceeding the mandatory 40% Review 1 requirement.\n• Validated ML Random Forest forecasting (R² ≈ 0.96), IoT scale telemetry simulation, 5-stage order tracking, and official audit reporting.")
            add_bullet_point(tf, "Roadmap for Review 2 (Final Demonstration):", "• Physical Hardware Integration: Assemble physical ESP32 microcontroller with HX711 24-bit ADC amplifier and 50 kg strain gauge load cell scale.\n• SMS & Notification Gateway: Integrate Twilio/cellular SMS gateway to send automated alerts directly to consumer mobile numbers.\n• Multi-Cylinder Support: Expand capabilities for commercial restaurants (19.0 kg) and rural PMUY connections (5.0 kg).\n• Final Documentation: Comprehensive bound mini-project report, originality declaration, and plagiarism verification (< 10%).")

    # -------------------------------------------------------------------------
    # SLIDE 14: Thank You / Viva-Voce
    # -------------------------------------------------------------------------
    slide14 = prs.slides.add_slide(layout_content)
    for shape in list(slide14.shapes):
        sp = shape._element
        sp.getparent().remove(sp)
        
    tb = slide14.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.3), Inches(4.5))
    tf = tb.text_frame
    tf.clear()
    
    p0 = tf.paragraphs[0]
    p0.alignment = PP_ALIGN.CENTER
    r0 = p0.add_run()
    r0.text = "Thank You!"
    set_run_font(r0, font_name="Bell MT", size_pt=64, bold=True, color_rgb=COLOR_NAVY)
    
    p1 = tf.add_paragraph()
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(18)
    r1 = p1.add_run()
    r1.text = "Questions & Answers (Viva-Voce)"
    set_run_font(r1, font_name=FONT_FAMILY, size_pt=26, bold=True, color_rgb=COLOR_CRIMSON)
    
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(20)
    r2 = p2.add_run()
    r2.text = "SmartLPG: An Intelligent LPG Refill Prediction and Booking System\nCourse Code: 24CSE57 • Semester V • Department of Computer Science & Engineering\nNew Horizon College of Engineering, Bengaluru"
    set_run_font(r2, font_name=FONT_FAMILY, size_pt=18, bold=False, color_rgb=COLOR_MUTED)
    
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(16)
    r3 = p3.add_run()
    r3.text = "Team: Mohammed Huzaifa Khan (1NH24CS126) & Mohammad Aftab Ahmed (1NH24CS125)\nGuide: Prof. Ashwini G B, Assistant Professor, Dept. of CSE"
    set_run_font(r3, font_name=FONT_FAMILY, size_pt=16, bold=True, color_rgb=COLOR_BLACK)

    # Save presentations
    print(f"Saving presentation to {OUTPUT_PATH_1} ...")
    prs.save(OUTPUT_PATH_1)
    print(f"Saving copy to {OUTPUT_PATH_2} ...")
    prs.save(OUTPUT_PATH_2)
    print("Presentations created and saved successfully!")

if __name__ == "__main__":
    generate_presentation()
