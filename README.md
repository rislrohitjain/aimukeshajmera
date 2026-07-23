# Mukesh Ajmera LIC & Post Office Services (मुकेश अजमेर एलआईसी & पोस्ट ऑफिस)

> **AI-Powered Smart Advisory for LIC & India Post Savings Plans**  
> *Sarwar, Rajasthan 305403 • Contact / WhatsApp: +91 98299 43216*

---

## 🚀 Overview

A high-converting, trust-building financial advisory web portal and AI Chatbot ("LIC MITRA") built for **Mukesh Ajmera LIC & Post Office Services**. The portal helps clients across Rajasthan discover, compare, and select the optimal LIC Insurance Policies and India Post Savings Schemes.

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask 3.0)
* **Database:** PostgreSQL (with SQLAlchemy ORM)
* **Frontend:** HTML5, jQuery, Tailwind CSS (CDNs), FontAwesome icons, Chart.js
* **AI Engine:** Pluggable provider supporting Local LLM (Ollama/LM Studio), OpenAI (GPT-4o), and Google Gemini with an Admin Dashboard toggle and domain-aware offline fallback.
* **Deployment:** Vercel-ready folder structure (`api/index.py` WSGI entry point & `vercel.json`).

---

## 🔑 Default Admin Account

* **Mobile Number / Phone:** `9829943216`
* **Password:** `9829943216`
* **Role:** `admin`
* **Admin Access URL:** `http://localhost:5050/admin/dashboard`

---

## 🏃 Local Development Quickstart (Port 5050)

1. **Single Click Launcher:**
   Double click **`run_app.bat`** (or run `python run_app.py`).

2. **Manual Startup:**
   ```bash
   python api/index.py
   ```
   Open `http://localhost:5050` or `http://<your-local-ip>:5050` in your web browser.

---

## 🗄️ Database Diagnostic URL

* Access `http://localhost:5050/checkdb` to inspect live PostgreSQL connection status, table counts, and active AI provider settings.
