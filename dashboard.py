import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import time
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

from services.crypto_api import get_top_10_prices
from services.risk_engine import calculate_risk
from db.models import add_holding, get_holdings

# =========================
# LOAD HISTORICAL DATA
# =========================
@st.cache_data(ttl=300)
def load_data():

    coins = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "XRP": "ripple",
        "SOL": "solana",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "TRX": "tron",
        "MATIC": "polygon"
    }

    all_df = []

    for c, cid in coins.items():
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart"
            r = requests.get(url, params={"vs_currency": "usd", "days": 120})
            data = r.json()

            if "prices" not in data:
                continue

            temp = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
            temp["Date"] = pd.to_datetime(temp["timestamp"], unit="ms")
            temp["Crypto"] = c

            all_df.append(temp[["Date", "Crypto", "Close"]])
            time.sleep(1)

        except:
            continue

    if not all_df:
        return pd.DataFrame(columns=["Date", "Crypto", "Close"])

    return pd.concat(all_df)


# =========================
# MAIN DASHBOARD
# =========================
def main():

    # TOP NAVIGATION
    page = st.radio(
        "",
        ["📊 Dashboard", "💰 Investment", "⚠ Risk", "🔮 Forecast", "👤 Portfolio"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # LOAD DATA
    with st.spinner("Loading market data..."):
        df = load_data()

    if df.empty:
        st.error("Failed to load data")
        return

    # ================= DASHBOARD =================
    if page == "📊 Dashboard":

        st.subheader("📊 Market Overview")

        selected = st.multiselect(
            "Select Cryptos",
            df["Crypto"].unique(),
            default=df["Crypto"].unique()
        )

        f = df[df["Crypto"].isin(selected)]

        # Price Chart
        st.plotly_chart(
            px.line(f, x="Date", y="Close", color="Crypto"),
            use_container_width=True
        )

        # Returns
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()
        st.plotly_chart(
            px.line(f, x="Date", y="Return", color="Crypto"),
            use_container_width=True
        )

        # Volatility
        f["Vol"] = f.groupby("Crypto")["Return"].transform(lambda x: x.rolling(7).std())
        st.plotly_chart(
            px.line(f, x="Date", y="Vol", color="Crypto"),
            use_container_width=True
        )

        # Correlation
        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        st.plotly_chart(
            px.imshow(corr, text_auto=True),
            use_container_width=True
        )

    # ================= INVESTMENT =================
    elif page == "💰 Investment":

        st.subheader("💰 Smart Investment Allocation")

        amount = st.number_input("Investment Amount ($)", value=1000.0)
        risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        vol = df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m = returns.merge(vol, on="Crypto")

        if risk_level == "Low":
            m["Score"] = 1 / m["Vol"]
        elif risk_level == "Medium":
            m["Score"] = m["Return"] / m["Vol"]
        else:
            m["Score"] = m["Return"]

        m["Allocation %"] = m["Score"] / m["Score"].sum() * 100
        m["Investment"] = m["Allocation %"] / 100 * amount

        st.dataframe(m)

        st.plotly_chart(
            px.pie(m, names="Crypto", values="Investment"),
            use_container_width=True
        )

    # ================= RISK =================
    elif page == "⚠ Risk":

        st.subheader("⚠ Risk Analysis")

        df["Volatility"] = df.groupby("Crypto")["Close"].transform(lambda x: x.std())

        risk_data = df.groupby("Crypto")["Volatility"].mean().reset_index()
        risk_data["Risk"] = risk_data["Volatility"].apply(calculate_risk)

        st.dataframe(risk_data)

    # ================= FORECAST =================
    elif page == "🔮 Forecast":

        st.subheader("🔮 Price Forecast")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        days = st.slider("Days to Forecast", 1, 30, 7)

        coin_df = df[df["Crypto"] == coin].sort_values("Date")

        coin_df["t"] = np.arange(len(coin_df))

        model = LinearRegression().fit(coin_df[["t"]], coin_df["Close"])

        future_t = np.arange(len(coin_df), len(coin_df) + days)
        future_prices = model.predict(future_t.reshape(-1, 1))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=coin_df["Date"], y=coin_df["Close"], name="Actual"))

        future_dates = pd.date_range(
            coin_df["Date"].iloc[-1],
            periods=days + 1
        )[1:]

        fig.add_trace(go.Scatter(x=future_dates, y=future_prices, name="Forecast"))

        st.plotly_chart(fig, use_container_width=True)

    # ================= PORTFOLIO =================
    elif page == "👤 Portfolio":

        st.subheader("👤 Portfolio Manager")

        email = st.session_state.get("email")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        amount = st.number_input("Investment Amount", min_value=0.0)
        date = st.date_input("Purchase Date")

        if st.button("Add Investment", key="add_portfolio"):
            add_holding(email, coin, amount, str(date))
            st.success("Investment added")

        data = get_holdings(email)

        if data:
            portfolio_df = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
            st.dataframe(portfolio_df)

            st.plotly_chart(
                px.pie(portfolio_df, names="Crypto", values="Amount"),
                use_container_width=True
            )
        else:
            st.info("No investments yet")
