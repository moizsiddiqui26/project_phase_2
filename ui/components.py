
import streamlit as st

def render_header(user):

    if "page" not in st.session_state:
        st.session_state.page = "📊 Dashboard"

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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


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
                    background: rgba(255,255,255,0.05);
                    padding: 18px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
                ">
                    <div style="color:gray;font-size:12px;">
                        {symbol}
                    </div>
                    <div style="
                        font-size:20px;
                        font-weight:bold;
                        color:#00ffcc;
                    ">
                        ${price:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
