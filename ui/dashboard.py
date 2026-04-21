import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# SERVICES
from services.crypto_api import get_historical_data
from services.risk_engine import run_risk_analysis, calculate_portfolio_risk
from services.forecast_engine import get_forecast_summary

# DB
from db.models import add_holding, get_holdings


# =========================
# GLOBAL UI STYLE
# =========================
st.markdown("""
<style>
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 10px;
}

.card {
    background: rgba(255,255,255,0.06);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

.small-card {
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=300)
def load_data():
    return get_historical_data()


# =========================
# MAIN DASHBOARD
# =========================
def main():

    page = st.session_state.get("page", "📊 Dashboard")

    with st.spinner("🚀 Loading crypto data..."):
        df = load_data()

    if df.empty:
        st.error("⚠ Failed to load data")
        return

    # =========================
    # 📊 DASHBOARD
    # =========================
    if page == "📊 Dashboard":

        st.markdown('<div class="section-title">📊 Market Overview</div>', unsafe_allow_html=True)
        all_coins = sorted(df["Crypto"].unique())
        default_coins = [c for c in ["BTC", "ETH", "BNB", "SOL"] if c in all_coins]

        if not default_coins:
            default_coins = all_coins[:4]

        coins = st.multiselect("Select Coins",all_coins,default=default_coins)
        f = df[df["Crypto"].isin(coins)].copy()

        if f.empty:
            st.warning("Select at least one coin")
            return

        # 🔥 METRICS CARDS

        # 📈 PRICE TREND
        fig1 = px.line(
            f, x="Date", y="Close", color="Crypto",
            title="📈 Price Trends",
            template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 📊 RETURNS
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()

        fig2 = px.line(
            f, x="Date", y="Return", color="Crypto",
            title="📊 Returns",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ⚠ VOLATILITY
        f["Volatility"] = f.groupby("Crypto")["Return"].transform(
            lambda x: x.rolling(7).std()
        )

        fig3 = px.line(
            f, x="Date", y="Volatility", color="Crypto",
            title="⚠ Volatility",
            template="plotly_dark"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # 🔗 CORRELATION
        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        fig4 = px.imshow(
            corr,
            text_auto=True,
            title="🔗 Correlation Matrix",
            template="plotly_dark"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # =========================
    # 💰 INVESTMENT
    # =========================
    elif page == "💰 Investment":

        st.markdown('<div class="section-title">💰 Smart Investment</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        amount = col1.number_input("Investment ($)", value=1000.0)
        risk = col2.selectbox("Risk Level", ["Low", "Medium", "High"])

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        vol = df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m = returns.merge(vol, on="Crypto")

        if risk == "Low":
            m["Score"] = 1 / m["Vol"]
        elif risk == "Medium":
            m["Score"] = m["Return"] / m["Vol"]
        else:
            m["Score"] = m["Return"]

        m["Allocation %"] = m["Score"] / m["Score"].sum() * 100
        m["Investment"] = m["Allocation %"] / 100 * amount

        st.dataframe(m, use_container_width=True)

        fig = px.pie(
            m,
            names="Crypto",
            values="Investment",
            title="📊 Portfolio Allocation",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ⚠ RISK
    # =========================
    elif page == "⚠ Risk":

        st.markdown('<div class="section-title">⚠ Risk Analysis</div>', unsafe_allow_html=True)

        risk_df = run_risk_analysis(df)
        st.dataframe(risk_df, use_container_width=True)

        portfolio = calculate_portfolio_risk(df)

        col1, col2 = st.columns(2)

        col1.markdown(f"""
        <div class="card">
            <h4>Risk Level</h4>
            <h2 style="color:#ff4b4b;">{portfolio['level']}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
            <h4>Risk Score</h4>
            <h2 style="color:#00ffcc;">{portfolio['score']}</h2>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # 🔮 FORECAST
    # =========================
    elif page == "🔮 Forecast":

        st.markdown('<div class="section-title">🔮 Forecast</div>', unsafe_allow_html=True)

        coin = st.selectbox("Select Coin", df["Crypto"].unique())
        amount = st.number_input("Investment ($)", value=1000.0)
        days = st.slider("Days", 1, 30, 7)

        coin_df = df[df["Crypto"] == coin]

        result = get_forecast_summary(coin_df, amount, days)

        if result:

            col1, col2, col3 = st.columns(3)

            col1.metric("Predicted Price", f"${result['predicted_price']:.2f}")
            col2.metric("Expected Value", f"${result['expected_value']:.2f}")
            col3.metric("Profit %", f"{result['profit_pct']:.2f}%")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=coin_df["Date"],
                y=coin_df["Close"],
                name="Actual"
            ))

            fig.add_trace(go.Scatter(
                x=result["future_dates"],
                y=result["future_prices"],
                name="Forecast"
            ))

            fig.update_layout(template="plotly_dark")

            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 👤 PORTFOLIO
    # =========================
    elif page == "👤 Portfolio":

        st.markdown('<div class="section-title">👤 Portfolio Manager</div>', unsafe_allow_html=True)

        email = st.session_state.get("email")

        col1, col2, col3 = st.columns(3)

        coin = col1.selectbox("Crypto", df["Crypto"].unique())
        amount = col2.number_input("Amount ($)", min_value=0.0)
        date = col3.date_input("Date")

        if st.button("➕ Add Investment"):
            add_holding(email, coin, amount, str(date))
            st.success("Investment added")

        data = get_holdings(email)

        if data:

            portfolio_df = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
            portfolio_df["Date"] = pd.to_datetime(portfolio_df["Date"])

            results = []
            performance = {}

            for _, row in portfolio_df.iterrows():

                coin_df = df[df["Crypto"] == row["Crypto"]]

                if coin_df.empty:
                    continue

                # Find closest date safely
                coin_df["diff"] = (coin_df["Date"] - row["Date"]).abs()

                buy_row = coin_df.loc[coin_df["diff"].idxmin()] if not coin_df["diff"].isna().all() else None

                if buy_row is None:
                    continue
                buy_price = buy_row["Close"] 
                if coin_df.empty:
                    continue
                current_price = coin_df["Close"].iloc[-1]

                units = row["Amount"] / buy_price
                current_value = units * current_price
                profit = current_value - row["Amount"]
                profit_pct = (profit / row["Amount"]) * 100

                results.append({
                    "Crypto": row["Crypto"],
                    "Invested": round(row["Amount"], 2),
                    "Current Value": round(current_value, 2),
                    "Profit": round(profit, 2),
                    "Profit %": round(profit_pct, 2)
                })

                coin_df = coin_df.copy()
                coin_df["Value"] = (coin_df["Close"] / buy_price) * row["Amount"]

                for _, r in coin_df.iterrows():
                    performance[r["Date"]] = performance.get(r["Date"], 0) + r["Value"]

            final_df = pd.DataFrame(results)

            st.dataframe(final_df, use_container_width=True)

            perf_df = pd.DataFrame(list(performance.items()), columns=["Date", "Value"])
            perf_df = perf_df.sort_values("Date")

            fig = px.line(
                perf_df,
                x="Date",
                y="Value",
                title="📈 Portfolio Growth",
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No investments yet")
