import sys
import os

# 🔥 FORCE ROOT PATH (STREAMLIT CLOUD FIX)
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# 🔥 ALSO ADD PARENT (IMPORTANT)
PARENT = os.path.dirname(ROOT)
if PARENT not in sys.path:
    sys.path.append(PARENT)
    
# =========================
# IMPORTS
# =========================
import streamlit as st
import time

# DB INIT
from db.database import init_db
init_db()

# AUTH SERVICES
from auth.auth_service import login_user

try:
    import sys
    import os

# FORCE ROOT PATH
    sys.path.append(os.getcwd())

# NOW IMPORT
    from .services.crypto_api import get_top_10_prices
except ModuleNotFoundError:
    import sys, os
    sys.path.append(os.getcwd())
    from .services.crypto_api import get_top_10_prices
    
# UI COMPONENTS
from ui.components import render_header, render_ticker

# CONFIG
from config import AUTO_REFRESH_INTERVAL


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🚀 Crypto SaaS Platform", layout="wide")

# =========================
# HIDE STREAMLIT DEFAULT UI
# =========================
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# =========================
# GLOBAL STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "mode" not in st.session_state:
    st.session_state.mode = "login"

if "otp" not in st.session_state:
    st.session_state.otp = None

if "temp_email" not in st.session_state:
    st.session_state.temp_email = None

# =========================
# AUTO REFRESH
# =========================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > AUTO_REFRESH_INTERVAL:
    st.session_state.last_refresh = time.time()
    st.rerun()


# =========================
# HEADER + TICKER
# =========================
def render_top():
    user = st.session_state.get("email", "Guest")
    render_header(user)

    prices = get_top_10_prices()
    render_ticker(prices)


# =========================
# AUTH UI
# =========================
def login_ui():

    render_top()

    # ---------- LOGIN ----------
    if st.session_state.mode == "login":

        st.subheader("🔐 Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Login"):
                res = login_user(email, password)

                if res["success"]:
                    st.session_state.auth = True
                    st.session_state.email = res["user"]["email"]
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error(res["msg"])

        with col2:
            if st.button("Register"):
                st.session_state.mode = "register"

        with col3:
            if st.button("OTP Login"):
                st.session_state.mode = "otp"

    # ---------- REGISTER ----------
    elif st.session_state.mode == "register":

        st.subheader("📝 Register")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            res = register_user(name, email, password)

            if res["success"]:
                send_welcome_email(email)
                st.success(res["msg"])
                st.session_state.mode = "login"
            else:
                st.error(res["msg"])

        if st.button("Back"):
            st.session_state.mode = "login"

    # ---------- OTP LOGIN ----------
    elif st.session_state.mode == "otp":

        st.subheader("🔐 OTP Login")

        email = st.text_input("Email")

        if st.button("Send OTP"):
            otp = generate_login_otp()

            st.session_state.otp = otp
            st.session_state.temp_email = email

            send_otp_email(email, otp)
            st.success("OTP sent")

        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if verify_otp(otp_input, st.session_state.otp):
                st.session_state.auth = True
                st.session_state.email = st.session_state.temp_email
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid OTP")

        if st.button("Back"):
            st.session_state.mode = "login"


# =========================
# MAIN APP
# =========================
def main_app():

    render_top()

    # Logout button
    col1, col2 = st.columns([9, 1])

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.auth = False
            st.rerun()

    # Load dashboard
    from ui.dashboard import main
    main()


# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    main_app()
