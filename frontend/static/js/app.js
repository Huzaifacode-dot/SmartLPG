// SmartLPG Core Frontend Application Logic

let currentCylinder = null;
let currentProfile = null;
let activeBooking = null;
let refillHistoryData = [];
let currentChartMode = 'history'; // 'history' or 'projection'
let simFlame = 'Medium';
let simEfficiency = false;

// Safe DOM Helper Functions
const setTxt = (id, val) => {
  const el = document.getElementById(id);
  if (el && val !== undefined && val !== null) el.textContent = val;
};

const setVal = (id, val) => {
  const el = document.getElementById(id);
  if (el && val !== undefined && val !== null) el.value = val;
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadAllData();
  setupEventListeners();
  setupWhatIfSimulator();
  
  // Refresh cylinder telemetry every 15 seconds
  setInterval(refreshTelemetry, 15000);
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('smartlpg_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.innerHTML = savedTheme === 'dark' ? '☀️' : '🌙';
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const newTheme = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('smartlpg_theme', newTheme);
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
  }
  // Redraw chart to reflect theme colors
  renderCurrentChart();
}

// Global Data Fetch
async function loadAllData() {
  await Promise.all([
    fetchProfile(),
    fetchCylinderStatus(),
    fetchActiveBooking(),
    fetchRefillHistory(),
    fetchAlerts(),
    fetchIoTTelemetry()
  ]);
}

// Helper for purpose selector
function selectPurpose(purpose) {
  setVal('famUsagePurpose', purpose);
  const houseBtn = document.getElementById('purposeHouseholdBtn');
  const commBtn = document.getElementById('purposeCommercialBtn');
  if (purpose === 'Commercial') {
    commBtn?.classList.add('active');
    houseBtn?.classList.remove('active');
  } else {
    houseBtn?.classList.add('active');
    commBtn?.classList.remove('active');
  }
}

// Fetch Profile
async function fetchProfile() {
  try {
    const res = await fetch('/api/profile');
    if (!res.ok) return;
    const data = await res.json();
    currentProfile = data;
    
    // Header & Meta Elements
    setTxt('agencyDisplay', data.distributor_name);
    
    // Fill Profile Modal (Registered User & Gas Provider Details)
    setTxt('profileSummaryName', data.primary_name);
    setTxt('profileSummaryPhone', data.phone);
    setTxt('profileSummaryConsumer', data.consumer_number);

    setVal('profileFullName', data.primary_name);
    setVal('profileMobile', data.phone);
    setVal('profileEmail', data.email);
    setVal('profileAddress', data.address);
    setVal('profileConnectionType', data.connection_type || '14.2 kg Subsidized Domestic (Single Cylinder)');
    setVal('profileProvider', data.lpg_provider);
    setVal('profileConsumerNo', data.consumer_number);
    setVal('profileDistributor', data.distributor_name);
    setVal('profileDistributorPhone', data.distributor_phone || '+91 80 2520 1199');
    setVal('profileLeadTime', data.lead_time_days || 3);
    
    // Fill Family Modal
    setVal('famHouseholdClassification', data.household_classification || 'Family Household');
    setVal('famTotalMembers', data.family_size || 4);
    setVal('famAdultsCount', data.adults_count || 2);
    setVal('famChildrenCount', data.children_count || 2);
    setVal('famCookingHours', data.daily_cooking_hours || 2.8);
    setVal('famMealsPerDay', data.cooking_meals_per_day || 3);
    setVal('famCylinderCapacity', data.cylinder_capacity || 14.2);
    setVal('famLastRefillDate', data.date_of_last_refill || '2026-10-12');
    setVal('famRefillPrice', data.current_refill_price || 858.00);

    // Update classification cards active state
    const currentClass = data.household_classification || 'Family Household';
    document.querySelectorAll('#classificationGrid .classification-card').forEach(card => {
      if (card.getAttribute('data-classification') === currentClass) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
      }
    });

    // Update purpose buttons
    selectPurpose(data.usage_purpose || 'Household');

    // Sync simulator inputs if present
    const simFam = document.getElementById('simFamilySize');
    if (simFam) {
      simFam.value = data.family_size || 4;
      setTxt('simFamilyVal', data.family_size || 4);
    }
    const simM = document.getElementById('simMeals');
    if (simM) {
      simM.value = data.cooking_meals_per_day || 3;
      setTxt('simMealsVal', data.cooking_meals_per_day || 3);
    }
    const simH = document.getElementById('simHours');
    if (simH) {
      simH.value = data.daily_cooking_hours || 2.8;
      setTxt('simHoursVal', `${data.daily_cooking_hours || 2.8} hrs`);
    }
    const simC = document.getElementById('simCylinderCap');
    if (simC && data.cylinder_capacity) {
      simC.value = String(data.cylinder_capacity);
    }
  } catch (err) {
    console.error('Error fetching profile:', err);
  }
}

