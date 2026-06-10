# 🌾 AgroCare - Smart Agriculture Field Monitoring System

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Overview

**AgroCare** is a farmer-friendly Smart Agriculture Field Monitoring System that helps farmers know **when and whether to irrigate each field**. The system simulates soil moisture sensors, provides intelligent irrigation recommendations, and offers a simple, intuitive dashboard.

### 🎯 Core Problem Solved

**"When should I water my fields?"**

AgroCare answers this question with clear, actionable recommendations - no complex charts or technical jargon.

---

## ✨ Features

### For Farmers 👨‍🌾
- 🔐 **User Authentication** - Secure login and signup with mobile number
- 🔄 **Forgot Password** - Reset password via mobile number
- 🌱 **Easy Setup** - Register your fields in minutes
- 📊 **Field Dashboard** - See all fields at a glance with color-coded status
- 💧 **Water Tank Meter** - Visual water level indicator (0-100%)
- 🎯 **Clear Irrigation Recommendations** - "Irrigate Today Evening", "No Irrigation Needed"
- 🚨 **Irrigation Priority List** - Shows which field needs attention first
- ☔ **Rainfall Tracking** - Recent rainfall affects recommendations
- 🔔 **Notification Bell** - Real-time alerts for critical fields
- 👁️ **Password Visibility Toggle** - Show/hide password on login/signup
- ➕ **Add Fields Anytime** - No need to redo setup
- 🗑️ **Delete Fields** - Remove fields when crops are harvested

### Technical Features 🔧
- 📡 **Sensor Simulation** - Realistic soil moisture, temperature, humidity, rainfall (20% rain chance)
- 🧠 **Smart Recommendation Engine** - Rule-based with rain override (>5mm delays irrigation)
- 🗄️ **SQLite Database** - All data stored permanently in `agrocare.db`
- 🔌 **REST APIs** - Full API access via Swagger UI
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Pure HTML/CSS** - No JavaScript frameworks, lightweight and fast

### Crop Types Supported 🌾
| Crop | Emoji |
|------|-------|
| Rice | 🌾 |
| Wheat | 🌾 |
| Cotton | 🌿 |
| Maize (Corn) | 🌽 |
| Sugarcane | 🎋 |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/AbishekP-28/agrocare-smart-agriculture.git
cd agrocare-smart-agriculture

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
