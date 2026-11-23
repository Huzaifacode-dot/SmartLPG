// SmartLPG Review 1 Prototype Application Controller
document.addEventListener("DOMContentLoaded", () => {
    // Input Elements
    const cylinderCapacity = document.getElementById("cylinderCapacity");
    const refillDate = document.getElementById("refillDate");
    const familySize = document.getElementById("familySize");
    const familySizeVal = document.getElementById("familySizeVal");
    const mealsPerDay = document.getElementById("mealsPerDay");
    const mealsPerDayVal = document.getElementById("mealsPerDayVal");
    const cookingHours = document.getElementById("cookingHours");
    const cookingHoursVal = document.getElementById("cookingHoursVal");
    const flameIntensity = document.getElementById("flameIntensity");
    const leadTime = document.getElementById("leadTime");
    const recalculateBtn = document.getElementById("recalculateBtn");

    // Output Telemetry Elements
    const gaugeCircle = document.getElementById("gaugeCircle");
    const percentRemaining = document.getElementById("percentRemaining");
    const daysRemaining = document.getElementById("daysRemaining");
    const depletionDate = document.getElementById("depletionDate");
    const bookingWindow = document.getElementById("bookingWindow");
    const kgRemaining = document.getElementById("kgRemaining");
    const burnRate = document.getElementById("burnRate");
    const daysConsumed = document.getElementById("daysConsumed");
    const leadBuffer = document.getElementById("leadBuffer");

    // Math Proof Elements
    const mathBurnRate = document.getElementById("mathBurnRate");
    const mathRemaining = document.getElementById("mathRemaining");
    const mathDays = document.getElementById("mathDays");

    // Alert Ribbon Elements
    const alertRibbon = document.getElementById("alertRibbon");
    const alertTitle = document.getElementById("alertTitle");
    const alertMessage = document.getElementById("alertMessage");
    const urgencyBadge = document.getElementById("urgencyBadge");

    // Modal Elements
    const scopeModal = document.getElementById("scopeModal");
    const viewScopeBtn = document.getElementById("viewScopeBtn");
    const closeModalBtn = document.getElementById("closeModalBtn");
    const closeModalFooterBtn = document.getElementById("closeModalFooterBtn");

    // Initialize Default Refill Date (22 days prior)
    const today = new Date();
    const defaultRefill = new Date(today);
    defaultRefill.setDate(today.getDate() - 22);
    refillDate.value = defaultRefill.toISOString().split("T")[0];

    // Helper: SVG Circumference
    const CIRCUMFERENCE = 2 * Math.PI * 70; // r=70 -> ~439.82

    // Update Slider Value Displays
    function updateSliderLabels() {
        familySizeVal.textContent = `${familySize.value} persons`;
        mealsPerDayVal.textContent = `${mealsPerDay.value} meals`;
        cookingHoursVal.textContent = `${parseFloat(cookingHours.value).toFixed(1)} hrs/day`;
    }

    // Trigger API Prediction
    async function fetchPrediction() {
        const payload = {
            cylinder_capacity: parseFloat(cylinderCapacity.value),
            refill_date: refillDate.value,
            family_size: parseInt(familySize.value),
            meals_per_day: parseInt(mealsPerDay.value),
            cooking_hours: parseFloat(cookingHours.value),
            lead_time_days: parseInt(leadTime.value),
            flame_intensity: flameIntensity.value
        };

        try {
            const res = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("API call failed");
            const data = await res.json();
            renderPredictionResults(data);
        } catch (err) {
            console.error("Error communicating with prediction server:", err);
        }
    }

    function renderPredictionResults(data) {
        // Update Gauge
        const pct = Math.max(0, Math.min(100, data.percentage_remaining));
        percentRemaining.textContent = `${pct}%`;
        
        const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
        gaugeCircle.style.strokeDashoffset = offset;

        // Dynamic Gauge color based on percentage
        if (pct <= 20) {
            gaugeCircle.style.stroke = "#ef4444"; // Red
        } else if (pct <= 35) {
            gaugeCircle.style.stroke = "#f59e0b"; // Amber
        } else {
            gaugeCircle.style.stroke = "#10b981"; // Green
        }

        // Hero Countdown Numbers
        daysRemaining.textContent = data.days_remaining;
        depletionDate.textContent = data.depletion_date;
        bookingWindow.textContent = data.recommended_booking_date;

        // Sub-metric chips
        kgRemaining.textContent = `${data.gas_remaining_kg} kg`;
        burnRate.textContent = `${data.predicted_daily_burn_rate_kg} kg/day`;
        daysConsumed.textContent = `${data.days_since_refill} Days`;
        leadBuffer.textContent = `${data.lead_time_days} Days Lead Time`;

        // Mathematical formulas display
        mathBurnRate.textContent = data.predicted_daily_burn_rate_kg;
        mathRemaining.textContent = data.gas_remaining_kg;
        mathDays.textContent = data.days_remaining;

        // Alert Banner
        alertRibbon.className = "alert-ribbon";
        urgencyBadge.textContent = data.urgency;

        if (data.urgency === "CRITICAL") {
            alertRibbon.classList.add("alert-critical");
            alertTitle.textContent = "Urgent: Refill Buffer Exhausted!";
        } else if (data.urgency === "WARNING") {
            alertRibbon.classList.add("alert-warning");
            alertTitle.textContent = "Refill Advisory Window Open";
        } else {
            alertRibbon.classList.add("alert-optimal");
            alertTitle.textContent = "Cylinder Reserve Adequate";
        }
        alertMessage.textContent = data.alert_message;
    }

    // Event Listeners for Live Interactivity
    [familySize, mealsPerDay, cookingHours].forEach(slider => {
        slider.addEventListener("input", () => {
            updateSliderLabels();
            fetchPrediction();
        });
    });

    [cylinderCapacity, refillDate, flameIntensity, leadTime].forEach(input => {
        input.addEventListener("change", fetchPrediction);
    });

    recalculateBtn.addEventListener("click", fetchPrediction);

    // Modal Handlers
    viewScopeBtn.addEventListener("click", () => scopeModal.classList.add("active"));
    closeModalBtn.addEventListener("click", () => scopeModal.classList.remove("active"));
    closeModalFooterBtn.addEventListener("click", () => scopeModal.classList.remove("active"));
    scopeModal.addEventListener("click", (e) => {
        if (e.target === scopeModal) scopeModal.classList.remove("active");
    });

    // Initial Execution
    updateSliderLabels();
    fetchPrediction();
});
