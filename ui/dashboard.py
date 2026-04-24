import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from services.crypto_api import get_historical_data
from services.risk_engine import run_risk_analysis, calculate_portfolio_risk
from services.forecast_engine import get_forecast_summary
from db.models import add_holding, get_holdings


# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=300)
def load_data():
    return get_historical_data()


# =========================
# UI HELPERS
# =========================
def space(h=25):
    st.markdown(f"<div style='height:{h}px'></div>", unsafe_allow_html=True)


# =========================
# MAIN ENTRY (ONLY FUNCTION THAT RENDERS)
# =========================
def main():

    page = st.session_state.get("page", "📊 Dashboard")
    df = load_data()

    if df is None or df.empty:
        st.error("⚠ Failed to load data")
        return

    # =========================
    # ROUTER (ONLY ONE PAGE)
    # =========================
    if page == "📊 Dashboard":
        render_dashboard(df)

    elif page == "💰 Investment":
        render_investment(df)

    elif page == "⚠ Risk":
        render_risk(df)

    elif page == "🔮 Forecast":
        render_forecast(df)

    elif page == "👤 Portfolio":
        render_portfolio(df)



# ============================================================
# 📊 DASHBOARD
# ============================================================
def render_dashboard(df):

    st.markdown('<div class="section-title">📊 Market Overview</div>', unsafe_allow_html=True)

    coins = sorted(df["Crypto"].unique())
    selected = st.multiselect("Select Coins", coins, default=coins[:4])

    f = df[df["Crypto"].isin(selected)].copy()

    if f.empty:
        st.warning("Select at least one coin")
        return

    # =========================
    # KPI
    # =========================
    latest = f.groupby("Crypto").last().reset_index()
    cols = st.columns(min(4, len(latest)))

    for i, row in latest.head(4).iterrows():
        price = row["Close"]

        change = f[f["Crypto"] == row["Crypto"]]["Close"].pct_change().iloc[-1]
        change = round(change * 100, 2) if pd.notna(change) else 0

        color = "#00ffcc" if change >= 0 else "#ff4b4b"

        cols[i].markdown(f"""
        <div class="kpi">
            <div style="color:gray">{row['Crypto']}</div>
            <div style="font-size:22px;font-weight:bold;color:#00ffcc;">
                ${price:.2f}
            </div>
            <div style="color:{color}">
                {change}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # PREP DATA
    # =========================
    f["Return"] = f.groupby("Crypto")["Close"].pct_change()

    pivot = f.pivot(index="Date", columns="Crypto", values="Close")
    corr = pivot.pct_change().corr()

    # =========================
    # GRID LAYOUT (2 x 2)
    # =========================
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # -------------------------
    # 📈 PRICE TREND
    # -------------------------
    with row1_col1:
        fig1 = px.line(f, x="Date", y="Close", color="Crypto", template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True, key="price_chart")


        st.caption("📈 Price movement over time — helps identify trends.")

    # -------------------------
    # 📉 RETURNS
    # -------------------------
    with row1_col2:
        fig2 = px.line(f, x="Date", y="Return", color="Crypto", template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True, key="returns_chart")

        st.caption("📉 Daily returns — shows volatility and risk spikes.")

    # -------------------------
    # 🔥 CORRELATION
    # -------------------------
    with row2_col1:
        fig3 = px.imshow(corr, text_auto=True, template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True, key="corr_chart")


        st.caption("🔥 Correlation between coins — useful for diversification.")

    # -------------------------
    # 📊 DISTRIBUTION
    # -------------------------
    with row2_col2:
        fig4 = px.histogram(
            f,
            x="Return",
            color="Crypto",
            nbins=50,
            template="plotly_dark",
            opacity=0.6
        )

        st.plotly_chart(fig4, use_container_width=True, key="dist_chart")

        st.caption("📊 Return distribution — wide spread = high risk.")
# ============================================================
# 💰 INVESTMENT
# ============================================================
def render_investment(df):

    st.markdown('<div class="section-title">💰 Smart Investment Allocation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    amount = col1.number_input("Investment ($)", value=1000.0)
    risk = col2.selectbox("Risk Level", ["Low", "Medium", "High"])

    returns = df.groupby("Crypto").apply(
        lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
    ).reset_index(name="Return")

    vol = df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

    m = returns.merge(vol, on="Crypto")

    # FIX: no negative allocations
    m["Return"] = m["Return"].clip(lower=0)

    if risk == "Low":
        m["Score"] = 1 / (m["Vol"] + 1e-6)
    elif risk == "Medium":
        m["Score"] = m["Return"] / (m["Vol"] + 1e-6)
    else:
        m["Score"] = m["Return"]

    m = m[m["Score"] > 0]

    m["Allocation %"] = m["Score"] / m["Score"].sum() * 100
    m["Investment"] = m["Allocation %"] / 100 * amount

    m = m.round(2)

    space()

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(m, use_container_width=True)

    with col2:
        fig = px.pie(m, names="Crypto", values="Investment", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# ⚠ RISK
# ============================================================
def render_risk(df):

    st.markdown('<div class="section-title">⚠ Risk Analysis</div>', unsafe_allow_html=True)

    risk_df = run_risk_analysis(df)
    st.dataframe(risk_df, use_container_width=True)

    space()

    portfolio = calculate_portfolio_risk(df)

    col1, col2 = st.columns(2)
    col1.metric("Risk Level", portfolio["level"])
    col2.metric("Risk Score", portfolio["score"])


# ============================================================
# 🔮 FORECAST
# ============================================================
def render_forecast(df):

    st.markdown('<div class="section-title">🔮 Forecast</div>', unsafe_allow_html=True)

    coin = st.selectbox("Select Coin", df["Crypto"].unique())
    amount = st.number_input("Investment ($)", value=1000.0)

    coin_df = df[df["Crypto"] == coin]

    result = get_forecast_summary(coin_df, amount, 7)

    if result:
        space()

        col1, col2, col3 = st.columns(3)
        col1.metric("Predicted Price", f"${result['predicted_price']:.2f}")
        col2.metric("Expected Value", f"${result['expected_value']:.2f}")
        col3.metric("Profit %", f"{result['profit_pct']:.2f}%")


# ============================================================
# 👤 PORTFOLIO
# ============================================================
def render_portfolio(df):

    st.markdown('<div class="section-title">👤 Portfolio</div>', unsafe_allow_html=True)

    email = st.session_state.get("email")

    col1, col2, col3 = st.columns(3)
    coin = col1.selectbox("Crypto", df["Crypto"].unique())
    amount = col2.number_input("Amount ($)", min_value=0.0)
    date = col3.date_input("Date")

    if st.button("Add Investment"):
        add_holding(email, coin, amount, str(date))
        st.success("Added!")

    st.markdown("<br>", unsafe_allow_html=True)

    data = get_holdings(email)

    if not data:
        st.info("No investments yet")
        return

    portfolio_df = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
    portfolio_df["Date"] = pd.to_datetime(portfolio_df["Date"])

    # =========================
    # 🔥 CALCULATE CURRENT PRICE
    # =========================
    latest_prices = df.groupby("Crypto").last().reset_index()[["Crypto", "Close"]]
    latest_prices.rename(columns={"Close": "Current Price"}, inplace=True)

    # Merge with portfolio
    portfolio_df = portfolio_df.merge(latest_prices, on="Crypto", how="left")

    # =========================
    # 🔥 CALCULATE BUY PRICE
    # =========================
    def get_buy_price(row):
        coin_df = df[df["Crypto"] == row["Crypto"]]
        past_data = coin_df[coin_df["Date"] <= row["Date"]]

        if past_data.empty:
            return np.nan

        return past_data.iloc[-1]["Close"]

    portfolio_df["Buy Price"] = portfolio_df.apply(get_buy_price, axis=1)

    # =========================
    # 🔥 CALCULATE PROFIT
    # =========================
    portfolio_df["Quantity"] = portfolio_df["Amount"] / portfolio_df["Buy Price"]

    portfolio_df["Current Value"] = portfolio_df["Quantity"] * portfolio_df["Current Price"]

    portfolio_df["Profit ($)"] = portfolio_df["Current Value"] - portfolio_df["Amount"]

    portfolio_df["Profit (%)"] = (portfolio_df["Profit ($)"] / portfolio_df["Amount"]) * 100

    # Clean format
    portfolio_df = portfolio_df.round(2)

    # =========================
    # 💎 DISPLAY
    # =========================
    st.dataframe(portfolio_df, use_container_width=True)

    # =========================
    # 📊 TOTAL PORTFOLIO SUMMARY
    # =========================
    total_invested = portfolio_df["Amount"].sum()
    total_value = portfolio_df["Current Value"].sum()
    total_profit = total_value - total_invested
    profit_pct = (total_profit / total_invested) * 100 if total_invested > 0 else 0

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Invested", f"${total_invested:.2f}")
    col2.metric("Current Value", f"${total_value:.2f}")
    col3.metric("Profit", f"${total_profit:.2f} ({profit_pct:.2f}%)")
    st.markdown("### 📊 Portfolio Insights")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(
        portfolio_df,
        names="Crypto",
        values="Current Value",
        title="Investment Allocation",
        template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True, key="portfolio_pie")

        st.caption("💰 Shows how your investment is distributed across coins.")

    with col2:
        fig2 = px.bar(
            portfolio_df,
            x="Crypto",
            y="Profit ($)",
            color="Profit ($)",
            color_continuous_scale=["red", "green"],
            title="Profit / Loss by Coin",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True, key="portfolio_profit")

        st.caption("📈 Shows which coins are making profit or loss.")
