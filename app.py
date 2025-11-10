import streamlit as st
import requests

# ✅ Backend API Base URL
API_BASE = "http://127.0.0.1:5000/api"

st.set_page_config(page_title="E-Commerce", layout="centered")

st.title("🛍️ E-Commerce (Streamlit Frontend)")

# --- Helper Functions ---
def safe_json(response):
    """Safely parse JSON from backend response."""
    try:
        return response.json()
    except Exception:
        return {"message": f"Server error ({response.status_code})"}

# --- Register Section ---
with st.expander("Register", expanded=True):
    name = st.text_input("Name", key="name")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")

    if st.button("Register"):
        if not email or not password:
            st.error("Please fill all fields")
        else:
            data = {"name": name, "email": email, "password": password}
            try:
                r = requests.post(f"{API_BASE}/register", json=data)
                if r.status_code == 201:
                    st.success("✅ Registration successful! Please login below.")
                else:
                    msg = safe_json(r).get("message", "Registration failed.")
                    st.error(msg)
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

# --- Login Section ---
with st.expander("Login", expanded=True):
    login_email = st.text_input("Email (login)", key="login_email")
    login_password = st.text_input("Password (login)", type="password", key="login_password")

    if st.button("Login"):
        if not login_email or not login_password:
            st.error("Please fill in both fields.")
        else:
            try:
                r = requests.post(f"{API_BASE}/login", json={"email": login_email, "password": login_password})
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["token"]
                    st.session_state["user"] = data["user"]
                    st.success(f"✅ Welcome, {data['user']['email']}!")
                else:
                    msg = safe_json(r).get("message", "Invalid credentials.")
                    st.error(msg)
            except Exception as e:
                st.error(f"Connection error: {e}")

# --- If logged in ---
if "user" in st.session_state:
    user = st.session_state["user"]
    st.subheader(f"Welcome, {user['email']} 👋")
    st.write(f"Role: **{user['role']}**")

    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully.")

    # Example of a protected API call
    st.markdown("---")
    st.write("🔒 Fetching products (example):")
    try:
        r = requests.get(f"{API_BASE}/products")
        if r.status_code == 200:
            data = safe_json(r)
            for p in data.get("products", []):
                st.write(f"- {p['name']} (${p['price']})")
        else:
            st.warning(f"Failed to fetch products: {r.status_code}")
    except Exception as e:
        st.error(f"Backend not reachable: {e}")

else:
    st.info("Please log in to view products and orders.")
