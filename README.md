# 📝 Task Manager API

A modern, lightweight REST API for task management. This project features **JWT Authentication**, **Role-Based Access Control (RBAC)**, and a clean **Streamlit** frontend for a seamless user experience.

---

## 🚀 Features

* **FastAPI Backend:** High-performance, asynchronous Python framework.
* **JWT Security:** Secure token-based authentication with `passlib` (bcrypt).
* **SQLite Database:** Simple, serverless data storage using `SQLAlchemy`.
* **Streamlit UI:** A simple, interactive dashboard to manage your tasks.
* **Modular Design:** Clean separation of concerns with a dedicated router structure.

---

## 📁 Project Structure

```text
taskapi/
├── main.py                  # FastAPI app entry point
├── database.py              # Database connection (SQLite)
├── models.py                # Database tables (User, Task)
├── schemas.py               # Request/response data shapes
├── auth.py                  # JWT tokens + password hashing
├── routers/
│   ├── auth_routes.py       # POST /auth/register, POST /auth/login
│   └── task_routes.py       # GET/POST/PUT/DELETE /tasks
├── frontend.py              # Streamlit UI
└── requirements.txt         # Project dependencies