// Fetch Cylinder Status & ML Analytics
async function fetchCylinderStatus() {
  try {
    const res = await fetch('/api/cylinder/current');
    if (!res.ok) return;
    const data = await res.json();
    currentCylinder = data;
    renderCylinderCard(data);
    renderPredictionCard(data);
    renderAlertBanner(data);
    if (currentChartMode === 'projection') {
      drawDepletionCountdownChart(data);
    }
  } catch (err) {
    console.error('Error fetching cylinder status:', err);
  }
}

function renderCylinderCard(cyl) {
  const pct = Math.min(100, Math.max(0, cyl.percentage_remaining));
  const gasWeight = cyl.current_gas_kg;
  const tareWeight = cyl.tare_weight;
  const grossWeight = cyl.gross_weight;
  
  // Update Cylinder Visual
  const fluid = document.getElementById('cylinderFluid');
  if (fluid) {
    fluid.style.height = `${pct}%`;
    if (pct <= 20) {
      fluid.style.background = 'linear-gradient(180deg, #f43f5e, #be123c)';
      fluid.style.boxShadow = '0 -4px 20px rgba(244, 63, 94, 0.4)';
    } else if (pct <= 45) {
      fluid.style.background = 'linear-gradient(180deg, #f59e0b, #d97706)';
      fluid.style.boxShadow = '0 -4px 20px rgba(245, 158, 11, 0.4)';
    } else {
      fluid.style.background = 'linear-gradient(180deg, #10b981, #059669)';
      fluid.style.boxShadow = '0 -4px 20px rgba(16, 185, 129, 0.4)';
    }
  }
  
  setTxt('gasPercentageVal', `${pct}%`);
  setTxt('gasWeightVal', `${gasWeight} kg Net LPG`);
  setTxt('grossWeightVal', `${grossWeight} kg`);
  setTxt('tareWeightVal', `${tareWeight} kg`);
  setTxt('cylSerialVal', cyl.cylinder_serial);
  setTxt('cylInstallDateVal', cyl.installed_date);
  
  const statusBadge = document.getElementById('cylinderStatusBadge');
  if (statusBadge) {
    statusBadge.textContent = cyl.status;
    if (cyl.is_leak_detected) {
      statusBadge.className = 'status-pill';
      statusBadge.style.color = '#f43f5e';
      statusBadge.style.borderColor = 'rgba(244, 63, 94, 0.4)';
      statusBadge.style.background = 'rgba(244, 63, 94, 0.15)';
    } else if (pct <= 20) {
      statusBadge.className = 'status-pill';
      statusBadge.style.color = '#f59e0b';
      statusBadge.style.borderColor = 'rgba(245, 158, 11, 0.4)';
      statusBadge.style.background = 'rgba(245, 158, 11, 0.15)';
    } else {
      statusBadge.className = 'status-pill';
      statusBadge.style.color = '#10b981';
      statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
      statusBadge.style.background = 'rgba(16, 185, 129, 0.15)';
    }
  }

  // Check Leak State
  const leakBanner = document.getElementById('emergencyLeakBanner');
  if (leakBanner) {
    if (cyl.is_leak_detected) {
      leakBanner.classList.add('active');
    } else {
      leakBanner.classList.remove('active');
    }
  }
}

