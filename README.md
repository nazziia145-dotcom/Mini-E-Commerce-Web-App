# EcommerceMiniprojectwebapp_Nazziia Begum

A simple mini e-commerce web app built with a **Flask backend** and **Streamlit frontend**.

---

## 🧩 Tech Stack
- **Backend:** Flask + SQLAlchemy (SQLite)
- **Frontend:** Streamlit
- **Auth:** JWT (JSON Web Token)
- **CORS Enabled**
- **Database:** SQLite (auto-created)

---

## 👩‍💻 Admin Credentials (seeded)
- **Email:** admin@example.com  
- **Password:** Admin@12345

---

## ⚙️ How to Run (Windows Example)

### 1️⃣ Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python app.py
```
Backend will run on:  
👉 http://localhost:5000  

### 2️⃣ Frontend
Open **a new terminal**:
```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Frontend will open in your browser automatically.  
In the Streamlit **sidebar**, set API Base URL to:  
👉 `http://localhost:5000/api`

---

## 📁 Files Included
- `backend/` → Flask API, database models, auth, seeding
- `frontend/` → Streamlit interface
- `README.md` → Documentation

---

## 🧠 Notes
- The backend now uses **Flask 2.3.3**, compatible with SQLAlchemy 2.x.
- Pagination updated to use the new `db.paginate()` syntax.
- Database tables are auto-created on startup (no manual migration needed).
- If you’d like, I can help deploy:
  - Backend → Render / Railway  
  - Frontend → Streamlit Cloud

---


EcommerceMiniproject_NazziiaBegum/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── auth.py
│   ├── config.py
│   └── ecommerce.db  (auto-created)
│
├── frontend/
│   └── app.py
│
└── README.txt



<!-- Task	Command
Run backend	->python app.py
Run frontend	-> streamlit run app.py
Seed admin & products	-> python seed.py
Frontend API URL ->	http://localhost:5000/api
Admin login	-> admin@example.com / Admin@12345
User login ->	nazia@gmail.com / (your password) -->
**Submitted by:** Nazziia Begum  

