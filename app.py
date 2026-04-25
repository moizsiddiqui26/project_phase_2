import streamlit as st
import os, importlib.util
import time

# =========================
# 🔥 GLOBAL CSS (FINAL UI FIX)
# =========================
st.markdown("""
<style>

/* 🔥 REMOVE STREAMLIT DEFAULT UI */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 🔥 REMOVE TOP TOOLBAR (BLACK BAR) */
div[data-testid="stToolbar"] {
    display: none !important;
}

/* 🔥 REMOVE ALL TOP SPACING */
div[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
}

.block-container {
    padding-top: 0rem !important;
}

section.main > div {
    padding-top: 0rem !important;
}

/* 🌌 BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1840, #24243e);
    color: #eaeaf0;
}

/* 🔘 BUTTON STYLE */
.stButton>button {
    background: linear-gradient(90deg, #00f5ff, #00ffcc);
    color: black;
    font-weight: bold;
    border-radius: 10px;
}

/* 💎 GLASS CARD */
.glass-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    padding: 20px;
}

/* 🎯 SELECT TAG FIX */
div[data-baseweb="tag"] {
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* 📉 SELECT BOX BACKGROUND */
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
}

</style>
""", unsafe_allow_html=True)


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
db = load_module("db", os.path.join(BASE_DIR, "db", "database.py"))

# =========================
# INIT DB
# =========================
db.init_db()

login_user = auth.login_user
register_user = auth.register_user

render_header = ui.render_header
render_ticker = ui.render_ticker

get_live_prices = live.get_live_prices


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="🚀 Crypto SaaS", layout="wide")


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
# PRICE CACHE (FAST + STABLE)
# =========================
@st.cache_data(ttl=5)
def get_cached_prices():
    return get_live_prices()


# =========================
# LOGIN UI
# =========================
def login_ui():

    if st.session_state.auth:
        return

    st.markdown("""
    <div style="text-align:center; padding:60px;">
        <h1 style="color:#00f5ff;">🚀 Crypto SaaS</h1>
        <p style="color:gray;">Smart Crypto Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,4,2])

    with col2:

        if st.session_state.mode == "login":

            st.markdown("### 🔐 Login")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("🚀 Login", use_container_width=True):
                res = login_user(email, password)

                if res["success"]:
                    st.session_state.auth = True
                    st.session_state.email = email
                    st.success("Login successful 🚀")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(res["msg"])

            if st.button("📝 Register", use_container_width=True):
                st.session_state.mode = "register"
                st.rerun()

        else:

            st.markdown("### 📝 Create Account")

            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("✅ Create Account", use_container_width=True):
                res = register_user(name, email, password)

                if res["success"]:
                    st.success("Account created successfully 🎉")
                    time.sleep(1)
                    st.session_state.mode = "login"
                    st.rerun()
                else:
                    st.error(res["msg"])

            if st.button("⬅ Back to Login"):
                st.session_state.mode = "login"
                st.rerun()


# =========================
# MAIN APP
# =========================
def main_app():

    render_header(st.session_state.email)

    now = time.time()

    # 🔄 Update only prices (no full rerender loop)
    if now - st.session_state.last_update > 5:
        st.session_state.prices = get_cached_prices()
        st.session_state.last_update = now

    prices = st.session_state.prices

    # 🔥 CLEAN FETCHING UI
    if prices:
        render_ticker(prices)
    else:
        st.markdown("""
        <div style="
            background: rgba(0,255,204,0.08);
            border: 1px solid rgba(0,255,204,0.2);
            padding: 16px;
            border-radius: 12px;
            color: #00ffcc;
        ">
        ⚡ Fetching live prices...
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()
    from services.alert_engine import check_alerts
    if prices:
        check_alerts(prices)
# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    st.empty()
    main_app()
