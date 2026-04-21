import streamlit as st
import os, importlib.util
import time

# =========================
# MODULE LOADER
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =========================
# LOAD MODULES
# =========================
auth = load_module("auth", os.path.join(BASE_DIR, "auth", "auth_service.py"))
ui = load_module("ui", os.path.join(BASE_DIR, "ui", "components.py"))
live = load_module("live", os.path.join(BASE_DIR, "services", "live_prices.py"))

login_user = auth.login_user
register_user = auth.register_user

render_header = ui.render_header
render_ticker = ui.render_ticker

get_live_prices = live.get_live_prices


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🚀 Crypto SaaS", layout="wide")

st.markdown("""
<style>

/* App Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* Section Titles */
.section-title {
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Glow text */
.glow {
    color: #00f5ff;
}

/* Inputs */
input, .stNumberInput, .stSelectbox {
    border-radius: 10px !important;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background: #00f5ff;
    color: black;
    font-weight: bold;
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

if "last_update" not in st.session_state:
    st.session_state.last_update = 0

if "prices" not in st.session_state:
    st.session_state.prices = {}


# =========================
# FAST PRICE FETCH
# =========================
@st.cache_data(ttl=2)
def get_cached_prices():
    return get_live_prices()


# =========================
# LOGIN UI
# =========================
def login_ui():

    st.markdown("""
    <div style="text-align:center; padding:40px;">
        <h1 style="color:#00f5ff;">🚀 Crypto SaaS</h1>
        <p style="color:gray;">Real-time Crypto Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,4,2])

    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("🚀 Login", use_container_width=True):
            res = login_user(email, password)
            if res["success"]:
                st.session_state.auth = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error(res["msg"])

        if st.button("📝 Register", use_container_width=True):
            st.session_state.mode = "register"


# =========================
# MAIN APP
# =========================
def main_app():

    render_header(st.session_state.email)

    # ✅ Update prices every 2 seconds
    now = time.time()

    if now - st.session_state.last_update > 2:
        st.session_state.prices = get_cached_prices()
        st.session_state.last_update = now

    prices = st.session_state.prices

    # =========================
    # TICKER
    # =========================
    if prices:
        render_ticker(prices)
    else:
        st.info("⚡ Fetching live prices...")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # =========================
    # DASHBOARD
    # =========================
    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()

    # =========================
    # AUTO REFRESH (SAFE)
    # =========================
    time.sleep(2)
    st.rerun()


# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    main_app()
