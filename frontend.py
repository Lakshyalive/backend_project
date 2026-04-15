# frontend.py
# Simple Streamlit UI to interact with the FastAPI backend.
# This gives you a Register / Login page and a Task Dashboard.
#
# To run: streamlit run frontend.py
# Make sure the FastAPI server is running first! (uvicorn main:app --reload)

import streamlit as st
import requests
import base64
import json
import os


def get_api_url() -> str:
    # Priority: env var -> Streamlit secrets -> local dev default.
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url.rstrip("/")
    try:
        secret_url = st.secrets.get("BACKEND_URL")
        if secret_url:
            return str(secret_url).rstrip("/")
    except Exception:
        pass
    return "http://127.0.0.1:8000"


API_URL = get_api_url()

st.set_page_config(page_title="Task Manager", page_icon="✅")
st.title("✅ Task Manager")


# ─── SESSION STATE ────────────────────────────────────────────────────────────
# session_state is like a global variable that persists across page reruns.
# We use it to store the JWT token after login.
if "token"    not in st.session_state: st.session_state.token    = None
if "username" not in st.session_state: st.session_state.username = None
if "role"     not in st.session_state: st.session_state.role     = "user"


# Helper: build the Authorization header using the stored token
def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def role_from_token(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return "user"
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8")).decode("utf-8")
        data = json.loads(decoded)
        return data.get("role", "user")
    except Exception:
        return "user"


def api_request(method: str, path: str, **kwargs):
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=10, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error(
            f"Cannot connect to backend at {API_URL}. "
            "If this is Streamlit Cloud, set BACKEND_URL to your deployed FastAPI URL."
        )
        return None


def response_detail(response: requests.Response, fallback: str) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            return body.get("detail", fallback)
        return fallback
    except ValueError:
        text = response.text.strip()
        return text if text else fallback


# ─── NOT LOGGED IN → SHOW LOGIN / REGISTER TABS ──────────────────────────────
if not st.session_state.token:

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    # LOGIN TAB
    with tab_login:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True):
            response = api_request("POST", "/auth/login", json={"username": username, "password": password})
            if response is None:
                st.stop()
            if response.status_code == 200:
                st.session_state.token    = response.json()["access_token"]
                st.session_state.username = username
                st.session_state.role     = role_from_token(st.session_state.token)
                st.success("Logged in successfully!")
                st.rerun()   # refresh the page to show the dashboard
            else:
                st.error(response_detail(response, "Login failed"))

    # REGISTER TAB
    with tab_register:
        st.subheader("Create a new account")
        new_username = st.text_input("Username",        key="reg_user")
        new_email    = st.text_input("Email",           key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Register", use_container_width=True):
            response = api_request(
                "POST",
                "/auth/register",
                json={"username": new_username, "email": new_email, "password": new_password},
            )
            if response is None:
                st.stop()
            if response.status_code == 200:
                st.success("✅ Account created! Please switch to the Login tab.")
            else:
                st.error(response_detail(response, "Registration failed"))


# ─── LOGGED IN → SHOW DASHBOARD ──────────────────────────────────────────────
else:

    # Header with username and logout button
    col_name, col_logout = st.columns([4, 1])
    with col_name:
        st.write(f"👋 Welcome, **{st.session_state.username}**! ({st.session_state.role})")
    with col_logout:
        if st.button("Logout"):
            st.session_state.token    = None
            st.session_state.username = None
            st.session_state.role     = "user"
            st.rerun()

    st.divider()

    # ── CREATE TASK FORM ──────────────────────────────────────────────────────
    st.subheader("➕ Add New Task")
    task_title = st.text_input("Task title")
    task_desc  = st.text_input("Description (optional)")

    if st.button("Add Task", use_container_width=True):
        if not task_title.strip():
            st.warning("Please enter a task title")
        else:
            response = api_request(
                "POST",
                "/tasks/",
                json={"title": task_title, "description": task_desc},
                headers=auth_headers(),
            )
            if response is None:
                st.stop()
            if response.status_code == 200:
                st.success("Task added!")
                st.rerun()
            else:
                st.error("Failed to add task - are you still logged in?")

    st.divider()

    # ── TASK LIST ─────────────────────────────────────────────────────────────
    st.subheader("📋 My Tasks")

    response = api_request("GET", "/tasks/", headers=auth_headers())
    if response is None:
        st.stop()

    if response.status_code != 200:
        st.error("Could not load tasks. Try logging in again.")
    else:
        tasks = response.json()

        if not tasks:
            st.info("No tasks yet! Add one above.")

        for task in tasks:
            col_text, col_done, col_delete = st.columns([5, 1, 1])

            with col_text:
                icon = "✅" if task["completed"] else "⬜"
                st.write(f"{icon} **{task['title']}**")
                if task["description"]:
                    st.caption(task["description"])

            with col_done:
                label = "Undo" if task["completed"] else "Done"
                if st.button(label, key=f"done_{task['id']}"):
                    response = api_request(
                        "PUT",
                        f"/tasks/{task['id']}",
                        json={"completed": not task["completed"]},
                        headers=auth_headers(),
                    )
                    if response is None:
                        st.stop()
                    st.rerun()

            with col_delete:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    response = api_request("DELETE", f"/tasks/{task['id']}", headers=auth_headers())
                    if response is None:
                        st.stop()
                    st.rerun()

    if st.session_state.role == "admin":
        st.divider()
        st.subheader("🛡️ Admin Panel - All Tasks")
        admin_response = api_request("GET", "/tasks/admin", headers=auth_headers())
        if admin_response is None:
            st.stop()
        if admin_response.status_code == 200:
            admin_tasks = admin_response.json()
            if not admin_tasks:
                st.info("No tasks found across users.")
            else:
                st.dataframe(admin_tasks, use_container_width=True)
        else:
            st.error(response_detail(admin_response, "Could not load admin tasks"))