# 🌱 AgriTwin AI — AI-Powered Sustainable Farming Decision & Simulation Platform

An AI-powered full-stack agricultural decision-support platform designed to help users analyze farm conditions, receive data-driven farming recommendations, and simulate alternative farming decisions before applying them in the real world.

---

# 🚀 Live Demo

**Live Application:**  
https://agritwin-ai-sigma.vercel.app/

**GitHub Repository:**  
https://github.com/Aprajita348/AgriTwin-AI

---

# ✨ Features

## 🌾 Farm Intelligence

- Farm Profile & Farm Size Analysis
- District & State Information
- Previous Crop Information
- Soil N/P/K Analysis
- Soil pH & Organic Matter Analysis
- Water Availability Analysis
- Irrigation Analysis
- Rainfall & Temperature Analysis
- Integrated AI Decision Pipeline

## 🤖 AI Yield Prediction

- XGBoost-based crop yield prediction
- 123K+ historical records
- 23 crops
- 18 years of agricultural data
- **MAE:** 288.05 kg/ha
- **RMSE:** 700.30 kg/ha
- **R²:** 0.8066

## 🌱 Crop Selection

- Compare 5 crop alternatives
- Yield comparison
- Profit comparison
- Sustainability comparison
- Climate-risk comparison
- Decision-score comparison

## 💧 Resource Analysis

- Water requirement analysis
- Water coverage calculation
- Fertilizer priority analysis
- Profit estimation
- Resource-efficiency insights

## 🌡️ Climate & Sustainability

- Climate-risk analysis
- Sustainability scoring
- Early-warning system
- Crop calendar
- Environmental impact analysis

## 🌦️ Live Intelligence

- Live weather information
- Current temperature
- Humidity
- Rainfall
- Today's maximum temperature
- Farm-specific coordinates
- Open-Meteo weather integration
- Live decision pipeline

## 🧠 AI Agricultural Advisor

- Personalized farming recommendation
- Decision reasoning
- Expected impact
- Warnings
- Next steps
- Rule-based fallback when external AI is unavailable

## 🔄 What-If Digital Farm Simulator

Users can simulate changes in:

- Temperature
- Rainfall
- Irrigation
- Fertilizer

and compare:

- Yield
- Profit
- Water
- Sustainability
- Climate Risk

## 📚 Decision History

- Save recent analyses
- Review previous decisions
- View crop recommendations
- View yield and profit
- View sustainability score
- View climate risk
- Track decision timestamps

## 🔐 Authentication

- User Registration
- User Login
- JWT Authentication
- Password Hashing
- Session Restoration
- Protected Farm Operations

---

# 🧠 Decision Pipeline

```text
Farm + Soil + Crop + Water + Weather
                  ↓
            Crop Selection
                  ↓
        XGBoost Yield Prediction
                  ↓
      Water / Fertilizer / Profit
                  ↓
          Climate Risk Analysis
                  ↓
        Sustainability Analysis
                  ↓
       Explainable Decision Layer
                  ↓
       Agricultural AI Advisor
                  ↓
       Final Farming Recommendation
                  ↓
        What-If Digital Simulation