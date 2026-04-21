import streamlit as st
import os, importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

crypto_api = load_module("crypto_api", os.path.join(BASE_DIR, "services", "crypto_api.py"))
auth_service = load_module("auth_service", os.path.join(BASE_DIR, "auth", "auth_service.py"))
ui = load_module("components", os.path.join(BASE_DIR, "ui", "components.py"))

get_prices = crypto_api.get_top_10_prices
login_user = auth_service.login_user

render_header = ui.render_header
render_ticker = ui.render_ticker

st.set_page_config(layout="wide")

# SESSION
if "auth" not in st.session_state:
    st.session_state.auth = False


# =========================
# CACHE PRICES (IMPORTANT)
# =========================
@st.cache_data(ttl=60)
def get_cached_prices():
    return get_prices()


# =========================
# LOGIN UI
# =========================
def login_ui():
    st.markdown("## 🚀 Crypto SaaS")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = login_user(email, password)
        if res["success"]:
            st.session_state.auth = True
            st.session_state.email = email
            st.rerun()


# =========================
# MAIN APP
# =========================
def main_app():

    render_header(st.session_state.email)

    prices = get_cached_prices()
    render_ticker(prices)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()


# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    main_app()

