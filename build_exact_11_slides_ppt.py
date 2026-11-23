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
            set_run_font(run, font_name=FONT_FAMILY, size_pt=34, bold=True, color_rgb=COLOR_CRIMSON)
            return

def add_bullet_point(text_frame, title_bold, text_normal, level=0, title_size=19, text_size=18, space_after=10):
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

def generate_exact_11_slides():
    print(f"Loading template from {TEMPLATE_PATH} ...")
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    # Verify exact template slide count is 11
    print(f"Template contains {len(prs.slides)} slides. No slides will be added or removed.")
    assert len(prs.slides) == 11, f"Expected 11 slides, found {len(prs.slides)}"

    # =========================================================================
    # SLIDE 1: Title Slide (Review 2 -> Review 1)
    # =========================================================================
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
            r2.text = "Review 1"  # Changed from Review 2 to Review 1
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

    # =========================================================================
    # SLIDE 2: Contents (EXACTLY matching the user's uploaded picture)
    # =========================================================================
    slide2 = prs.slides[1]
    for shape in slide2.shapes:
        if shape.name == "Title 1":
            tf = shape.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = "Contents"
            set_run_font(run, font_name=FONT_FAMILY, size_pt=48, bold=True, color_rgb=COLOR_CRIMSON)
            
        elif shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            # Exact 8 items from the uploaded picture!
            exact_contents = [
                "Objectives",
                "Abstract",
                "Requirement Specification",
                "Design",
                "Methodology",
                "Implementation Roadmap",
                "Result & Analysis",
                "Conclusion"
            ]
            for idx, item in enumerate(exact_contents):
                p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
                p.space_after = Pt(12)
                p.level = 0
                run = p.add_run()
                run.text = item
                set_run_font(run, font_name=FONT_FAMILY, size_pt=24, bold=False, color_rgb=COLOR_BLACK)

    # =========================================================================
    # SLIDE 3: Objectives
    # =========================================================================
    slide3 = prs.slides[2]
    set_slide_title(slide3, "Objectives")
    for shape in slide3.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Intelligent Consumption Forecasting:", "Develop and train a Scikit-Learn Random Forest Regressor (R² ≥ 0.95) to predict daily burn rate (kg/day) based on family size, meal frequency, cooking hours, and flame intensity.", title_size=19, text_size=18, space_after=12)
            add_bullet_point(tf, "2. Proactive Buffer-Aware Alert Engine:", "Engineer an automated threshold alert system warning users at 2–3 days remaining and calculating safe booking dates that factor in agency delivery lead times.", title_size=19, text_size=18, space_after=12)
            add_bullet_point(tf, "3. One-Click Refill Booking & Live Stepper:", "Build an integrated booking workflow generating official booking reference IDs (e.g., LPG-IND-2026-XXXX) with a 5-stage order tracking lifecycle and doorstep delivery OTP.", title_size=19, text_size=18, space_after=12)
            add_bullet_point(tf, "4. HX711 IoT Telemetry & Leak Containment:", "Implement an IoT load cell weight telemetry interface (ESP32 + HX711 24-bit ADC) with tare/gross weight separation and real-time rapid leak anomaly containment.", title_size=19, text_size=18, space_after=12)
            add_bullet_point(tf, "5. Fuel Economics & Audit Reporting:", "Provide households with an interactive 'What-If' energy simulator, gas conservation advisor, and a printable official LPG consumption audit report for household budgeting.", title_size=19, text_size=18, space_after=12)

    # =========================================================================
    # SLIDE 4: Abstract (Problem Definition & Societal Relevance)
    # =========================================================================
    slide4 = prs.slides[3]
    set_slide_title(slide4, "Abstract")
    for shape in slide4.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Problem Definition:", "Over 310 million households across India depend on 14.2 kg domestic LPG cylinders as their primary cooking fuel. Because cylinders are heavy, opaque steel pressure vessels with no level gauge or metering, remaining gas is completely unmetered. Sudden fuel exhaustion strikes during peak cooking hours, causing severe household disruption compounded by distributor delivery delays of 2 to 4 days.", title_size=19, text_size=18, space_after=14)
            add_bullet_point(tf, "Proposed Solution (SmartLPG):", "An intelligent, full-stack IoT and machine learning-driven refill prediction and booking platform. Unifies physical HX711 load cell weight telemetry with Random Forest consumption forecasting to predict exact cylinder empty dates and optimal buffer booking windows.", title_size=19, text_size=18, space_after=14)
            add_bullet_point(tf, "Societal Relevance & Beneficiaries:", "Directly benefits domestic homemakers, joint families, rural PMUY households, and working professionals. Eliminates cooking downtime, provides household fuel budget transparency, prevents toxic gas leak fire hazards, and encourages clean cooking fuel continuity over firewood.", title_size=19, text_size=18, space_after=14)

    # =========================================================================
    # SLIDE 5: Requirement Specification
    # =========================================================================
    slide5 = prs.slides[4]
    set_slide_title(slide5, "Requirement Specification")
    for shape in slide5.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Functional Requirements:", "• Household demographic profiling (family size, meals/day, daily cooking hours, lead time).\n• Random Forest ML daily consumption & depletion timeline engine.\n• Proactive threshold alerts (warning at 5 days, critical at 3 days) & emergency leak interceptor.\n• One-click authorized refill booking generator with realistic reference IDs (LPG-IND-XXXX).\n• 5-stage live order tracking stepper (Booked ➔ Confirmed ➔ Dispatched ➔ Out ➔ Delivered) with OTP.\n• Dual-mode canvas charts (Historical lifespan trend & countdown buffer curve) and PDF audit report.", title_size=19, text_size=17.5, space_after=14)
            add_bullet_point(tf, "Hardware & Software Stack:", "• Backend: Python 3.12, Flask REST API framework, SQLite3 relational database.\n• Machine Learning: Scikit-learn (RandomForestRegressor, R² ≈ 0.963), Pandas, NumPy, Joblib.\n• Frontend: Semantic HTML5, CSS3 Glassmorphism UI, Vanilla ES6 JavaScript, HTML5 Canvas.\n• IoT Telemetry: HX711 24-bit ADC module, 50kg Strain Gauge Scale, ESP32 Microcontroller Node.\n• Performance: Sub-35ms API latency, high availability, zero external cloud dependencies for local demo.", title_size=19, text_size=17.5, space_after=10)

    # =========================================================================
    # SLIDE 6: Design (System Architecture & High-Level Design)
    # =========================================================================
    slide6 = prs.slides[5]
    set_slide_title(slide6, "Design")
    for shape in slide6.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "5-Tier Modular System Architecture:", "", title_size=20, text_size=18, space_after=10)
            add_bullet_point(tf, "• Presentation Tier (Client Dashboard):", "Glassmorphic responsive interface featuring animated 3D cylinder gauge, dual-mode chart canvas, booking modal, household profile calibration, and printable audit report generator.", title_size=18, text_size=17, space_after=8)
            add_bullet_point(tf, "• Application Controller Tier (Flask REST API):", "Modular REST API servicing endpoints for profile updates, current cylinder telemetry, what-if predictions, booking creation, order stepper advancing, and alert feeds.", title_size=18, text_size=17, space_after=8)
            add_bullet_point(tf, "• Machine Learning & Intelligence Tier:", "Random Forest Regressor trained on domestic energy patterns; maps family demographics, flame intensity (Low/Med/High), and cooking habits to burn rate (kg/day).", title_size=18, text_size=17, space_after=8)
            add_bullet_point(tf, "• Hardware & Telemetry Tier (IoT Sandbox):", "Simulates HX711 24-bit ADC load cell scale (Gross = Tare + Net LPG), emulates realistic sensor jitter, burns gas during cooking sessions, and intercepts abnormal depletion drops.", title_size=18, text_size=17, space_after=8)
            add_bullet_point(tf, "• Persistence Data Tier (SQLite3):", "Relational database schema storing user profiles, active cylinder status, past refill cycles, authorized bookings, alerts, and IoT telemetry records.", title_size=18, text_size=17, space_after=8)

    # =========================================================================
    # SLIDE 7: Methodology (Literature Survey, Research Gap & Algorithms)
    # =========================================================================
    slide7 = prs.slides[6]
    set_slide_title(slide7, "Methodology")
    for shape in slide7.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Literature Survey & Research Gap:", "Prior works either rely on raw sensor hardware with basic SMS (Sharma et al., 2021) or theoretical macro energy modeling without physical scales or booking automation (Kumar et al., 2023). SmartLPG bridges this gap by unifying physical load cell telemetry, predictive ML burn modeling, and distributor booking workflows.", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "ML Consumption Modeling Algorithm:", "A synthetic domestic training dataset (N=600) based on Indian household consumption studies was developed. The Random Forest model predicts daily burn rate (kg/day) with multi-factor flame intensity calibration (Low: -12%, Medium: 0%, High: +18%) and energy-saving mode (-15% burn).", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "Buffer-Aware Refill Recommendation Algorithm:", "Days Remaining = Current Gas (kg) / Daily Burn Rate (kg/d). Safe Booking Date = Today + (Days Remaining - Distributor Delivery Lead Time). Prevents stockouts by factoring in agency delivery lag.", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "IoT Load Cell Telemetry & Leak Containment Protocol:", "Gross Weight = Tare Weight (15.3 kg) + Net LPG. Anomaly filter tracks depletion velocity; if rate > 0.45 kg / 10 min, it immediately triggers emergency safety protocol banners.", title_size=18.5, text_size=17, space_after=8)

    # =========================================================================
    # SLIDE 8: Implementation Roadmap (Milestones, Resources & ≥ 40% Target)
    # =========================================================================
    slide8 = prs.slides[7]
    set_slide_title(slide8, "Implementation Roadmap")
    for shape in slide8.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Project Plan & Milestones:", "", title_size=19, text_size=18, space_after=6)
            add_bullet_point(tf, "• Phase 1 (W1–3):", "Problem formulation, societal relevance & literature survey [100% Completed - Huzaifa & Aftab].", title_size=17.5, text_size=16.5, space_after=5)
            add_bullet_point(tf, "• Phase 2 (W4–5):", "Dataset synthesis, Random Forest ML training (R² ≈ 0.963) [100% Completed - Huzaifa].", title_size=17.5, text_size=16.5, space_after=5)
            add_bullet_point(tf, "• Phase 3 (W6–7):", "Flask REST API architecture & SQLite database schema [100% Completed - Huzaifa & Aftab].", title_size=17.5, text_size=16.5, space_after=5)
            add_bullet_point(tf, "• Phase 4 (W8–9):", "Glassmorphic frontend, 3D gauge & HX711 telemetry simulator [100% Completed - Aftab].", title_size=17.5, text_size=16.5, space_after=5)
            add_bullet_point(tf, "• Phase 5 (W10–11):", "Booking stepper, OTP, gas saving advisor & PDF audit report [100% Completed - Huzaifa & Aftab].", title_size=17.5, text_size=16.5, space_after=8)
            add_bullet_point(tf, "Review 1 Implementation Progress (≥ 40% Target):", "", title_size=19, text_size=18, space_after=6)
            add_bullet_point(tf, "• Profile & Relational DB: 100% Functional", "| ML Depletion Predictor: 100% Functional", title_size=17, text_size=16.5, space_after=4)
            add_bullet_point(tf, "• Buffer-Aware Alert System: 100% Functional", "| 1-Click Booking & Stepper: 100% Functional", title_size=17, text_size=16.5, space_after=4)
            add_bullet_point(tf, "• HX711 Telemetry & Leak Sandbox: 100% Functional", "| Dual Charts & Audit Report: 100% Functional", title_size=17, text_size=16.5, space_after=4)
            add_bullet_point(tf, "• Review 1 Implementation Achieved: ~80% Complete", "(Substantially exceeds mandatory 40% target).", title_size=18, text_size=17, space_after=4)

    # =========================================================================
    # SLIDE 9: Result & Analysis
    # =========================================================================
    slide9 = prs.slides[8]
    set_slide_title(slide9, "Result & Analysis")
    for shape in slide9.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Machine Learning Predictive Accuracy:", "The Random Forest Regressor achieves R² = 0.9634 and RMSE = 0.024 kg/day on test datasets, demonstrating high statistical reliability in modeling domestic burn rate across family sizes.", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "2. Multi-Factor Flame & Fuel Savings Impact:", "Low flame intensity reduces daily consumption by 12%; High flame increases burn by 18%. Energy-saving habits (lids & pressure cooking) reduce burn rate by 15%, extending 14.2 kg cylinder longevity by ~4 to 6 days (saving ₹110–140/month per household).", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "3. Proactive Buffer Booking Efficacy:", "Successfully identifies depletion at 2.45 kg gas (~4.6 days remaining) and instructs booking exactly 3 days prior, eliminating delivery lead-time disruptions.", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "4. Emergency Leak Anomaly Response:", "The HX711 telemetry engine immediately flags anomalous weight drops (-0.48 kg / 10 min), activating red emergency alert banners and safety instructions.", title_size=18.5, text_size=17, space_after=10)
            add_bullet_point(tf, "5. System Performance & Latency:", "Local Flask REST API responds in < 35ms; client dashboard operates 100% offline with zero external cloud dependencies.", title_size=18.5, text_size=17, space_after=8)

    # =========================================================================
    # SLIDE 10: Conclusion
    # =========================================================================
    slide10 = prs.slides[9]
    set_slide_title(slide10, "Conclusion")
    for shape in slide10.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Review 1 Summary & Societal Impact:", "", title_size=20, text_size=18, space_after=8)
            add_bullet_point(tf, "• Solved Critical Problem:", "Designed and built an end-to-end intelligent LPG prediction and booking system addressing sudden household cooking gas exhaustion and safety hazards.", title_size=18, text_size=17, space_after=6)
            add_bullet_point(tf, "• Exceeded Implementation Target:", "Achieved ~80% functional implementation, significantly surpassing the mandatory 40% Review 1 requirement.", title_size=18, text_size=17, space_after=6)
            add_bullet_point(tf, "• Comprehensive Validation:", "Validated ML Random Forest forecasting (R² ≈ 0.96), IoT load cell scale telemetry simulation, buffer-aware alerts, one-click booking lifecycle, and printable audit reporting.", title_size=18, text_size=17, space_after=6)
            add_bullet_point(tf, "• Real-World Societal Benefits:", "Delivers zero cooking disruption, ₹110–140 monthly savings, and home safety assurance.", title_size=18, text_size=17, space_after=12)
            add_bullet_point(tf, "Roadmap for Review 2 (Final Evaluation):", "", title_size=20, text_size=18, space_after=8)
            add_bullet_point(tf, "• Physical Hardware Prototype:", "Interface physical ESP32 microcontroller with HX711 24-bit ADC amplifier and 50 kg load cell scale.", title_size=18, text_size=17, space_after=6)
            add_bullet_point(tf, "• SMS Notification Gateway:", "Integrate Twilio / cellular SMS gateway for direct mobile phone SMS alerts.", title_size=18, text_size=17, space_after=6)
            add_bullet_point(tf, "• Final Deliverables:", "Complete bound mini-project report, originality declaration, and plagiarism verification (< 10%).", title_size=18, text_size=17, space_after=6)

    # =========================================================================
    # SLIDE 11: Thank You
    # =========================================================================
    slide11 = prs.slides[10]
    for shape in list(slide11.shapes):
        sp = shape._element
        sp.getparent().remove(sp)
        
    tb = slide11.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(10.8), Inches(4.8))
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
    p2.space_before = Pt(22)
    r2 = p2.add_run()
    r2.text = "SmartLPG: An Intelligent LPG Refill Prediction and Booking System\nCourse Code: 24CSE57 • Semester V • Department of Computer Science & Engineering\nNew Horizon College of Engineering, Bengaluru"
    set_run_font(r2, font_name=FONT_FAMILY, size_pt=18, bold=False, color_rgb=COLOR_MUTED)
    
    p3 = tf.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(16)
    r3 = p3.add_run()
    r3.text = "Team: Mohammed Huzaifa Khan (1NH24CS126) & Mohammad Aftab Ahmed (1NH24CS125)\nGuide: Prof. Ashwini G B, Assistant Professor, Dept. of CSE"
    set_run_font(r3, font_name=FONT_FAMILY, size_pt=16.5, bold=True, color_rgb=COLOR_BLACK)

    # Save presentations
    output_paths = [
        OUTPUT_PATH_2,
        os.path.join("mini_project docs", "SmartLPG - Mini Project Review 1 (Official).pptx"),
        OUTPUT_PATH_1
    ]
    for p in output_paths:
        try:
            prs.save(p)
            print(f"Successfully saved exact 11-slide presentation to: {p}")
        except Exception as e:
            print(f"Notice: Could not write to {p} (file may be open in LibreOffice/PowerPoint: {e})")

    print("Exact 11-slide presentation generated successfully!")

if __name__ == "__main__":
    generate_exact_11_slides()
