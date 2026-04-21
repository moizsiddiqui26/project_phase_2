import streamlit as st
import os, importlib.util
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# LOAD MODULES
auth = load_module("auth", os.path.join(BASE_DIR, "auth", "auth_service.py"))
ui = load_module("ui", os.path.join(BASE_DIR, "ui", "components.py"))
live = load_module("live", os.path.join(BASE_DIR, "services", "live_prices.py"))

login_user = auth.login_user
register_user = auth.register_user

render_header = ui.render_header
render_ticker = ui.render_ticker

get_live_prices = live.get_live_prices

st.set_page_config(layout="wide")

# SESSION
if "auth" not in st.session_state:
    st.session_state.auth = False

if "mode" not in st.session_state:
    st.session_state.mode = "login"


# ================= LOGIN =================
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

    if st.button("Register"):
        st.session_state.mode = "register"


# ================= MAIN APP =================
def main_app():

    render_header(st.session_state.email)

    placeholder = st.empty()

    # live refresh loop
    for _ in range(1000):

        prices = get_live_prices()

        with placeholder.container():
            render_ticker(prices)

        time.sleep(2)


# ================= ROUTING =================
if not st.session_state.auth:
    login_ui()
else:
    main_app()

