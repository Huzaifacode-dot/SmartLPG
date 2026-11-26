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
  initWizardInteractions();
  goToWizardStep(1);
  
  // Refresh cylinder telemetry every 15 seconds
  setInterval(refreshTelemetry, 15000);
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('smartlpg_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.setAttribute('aria-label', savedTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const newTheme = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('smartlpg_theme', newTheme);
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.setAttribute('aria-label', newTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
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
    
    // Fill 5-Step Details Wizard Fields (from Screenshots)
    if (data.cylinder_capacity) {
      setVal('wizCylinderCapacity', data.cylinder_capacity);
      document.querySelectorAll('#capacityPillGroup .cap-pill').forEach(b => {
        if (parseFloat(b.getAttribute('data-cap')) === parseFloat(data.cylinder_capacity)) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
      });
    }
    if (data.date_of_last_refill) setVal('wizLastRefillDate', data.date_of_last_refill);
    if (data.current_refill_price) setVal('wizRefillPrice', data.current_refill_price);

    if (data.household_classification) {
      setVal('wizClassification', data.household_classification);
      document.querySelectorAll('#wizClassificationGroup .class-card-item').forEach(c => {
        if (c.getAttribute('data-class') === data.household_classification) {
          c.classList.add('active');
        } else {
          c.classList.remove('active');
        }
      });
    }
    if (data.adults_count) {
      setVal('wizAdultsCount', data.adults_count);
      setTxt('wizAdultsCountVal', data.adults_count);
    }
    if (data.children_count !== undefined) {
      setVal('wizChildrenCount', data.children_count);
      setTxt('wizChildrenCountVal', data.children_count);
    }
    if (data.cooking_meals_per_day) setVal('wizMealsPerDay', data.cooking_meals_per_day);
    if (data.cooking_days_per_week) setVal('wizCookingDays', data.cooking_days_per_week);
    if (data.avg_time_per_meal) setVal('wizAvgTimeMeal', data.avg_time_per_meal);
    if (data.flame_intensity) {
      setVal('wizFlameIntensity', data.flame_intensity);
      document.querySelectorAll('#wizFlameGroup .cap-pill').forEach(b => {
        if (b.getAttribute('data-flame') === data.flame_intensity) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
      });
    }
    if (data.extra_weekly_hours !== undefined) setVal('wizExtraHours', data.extra_weekly_hours);
    const setWizChecked = (id, val) => {
      const el = document.getElementById(id);
      if (el) {
        el.checked = Boolean(val);
        const card = el.closest('.toggle-card-large');
        if (card) {
          if (el.checked) card.classList.add('checked');
          else card.classList.remove('checked');
        }
      }
    };
    if (data.use_pressure_cooker !== undefined) setWizChecked('wizUsePressureCooker', data.use_pressure_cooker);
    if (data.use_saving_lids !== undefined) setWizChecked('wizUseSavingLids', data.use_saving_lids);
    if (data.cook_in_batches !== undefined) setWizChecked('wizCookInBatches', data.cook_in_batches);
    if (data.reheat_on_stove !== undefined) setWizChecked('wizReheatOnStove', data.reheat_on_stove);

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
  setTxt('navGasLeft', `${pct}%`);
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
  
  // Handle 25-Day Regulatory Inter-Booking Lock Notice
  const lockNotice = document.getElementById('bookingLockNotice');
  const modalLockNotice = document.getElementById('bookingModalLockNotice');
  const confirmBtn = document.getElementById('confirmBookingBtn');
  const elig = booking ? booking.eligibility : null;

  if (elig && !elig.can_book) {
    if (lockNotice) lockNotice.style.display = 'block';
    if (modalLockNotice) modalLockNotice.style.display = 'block';
    setTxt('lockEligibleDate', elig.eligible_date);
    setTxt('modalLockEligibleDate', elig.eligible_date);
    setTxt('lockDaysLeft', elig.days_remaining);
    setTxt('modalLockDaysLeft', elig.days_remaining);

    if (confirmBtn) {
      confirmBtn.disabled = true;
      confirmBtn.innerHTML = `🔒 Refill Locked (${elig.days_remaining}d remaining)`;
    }
  } else {
    if (lockNotice) lockNotice.style.display = 'none';
    if (modalLockNotice) modalLockNotice.style.display = 'none';
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.innerHTML = `Confirm & Book Refill`;
    }
  }

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
      advanceBtn.textContent = '✓ Delivered & Installed (Click to Restart)';
      advanceBtn.disabled = false;
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
    if (data.reset) {
      showToast('Refill cycle finished! Demo restarted to Step 1.');
    } else {
      showToast(`Order updated to: ${data.status}`);
    }
    await fetchActiveBooking();
    await fetchCylinderStatus();
    await fetchRefillHistory();
    await fetchAlerts();
  } catch (err) {
    console.error('Error advancing tracking:', err);
  }
}