function renderPredictionCard(cyl) {
  setTxt('predDaysVal', `${cyl.days_remaining} Days`);
  setTxt('predBurnRateVal', `${cyl.daily_burn_rate_kg} kg / day`);
  setTxt('predDailyCostVal', `₹${cyl.daily_cost_inr || (cyl.daily_burn_rate_kg * 60.42).toFixed(2)} / day`);
  setTxt('predDepletionDateVal', cyl.depletion_date_formatted || cyl.depletion_date);
  setTxt('predRecBookingVal', cyl.recommended_booking_date_formatted || cyl.recommended_booking_date);
  setTxt('predConfidenceVal', `🎯 ${cyl.confidence_score || 97}% Confidence`);
  
  const bookBtn = document.getElementById('quickBookRefillBtn');
  if (bookBtn) {
    if (cyl.refill_needed) {
      bookBtn.innerHTML = `⚡ Book Refill Now (${cyl.days_remaining}d Left)`;
      bookBtn.classList.add('pulse-glow');
    } else {
      bookBtn.innerHTML = `⚡ Book LPG Refill (${cyl.provider || 'Indane'})`;
      bookBtn.classList.remove('pulse-glow');
    }
  }
}

function renderAlertBanner(cyl) {
  const banner = document.getElementById('alertBannerCard');
  if (!banner) return;
  
  if (cyl.refill_needed && !cyl.is_leak_detected) {
    banner.style.display = 'flex';
    setTxt('alertTitleText', cyl.urgency === 'CRITICAL' ? '⚠️ Critical Gas Shortage Warning' : '🔔 LPG Refill Advisory');
    setTxt('alertDescText', cyl.alert_message);
  } else {
    banner.style.display = 'none';
  }
}

// Fetch Active Booking & Tracking
async function fetchActiveBooking() {
  try {
    const res = await fetch('/api/booking/active');
    if (!res.ok) return;
    const data = await res.json();
    activeBooking = data;
    renderTrackingSection(data);
  } catch (err) {
    console.error('Error fetching active booking:', err);
  }
}

function renderTrackingSection(booking) {
  const noBookingBox = document.getElementById('noActiveBookingState');
  const activeBookingBox = document.getElementById('activeBookingState');
  
  if (!booking || !booking.booking_id) {
    if (noBookingBox) noBookingBox.style.display = 'block';
    if (activeBookingBox) activeBookingBox.style.display = 'none';
    return;
  }
  
  if (noBookingBox) noBookingBox.style.display = 'none';
  if (activeBookingBox) activeBookingBox.style.display = 'block';
  
  setTxt('trackBookingIdVal', booking.booking_id);
  setTxt('trackEstDeliveryVal', booking.estimated_delivery_date);
  setTxt('trackAgentNameVal', booking.delivery_agent_name || 'Assigned Partner');
  setTxt('trackAgentPhoneVal', booking.delivery_agent_phone || '--');
  setTxt('trackOtpVal', booking.delivery_otp || '----');
  
  const currentStep = booking.tracking_step || 1;
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`stepItem${i}`);
    if (!stepEl) continue;
    stepEl.classList.remove('completed', 'active');
    if (i < currentStep) {
      stepEl.classList.add('completed');
    } else if (i === currentStep) {
      stepEl.classList.add('active');
    }
  }
  
  const advanceBtn = document.getElementById('advanceStatusBtn');
  if (advanceBtn) {
    if (currentStep >= 5) {
      advanceBtn.textContent = '✓ Refill Completed';
      advanceBtn.disabled = true;
    } else {
      const stepNames = ['Confirm Order', 'Dispatch Cylinder', 'Out for Delivery', 'Deliver & Mount Cylinder'];
      advanceBtn.textContent = `▶ Advance to: ${stepNames[currentStep - 1]}`;
      advanceBtn.disabled = false;
    }
  }
}

// Advance Booking Step (Simulation)
async function advanceTrackingStatus() {
  if (!activeBooking || !activeBooking.booking_id) return;
  try {
    const res = await fetch(`/api/booking/advance-step/${activeBooking.booking_id}`, { method: 'POST' });
    const data = await res.json();
    showToast(`Order updated to: ${data.status}`);
    await fetchActiveBooking();
    await fetchCylinderStatus();
    await fetchRefillHistory();
    await fetchAlerts();
  } catch (err) {
    console.error('Error advancing tracking:', err);
  }
}

// Fetch Refill History
async function fetchRefillHistory() {
  try {
    const res = await fetch('/api/refills');
    if (!res.ok) return;
    const data = await res.json();
    refillHistoryData = data.history || [];
    renderRefillHistoryTable(refillHistoryData);
    renderRefillMetrics(data.metrics);
    renderCurrentChart();
  } catch (err) {
    console.error('Error fetching refills:', err);
  }
}

