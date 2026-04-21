import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.crypto_api import get_historical_data
from services.risk_engine import run_risk_analysis, calculate_portfolio_risk
from services.forecast_engine import get_forecast_summary

from db.models import add_holding, get_holdings
from ui.components import top_nav


@st.cache_data(ttl=300)
def load_data():
    return get_historical_data()


def main():

    page = top_nav()

    # 🔄 Refresh
    col1, col2 = st.columns([9,1])
    with col2:
        if st.button("🔄"):
            st.cache_data.clear()
            st.rerun()

    df = load_data()

    if df.empty:
        st.error("No data")
        return

    # =========================
    # 📊 DASHBOARD
    # =========================
    if page == "📊 Dashboard":

        st.markdown("## 📊 Market Overview")

        coins = sorted(df["Crypto"].unique())

        # FILTER BAR
        c1, c2, c3 = st.columns(3)

        with c1:
            search = st.text_input("🔍 Search")

        with c2:
            quick = st.selectbox("Quick Select", ["All", "Top 3", "Top 5"])

        with c3:
            compare = st.checkbox("Compare Mode")

        filtered = coins

        if search:
            filtered = [c for c in coins if search.lower() in c.lower()]

        if quick == "Top 3":
            filtered = filtered[:3]
        elif quick == "Top 5":
            filtered = filtered[:5]

        selected = st.multiselect("Coins", coins, default=filtered)

        f = df[df["Crypto"].isin(selected)]

        if f.empty:
            st.warning("Select coins")
            return

        # 📈 PRICE
        st.markdown("### 📈 Price Chart")

        fig = go.Figure()

        for coin in selected:
            coin_df = f[f["Crypto"] == coin]
            fig.add_trace(go.Scatter(
                x=coin_df["Date"],
                y=coin_df["Close"],
                name=coin
            ))

        st.plotly_chart(fig, use_container_width=True)

        # 📊 RETURNS
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()

        st.plotly_chart(
            px.line(f, x="Date", y="Return", color="Crypto"),
            use_container_width=True
        )

        # ⚠ VOLATILITY
        f["Vol"] = f.groupby("Crypto")["Return"].transform(lambda x: x.rolling(7).std())

        st.plotly_chart(
            px.line(f, x="Date", y="Vol", color="Crypto"),
            use_container_width=True
        )

        # 🔗 CORRELATION
        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        st.plotly_chart(px.imshow(corr, text_auto=True), use_container_width=True)

        # 📌 METRICS
        latest = f.groupby("Crypto").tail(1)
        cols = st.columns(len(selected))

        for i, (_, row) in enumerate(latest.iterrows()):
            cols[i].metric(row["Crypto"], f"${row['Close']:.2f}")

    # =========================
    # 💰 INVESTMENT
    # =========================
    elif page == "💰 Investment":

        st.markdown("## 💰 Investment Planner")

        amount = st.number_input("Amount", value=1000.0)

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        st.dataframe(returns)

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
        st.dataframe(risk_df)

        r = calculate_portfolio_risk(df)

        st.metric("Risk Level", r["level"])
        st.metric("Score", r["score"])

    # =========================
    # 🔮 FORECAST
    # =========================
    elif page == "🔮 Forecast":

        st.markdown("## 🔮 Forecast")

        coin = st.selectbox("Coin", df["Crypto"].unique())
        coin_df = df[df["Crypto"] == coin]

        res = get_forecast_summary(coin_df, 1000, 7)

        if res:
            st.metric("Predicted", f"${res['predicted_price']:.2f}")
            st.metric("Profit %", f"{res['profit_pct']:.2f}%")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=coin_df["Date"],
                y=coin_df["Close"],
                name="Actual"
            ))

            fig.add_trace(go.Scatter(
                x=res["future_dates"],
                y=res["future_prices"],
                name="Forecast"
            ))

            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 👤 PORTFOLIO
    # =========================
    elif page == "👤 Portfolio":

        st.markdown("## 👤 Portfolio")

        email = st.session_state.get("email")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        amount = st.number_input("Amount", min_value=0.0)
        date = st.date_input("Date")

        if st.button("Add"):
            add_holding(email, coin, amount, str(date))

        data = get_holdings(email)

        if data:

            pdf = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
            pdf["Date"] = pd.to_datetime(pdf["Date"])

            perf = {}

            rows = []

            for _, r in pdf.iterrows():

                cdf = df[df["Crypto"] == r["Crypto"]]

                buy = cdf.iloc[(cdf["Date"] - r["Date"]).abs().argsort()[:1]]["Close"].values[0]
                curr = cdf["Close"].iloc[-1]

                units = r["Amount"] / buy
                val = units * curr
                profit = val - r["Amount"]

                rows.append({
                    "Crypto": r["Crypto"],
                    "Invested": r["Amount"],
                    "Current": val,
                    "Profit": profit
                })

                cdf["Value"] = (cdf["Close"] / buy) * r["Amount"]

                for i, row in cdf.iterrows():
                    perf[row["Date"]] = perf.get(row["Date"], 0) + row["Value"]

            st.dataframe(pd.DataFrame(rows))

            perf_df = pd.DataFrame(list(perf.items()), columns=["Date", "Value"])

            st.plotly_chart(
                px.line(perf_df.sort_values("Date"), x="Date", y="Value"),
                use_container_width=True
            )
