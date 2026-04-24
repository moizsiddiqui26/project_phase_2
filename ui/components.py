
import streamlit as st

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
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([2,6,2])

        with col1:
            st.markdown("### 🚀 Crypto SaaS")

        with col2:
            nav = st.radio(
                "",
                ["📊 Dashboard", "💰 Investment", "⚠ Risk", "🔮 Forecast", "👤 Portfolio"],
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state.page = nav

        with col3:
            st.markdown(f"👤 {user}")
            if st.button("Logout"):
                st.session_state.auth = False
                st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

def render_ticker(prices):

    st.markdown("### 💰 Live Market Prices")

    if not prices:
        st.info("⚡ Updating live market...")
        return

    coins = list(prices.items())
    cols_per_row = 4

    for i in range(0, len(coins), cols_per_row):
        row = coins[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if j < len(row):
                symbol, price = row[j]

                cols[j].markdown(f"""
<div style="
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    backdrop-filter: blur(8px);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.4);
">
    <div style="color:gray;font-size:12px;">
        {symbol}
    </div>
    <div style="
        font-size:22px;
        font-weight:bold;
        color:#00ffcc;
    ">
        ${price:.2f}
    </div>
</div>
""", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