function renderRefillHistoryTable(rows) {
  const tbody = document.getElementById('refillHistoryTbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  
  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${r.booking_id}</strong></td>
      <td>${r.booking_date}</td>
      <td>${r.delivery_date}</td>
      <td>${r.provider}</td>
      <td>₹${r.amount_paid.toFixed(2)}</td>
      <td><strong>${r.days_lasted} Days</strong></td>
      <td>${r.avg_daily_consumption.toFixed(3)} kg/d</td>
      <td><span class="badge-status delivered">${r.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderRefillMetrics(m) {
  if (!m) return;
  setTxt('metricTotalRefills', m.total_refills);
  setTxt('metricTotalSpent', `₹${m.total_spent_inr.toLocaleString()}`);
  setTxt('metricAvgCycle', `${m.avg_cycle_days} Days`);
  setTxt('metricAvgBurn', `${m.avg_burn_rate_kg} kg/d`);
}

// Chart Rendering Router
function renderCurrentChart() {
  if (currentChartMode === 'projection' && currentCylinder) {
    drawDepletionCountdownChart(currentCylinder);
  } else {
    drawConsumptionChart(refillHistoryData);
  }
}

// Mode 1: Historical Duration Chart
function drawConsumptionChart(history) {
  const canvas = document.getElementById('consumptionChartCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  
  const w = rect.width;
  const h = rect.height;
  ctx.clearRect(0, 0, w, h);
  
  setTxt('chartCaptionText', '● Durations reflect actual days lasted per 14.2 kg cylinder');
  
  if (!history || history.length === 0) return;
  
  const padding = { top: 25, right: 30, bottom: 40, left: 45 };
  const graphW = w - padding.left - padding.right;
  const graphH = h - padding.top - padding.bottom;
  
  // Grid lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 1;
  const numGridLines = 4;
  for (let i = 0; i <= numGridLines; i++) {
    const y = padding.top + (graphH / numGridLines) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(w - padding.right, y);
    ctx.stroke();
    
    ctx.fillStyle = '#64748b';
    ctx.font = '10.5px Plus Jakarta Sans';
    ctx.textAlign = 'right';
    const val = Math.round(40 - (40 / numGridLines) * i);
    ctx.fillText(`${val}d`, padding.left - 8, y + 4);
  }
  
  const sorted = [...history].reverse();
  const stepX = graphW / (sorted.length - 1 || 1);
  const maxDays = 40;
  
  // Area gradient
  const grad = ctx.createLinearGradient(0, padding.top, 0, h - padding.bottom);
  grad.addColorStop(0, 'rgba(255, 119, 0, 0.35)');
  grad.addColorStop(1, 'rgba(255, 119, 0, 0.0)');
  
  ctx.beginPath();
  sorted.forEach((pt, i) => {
    const x = padding.left + i * stepX;
    const y = padding.top + graphH * (1 - pt.days_lasted / maxDays);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  
  ctx.strokeStyle = '#ff7700';
  ctx.lineWidth = 3;
  ctx.stroke();
  
  ctx.lineTo(padding.left + (sorted.length - 1) * stepX, h - padding.bottom);
  ctx.lineTo(padding.left, h - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
  
  // Points
  sorted.forEach((pt, i) => {
    const x = padding.left + i * stepX;
    const y = padding.top + graphH * (1 - pt.days_lasted / maxDays);
    
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#ff7700';
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px Plus Jakarta Sans';
    ctx.textAlign = 'center';
    const dateLabel = pt.booking_date.substring(5);
    ctx.fillText(dateLabel, x, h - padding.bottom + 20);
    
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 11px Outfit';
    ctx.fillText(`${pt.days_lasted}d`, x, y - 10);
  });
}

// Mode 2: Live Depletion Countdown & Buffer Curve
function drawDepletionCountdownChart(cyl) {
  const canvas = document.getElementById('consumptionChartCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio;
  canvas.height = rect.height * window.devicePixelRatio;
  ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  
  const w = rect.width;
  const h = rect.height;
  ctx.clearRect(0, 0, w, h);
  
  setTxt('chartCaptionText', `● Real-time countdown from ${cyl.current_gas_kg} kg to 0 kg. Safe buffer: ≤ ${cyl.lead_time_days} days.`);
  
  const padding = { top: 25, right: 30, bottom: 40, left: 45 };
  const graphW = w - padding.left - padding.right;
  const graphH = h - padding.top - padding.bottom;
  
  const totalDays = Math.max(5, Math.ceil(cyl.days_remaining));
  const maxGas = Math.max(3.0, cyl.current_gas_kg * 1.2);
  const burnRate = cyl.daily_burn_rate_kg || 0.42;
  const leadTime = cyl.lead_time_days || 3;
  
  // Grid
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (graphH / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(w - padding.right, y);
    ctx.stroke();
    
    const kgVal = (maxGas * (1 - i / 4)).toFixed(1);
    ctx.fillStyle = '#64748b';
    ctx.font = '10.5px Plus Jakarta Sans';
    ctx.textAlign = 'right';
    ctx.fillText(`${kgVal}kg`, padding.left - 8, y + 4);
  }
  
  // Safe buffer threshold area (Days <= leadTime)
  const bufferStartX = padding.left + graphW * Math.max(0, (totalDays - leadTime) / totalDays);
  ctx.fillStyle = 'rgba(244, 63, 94, 0.12)';
  ctx.fillRect(bufferStartX, padding.top, w - padding.right - bufferStartX, graphH);
  
  // Buffer Label
  ctx.fillStyle = '#f43f5e';
  ctx.font = 'bold 10px Plus Jakarta Sans';
  ctx.textAlign = 'center';
  ctx.fillText('CRITICAL LEAD BUFFER', (bufferStartX + w - padding.right) / 2, padding.top + 14);
  
  // Draw Countdown Curve
  const points = [];
  for (let d = 0; d <= totalDays; d++) {
    const gasRem = Math.max(0, cyl.current_gas_kg - d * burnRate);
    const x = padding.left + (d / totalDays) * graphW;
    const y = padding.top + graphH * (1 - gasRem / maxGas);
    points.push({ x, y, day: d, gas: gasRem });
  }
  
  // Gradient fill
  const grad = ctx.createLinearGradient(0, padding.top, 0, h - padding.bottom);
  grad.addColorStop(0, 'rgba(56, 189, 248, 0.35)');
  grad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
  
  ctx.beginPath();
  points.forEach((pt, i) => {
    if (i === 0) ctx.moveTo(pt.x, pt.y);
    else ctx.lineTo(pt.x, pt.y);
  });
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 3;
  ctx.stroke();
  
  ctx.lineTo(points[points.length - 1].x, h - padding.bottom);
  ctx.lineTo(padding.left, h - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
  
  // Plotted points
  points.forEach((pt, i) => {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, i === 0 ? 6 : 4, 0, Math.PI * 2);
    ctx.fillStyle = i === 0 ? '#10b981' : (pt.gas <= 0.2 ? '#f43f5e' : '#38bdf8');
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();
    
    // Label day
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Plus Jakarta Sans';
    ctx.textAlign = 'center';
    ctx.fillText(`+${pt.day}d`, pt.x, h - padding.bottom + 18);
    
    // Weight value on key points
    if (i === 0 || i === points.length - 1 || pt.day === totalDays - leadTime) {
      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 10px Outfit';
      ctx.fillText(`${pt.gas.toFixed(1)}kg`, pt.x, pt.y - 10);
    }
  });
}

// Enhanced What-If ML Simulator
function setupWhatIfSimulator() {
  const familySlider = document.getElementById('simFamilySize');
  const mealsSlider = document.getElementById('simMeals');
  const hoursSlider = document.getElementById('simHours');
  const capSelect = document.getElementById('simCylinderCap');
  const effToggle = document.getElementById('simEfficiencyMode');
  
  if (!familySlider || !mealsSlider || !hoursSlider) return;
  
  // Flame pill buttons
  document.querySelectorAll('#simFlameGroup .flame-pill-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('#simFlameGroup .flame-pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      simFlame = btn.getAttribute('data-flame') || 'Medium';
      updateSim();
    });
  });
  
  // Efficiency mode toggle
  effToggle?.addEventListener('change', (e) => {
    simEfficiency = e.target.checked;
    updateSim();
  });
  
  capSelect?.addEventListener('change', updateSim);
  
  const updateSim = async () => {
    setTxt('simFamilyVal', familySlider.value);
    setTxt('simMealsVal', mealsSlider.value);
    setTxt('simHoursVal', `${hoursSlider.value} hrs`);
    
    const cap = parseFloat(capSelect?.value || '14.2');
    
    try {
      const res = await fetch('/api/predict/what-if', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          family_size: familySlider.value,
          meals_per_day: mealsSlider.value,
          cooking_hours: hoursSlider.value,
          cylinder_capacity: cap,
          flame_intensity: simFlame,
          efficiency_mode: simEfficiency,
          refill_price: cap === 14.2 ? 858.0 : (cap === 5.0 ? 320.0 : 1650.0)
        })
      });
      const data = await res.json();
      setTxt('simResultBurnRate', `${data.predicted_burn_rate_kg} kg/d`);
      setTxt('simResultLongevity', `~${data.estimated_cylinder_life_days} Days`);
      setTxt('simResultDailyCost', `₹${data.daily_cost_inr}/d`);
      setTxt('simResultMonthly', `₹${data.monthly_cost_inr} / Mo`);
      setTxt('simConfidenceBadge', `🎯 ${data.confidence_score || 97}% Confidence`);
    } catch (err) {
      console.error('Error running what-if:', err);
    }
  };
  
  familySlider.addEventListener('input', updateSim);
  mealsSlider.addEventListener('input', updateSim);
  hoursSlider.addEventListener('input', updateSim);
  
  // Trigger initial
  updateSim();
}

// Fetch Alerts
async function fetchAlerts() {
  try {
    const res = await fetch('/api/alerts');
    if (!res.ok) return;
    const data = await res.json();
    const bellBadge = document.getElementById('unreadAlertsBadge');
    if (bellBadge) {
      bellBadge.textContent = data.unread_count;
      bellBadge.style.display = data.unread_count > 0 ? 'flex' : 'none';
    }
    renderAlertsList(data.alerts);
  } catch (err) {
    console.error('Error fetching alerts:', err);
  }
}

function renderAlertsList(alerts) {
  const container = document.getElementById('alertsListContainer');
  if (!container) return;
  container.innerHTML = '';
  
  if (!alerts || alerts.length === 0) {
    container.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No new alerts</div>';
    return;
  }
  
  alerts.forEach(a => {
    const item = document.createElement('div');
    item.style.padding = '12px 16px';
    item.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
    item.style.fontSize = '13px';
    
    const icon = a.alert_type === 'critical' ? '🚨' : (a.alert_type === 'warning' ? '⚠️' : 'ℹ️');
    item.innerHTML = `
      <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
        <strong style="color:var(--text-primary);">${icon} ${a.title}</strong>
        <span style="font-size:11px; color:var(--text-muted);">${a.created_at.substring(11, 16)}</span>
      </div>
      <div style="color:var(--text-secondary); font-size:12.5px;">${a.message}</div>
    `;
    container.appendChild(item);
  });
}

// IoT Telemetry & Sandbox Controls
async function fetchIoTTelemetry() {
  try {
    const res = await fetch('/api/iot/telemetry');
    if (!res.ok) return;
    const data = await res.json();
    if (data) {
      setTxt('iotGrossWeightVal', `${data.gross_weight} kg`);
      setTxt('iotNetWeightVal', `${data.net_lpg_weight} kg`);
      setTxt('iotBatteryVal', `${data.battery_level}%`);
    }
  } catch (err) {
    console.error('Error fetching telemetry:', err);
  }
}

async function refreshTelemetry() {
  await fetchCylinderStatus();
  await fetchIoTTelemetry();
}

async function simulateCookingAction() {
  try {
    const res = await fetch('/api/iot/simulate-cooking', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hours: 1.0, intensity: 'Medium' })
    });
    const data = await res.json();
    showToast(data.message);
    await fetchCylinderStatus();
    await fetchIoTTelemetry();
  } catch (err) {
    console.error('Error simulating cooking:', err);
  }
}

