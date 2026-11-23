# SmartLPG: An Intelligent LPG Refill Prediction and Booking System

**Course:** Societal Based Mini Project (Course Code: `24CSE57`)  
**Semester:** V  
**Department:** Computer Science and Engineering  
**Guide:** Prof. Ashwini G B  
**Duration:** Sep 2026 – Dec 2026  

### Student Details:
| USN | Student Name | Section |
| :--- | :--- | :---: |
| **1NH24CS126** | **Mohammed Huzaifa Khan** | 5C |
| **1NH24CS125** | **Mohammad Aftab Ahmed** | 5C |

---

## 📖 Problem Statement
Households frequently face uncertainty regarding the exact remaining LPG in their domestic cylinders and the optimal time to book a refill. This often results in sudden gas exhaustion during peak cooking hours, emergency last-minute bookings, and prolonged inconvenience due to agency delivery lead times. 

**SmartLPG** solves this societal challenge through:
- Machine Learning (Random Forest) consumption forecasting based on household demographics and cooking patterns.
- Timely proactive alerts when gas reserves reach critical thresholds (≤ 2–3 days).
- Buffer-aware refill booking recommendations that factor in distributor delivery lead times.
- One-click integrated authorized refill booking workflow (Indane, Bharat Gas, HP Gas).
- Real-time order delivery lifecycle tracking (*Booked ➔ Confirmed ➔ Dispatched ➔ Out for Delivery ➔ Delivered*) with OTP verification.
- 100% Data-Driven & Sensor-Free: Eliminates expensive, fragile hardware scales by modeling domestic consumption purely through demographic parameters and machine learning.

---

## 🚀 Key Features

1. **Intelligent Depletion Prediction Model**:
   - Trained with Scikit-Learn (Random Forest Regressor, $R^2 \approx 0.96$).
   - Calculates daily burn rate ($\text{kg/day}$) factoring in family size, meal frequency, cooking hours, and seasonal variations.
   - Computes exact depletion date and safe booking buffer date.

2. **Proactive Refill Warning System**:
   - Automated color-coded alert banner triggered when reserve drops below threshold.
   - Prevents gas shortages before they occur.

3. **One-Click Refill Booking Interface**:
   - Pre-fills consumer information and distributor SV credentials.
   - Generates official booking references (e.g. `LPG-IND-2026-XXXX`).
   - Supports online payment modes (UPI / Net Banking) and Cash on Delivery.

4. **Live Delivery Status Tracking**:
   - Interactive 5-stage delivery stepper.
   - Shows delivery partner details, direct contact, and delivery authentication OTP.
   - Interactive demo advancement button to showcase full lifecycle during project evaluation.

5. **Dynamic Consumption Simulator & Sandbox**:
   - Simulates cooking sessions, burner usage, and accelerated domestic burn rates.
   - Live visual depletion tracking with real-time cylinder level animations.
   - Anomaly detection testing for unexpected consumption surges.
   - "Mount New Cylinder" feature resetting capacity to 100% (14.2 kg standard domestic cylinder).

6. **Refill History & Analytics Report**:
   - Detailed logs of past refill cycles, duration lasted, daily average consumption, and expenditure.
   - Canvas-based trend visualization.

7. **"What-If" AI Consumption Calculator**:
   - Interactive sliders for family size, meals, and hours to test hypothetical burn rates and cylinder longevity.

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Flask REST API
- **Machine Learning:** Scikit-learn (RandomForestRegressor), NumPy, Pandas, Joblib
- **Database:** SQLite3
- **Frontend:** Modern Semantic HTML5, Vanilla JavaScript, Responsive Glassmorphism CSS Design System
- **Architecture:** 100% Sensorless, Data-Driven Predictive Modeling System

---

## 🏃 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed:
```bash
python --version
```

### 2. Run the Application
From the project root directory, execute:
```bash
python run.py
```

### 3. Open in Browser
Visit the dashboard at:
```
http://127.0.0.1:5000/
```
