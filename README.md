# AgriTwin AI 🌱

> **AI-powered sustainable farming decision & simulation platform**
>
> AgriTwin AI creates a virtual farm where farmers can simulate farming decisions and use AI/ML to choose strategies that balance expected yield, profitability, resource consumption, climate risk, and sustainability.

## 🚜 Problem

Farm decisions are interconnected. Crop choice affects water demand, fertilizer needs, expected yield, profitability, and sustainability. Traditional dashboards often show what is happening, but they do not help compare possible actions before a decision is made.

**AgriTwin AI focuses on two questions:**

- **What should I do?**
- **What will happen if I do it?**

## 💡 What AgriTwin AI Does

The platform combines historical agricultural data, weather/environment data, machine learning, optimization logic, rule-based intelligence, and what-if simulation to produce an integrated farming decision.

### Core capabilities

- **Yield Prediction** — XGBoost-based crop yield prediction using historical agricultural and weather features.
- **Crop Selection & Rotation** — compares candidate crops using crop suitability and farm conditions.
- **Water Optimization** — estimates crop water demand and irrigation coverage.
- **Fertilizer Optimization** — evaluates soil N/P/K conditions and identifies nutrient priorities.
- **Profit Optimization** — estimates crop-level planning profit using the project's configured economic assumptions.
- **Climate Risk Analysis** — evaluates temperature and rainfall-related risk.
- **Sustainability Scoring** — combines water, fertilizer, soil health, irrigation, rotation, and profitability factors into a sustainability score.
- **What-If Digital Farm Simulator** — tests changes in temperature, rainfall, irrigation, and fertilizer and compares the scenario with the baseline.
- **Early Warning System** — highlights conditions such as heat stress, low rainfall, water shortage, and nutrient deficiencies.
- **Crop Calendar** — provides crop-specific farming timeline information for supported crops.
- **Explainable Decision Layer** — provides rule-based reasons behind the recommendation.
- **Decision Replay** — compares predicted outcomes with actual results for later feedback analysis.
- **Decision History** — stores recent analyses locally in the browser for comparison.

## 🧠 Decision Pipeline

```text
Farm + Soil + Crop + Water + Weather Data
                    ↓
            Crop Selection Engine
                    ↓
        Crop-specific Yield Prediction
                    ↓
      Water / Fertilizer / Profit Analysis
                    ↓
             Climate Risk Engine
                    ↓
         Sustainability Evaluation
                    ↓
          Explainable AI + Advisor
                    ↓
          Final Farming Recommendation
                    ↓
             What-If Simulation
```

## 🤖 Machine Learning

The current yield model uses **XGBoost Regression**.

### Training data

The ML dataset was prepared from the project's ICRISAT-based agricultural data and ICRISAT environmental/weather data.

- Historical period: **2000–2017**
- Crops represented: **23**
- Training split: **2000–2014**
- Test split: **2015–2017**
- Target: `yield_kg_per_ha`

### Current model evaluation

| Metric | Value |
|---|---:|
| MAE | 288.05 kg/ha |
| RMSE | 700.30 kg/ha |
| R² | 0.8066 |

The trained model is stored at:

```text
backend/models/yield_prediction_model.pkl
```

> **Note:** The current project also contains rule-based optimization and advisory components. They are not all machine-learning models.

## 📊 Data

The project currently uses:

- **ICRISAT District-Level Database** as the historical agriculture backbone.
- **ICRISAT district-level environmental/weather data** for model inputs and analysis.
- Soil and live-weather integrations are planned for later versions.

### Local data structure

```text
data/
├── raw/
│   └── ICRISAT-District-Level-Data.csv
├── processed/
│   ├── ICRISAT-Long-Format.csv
│   └── AgriTwin-Yield-Dataset.csv
└── scripts/
    ├── prepare_icrisat.py
    ├── prepare_ml_dataset.py
    └── train_yield_model.py
```

