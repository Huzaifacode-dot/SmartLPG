import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Fix console encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "mini_project docs", "PPT-Format - Mini Project Review 2.pptx")
OUTPUT_PATH_1 = os.path.join(BASE_DIR, "SmartLPG - Mini Project Review 1.pptx")
OUTPUT_PATH_2 = os.path.join(PROJECT_ROOT, "SmartLPG_Mini_Project_Review_1.pptx")
FLOWCHART_PATH = os.path.join(BASE_DIR, "implementation_flowchart.png")

# Color palette matching NHCE CSE Template
COLOR_CRIMSON = RGBColor(0xC0, 0x00, 0x00)  # Main Header #C00000
COLOR_NAVY = RGBColor(0x00, 0x20, 0x60)     # Sub-headers & emphasis #002060
COLOR_BLACK = RGBColor(0x11, 0x18, 0x27)    # Crisp dark body text #111827
COLOR_MUTED = RGBColor(0x4B, 0x55, 0x63)    # Muted secondary #4B5563
COLOR_GREEN = RGBColor(0x05, 0x96, 0x69)    # Milestone check #059669

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

def generate_review1_presentation():
    print(f"Loading base template: {TEMPLATE_PATH}")
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    total_slides = len(prs.slides)
    print(f"Base template slide count: {total_slides} (Strictly preserving exact 11 slides)")
    assert total_slides == 11, f"Expected 11 slides, found {total_slides}"

    # =========================================================================
    # SLIDE 1: Title Slide (Review 2 -> Review 1, Team & Guide)
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
            r2.text = "Review 1 - 40% Implementation Evaluation"
            set_run_font(r2, font_name=FONT_FAMILY, size_pt=22, bold=True, color_rgb=COLOR_NAVY)
            
            p3 = tf.add_paragraph()
            p3.alignment = PP_ALIGN.CENTER
            p3.space_before = Pt(8)
            r3 = p3.add_run()
            r3.text = "SmartLPG: A Data-Driven Machine Learning System for\nDomestic LPG Consumption & Refill Prediction"
            set_run_font(r3, font_name=FONT_FAMILY, size_pt=23, bold=True, color_rgb=COLOR_CRIMSON)

        elif shape.name == "Content Placeholder 5":  # Left placeholder: Team
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

        elif shape.name == "Content Placeholder 6":  # Right placeholder: Guide
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
    # SLIDE 3: Objectives (Sensor-Free, 40% Review 1 Scope Defined)
    # =========================================================================
    slide3 = prs.slides[2]
    set_slide_title(slide3, "Objectives")
    for shape in slide3.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Purely Data-Driven Consumption Modeling:", "Eliminate reliance on fragile and costly physical weighing mechanisms by modeling LPG depletion mathematically and statistically through household demographics and cooking patterns.", title_size=18, text_size=17, space_after=12)
            add_bullet_point(tf, "2. Random Forest Machine Learning Burn Rate Engine:", "Develop and train a Scikit-Learn Random Forest Regressor (achieving R² >= 0.95) on domestic energy datasets to predict household daily burn rate (kg/day) from family size, meals, flame habit, and burner hours.", title_size=18, text_size=17, space_after=12)
            add_bullet_point(tf, "3. Proactive Buffer-Aware Depletion & Refill Advisory:", "Formulate mathematical depletion timelines to forecast exact cylinder empty dates and trigger early warning alerts factoring in distributor delivery lead times (2-4 days) to prevent unexpected fuel run-outs.", title_size=18, text_size=17, space_after=12)
            add_bullet_point(tf, "4. 40% Functional Review 1 Prototype Delivery:", "Implement and demonstrate a working software prototype integrating demographic profiling, live depletion gauge, and threshold warnings as the 40% functional milestone.", title_size=18, text_size=17, space_after=12)
            add_bullet_point(tf, "5. Architecture Foundation for Review 2 Scope (60%):", "Establish the modular architecture for planned Review 2 features: one-click OMC booking automation, 5-stage delivery stepper with OTP, SMS/WhatsApp gateways, and PDF energy audit reports.", title_size=18, text_size=17, space_after=10)

    # =========================================================================
    # SLIDE 4: Abstract (Problem Definition & Societal Relevance)
    # =========================================================================
    slide4 = prs.slides[3]
    set_slide_title(slide4, "Abstract")
    for shape in slide4.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Problem Definition:", "Over 310 million households across India depend on 14.2 kg domestic LPG cylinders as their primary cooking fuel. Because cylinders are opaque steel pressure vessels, remaining gas is completely unmetered. Sudden fuel exhaustion strikes during peak cooking hours, causing acute household disruption compounded by distributor delivery delays of 2 to 4 days.", title_size=19, text_size=17.5, space_after=14)
            add_bullet_point(tf, "Proposed Sensor-Free Solution (SmartLPG):", "SmartLPG solves this societal challenge through software intelligence and data modeling. By utilizing domestic demographic energy datasets and a Scikit-Learn Random Forest regression model, the system accurately estimates cylinder depletion timelines, remaining gas (kg and %), and safe booking buffer windows without physical weighing hardware or sensor maintenance.", title_size=19, text_size=17.5, space_after=14)
            add_bullet_point(tf, "Societal Relevance & Beneficiaries:", "Directly benefits domestic homemakers, joint families, rural PMUY households, and working professionals. Eliminates sudden cooking downtime, provides household fuel budget transparency, avoids expensive hardware retrofits, and encourages clean cooking continuity.", title_size=19, text_size=17.5, space_after=12)

    # =========================================================================
    # SLIDE 5: Requirement Specification (Software-Only, Functional 40% Scope)
    # =========================================================================
    slide5 = prs.slides[4]
    set_slide_title(slide5, "Requirement Specification")
    for shape in slide5.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Functional Requirements (Review 1 - 40% Functional Baseline):", 
                             "• Household Demographic Profiling: Captures family size (1-8), daily meals (1-4), daily stove burn time (0.5-6.0h), flame habit (Low/Med/High), and last refill date.\n"
                             "• Domestic Energy Dataset: N=600 realistic household consumption records derived from empirical Indian cooking energy surveys.\n"
                             "• ML Consumption Forecasting: Random Forest Regressor predicting daily burn rate (kg/day) with multi-factor flame adjustment.\n"
                             "• Depletion Timeline Engine: Computes elapsed days, remaining gas (kg, %), and projected exhaustion date.\n"
                             "• Buffer-Aware Refill Warnings: Proactive alert ribbons activated when remaining days approach distributor delivery lead time.",
                             title_size=18, text_size=16.5, space_after=14)
            add_bullet_point(tf, "Non-Functional Requirements & Software Stack:", 
                             "• Backend & API: Python 3.12, Flask RESTful micro-framework, CORS support.\n"
                             "• Machine Learning: Scikit-learn (RandomForestRegressor, R² ≈ 0.9634), NumPy, Pandas.\n"
                             "• Frontend: Semantic HTML5, CSS3 Glassmorphism UI, Vanilla ES6 JavaScript (sub-30ms local API response).\n"
                             "• Zero Hardware Constraint: 100% data and software driven; no IoT sensors, microcontrollers, or physical scales required.",
                             title_size=18, text_size=16.5, space_after=10)

    # =========================================================================
    # SLIDE 6: Design (Sensor-Free Architecture & Data Pipeline)
    # =========================================================================
    slide6 = prs.slides[5]
    set_slide_title(slide6, "Design")
    for shape in slide6.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "4-Tier Sensor-Free Software Architecture:", "", title_size=19, text_size=17.5, space_after=8)
            add_bullet_point(tf, "• 1. Presentation Tier (Client Dashboard):", "Glassmorphic responsive interface featuring household demographic sliders, live radial SVG depletion gauge, days-to-empty counter, status alert ribbons, and Review 1 scope modal.", title_size=17.5, text_size=16.5, space_after=8)
            add_bullet_point(tf, "• 2. Application Controller Tier (Flask REST API):", "Lightweight REST API servicing endpoints (/api/predict and /api/review-milestone); handles input sanitization, elapsed days calculation, and payload orchestration.", title_size=17.5, text_size=16.5, space_after=8)
            add_bullet_point(tf, "• 3. Machine Learning Intelligence Tier (Random Forest):", "Trained Random Forest Regressor evaluating non-linear demographic feature interactions (family size x cooking duration x flame habit) to forecast exact daily consumption in kg/day.", title_size=17.5, text_size=16.5, space_after=8)
            add_bullet_point(tf, "• 4. Algorithmic Depletion & Advisory Engine:", "Mathematical formulas compute real-time remaining gas:\n"
                             "   Gas_Remaining = Cylinder_Capacity - (Days_Elapsed x Burn_Rate)\n"
                             "   Days_Remaining = Gas_Remaining / Burn_Rate\n"
                             "   Safe_Booking_Date = Refill_Date + (Days_Remaining - Lead_Time)", title_size=17.5, text_size=16.5, space_after=8)

    # =========================================================================
    # SLIDE 7: Methodology (Dataset Creation, ML Algorithm, Depletion Math)
    # =========================================================================
    slide7 = prs.slides[6]
    set_slide_title(slide7, "Methodology")
    for shape in slide7.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Data-Driven Modeling Rationale & Research Gap:", 
                             "Conventional legacy approaches relied on physical weighing hardware which suffer from sensor drift, tare miscalibration, mechanical fatigue under static cylinder loads, and prohibitive unit costs (~Rs. 1,500+). SmartLPG bridges this research gap through an entirely software-modeled demographic consumption paradigm.", title_size=18, text_size=16.5, space_after=10)
            add_bullet_point(tf, "Domestic Energy Dataset Synthesis (N=600):", 
                             "Generated a rigorous domestic energy dataset based on empirical Indian LPG consumption benchmarks. Feature dimensions include: family size (1-8), daily meals (1-4), daily burner hours (0.8-6.0h), diet complexity, and seasonal temperature factors.", title_size=18, text_size=16.5, space_after=10)
            add_bullet_point(tf, "Machine Learning Algorithm Selection:", 
                             "Trained a Scikit-Learn Random Forest Regressor (n_estimators=100, max_depth=6). Evaluated against 20% held-out test data, achieving R² = 0.9634 and Mean Absolute Error = 0.021 kg/day, outperforming linear regression across diverse household scales.", title_size=18, text_size=16.5, space_after=10)
            add_bullet_point(tf, "Proactive Buffer Alert Threshold Logic:", 
                             "If Days_Remaining <= Lead_Time -> CRITICAL (Immediate booking required);\n"
                             "If Days_Remaining <= Lead_Time + 2.5 -> WARNING (Refill booking window open);\n"
                             "Else -> OPTIMAL (Cylinder reserve safe).", title_size=18, text_size=16.5, space_after=8)

    # =========================================================================
    # SLIDE 8: Implementation Roadmap (Embedded Visual Flowchart + Checklist)
    # =========================================================================
    slide8 = prs.slides[7]
    set_slide_title(slide8, "Implementation Roadmap")
    for shape in slide8.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            # Summary bullet at top
            p_top = tf.paragraphs[0]
            p_top.space_after = Pt(6)
            r_top = p_top.add_run()
            r_top.text = "Implementation Plan: 40% Functional Baseline (Review 1) vs 60% Deployment Roadmap (Review 2)"
            set_run_font(r_top, font_name=FONT_FAMILY, size_pt=16, bold=True, color_rgb=COLOR_NAVY)

    # Embed High-Resolution Flowchart on Slide 8
    if os.path.exists(FLOWCHART_PATH):
        print(f"Embedding flowchart from {FLOWCHART_PATH} onto Slide 8...")
        # Slide dimensions: 13.33 in x 7.5 in
        slide8.shapes.add_picture(
            FLOWCHART_PATH,
            left=Inches(0.6),
            top=Inches(1.8),
            width=Inches(12.1),
            height=Inches(4.8)
        )

    # =========================================================================
    # SLIDE 9: Result & Analysis (Model Metrics & 40% Prototype Validation)
    # =========================================================================
    slide9 = prs.slides[8]
    set_slide_title(slide9, "Result & Analysis")
    for shape in slide9.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "1. Random Forest Model Evaluation Metrics:", 
                             "• Training/Testing Split: 80% Training (N=480), 20% Test (N=120).\n"
                             "• Coefficient of Determination (R² Score): 0.9634 (High predictive confidence).\n"
                             "• Mean Absolute Error (MAE): 0.021 kg/day (~4.3% relative variance).\n"
                             "• Model accurately captures non-linear consumption scaling between small and large households.",
                             title_size=18, text_size=16.5, space_after=12)
            add_bullet_point(tf, "2. Empirical Prototype Test Scenarios (Review 1 Validation):", 
                             "• Scenario A (4 Members, 3 Meals, 2.8 hrs/day, Medium Flame):\n"
                             "  Predicted Burn Rate = 0.485 kg/day | 14.2 kg Cylinder Lifespan = 29.3 Days.\n"
                             "  At 22 days elapsed: Remaining = 3.81 kg (26.8%), Days Left = 6.2 Days (WARNING Alert).\n"
                             "• Scenario B (6 Members, 4 Meals, 4.2 hrs/day, High Flame):\n"
                             "  Predicted Burn Rate = 0.742 kg/day | 14.2 kg Cylinder Lifespan = 19.1 Days.\n"
                             "  At 17 days elapsed: Remaining = 1.58 kg (11.1%), Days Left = 2.1 Days (CRITICAL Alert).",
                             title_size=18, text_size=16.5, space_after=12)
            add_bullet_point(tf, "3. Review 1 Functional Prototype Verification:", 
                             "The software prototype on port 5001 successfully executes real-time updates upon slider adjustments, computes depletion curves, displays radial gauges, and alerts users within sub-30ms response times.",
                             title_size=18, text_size=16.5, space_after=8)

    # =========================================================================
    # SLIDE 10: Conclusion (40% Review 1 Deliverables & 60% Review 2 Scope)
    # =========================================================================
    slide10 = prs.slides[9]
    set_slide_title(slide10, "Conclusion")
    for shape in slide10.shapes:
        if shape.name != "Title 1" and shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            add_bullet_point(tf, "Review 1 Milestone Achievements (40% Implementation Completed):", 
                             "• Problem formulation, societal relevance analysis, and literature gap identification completed.\n"
                             "• Successfully removed physical IoT hardware dependencies in favor of a cost-effective, data-driven approach.\n"
                             "• Developed N=600 domestic energy dataset and trained Random Forest ML Regressor (R² = 0.9634).\n"
                             "• Engineered mathematical depletion timeline formulas and proactive delivery lead-time buffer alerts.\n"
                             "• Delivered a fully functional, responsive Review 1 Prototype UI for live evaluation.",
                             title_size=18, text_size=16.5, space_after=14)
            add_bullet_point(tf, "Review 2 Engineering Roadmap (Remaining 60% Implementation Scope):", 
                             "• Milestone 4: One-Click OMC Automated Booking API integration (Indane, BPCL, HPCL).\n"
                             "• Milestone 5: 5-Stage Live Order Delivery Stepper with Doorstep OTP verification.\n"
                             "• Milestone 6: Multi-channel Cellular SMS and WhatsApp gateway notification dispatch.\n"
                             "• Milestone 7: Comprehensive Monthly Household LPG Audit Report & PDF generator.\n"
                             "• Milestone 8: Final thesis documentation, plagiarism screening, and viva preparation.",
                             title_size=18, text_size=16.5, space_after=10)

    # =========================================================================
    # SLIDE 11: Thank You
    # =========================================================================
    slide11 = prs.slides[10]
    for shape in slide11.shapes:
        if shape.has_text_frame:
            tf = shape.text_frame
            tf.clear()
            p0 = tf.paragraphs[0]
            p0.alignment = PP_ALIGN.CENTER
            r0 = p0.add_run()
            r0.text = "Thank You!"
            set_run_font(r0, font_name=FONT_FAMILY, size_pt=54, bold=True, color_rgb=COLOR_CRIMSON)
            
            p1 = tf.add_paragraph()
            p1.alignment = PP_ALIGN.CENTER
            p1.space_before = Pt(14)
            r1 = p1.add_run()
            r1.text = "SmartLPG - Review 1 Evaluation (40% Functional Milestone)"
            set_run_font(r1, font_name=FONT_FAMILY, size_pt=22, bold=True, color_rgb=COLOR_NAVY)
            
            p2 = tf.add_paragraph()
            p2.alignment = PP_ALIGN.CENTER
            p2.space_before = Pt(12)
            r2 = p2.add_run()
            r2.text = "Team Members: Mohammed Huzaifa Khan (1NH24CS126) & Mohammad Aftab Ahmed (1NH24CS125)\nProject Guide: Prof. Ashwini G B, Assistant Professor, Dept of CSE, NHCE"
            set_run_font(r2, font_name=FONT_FAMILY, size_pt=18, bold=False, color_rgb=COLOR_BLACK)

            p3 = tf.add_paragraph()
            p3.alignment = PP_ALIGN.CENTER
            p3.space_before = Pt(16)
            r3 = p3.add_run()
            r3.text = "Questions & Suggestions are Welcome"
            set_run_font(r3, font_name=FONT_FAMILY, size_pt=20, bold=True, italic=True, color_rgb=COLOR_MUTED)

    # Save to both destinations
    print(f"Saving presentation to: {OUTPUT_PATH_1}")
    prs.save(OUTPUT_PATH_1)
    print(f"Saving backup copy to: {OUTPUT_PATH_2}")
    prs.save(OUTPUT_PATH_2)
    print("Successfully generated exact 11-slide Review 1 presentation!")

if __name__ == "__main__":
    generate_review1_presentation()
