import streamlit as st

# =========================
# HEADER / NAVBAR (FUNCTIONAL)
# =========================
def render_header(user):

    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "📊 Dashboard"

    # ================= CSS =================
    st.markdown("""
    <style>
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #0f0c29, #302b63);
        padding: 15px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 999;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    }

    .logo {
        font-size: 22px;
        font-weight: bold;
        color: #00f5ff;
    }

    .nav {
        display: flex;
        gap: 15px;
    }

    .spacer {
        height: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ================= HEADER =================
    col1, col2, col3 = st.columns([2,6,2])

    with col1:
        st.markdown('<div class="logo">🚀 Crypto SaaS</div>', unsafe_allow_html=True)

    with col2:
        nav = st.radio(
            "",
            ["📊 Dashboard", "💰 Investment", "⚠ Risk", "🔮 Forecast", "👤 Portfolio"],
            horizontal=True,
            label_visibility="collapsed",
            key="nav_radio"
        )
        st.session_state.page = nav

    with col3:
        st.write(f"👤 {user}")
        if st.button("🚪 Logout"):
            st.session_state.auth = False
            st.rerun()

    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)


# =========================
# LIVE TICKER
# =========================
def render_ticker(prices):

    st.markdown("### 💰 Live Market Prices")

    cols = st.columns(len(prices))

    for i, (coin, data) in enumerate(prices.items()):

        price = list(data.values())[0]

        cols[i].markdown(f"""
        <div style="
            background: #1e1e2f;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        ">
            <div style="font-size: 13px; color: #aaa;">{coin.upper()}</div>
            <div style="font-size: 18px; font-weight: bold; color: #00ffcc;">
                ${price}
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# CARD COMPONENT
# =========================
def card(title, value, color="white"):
    st.markdown(f"""
    <div style="
    background: rgba(255,255,255,0.08);
    padding:20px;
    border-radius:15px;
    text-align:center;
    ">
        <h4 style="margin:0;color:gray;">{title}</h4>
        <h2 style="margin:0;color:{color};">{value}</h2>
    </div>
    """, unsafe_allow_html=True)


# =========================
# METRIC ROW
# =========================
def metric_row(metrics: list):
    cols = st.columns(len(metrics))

    for i, m in enumerate(metrics):
        with cols[i]:
            card(m["title"], m["value"], m.get("color", "white"))


# =========================
# SECTION TITLE
# =========================
def section(title):
    st.markdown(f"### {title}")


# =========================
# ALERTS
# =========================
def show_success(msg):
    st.success(msg)


def show_error(msg):
    st.error(msg)


# =========================
# LOADING
# =========================
def loading(text="Loading..."):
    return st.spinner(text)