async function simulateLeakAction() {
  const isLeak = currentCylinder && currentCylinder.is_leak_detected;
  try {
    const res = await fetch('/api/iot/simulate-leak', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active: !isLeak })
    });
    const data = await res.json();
    showToast(data.message);
    await fetchCylinderStatus();
    await fetchAlerts();
  } catch (err) {
    console.error('Error simulating leak:', err);
  }
}

async function resetCylinderAction() {
  if (!confirm('Mount a brand new 14.2 kg LPG cylinder onto the load cell scale?')) return;
  try {
    const res = await fetch('/api/iot/reset-cylinder', { method: 'POST' });
    const data = await res.json();
    showToast(`New cylinder installed (${data.serial})`);
    await fetchCylinderStatus();
    await fetchIoTTelemetry();
    await fetchAlerts();
  } catch (err) {
    console.error('Error resetting cylinder:', err);
  }
}

// Official Audit Report Generator
function populateAndOpenAuditReport() {
  if (!currentProfile || !currentCylinder) {
    showToast('Loading data, please wait...');
    return;
  }
  
  setTxt('reportAuditDate', new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }));
  setTxt('reportConsumerName', currentProfile.primary_name);
  setTxt('reportConsumerId', currentProfile.consumer_number);
  setTxt('reportAddress', currentProfile.address);
  setTxt('reportProvider', currentProfile.lpg_provider);
  setTxt('reportDistributor', currentProfile.distributor_name);
  
  setTxt('reportGrossWeight', `${currentCylinder.gross_weight || (currentCylinder.tare_weight + currentCylinder.current_gas_kg).toFixed(2)} kg`);
  setTxt('reportNetLpg', `${currentCylinder.current_gas_kg} kg`);
  setTxt('reportDaysRemaining', `${currentCylinder.days_remaining} Days`);
  setTxt('reportDailyBurn', `${currentCylinder.daily_burn_rate_kg} kg/d`);
  
  setTxt('reportDepletionDate', currentCylinder.depletion_date_formatted || currentCylinder.depletion_date);
  setTxt('reportBookingDate', currentCylinder.recommended_booking_date_formatted || currentCylinder.recommended_booking_date);
  
  const tbody = document.getElementById('reportHistoryTbody');
  if (tbody && refillHistoryData) {
    tbody.innerHTML = '';
    refillHistoryData.slice(0, 5).forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${r.booking_id}</strong></td>
        <td>${r.booking_date}</td>
        <td>${r.delivery_date}</td>
        <td>₹${r.amount_paid.toFixed(2)}</td>
        <td>${r.days_lasted} Days</td>
        <td>${r.avg_daily_consumption.toFixed(3)} kg/d</td>
      `;
      tbody.appendChild(tr);
    });
  }
  
  openModal('auditReportModal');
}

// Modal Handlers & Forms
function setupEventListeners() {
  // Theme Toggle
  document.getElementById('themeToggleBtn')?.addEventListener('click', toggleTheme);
  
  // Modals
  document.getElementById('quickBookRefillBtn')?.addEventListener('click', () => openModal('bookingModal'));
  document.getElementById('openProfileModalBtn')?.addEventListener('click', () => openModal('profileModal'));
  document.getElementById('openFamilyModalBtn')?.addEventListener('click', () => openModal('familyModal'));
  document.getElementById('alertsBellBtn')?.addEventListener('click', () => openModal('alertsModal'));
  document.getElementById('openAuditReportBtn')?.addEventListener('click', populateAndOpenAuditReport);
  
  // Classification Cards Selection
  document.querySelectorAll('#classificationGrid .classification-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('#classificationGrid .classification-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const classification = card.getAttribute('data-classification');
      setVal('famHouseholdClassification', classification);
      
      const purpose = card.getAttribute('data-purpose');
      if (purpose) selectPurpose(purpose);
      
      const members = card.getAttribute('data-members');
      if (members) setVal('famTotalMembers', members);
      
      const adults = card.getAttribute('data-adults');
      if (adults) setVal('famAdultsCount', adults);
      
      const children = card.getAttribute('data-children');
      if (children) setVal('famChildrenCount', children);
      
      const cap = card.getAttribute('data-capacity');
      if (cap) setVal('famCylinderCapacity', cap);
    });
  });

  // Purpose Pills
  document.getElementById('purposeHouseholdBtn')?.addEventListener('click', () => selectPurpose('Household'));
  document.getElementById('purposeCommercialBtn')?.addEventListener('click', () => selectPurpose('Commercial'));

  // Sync adults + children to total family members
  const updateFamilyTotal = () => {
    const adults = parseInt(document.getElementById('famAdultsCount')?.value || 0, 10);
    const children = parseInt(document.getElementById('famChildrenCount')?.value || 0, 10);
    setVal('famTotalMembers', adults + children);
  };
  document.getElementById('famAdultsCount')?.addEventListener('input', updateFamilyTotal);
  document.getElementById('famChildrenCount')?.addEventListener('input', updateFamilyTotal);

  // Chart Tabs
  document.getElementById('tabChartHistory')?.addEventListener('click', (e) => {
    document.getElementById('tabChartHistory').classList.add('active');
    document.getElementById('tabChartProjection').classList.remove('active');
    currentChartMode = 'history';
    drawConsumptionChart(refillHistoryData);
  });
  
  document.getElementById('tabChartProjection')?.addEventListener('click', (e) => {
    document.getElementById('tabChartProjection').classList.add('active');
    document.getElementById('tabChartHistory').classList.remove('active');
    currentChartMode = 'projection';
    if (currentCylinder) {
      drawDepletionCountdownChart(currentCylinder);
    }
  });

  // Close Modals
  document.querySelectorAll('.close-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal-backdrop');
      if (modal) modal.classList.remove('open');
    });
  });
  
  // Backdrop click to close
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
  });
  
  // One-Click Refill Booking Submit Form
  document.getElementById('bookingForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const provider = document.getElementById('bookProviderSelect').value;
    const payment = document.getElementById('bookPaymentSelect').value;
    
    try {
      const res = await fetch('/api/booking/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, payment_mode: payment })
      });
      const data = await res.json();
      closeModal('bookingModal');
      showToast(`🎉 Refill Booked! ID: ${data.booking.booking_id}`);
      await fetchActiveBooking();
      await fetchAlerts();
    } catch (err) {
      console.error('Error creating booking:', err);
    }
  });
  
  // Profile Update Form (Registered User & Gas Provider Details)
  document.getElementById('profileForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      primary_name: document.getElementById('profileFullName').value,
      phone: document.getElementById('profileMobile').value,
      email: document.getElementById('profileEmail').value,
      connection_type: document.getElementById('profileConnectionType').value,
      address: document.getElementById('profileAddress').value,
      lpg_provider: document.getElementById('profileProvider').value,
      consumer_number: document.getElementById('profileConsumerNo').value,
      distributor_name: document.getElementById('profileDistributor').value,
      distributor_phone: document.getElementById('profileDistributorPhone').value,
      lead_time_days: parseInt(document.getElementById('profileLeadTime').value || 3, 10)
    };
    
    try {
      const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      closeModal('profileModal');
      showToast('✓ Profile & Gas Provider details updated!');
      await fetchProfile();
      await fetchCylinderStatus();
    } catch (err) {
      console.error('Error updating profile:', err);
    }
  });

  // Family Profile Update Form
  document.getElementById('familyForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      household_classification: document.getElementById('famHouseholdClassification').value,
      usage_purpose: document.getElementById('famUsagePurpose').value,
      family_size: parseInt(document.getElementById('famTotalMembers').value || 4, 10),
      adults_count: parseInt(document.getElementById('famAdultsCount').value || 2, 10),
      children_count: parseInt(document.getElementById('famChildrenCount').value || 2, 10),
      daily_cooking_hours: parseFloat(document.getElementById('famCookingHours').value || 2.8),
      cooking_meals_per_day: parseInt(document.getElementById('famMealsPerDay').value || 3, 10),
      cylinder_capacity: parseFloat(document.getElementById('famCylinderCapacity').value || 14.2),
      date_of_last_refill: document.getElementById('famLastRefillDate').value,
      current_refill_price: parseFloat(document.getElementById('famRefillPrice').value || 858.00)
    };
    
    try {
      const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      closeModal('familyModal');
      showToast('✓ Family profile updated & ML prediction recalibrated!');
      await fetchProfile();
      await fetchCylinderStatus();

      // Trigger simulator slider change to recompute what-if
      const simFam = document.getElementById('simFamilySize');
      if (simFam) {
        simFam.dispatchEvent(new Event('input'));
      }
    } catch (err) {
      console.error('Error updating family details:', err);
    }
  });
  
  // Stepper advance demo button
  document.getElementById('advanceStatusBtn')?.addEventListener('click', advanceTrackingStatus);
  
  // IoT Sandbox Buttons
  document.getElementById('btnSimulateCooking')?.addEventListener('click', simulateCookingAction);
  document.getElementById('btnSimulateLeak')?.addEventListener('click', simulateLeakAction);
  document.getElementById('btnResetCylinder')?.addEventListener('click', resetCylinderAction);
}

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('open');
}

// Toast Helper
function showToast(message) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.innerHTML = `<span>✨</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