// Reset Demo Booking & Telemetry
async function resetTrackingDemo() {
  try {
    const res = await fetch('/api/booking/reset-demo', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('Demo reset to Step 1 (Order Booked). Reserve fuel: 2.45 kg');
      await fetchActiveBooking();
      await fetchCylinderStatus();
      await fetchRefillHistory();
      await fetchAlerts();
    }
  } catch (err) {
    console.error('Error resetting tracking demo:', err);
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
      <td class="tabular-nums"><strong>${r.booking_id}</strong></td>
      <td class="tabular-nums">${r.booking_date}</td>
      <td class="tabular-nums">${r.delivery_date}</td>
      <td>${r.provider}</td>
      <td class="num-col tabular-nums">₹${r.amount_paid.toFixed(2)}</td>
      <td class="num-col tabular-nums"><strong>${r.days_lasted} Days</strong></td>
      <td class="num-col tabular-nums">${r.avg_daily_consumption.toFixed(3)} kg/d</td>
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
  
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  const gridColor = isLight ? 'rgba(15, 23, 42, 0.08)' : 'rgba(255, 255, 255, 0.06)';
  const axisLabelColor = isLight ? '#64748B' : '#94A3B8';
  const valueLabelColor = isLight ? '#0F172A' : '#F8FAFC';
  const pointBorderColor = isLight ? '#FFFFFF' : '#11131A';
  const lineAccent = isLight ? '#0D9488' : '#14B8A6';

  // Grid lines
  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 1;
  const numGridLines = 4;
  for (let i = 0; i <= numGridLines; i++) {
    const y = padding.top + (graphH / numGridLines) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(w - padding.right, y);
    ctx.stroke();
    
    ctx.fillStyle = axisLabelColor;
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
  grad.addColorStop(0, isLight ? 'rgba(13, 148, 136, 0.24)' : 'rgba(20, 184, 166, 0.26)');
  grad.addColorStop(1, isLight ? 'rgba(13, 148, 136, 0.0)' : 'rgba(20, 184, 166, 0.0)');
  
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
  
  ctx.strokeStyle = lineAccent;
  ctx.lineWidth = 2.5;
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
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fillStyle = lineAccent;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = pointBorderColor;
    ctx.stroke();
    
    ctx.fillStyle = axisLabelColor;
    ctx.font = '11px Plus Jakarta Sans';
    ctx.textAlign = 'center';
    const dateLabel = pt.booking_date.substring(5);
    ctx.fillText(dateLabel, x, h - padding.bottom + 20);
    
    ctx.fillStyle = valueLabelColor;
    ctx.font = '600 11px Outfit';
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
  
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  const gridColor = isLight ? 'rgba(15, 23, 42, 0.08)' : 'rgba(255, 255, 255, 0.06)';
  const axisLabelColor = isLight ? '#64748B' : '#94A3B8';
  const valueLabelColor = isLight ? '#0F172A' : '#F8FAFC';
  const pointBorderColor = isLight ? '#FFFFFF' : '#11131A';
  const curveColor = isLight ? '#0D9488' : '#14B8A6';

  // Grid
  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (graphH / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(w - padding.right, y);
    ctx.stroke();
    
    const kgVal = (maxGas * (1 - i / 4)).toFixed(1);
    ctx.fillStyle = axisLabelColor;
    ctx.font = '10.5px Plus Jakarta Sans';
    ctx.textAlign = 'right';
    ctx.fillText(`${kgVal}kg`, padding.left - 8, y + 4);
  }
  
  // Safe buffer threshold area (Days <= leadTime)
  const bufferStartX = padding.left + graphW * Math.max(0, (totalDays - leadTime) / totalDays);
  ctx.fillStyle = 'rgba(239, 68, 68, 0.09)';
  ctx.fillRect(bufferStartX, padding.top, w - padding.right - bufferStartX, graphH);
  
  // Buffer Label
  ctx.fillStyle = '#EF4444';
  ctx.font = '700 10px Plus Jakarta Sans';
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
  grad.addColorStop(0, isLight ? 'rgba(13, 148, 136, 0.24)' : 'rgba(20, 184, 166, 0.25)');
  grad.addColorStop(1, isLight ? 'rgba(13, 148, 136, 0.0)' : 'rgba(20, 184, 166, 0.0)');
  
  ctx.beginPath();
  points.forEach((pt, i) => {
    if (i === 0) ctx.moveTo(pt.x, pt.y);
    else ctx.lineTo(pt.x, pt.y);
  });
  ctx.strokeStyle = curveColor;
  ctx.lineWidth = 2.5;
  ctx.stroke();
  
  ctx.lineTo(points[points.length - 1].x, h - padding.bottom);
  ctx.lineTo(padding.left, h - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();
  
  // Plotted points
  points.forEach((pt, i) => {
    ctx.beginPath();
    ctx.arc(pt.x, pt.y, i === 0 ? 5.5 : 3.5, 0, Math.PI * 2);
    ctx.fillStyle = i === 0 ? '#10B981' : (pt.gas <= 0.2 ? '#EF4444' : curveColor);
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = pointBorderColor;
    ctx.stroke();
    
    // Label day
    ctx.fillStyle = axisLabelColor;
    ctx.font = '10px Plus Jakarta Sans';
    ctx.textAlign = 'center';
    ctx.fillText(`+${pt.day}d`, pt.x, h - padding.bottom + 18);
    
    // Weight value on key points
    if (i === 0 || i === points.length - 1 || pt.day === totalDays - leadTime) {
      ctx.fillStyle = valueLabelColor;
      ctx.font = '600 10px Outfit';
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
  
  let debounceTimer = null;

  // Real-time dynamic calculation function (instant client-side + debounced ML API confirmation)
  const updateSim = () => {
    const fam = parseInt(familySlider.value) || 4;
    const meals = parseInt(mealsSlider.value) || 3;
    const hrs = parseFloat(hoursSlider.value) || 2.5;
    const cap = parseFloat(capSelect?.value || '14.2');

    // 1. Instant dynamic numerical label updates (changes as slider moves)
    setTxt('simFamilyVal', fam);
    setTxt('simMealsVal', meals);
    setTxt('simHoursVal', `${hrs.toFixed(1)} hrs`);

    // 2. Instant client-side dynamic preview (0ms latency for smooth 60fps sliding)
    const flameMult = simFlame === 'High' ? 1.25 : (simFlame === 'Low' ? 0.78 : 1.0);
    const effMult = simEfficiency ? 0.85 : 1.0;
    const instantBurn = Math.max(0.12, (0.055 * fam + 0.045 * meals + 0.08 * hrs) * flameMult * effMult);
    const instantDays = (cap / instantBurn).toFixed(1);
    const refillPrice = cap === 14.2 ? 858.0 : (cap === 5.0 ? 320.0 : 1650.0);
    const instantDailyCost = (instantBurn * (refillPrice / cap)).toFixed(2);
    const instantMonthly = Math.round(instantDailyCost * 30);

    setTxt('simResultBurnRate', `${instantBurn.toFixed(2)} kg/d`);
    setTxt('simResultLongevity', `~${instantDays} Days`);
    setTxt('simResultDailyCost', `₹${instantDailyCost}/d`);
    setTxt('simResultMonthly', `₹${instantMonthly} / Mo`);

    // 3. Debounced query to server ML model to confirm exact model predictions & confidence
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch('/api/predict/what-if', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            family_size: fam,
            meals_per_day: meals,
            cooking_hours: hrs,
            cylinder_capacity: cap,
            flame_intensity: simFlame,
            efficiency_mode: simEfficiency,
            refill_price: refillPrice
          })
        });
        if (!res.ok) return;
        const data = await res.json();
        setTxt('simResultBurnRate', `${data.predicted_burn_rate_kg} kg/d`);
        setTxt('simResultLongevity', `~${data.estimated_cylinder_life_days} Days`);
        setTxt('simResultDailyCost', `₹${data.daily_cost_inr}/d`);
        setTxt('simResultMonthly', `₹${data.monthly_cost_inr} / Mo`);
        setTxt('simConfidenceBadge', `🎯 ${data.confidence_score || 97}% Confidence`);
      } catch (err) {
        console.error('Error querying what-if ML model:', err);
      }
    }, 150);
  };

  // Flame pill buttons
  document.querySelectorAll('#simFlameGroup .flame-pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
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

  // Cylinder capacity dropdown
  capSelect?.addEventListener('change', updateSim);

  // Bind both 'input' and 'change' events to sliders for instant reactivity
  ['input', 'change'].forEach(evt => {
    familySlider.addEventListener(evt, updateSim);
    mealsSlider.addEventListener(evt, updateSim);
    hoursSlider.addEventListener(evt, updateSim);
  });

  // Trigger initial calculation
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
  if (!confirm('Mount and install a brand new 14.2 kg LPG cylinder?')) return;
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
        <td class="tabular-nums"><strong>${r.booking_id}</strong></td>
        <td class="tabular-nums">${r.booking_date}</td>
        <td class="tabular-nums">${r.delivery_date}</td>
        <td class="num-col tabular-nums">₹${r.amount_paid.toFixed(2)}</td>
        <td class="num-col tabular-nums">${r.days_lasted} Days</td>
        <td class="num-col tabular-nums">${r.avg_daily_consumption.toFixed(3)} kg/d</td>
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
      if (!res.ok) {
        showToast(`❌ ${data.error || 'Refill booking locked'}`);
        await fetchActiveBooking();
        return;
      }
      closeModal('bookingModal');
      showToast(`🎉 Refill Booked! ID: ${data.booking.booking_id}`);
      await fetchActiveBooking();
      await fetchCylinderStatus();
      await fetchAlerts();
    } catch (err) {
      console.error('Error creating booking:', err);
    }
  });

  // Landing Page Start Prediction CTA
  document.getElementById('heroStartPredictionBtn')?.addEventListener('click', () => {
    goToWizardStep(1);
    openModal('familyModal');
  });

  // Fast forward 25 days demo button
  document.getElementById('fastForwardBookingBtn')?.addEventListener('click', fastForward25DaysDemo);

  // 5-Step Details Wizard Form Submission
  document.getElementById('wizardDetailsForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await saveWizardDetails();
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
  
  // Stepper advance and demo reset buttons
  document.getElementById('advanceStatusBtn')?.addEventListener('click', advanceTrackingStatus);
  document.getElementById('resetTrackingBtn')?.addEventListener('click', resetTrackingDemo);
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

// ==========================================
// 5-STEP DETAILS WIZARD LOGIC (MULTI-FACTOR ML MODEL)
// ==========================================

const wizardStepMeta = {
  1: {
    title: 'Cylinder & Refill Details',
    subtitle: 'Select cylinder capacity, refill cost, and date of last refill.',
    progress: '20%'
  },
  2: {
    title: 'Household Size & Composition',
    subtitle: 'How many adults and children share this gas cylinder?',
    progress: '40%'
  },
  3: {
    title: 'Cooking Habits & Food Types',
    subtitle: 'Frequency, duration, and specific foods cooked routinely.',
    progress: '60%'
  },
  4: {
    title: 'Extra Gas Appliances & Usages',
    subtitle: 'Water heating, commercial cooking, or outdoor gas appliances.',
    progress: '80%'
  },
  5: {
    title: 'Efficiency Habits & Lifestyle',
    subtitle: 'Energy saving practices and meal preparation behaviors.',
    progress: '100%'
  }
};

let currentWizardStep = 1;

function goToWizardStep(step) {
  if (step < 1) step = 1;
  if (step > 5) step = 5;
  currentWizardStep = step;

  const meta = wizardStepMeta[step];
  setTxt('wizardStepNum', step);
  setTxt('wizardStepTitle', meta.title);
  setTxt('wizardStepSubtitle', meta.subtitle);

  const fill = document.getElementById('wizardProgressFill');
  if (fill) fill.style.width = meta.progress;

  for (let s = 1; s <= 5; s++) {
    const pane = document.getElementById(`wizardStepPane${s}`);
    if (pane) pane.style.display = s === step ? 'block' : 'none';
  }

  const backBtn = document.getElementById('wizBackBtn');
  if (backBtn) {
    backBtn.disabled = (step === 1);
  }

  const nextBtn = document.getElementById('wizNextBtn');
  if (nextBtn) {
    if (step === 5) {
      nextBtn.innerHTML = 'Calculate & Save Prediction ➔';
      nextBtn.className = 'wizard-next-btn btn-primary';
    } else {
      nextBtn.innerHTML = 'Next Step &gt;';
      nextBtn.className = 'wizard-next-btn';
    }
  }
}

function adjustWizCounter(type, delta) {
  if (type === 'adults') {
    const input = document.getElementById('wizAdultsCount');
    let val = parseInt(input?.value || 2, 10) + delta;
    if (val < 1) val = 1;
    if (val > 20) val = 20;
    if (input) input.value = val;
    setTxt('wizAdultsCountVal', val);
  } else if (type === 'children') {
    const input = document.getElementById('wizChildrenCount');
    let val = parseInt(input?.value || 0, 10) + delta;
    if (val < 0) val = 0;
    if (val > 20) val = 20;
    if (input) input.value = val;
    setTxt('wizChildrenCountVal', val);
  }
}
window.adjustWizCounter = adjustWizCounter;

function initWizardInteractions() {
  // Step 1: Capacity Pills
  document.querySelectorAll('#capacityPillGroup .cap-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#capacityPillGroup .cap-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cap = btn.getAttribute('data-cap');
      setVal('wizCylinderCapacity', cap);
      const customCheck = document.getElementById('wizCustomCapCheck');
      if (customCheck) customCheck.checked = false;
      const customBox = document.getElementById('wizCustomCapBox');
      if (customBox) customBox.style.display = 'none';
    });
  });

  // Step 1: Custom Capacity Checkbox
  const customCheck = document.getElementById('wizCustomCapCheck');
  const customBox = document.getElementById('wizCustomCapBox');
  const customInput = document.getElementById('wizCustomCapInput');
  customCheck?.addEventListener('change', (e) => {
    if (e.target.checked) {
      if (customBox) customBox.style.display = 'block';
      document.querySelectorAll('#capacityPillGroup .cap-pill').forEach(b => b.classList.remove('active'));
      if (customInput && customInput.value) {
        setVal('wizCylinderCapacity', customInput.value);
      }
    } else {
      if (customBox) customBox.style.display = 'none';
      const defPill = document.querySelector('#capacityPillGroup .cap-pill[data-cap="14.2"]');
      if (defPill) {
        defPill.classList.add('active');
        setVal('wizCylinderCapacity', '14.2');
      }
    }
  });
  customInput?.addEventListener('input', (e) => {
    if (e.target.value) setVal('wizCylinderCapacity', e.target.value);
  });

  // Step 2: Household Classification Cards
  document.querySelectorAll('#wizClassificationGroup .class-card-item').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('#wizClassificationGroup .class-card-item').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const cls = card.getAttribute('data-class');
      setVal('wizClassification', cls);
      const adults = card.getAttribute('data-adults');
      const children = card.getAttribute('data-children');
      if (adults) {
        setVal('wizAdultsCount', adults);
        setTxt('wizAdultsCountVal', adults);
      }
      if (children !== null && children !== undefined) {
        setVal('wizChildrenCount', children);
        setTxt('wizChildrenCountVal', children);
      }
    });
  });

  // Step 3: Cooking Flame Intensity
  document.querySelectorAll('#wizFlameGroup .cap-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#wizFlameGroup .cap-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const flame = btn.getAttribute('data-flame');
      setVal('wizFlameIntensity', flame);
    });
  });

  // Step 3 & 4: Food & Appliance Checkbox Cards
  document.querySelectorAll('.food-check-card').forEach(label => {
    const check = label.querySelector('input[type="checkbox"]');
    if (check) {
      check.addEventListener('change', () => {
        if (check.checked) label.classList.add('checked');
        else label.classList.remove('checked');
      });
    }
  });

  // Step 5: Large Toggle Cards
  document.querySelectorAll('.toggle-card-large').forEach(label => {
    const check = label.querySelector('input[type="checkbox"]');
    if (check) {
      check.addEventListener('change', () => {
        if (check.checked) label.classList.add('checked');
        else label.classList.remove('checked');
      });
    }
  });

  // Wizard Navigation Buttons
  document.getElementById('wizBackBtn')?.addEventListener('click', () => {
    if (currentWizardStep > 1) {
      goToWizardStep(currentWizardStep - 1);
    }
  });

  document.getElementById('wizNextBtn')?.addEventListener('click', () => {
    if (currentWizardStep < 5) {
      goToWizardStep(currentWizardStep + 1);
    } else {
      saveWizardDetails();
    }
  });
}

