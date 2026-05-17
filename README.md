# 💼 JobPortal Admin Dashboard

A professional dark-themed admin dashboard for a job portal.

## 📁 Project Structure

```
job-portal-admin/
├── backend/
│   └── server.py       ← Python Flask API
└── frontend/
    └── public/
        └── index.html  ← Dashboard UI
```

## 🚀 How to Run (Windows)

### Step 1 — Install Python
https://www.python.org/downloads/ — check "Add Python to PATH"

### Step 2 — Install dependencies
```
pip install flask flask-cors
```

### Step 3 — Start backend
Open Command Prompt:
```
cd Desktop\job-portal-admin\backend
python server.py
```
✅ You'll see: Server running at http://localhost:5000

### Step 4 — Open frontend
Double-click: frontend/public/index.html in File Explorer

---

## ✨ Features
- Dashboard stats (Total Jobs, Apps, Users, Active Jobs)
- Bar chart: Applications per job
- Donut chart: Jobs by category
- Jobs table: search, filter by category/status, delete, toggle status
- Applications table: update status, delete
- Users table: view all with roles
- Post Job modal form

## 🛠️ Tech Stack
- Frontend: HTML + CSS + Vanilla JS + Chart.js
- Backend: Python Flask + SQLite
- Sample data auto-seeded on first run

## ❓ Troubleshooting
- "Cannot connect to backend" → make sure python server.py is running
- Port 5000 busy → change port in server.py and update API const in index.html
