import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_PATH = os.path.join("first review", "implementation_flowchart.png")

def create_flowchart():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Background canvas
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Title
    ax.text(7, 8.1, "SmartLPG: Implementation Plan & Module Roadmap",
            ha='center', va='center', fontsize=18, fontweight='bold', color='#111827', fontfamily='sans-serif')
    ax.text(7, 7.7, "40% Target Milestone (Review 1 - Completed) vs 60% Deployment Roadmap (Review 2 - Planned)",
            ha='center', va='center', fontsize=11, color='#4b5563', fontfamily='sans-serif')

    # Container Box for Phase 1 (Review 1: 40% Completed)
    rect1 = patches.FancyBboxPatch((0.4, 3.8), 13.2, 3.5, boxstyle="round,pad=0.2",
                                  ec="#059669", fc="#ecfdf5", lw=2, linestyle='-')
    ax.add_patch(rect1)
    ax.text(0.7, 7.0, "PHASE 1: REVIEW 1 MILESTONE (40% COMPLETED - FUNCTIONAL BASELINE)",
            fontsize=11, fontweight='bold', color="#065f46")
    ax.text(12.3, 7.0, "[✓ 40% ACHIEVED]",
            fontsize=10, fontweight='bold', color="#059669", ha='right')

    # Phase 1 Steps (5 horizontal boxes)
    p1_boxes = [
        ("Step 1: Household Input", "• Household Size\n• Meals Cooked/Day\n• Daily Cooking Hours\n• Cylinder Size (14.2kg)\n• Refill Date", 0.7, 4.1, 2.2),
        ("Step 2: Dataset Engine", "• Synthetic Domestic\n  Energy Dataset (N=600)\n• Usage Feature Scaling\n• No Hardware/IoT needed\n• Data-driven modeling", 3.3, 4.1, 2.2),
        ("Step 3: ML Depletion Model", "• Scikit-learn Random\n  Forest Regressor\n• Accurate Burn Rate\n  (kg/day, R² ≈ 0.96)\n• Consumption Forecast", 5.9, 4.1, 2.2),
        ("Step 4: Buffer Alert Engine", "• Days Remaining Calc\n• Empty Date Prediction\n• Delivery Lead Time Buffer\n• Color-Coded Alerts\n  (Normal / Critical)", 8.5, 4.1, 2.2),
        ("Step 5: Review 1 Prototype", "• Functional Web GUI\n• Live Depletion Gauge\n• Proactive Banner\n• Profile Recalibration\n• Ready for Evaluation", 11.1, 4.1, 2.2),
    ]

    for title, desc, x, y, w in p1_boxes:
        box = patches.FancyBboxPatch((x, y), w, 2.6, boxstyle="round,pad=0.1",
                                    ec="#10b981", fc="#ffffff", lw=1.5)
        ax.add_patch(box)
        ax.text(x + w/2, y + 2.3, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color="#065f46")
        ax.text(x + 0.15, y + 1.1, desc, ha='left', va='center', fontsize=8, color="#1f2937", linespacing=1.35)

    # Arrows for Phase 1
    arrow_props = dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6, headlength=6)
    for x_end in [3.3, 5.9, 8.5, 11.1]:
        ax.annotate('', xy=(x_end, 5.4), xytext=(x_end - 0.4, 5.4), arrowprops=arrow_props)

    # Vertical Handover Arrow from Phase 1 to Phase 2
    down_arrow = dict(facecolor='#2563eb', edgecolor='#2563eb', width=2, headwidth=8, headlength=8)
    ax.annotate('', xy=(6.5, 3.4), xytext=(6.5, 3.8), arrowprops=down_arrow)
    ax.text(7.6, 3.6, "Handover to Review 2", fontsize=9, fontweight='bold', color="#1d4ed8")

    # Container Box for Phase 2 (Review 2: 60% Planned)
    rect2 = patches.FancyBboxPatch((0.4, 0.4), 13.2, 2.9, boxstyle="round,pad=0.2",
                                  ec="#3b82f6", fc="#eff6ff", lw=2, linestyle='--')
    ax.add_patch(rect2)
    ax.text(0.7, 3.0, "PHASE 2: REVIEW 2 MILESTONE (REMAINING 60% PLANNED - ADVANCED CAPABILITIES)",
            fontsize=11, fontweight='bold', color="#1e40af")
    ax.text(12.3, 3.0, "[PLANNED / IN PROGRESS]",
            fontsize=10, fontweight='bold', color="#2563eb", ha='right')

    # Phase 2 Steps (4 horizontal boxes)
    p2_boxes = [
        ("Step 6: 1-Click Booking", "• OMC Provider APIs\n  (Indane, Bharat, HP)\n• Booking Reference Gen\n• Subsidized Tariff Rates", 0.9, 0.7, 2.7),
        ("Step 7: 5-Stage Stepper", "• Booked ➔ Confirmed\n• Dispatched ➔ Out\n• Doorstep OTP Check\n• Delivery Agent Info", 3.9, 0.7, 2.7),
        ("Step 8: Cellular Alerts", "• Twilio / SMS Gateway\n• Auto Mobile SMS\n• Low-Reserve WhatsApp\n• Outage Warning Ping", 6.9, 0.7, 2.7),
        ("Step 9: Energy Advisor", "• Multi-Factor Flame Modes\n• Batch Cooking Advice\n• Printable PDF Audit\n• Final Bound Thesis", 9.9, 0.7, 2.7),
    ]

    for title, desc, x, y, w in p2_boxes:
        box = patches.FancyBboxPatch((x, y), w, 2.0, boxstyle="round,pad=0.1",
                                    ec="#60a5fa", fc="#ffffff", lw=1.5, linestyle='--')
        ax.add_patch(box)
        ax.text(x + w/2, y + 1.7, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color="#1e3a8a")
        ax.text(x + 0.2, y + 0.85, desc, ha='left', va='center', fontsize=8, color="#374151", linespacing=1.35)

    # Arrows for Phase 2
    arrow_props_p2 = dict(facecolor='#3b82f6', edgecolor='#3b82f6', width=1.5, headwidth=6, headlength=6)
    for x_end in [3.9, 6.9, 9.9]:
        ax.annotate('', xy=(x_end, 1.7), xytext=(x_end - 0.3, 1.7), arrowprops=arrow_props_p2)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, bbox_inches='tight')
    plt.close()
    print(f"Flowchart saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_flowchart()
