import os
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =========================
# LOAD MODULES
# =========================
crypto_api = load_module("crypto_api", os.path.join(BASE_DIR, "services", "crypto_api.py"))
email_service = load_module("email_service", os.path.join(BASE_DIR, "services", "email_service.py"))
auth_service = load_module("auth_service", os.path.join(BASE_DIR, "auth", "auth_service.py"))
db_module = load_module("database", os.path.join(BASE_DIR, "db", "database.py"))
ui_components = load_module("components", os.path.join(BASE_DIR, "ui", "components.py"))

# Extract
get_top_10_prices = crypto_api.get_top_10_prices
send_welcome_email = email_service.send_welcome_email
send_otp_email = email_service.send_otp_email

login_user = auth_service.login_user
register_user = auth_service.register_user
generate_login_otp = auth_service.generate_login_otp
verify_otp = auth_service.verify_otp

init_db = db_module.init_db

render_header = ui_components.render_header
render_ticker = ui_components.render_ticker


# =========================
# IMPORTS
# =========================
import streamlit as st


# =========================
# INIT
# =========================
init_db()

st.set_page_config(page_title="🚀 Crypto SaaS Platform", layout="wide")


# =========================
# HIDE DEFAULT UI
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
# HEADERS
# =========================
def render_public_header():
    st.markdown("## 🚀 Welcome to Crypto SaaS")
    prices = get_top_10_prices()
    render_ticker(prices)


def render_private_header():
    user = st.session_state.get("email", "Guest")
    render_header(user)

    prices = get_top_10_prices()
    render_ticker(prices)


# =========================
# AUTH UI
# =========================
def login_ui():

    render_public_header()

    # ================= LOGIN =================
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

    # ================= REGISTER =================
    elif st.session_state.mode == "register":

        st.subheader("📝 Register")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            res = register_user(name, email, password)

            if res["success"]:
                send_welcome_email(email)

                # ✅ AUTO LOGIN AFTER REGISTER
                st.session_state.auth = True
                st.session_state.email = email

                st.success("Account created & logged in successfully 🚀")
                st.rerun()
            else:
                st.error(res["msg"])

        if st.button("Back"):
            st.session_state.mode = "login"

    # ================= OTP LOGIN =================
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

    render_private_header()

    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()


# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    main_app()
