```python
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
db = load_module("db", os.path.join(BASE_DIR, "db", "database.py"))  # ✅ NEW

# =========================
# INIT DATABASE (CRITICAL)
# =========================
db.init_db()   # ✅ THIS FIXES YOUR ERROR

# =========================
# FUNCTIONS
# =========================
login_user = auth.login_user
register_user = auth.register_user

render_header = ui.render_header
render_ticker = ui.render_ticker

get_live_prices = live.get_live_prices


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="🚀 Crypto SaaS", layout="wide")


# =========================
# PREMIUM GLOBAL UI
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}
.block-container {
    padding-top: 1rem;
}
.stButton>button {
    background: linear-gradient(90deg, #00f5ff, #00ffcc);
    color: black;
    font-weight: bold;
    border-radius: 10px;
}
input {
    border-radius: 10px !important;
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
    <div style="text-align:center; padding:50px;">
        <h1 style="color:#00f5ff;">🚀 Crypto SaaS</h1>
        <p style="color:gray;">Smart Crypto Dashboard</p>
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

    now = time.time()

    if now - st.session_state.last_update > 2:
        st.session_state.prices = get_cached_prices()
        st.session_state.last_update = now

    prices = st.session_state.prices

    if prices:
        render_ticker(prices)
    else:
        st.info("⚡ Fetching live prices...")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()

    time.sleep(2)
    st.rerun()


# =========================
# ROUTING
# =========================
if not st.session_state.auth:
    login_ui()
else:
    main_app()
```
