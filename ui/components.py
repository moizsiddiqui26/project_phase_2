import streamlit as st

# =========================
# HEADER / NAVBAR
# =========================
def render_header(user):

    import streamlit as st

    st.markdown(f"""
    <style>
    .navbar {{
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
    }}

    .logo {{
        font-size: 22px;
        font-weight: bold;
        color: #00f5ff;
    }}

    .nav {{
        display: flex;
        gap: 25px;
        align-items: center;
    }}

    .nav-item {{
        color: white;
        font-size: 14px;
        cursor: pointer;
    }}

    .nav-item:hover {{
        color: #00f5ff;
    }}

    .right {{
        display: flex;
        align-items: center;
        gap: 20px;
    }}

    .logout {{
        background: #1e1e2f;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #444;
        color: white;
        cursor: pointer;
    }}

    .spacer {{
        height: 80px;
    }}
    </style>

    <div class="navbar">
        <div class="logo">🚀 Crypto SaaS</div>

        <div class="nav">
            <div class="nav-item">📊 Dashboard</div>
            <div class="nav-item">💰 Investment</div>
            <div class="nav-item">⚠ Risk</div>
            <div class="nav-item">🔮 Forecast</div>
            <div class="nav-item">👤 Portfolio</div>
        </div>

        <div class="right">
            <div>👤 {user}</div>
            <div class="logout">Logout</div>
        </div>
    </div>

    <div class="spacer"></div>
    """, unsafe_allow_html=True)
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
            <div style="font-size: 14px; color: #aaa;">{coin.upper()}</div>
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
# METRIC ROW (MULTI CARDS)
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
# SUCCESS / ERROR ALERTS
# =========================
def show_success(msg):
    st.success(msg)


def show_error(msg):
    st.error(msg)


# =========================
# LOADING SPINNER
# =========================
def loading(text="Loading..."):
    return st.spinner(text)


# =========================
# NAVIGATION BAR (TOP MENU)
# =========================
def top_nav():
    return st.radio(
        "",
        ["📊 Dashboard", "💰 Investment", "⚠ Risk", "🔮 Forecast", "👤 Portfolio"],
        horizontal=True,
        label_visibility="collapsed"
    )
