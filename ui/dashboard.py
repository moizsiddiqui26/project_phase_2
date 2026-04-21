import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# MAIN DASHBOARD
# =========================
def main():

    page = st.session_state.get("page", "📊 Dashboard")

    # =========================
    # REFRESH BUTTON
    # =========================
    col1, col2 = st.columns([8,1])
    with col2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    # =========================
    # LOAD DATA
    # =========================
    with st.spinner("🚀 Loading crypto data..."):
        df = load_data()

    if df.empty:
        st.error("⚠ Failed to load data")
        return

    # =========================
    # 📊 DASHBOARD
    # =========================
    if page == "📊 Dashboard":

        st.markdown("## 📊 Market Dashboard")

        all_coins = sorted(df["Crypto"].unique())

        # 🔍 FILTER BAR
        col1, col2, col3 = st.columns(3)

        with col1:
            search = st.text_input("🔍 Search Coin")

        with col2:
            quick = st.selectbox("Quick Select", ["All", "Top 3", "Top 5"])

        with col3:
            compare = st.checkbox("Compare Mode")

        # FILTER LOGIC
        filtered = all_coins

        if search:
            filtered = [c for c in all_coins if search.lower() in c.lower()]

        if quick == "Top 3":
            filtered = filtered[:3]
        elif quick == "Top 5":
            filtered = filtered[:5]

        selected = st.multiselect("Select Coins", all_coins, default=filtered)

        f = df[df["Crypto"].isin(selected)].copy()

        if f.empty:
            st.warning("Select at least one coin")
            return

        st.markdown("---")

        # ================= PRICE CHART =================
        st.markdown("### 📈 Price Trends")

        fig = go.Figure()
        for coin in selected:
            coin_df = f[f["Crypto"] == coin]
            fig.add_trace(go.Scatter(
                x=coin_df["Date"],
                y=coin_df["Close"],
                name=coin
            ))

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ================= RETURNS + VOL =================
        col1, col2 = st.columns(2)

        f["Return"] = f.groupby("Crypto")["Close"].pct_change()
        f["Vol"] = f.groupby("Crypto")["Return"].transform(lambda x: x.rolling(7).std())

        with col1:
            st.markdown("### 📊 Returns")
            st.plotly_chart(
                px.line(f, x="Date", y="Return", color="Crypto"),
                use_container_width=True
            )

        with col2:
            st.markdown("### ⚠ Volatility")
            st.plotly_chart(
                px.line(f, x="Date", y="Vol", color="Crypto"),
                use_container_width=True
            )

        st.markdown("---")

        # ================= CORRELATION =================
        st.markdown("### 🔗 Correlation Matrix")

        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        st.plotly_chart(px.imshow(corr, text_auto=True), use_container_width=True)

        st.markdown("---")

        # ================= METRICS =================
        st.markdown("### 📌 Latest Prices")

        latest = f.groupby("Crypto").tail(1)
        cols = st.columns(len(latest))

        for i, (_, row) in enumerate(latest.iterrows()):
            cols[i].metric(row["Crypto"], f"${row['Close']:.2f}")

    # =========================
    # 💰 INVESTMENT
    # =========================
    elif page == "💰 Investment":

        st.markdown("## 💰 Investment Planner")

        amount = st.number_input("Investment Amount ($)", value=1000.0)

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        st.dataframe(returns, use_container_width=True)

        st.plotly_chart(
            px.pie(returns, names="Crypto", values="Return"),
            use_container_width=True
        )

    # =========================
    # ⚠ RISK
    # =========================
    elif page == "⚠ Risk":

        st.markdown("## ⚠ Risk Analysis")

        risk_df = run_risk_analysis(df)
        st.dataframe(risk_df, use_container_width=True)

        r = calculate_portfolio_risk(df)

        col1, col2 = st.columns(2)
        col1.metric("Risk Level", r["level"])
        col2.metric("Risk Score", r["score"])

    # =========================
    # 🔮 FORECAST
    # =========================
    elif page == "🔮 Forecast":

        st.markdown("## 🔮 Price Forecast")

        coin = st.selectbox("Select Coin", df["Crypto"].unique())
        coin_df = df[df["Crypto"] == coin]

        result = get_forecast_summary(coin_df, 1000, 7)

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

            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 👤 PORTFOLIO
    # =========================
    elif page == "👤 Portfolio":

        st.markdown("## 👤 Portfolio Manager")

        email = st.session_state.get("email")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        amount = st.number_input("Investment Amount ($)", min_value=0.0)
        date = st.date_input("Purchase Date")

        if st.button("Add Investment"):
            add_holding(email, coin, amount, str(date))
            st.success("✅ Added successfully")

        data = get_holdings(email)

        if data:

            pdf = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
            pdf["Date"] = pd.to_datetime(pdf["Date"])

            results = []
            perf = {}

            for _, r in pdf.iterrows():

                cdf = df[df["Crypto"] == r["Crypto"]]

                buy = cdf.iloc[(cdf["Date"] - r["Date"]).abs().argsort()[:1]]["Close"].values[0]
                curr = cdf["Close"].iloc[-1]

                units = r["Amount"] / buy
                val = units * curr
                profit = val - r["Amount"]

                results.append({
                    "Crypto": r["Crypto"],
                    "Invested": r["Amount"],
                    "Current Value": val,
                    "Profit": profit
                })

                cdf["Value"] = (cdf["Close"] / buy) * r["Amount"]

                for i, row in cdf.iterrows():
                    perf[row["Date"]] = perf.get(row["Date"], 0) + row["Value"]

            st.dataframe(pd.DataFrame(results), use_container_width=True)

            perf_df = pd.DataFrame(list(perf.items()), columns=["Date", "Value"])

            st.markdown("### 📈 Portfolio Performance")

            st.plotly_chart(
                px.line(perf_df.sort_values("Date"), x="Date", y="Value"),
                use_container_width=True
            )

        else:
            st.info("No investments yet")
