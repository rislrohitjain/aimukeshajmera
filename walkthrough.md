# Comprehensive Walkthrough & URL Guide - Mukesh Ajmera LIC Portal

We have completed all enhanced features requested for **Mukesh Ajmera LIC & Post Office Services** (Sarwar, Rajasthan).

---

## ⚡ Single-Click Local IP Launcher (Port 5050)

You can launch the application with a single click locally on your network on **port 5050**:

1. **Windows 1-Click Launcher**: Double click `run_app.bat` inside `d:\projects\python\aimukeshajmera\`.
2. **Python Launcher**: Run `python run_app.py`.

### What the Launcher Does:
- Automatically detects your local Wi-Fi / Ethernet IP address (e.g., `http://192.168.x.x:5050` or `http://localhost:5050`).
- Connects to PostgreSQL, checks database `aimukeshajmera`, creates tables, and seeds 20 pre-loaded plans.
- Binds the Flask server to `0.0.0.0:5050` so it can be accessed from any device on your local network.
- Automatically opens your default web browser to the portal!

---

## 📊 All Application URLs List (Port 5050)

| URL | Description | Access Permission |
|---|---|---|
| `/` | **Landing Page**: Hero Section, LIC vs Post Office Matrix, 20 Plans Catalog, Contact Us Form, Subscribe Widget, Google Map | Public |
| `/login` | **Mobile Auth**: Login & Auto-registration using 10-digit mobile number | Public |
| `/profile` | **Client Profile**: View & Update Name, DOB, Location, Email | Logged-in User |
| `/blogs` | **Knowledge Center**: Financial & Insurance Guides Catalog | Public |
| `/blog/<slug>` | **Guide Reader**: Detailed article reader with WhatsApp CTA | Public |
| `/sitemap.xml` | **SEO Sitemap**: Dynamic XML Sitemap | Public |
| `/checkdb` | **Database Health Check**: Returns JSON with DB status, table counts, connection metrics | Public |
| `/api/chat` | **AI Chatbot API**: Powers "LIC MITRA" with WhatsApp link builder | Public |
| `/api/products` | **Products API**: Returns LIC & Post Office schemes JSON | Public |
| `/contact` | **Contact Form Submission API**: Submits consultation requests | Public |
| `/subscribe` | **Newsletter Subscription API**: Submits email/mobile updates | Public |
| `/admin/dashboard` | **Graphical Admin Dashboard**: Chart.js Analytics, Product & Blog CRUD, AI Provider Switcher, Sitemap & Contact Leads | Admin Only (Phone: `9829943216`) |
| `/admin/users` | **User Directory**: View registered mobile users & AI Chat logs | Admin Only |

---

## 🎨 New Features & Enhancements

### 1. Admin Graphical Analytics Dashboard (`/admin/dashboard`)
Integrated **Chart.js** with 3 real-time interactive charts:
- **Scheme Distribution Chart**: Visual break-up of 10 LIC Insurance Plans vs 10 Post Office Schemes.
- **Leads & Growth Bar Chart**: Tracks Registered Users, Contact Form Leads, and Newsletter Subscribers.
- **AI Chatbot Interaction Line Chart**: Tracks daily AI Chatbot queries and consultation demands.

### 2. Contact Us Form & Lead Engine
- High-converting form added to landing page (`#contact-us`) collecting **Full Name**, **Mobile Number**, **Location**, and **Interested Plan Message**.
- Submissions are saved to `contact_leads` database table and immediately visible in the Admin Dashboard with direct **WhatsApp Reply** action buttons!

### 3. Newsletter Subscribe Widget
- Allows users to enter mobile number or email to subscribe to LIC bonus rate updates & Post Office interest rate changes.

### 4. Admin Sitemap Management (`/sitemap.xml`)
- Dynamic XML sitemap generator.
- Admin Panel includes a dedicated **Sitemap Management UI** to add or remove indexable URL paths and custom priorities.

### 5. Database Diagnostic Endpoint (`/checkdb`)
- Accessing `http://localhost:5050/checkdb` returns a clean JSON summary:
  ```json
  {
    "status": "online",
    "database_connection": "successful",
    "sanitized_db_url": "postgresql://****:****@localhost:5432/aimukeshajmera",
    "counts": {
      "users": 2,
      "lic_products": 10,
      "post_office_products": 10,
      "blogs": 2,
      "contact_leads": 1,
      "subscribers": 1,
      "chat_logs": 1
    },
    "active_ai_provider": "local"
  }
  ```

---

## 🧪 Test Verification Results

All 7 automated feature tests passed with 100% success rate:
```
Ran 7 tests in 2.079s

OK
OK - Test 01 Passed: 10 LIC + 10 Post Office plans pre-seeded successfully.
OK - Test 02 Passed: Mobile user registration/login verified for phone 9876543210.
OK - Test 03 Passed: Profile update (Name, DOB, Location) verified.
OK - Test 04 Passed: AI Chatbot response & WhatsApp URL generated.
OK - Test 05 Passed: Admin AI Engine toggle verified.
OK - Test 06 Passed: Contact Us form & Subscriber endpoints verified.
OK - Test 07 Passed: /checkdb and /sitemap.xml endpoints verified.
```
