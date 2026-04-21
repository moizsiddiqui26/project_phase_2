import streamlit as st
import os, importlib.util
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ================= LOAD MODULES =================
auth = load_module("auth", os.path.join(BASE_DIR, "auth", "auth_service.py"))
ui = load_module("ui", os.path.join(BASE_DIR, "ui", "components.py"))
live = load_module("live", os.path.join(BASE_DIR, "services", "live_prices.py"))

login_user = auth.login_user
register_user = auth.register_user

render_header = ui.render_header
render_ticker = ui.render_ticker

get_live_prices = live.get_live_prices


# ================= CONFIG =================
st.set_page_config(layout="wide")

st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ================= SESSION =================
if "auth" not in st.session_state:
    st.session_state.auth = False

if "mode" not in st.session_state:
    st.session_state.mode = "login"

if "last_update" not in st.session_state:
    st.session_state.last_update = 0

if "prices" not in st.session_state:
    st.session_state.prices = {}


# ================= FAST PRICE FETCH =================
@st.cache_data(ttl=2)
def get_cached_prices():
    return get_live_prices()


# ================= LOGIN =================
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

        if st.button("Login", use_container_width=True):
            res = login_user(email, password)
            if res["success"]:
                st.session_state.auth = True
                st.session_state.email = email
                st.rerun()

        if st.button("Register", use_container_width=True):
            st.session_state.mode = "register"


# ================= MAIN APP =================
def main_app():

    render_header(st.session_state.email)

    # 🔥 SMART AUTO REFRESH (NO LOOP)
    now = time.time()

    if now - st.session_state.last_update > 2:
        st.session_state.prices = get_cached_prices()
        st.session_state.last_update = now

    prices = st.session_state.prices

    # UI
    if prices:
        render_ticker(prices)
    else:
        st.info("⚡ Fetching live prices...")

    # small spacing
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # load dashboard
    dashboard = load_module("dashboard", os.path.join(BASE_DIR, "ui", "dashboard.py"))
    dashboard.main()

    # 🔁 trigger refresh
    st.experimental_rerun()


# ================= ROUTING =================
if not st.session_state.auth:
    login_ui()
else:
    main_app()