## 🏗️ Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS 4
- JavaScript

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Joblib

### Data / ML

- ICRISAT agricultural data
- ICRISAT environmental/weather data
- XGBoost regression

## 📁 Project Structure

```text
AgriTwin-AI/
├── backend/
│   ├── app/
│   │   ├── agricultural_advisor.py
│   │   ├── climate_risk.py
│   │   ├── crop_calendar.py
│   │   ├── crop_optimizer.py
│   │   ├── database.py
│   │   ├── decision_pipeline.py
│   │   ├── decision_replay.py
│   │   ├── early_warning.py
│   │   ├── explainable_ai.py
│   │   ├── fertilizer_optimizer.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── profit_optimizer.py
│   │   ├── schemas.py
│   │   ├── sustainability_engine.py
│   │   ├── water_optimizer.py
│   │   └── what_if_simulator.py
│   ├── models/
│   │   └── yield_prediction_model.pkl
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── scripts/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── DecisionHistory.jsx
│   │   ├── FarmInsights.jsx
│   │   ├── WhatIfSimulator.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── requirements.txt
```

## ▶️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Aprajita348/AgriTwin-AI.git
cd AgriTwin-AI
```

### 2. Backend setup

Create and activate a virtual environment, then install dependencies:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API server:

```powershell
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend setup

Open a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## 🔌 Key API Endpoints

The backend exposes endpoints for the project's major intelligence modules, including:

```text
POST /predict-yield
POST /optimize-water
POST /optimize-fertilizer
POST /select-crops
POST /optimize-profit
POST /climate-risk
POST /early-warning
POST /what-if
POST /crop-calendar
POST /explain-decision
POST /agricultural-advisor
POST /decision-replay
POST /decision-pipeline
```

The main integrated endpoint is:

```text
POST /decision-pipeline
```

It combines crop selection, crop-specific yield prediction, profit, fertilizer priority, water coverage, climate risk, sustainability, explainability, and advisory logic into one decision flow.

## 🎯 What Makes It Different

Many agriculture systems focus on monitoring and prediction.

**AgriTwin AI focuses on decision simulation.**

Instead of only showing:

> "The farm may face higher climate risk."

the platform aims to help compare:

> "What should I do, and what will happen if I do it?"

The **What-If Digital Farm Simulator** is the central product concept: users can change environmental or resource-management assumptions and compare the resulting scenario with the baseline.

## ⚠️ Current Limitations

This is an evolving prototype / MVP. Some modules use simplified project assumptions rather than live field-calibrated recommendations.

- Profit calculations use configured planning assumptions rather than live market prices.
- Fertilizer recommendations are currently rule-based.
- The current agricultural advisor is rule-based/template-driven rather than an external LLM integration.
- Decision history is currently stored in browser local storage.
- Live soil, live weather, and satellite/geospatial integrations are planned for future versions.
- The current yield model provides a point prediction; its displayed model score should not be interpreted as per-prediction uncertainty.

## 🚀 Future Scope

- NASA POWER live weather integration
- SoilGrids-based soil intelligence
- Geospatial and satellite intelligence
- Live field/weather updates
- LLM-powered agricultural conversational advisor
- Disease-risk and crop-stress intelligence
- Database-backed decision feedback learning
- Advanced optimization with field-specific constraints
- Cloud deployment with managed database

## 📸 Screenshots

Add project screenshots here, for example:

```text
screenshots/
├── dashboard.png
├── what-if.png
├── farm-insights.png
└── history.png
```

Then reference them in this section using standard Markdown image syntax.

## 👩‍💻 Author

**Aprajita Goswami**

- GitHub: [@Aprajita348](https://github.com/Aprajita348)
- LinkedIn: [Aprajita Goswami](https://www.linkedin.com/in/aprajita-goswami-3258b92b8/)

---

⭐ **AgriTwin AI — Predict. Optimize. Simulate. Decide.**
