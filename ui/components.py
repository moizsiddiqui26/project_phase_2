import streamlit as st

def render_header(user):

    st.markdown("""
    <style>

    /* HEADER */
    .header {
    
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 10px 20px;
   }

    /* NAV */
    div[role="radiogroup"] > label {
        padding: 8px 12px;
        border-radius: 10px;
        transition: 0.2s ease;
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08);
    }

    div[role="radiogroup"] > label[aria-checked="true"] {
        background: rgba(0,255,204,0.15);
        border: 1px solid rgba(0,255,204,0.35);
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,6,2])

    with col1:
        st.markdown("### 🚀 CRYPTOPORT")

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

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# =========================
# TICKER (IMPROVED CARD UI)
# =========================
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
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
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
