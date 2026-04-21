import streamlit as st

# =========================
# GLOBAL STYLES
# =========================
st.markdown("""
<style>

/* ===== NAVBAR ===== */
.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    background: linear-gradient(90deg, #0f0c29, #302b63);
    padding: 12px 30px;
    border-radius: 0 0 12px 12px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

/* ===== LOGO ===== */
.logo {
    font-size: 22px;
    font-weight: bold;
    color: #00f5ff;
}

/* ===== USER ===== */
.user-box {
    text-align: right;
    font-size: 14px;
}

/* ===== CARD ===== */
.card {
    background: rgba(255,255,255,0.06);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}

/* ===== TICKER CARD ===== */
.ticker {
    background: #1e1e2f;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.3);
    transition: 0.3s;
}

.ticker:hover {
    transform: scale(1.05);
}

/* ===== SECTION ===== */
.section-title {
    font-size: 24px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* ===== BUTTON ===== */
.stButton>button {
    border-radius: 8px;
    padding: 6px 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# HEADER / NAVBAR
# =========================
def render_header(user):

    if "page" not in st.session_state:
        st.session_state.page = "📊 Dashboard"

    col1, col2, col3 = st.columns([2,6,2])

    # LOGO
    with col1:
        st.markdown('<div class="logo">🚀 Crypto SaaS</div>', unsafe_allow_html=True)

    # NAVIGATION
    with col2:
        nav = st.radio(
            "",
            ["📊 Dashboard", "💰 Investment", "⚠ Risk", "🔮 Forecast", "👤 Portfolio"],
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state.page = nav

    # USER + LOGOUT
    with col3:
        st.markdown(f'<div class="user-box">👤 {user}</div>', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# =========================
# LIVE TICKER (IMPROVED)
# =========================
def render_ticker(prices):

    st.markdown("### 💰 Live Market Prices")

    symbol_map = {
        "bitcoin": "BTC",
        "ethereum": "ETH",
        "tether": "USDT",
        "binancecoin": "BNB",
        "ripple": "XRP",
        "solana": "SOL",
        "cardano": "ADA",
        "dogecoin": "DOGE",
        "tron": "TRX",
        "polygon": "MATIC"
    }

    if not prices:
        return

    coins = list(prices.items())

    # ✅ FIXED GRID: 4 per row (best balance)
    cols_per_row = 4

    for i in range(0, len(coins), cols_per_row):
        row = coins[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if j < len(row):
                coin, data = row[j]
                symbol = symbol_map.get(coin, coin.upper())
                price = list(data.values())[0]

                cols[j].markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.05);
                    padding: 18px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
                    transition: 0.3s;
                ">
                    <div style="color:gray;font-size:12px;">
                        {symbol}
                    </div>
                    <div style="
                        font-size:20px;
                        font-weight:bold;
                        color:#00ffcc;
                    ">
                        ${price}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ✅ proper spacing between rows
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
# =========================
# CARD COMPONENT
# =========================
def card(title, value, color="white"):
    st.markdown(f"""
    <div class="card">
        <div style="color:gray;">{title}</div>
        <div style="font-size:22px;font-weight:bold;color:{color};">
            {value}
        </div>
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
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


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

