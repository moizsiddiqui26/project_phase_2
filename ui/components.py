import streamlit as st


# =========================
# HEADER + NAV
# =========================
def render_header(user):

    st.markdown("""
    <style>
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background: linear-gradient(90deg, #0f0c29, #302b63, #24243e);
        padding: 15px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .nav-item {
        font-size: 16px;
        padding: 8px 12px;
    }
    .section-title {
        font-size: 22px;
        font-weight: bold;
        color: #00f5ff;
        margin-bottom: 16px;
    }
    .kpi {
        background: rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # BUG FIX: initialise page in session_state before radio renders
    # so it survives reruns without resetting to default unexpectedly
    pages = [
        "📊 Dashboard",
        "💰 Investment",
        "⚠ Risk",
        "🔮 Forecast",
        "👤 Portfolio",
        "🔔 Alerts",
    ]

    if "page" not in st.session_state:
        st.session_state.page = pages[0]

    with st.container():
        col1, col2, col3 = st.columns([2, 7, 2])

        with col1:
            st.markdown("### 🚀 Crypto SaaS")

        with col2:
            # BUG FIX: use index= so the radio reflects current page on rerun
            current_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0

            nav = st.radio(
                "",
                pages,
                index=current_index,
                horizontal=True,
                label_visibility="collapsed",
                key="nav_radio",
            )
            st.session_state.page = nav

        with col3:
            st.markdown(f"<p style='color:#aaa;margin-bottom:4px;'>👤 {user}</p>", unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn"):
                # BUG FIX: clear all session keys on logout so stale state
                # doesn't leak into the next login session
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =========================
# LIVE PRICE TICKER
# =========================
def render_ticker(prices):

    st.markdown("### 💰 Live Market Prices")

    if not prices:
        st.info("⚡ Updating live market...")
        return

    coins = list(prices.items())
    cols_per_row = 4

    for i in range(0, len(coins), cols_per_row):
        row  = coins[i : i + cols_per_row]
        # BUG FIX: create only as many columns as we actually have coins in
        # this row — avoids empty ghost columns on the last row
        cols = st.columns(len(row))

        for j, (symbol, price) in enumerate(row):
            # BUG FIX: guard against non-numeric prices coming from the API
            try:
                price_str = f"${float(price):,.2f}"
            except (TypeError, ValueError):
                price_str = "N/A"

            cols[j].markdown(f"""
<div style="
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    backdrop-filter: blur(8px);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
">
    <div style="color:gray;font-size:12px;letter-spacing:1px;">
        {symbol}
    </div>
    <div style="font-size:22px;font-weight:bold;color:#00ffcc;">
        {price_str}
    </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