// Save Multi-Factor Wizard Details and Calibrate Prediction
async function saveWizardDetails() {
  const cap = parseFloat(document.getElementById('wizCylinderCapacity')?.value || 14.2);
  const lastRefillDate = document.getElementById('wizLastRefillDate')?.value || '';
  const refillPrice = parseFloat(document.getElementById('wizRefillPrice')?.value || 858.0);
  const classification = document.getElementById('wizClassification')?.value || 'Family Household';
  const adults = parseInt(document.getElementById('wizAdultsCount')?.value || 2, 10);
  const children = parseInt(document.getElementById('wizChildrenCount')?.value || 2, 10);
  const familySize = adults + children;
  const mealsPerDay = parseInt(document.getElementById('wizMealsPerDay')?.value || 3, 10);
  const cookingDays = parseInt(document.getElementById('wizCookingDays')?.value || 7, 10);
  const avgTime = parseInt(document.getElementById('wizAvgTimeMeal')?.value || 20, 10);
  const flameIntensity = document.getElementById('wizFlameIntensity')?.value || 'Medium Flame';

  // Frequently cooked foods
  const foods = [];
  document.querySelectorAll('#wizFoodsGrid input[type="checkbox"]:checked').forEach(c => foods.push(c.value));

  // Extra appliances
  const appliances = [];
  document.querySelectorAll('#wizAppliancesGrid input[type="checkbox"]:checked').forEach(c => appliances.push(c.value));
  const extraHours = parseFloat(document.getElementById('wizExtraHours')?.value || 0);

  // Efficiency habits
  const pressureCooker = Boolean(document.getElementById('wizUsePressureCooker')?.checked);
  const savingLids = Boolean(document.getElementById('wizUseSavingLids')?.checked);
  const batchCooking = Boolean(document.getElementById('wizCookInBatches')?.checked);
  const reheatStove = Boolean(document.getElementById('wizReheatOnStove')?.checked);

  // Compute cooking hours per day
  const dailyCookingHours = parseFloat(((mealsPerDay * avgTime) / 60 * (cookingDays / 7)).toFixed(2));

  const payload = {
    cylinder_capacity: cap,
    date_of_last_refill: lastRefillDate,
    current_refill_price: refillPrice,
    household_classification: classification,
    adults_count: adults,
    children_count: children,
    family_size: familySize,
    cooking_meals_per_day: mealsPerDay,
    cooking_days_per_week: cookingDays,
    avg_time_per_meal: avgTime,
    daily_cooking_hours: dailyCookingHours,
    flame_intensity: flameIntensity,
    frequently_cooked_foods: foods,
    extra_appliances: appliances,
    extra_weekly_hours: extraHours,
    use_pressure_cooker: pressureCooker,
    use_saving_lids: savingLids,
    cook_in_batches: batchCooking,
    reheat_on_stove: reheatStove
  };

  try {
    const res = await fetch('/api/profile/details-update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    closeModal('familyModal');
    showToast('🎯 Multi-Factor Details Saved! ML model recalibrated.');
    await fetchProfile();
    await fetchCylinderStatus();

    // Trigger simulator slider change to recompute what-if
    const simFam = document.getElementById('simFamilySize');
    if (simFam) {
      simFam.value = familySize;
      simFam.dispatchEvent(new Event('input'));
    }
  } catch (err) {
    console.error('Error saving wizard details:', err);
    showToast('Failed to save details. Please try again.');
  }
}

// Fast Forward 25 Days Demo Action
async function fastForward25DaysDemo() {
  try {
    const res = await fetch('/api/booking/fast-forward-25-days', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('⏩ Fast-forwarded 26 days! 25-day refill lock is now lifted.');
      await fetchActiveBooking();
      await fetchCylinderStatus();
      await fetchAlerts();
    }
  } catch (err) {
    console.error('Error fast-forwarding 25 days:', err);
  }
}
