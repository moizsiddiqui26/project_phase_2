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
# LOAD DATA
# =========================
@st.cache_data(ttl=300)
def load_data():
    return get_historical_data()


# =========================
# MAIN
# =========================
def main():

    page = st.session_state.get("page", "📊 Dashboard")

    df = load_data()

    if df.empty:
        st.error("⚠ Failed to load data")
        return

    # =========================
    # 📊 DASHBOARD
    # =========================
    if page == "📊 Dashboard":

        st.markdown("## 📊 Market Overview")

        all_coins = sorted(df["Crypto"].unique())

        # ✅ Safe default selection
        default_coins = all_coins[:4]

        coins = st.multiselect(
            "Select Coins",
            all_coins,
            default=default_coins
        )

        f = df[df["Crypto"].isin(coins)].copy()

        if f.empty:
            st.warning("Select at least one coin")
            return

        # ================= PRICE =================
        fig1 = px.line(
            f,
            x="Date",
            y="Close",
            color="Crypto",
            title="📈 Price Trends",
            template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ================= RETURNS =================
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()

        fig2 = px.line(
            f,
            x="Date",
            y="Return",
            color="Crypto",
            title="📊 Returns",
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ================= VOLATILITY =================
        f["Volatility"] = f.groupby("Crypto")["Return"].transform(
            lambda x: x.rolling(7).std()
        )

        fig3 = px.line(
            f,
            x="Date",
            y="Volatility",
            color="Crypto",
            title="⚠ Volatility",
            template="plotly_dark"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ================= CORRELATION =================
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

        st.markdown("## 💰 Smart Investment Allocation")

        col1, col2 = st.columns(2)
        amount = col1.number_input("Investment ($)", value=1000.0)
        risk = col2.selectbox("Risk Level", ["Low", "Medium", "High"])

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        vol = df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        m = returns.merge(vol, on="Crypto")

        # Ensure no negative scores
        m["Return"] = m["Return"].clip(lower=0)

        if risk == "Low":
            m["Score"] = 1 / (m["Vol"] + 1e-6)

        elif risk == "Medium":
            m["Score"] = m["Return"] / (m["Vol"] + 1e-6)

        else:
            m["Score"] = m["Return"]

        # Remove zero scores
        m = m[m["Score"] > 0]

        # Normalize safely
        m["Allocation %"] = m["Score"] / m["Score"].sum() * 100
        m["Investment"] = m["Allocation %"] / 100 * amount


        st.dataframe(m, use_container_width=True)

        fig = px.pie(
            m,
            names="Crypto",
            values="Investment",
            title="📊 Allocation",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ⚠ RISK
    # =========================
    elif page == "⚠ Risk":

        st.markdown("## ⚠ Risk Analysis")

        risk_df = run_risk_analysis(df)
        st.dataframe(risk_df, use_container_width=True)

        portfolio = calculate_portfolio_risk(df)

        col1, col2 = st.columns(2)
        col1.metric("Risk Level", portfolio["level"])
        col2.metric("Risk Score", portfolio["score"])

    # =========================
    # 🔮 FORECAST
    # =========================
    elif page == "🔮 Forecast":

        st.markdown("## 🔮 Forecast")

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

        st.markdown("## 👤 Portfolio Manager")

        email = st.session_state.get("email")

        col1, col2, col3 = st.columns(3)

        coin = col1.selectbox("Crypto", df["Crypto"].unique())
        amount = col2.number_input("Amount ($)", min_value=0.0)
        date = col3.date_input("Date")

        if st.button("➕ Add Investment"):
            add_holding(email, coin, amount, str(date))
            st.success("Investment added")

        data = get_holdings(email)

        if not data:
            st.info("No investments yet")
            return

        portfolio_df = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])
        portfolio_df["Date"] = pd.to_datetime(portfolio_df["Date"])

        results = []
        performance = {}

        for _, row in portfolio_df.iterrows():

            coin_df = df[df["Crypto"] == row["Crypto"]].copy()

            if coin_df.empty:
                continue

            # SAFE DATE MATCH
            coin_df["diff"] = (coin_df["Date"] - row["Date"]).abs()

            if coin_df["diff"].isna().all():
                continue

            buy_row = coin_df.loc[coin_df["diff"].idxmin()]
            buy_price = buy_row["Close"]

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

            # PERFORMANCE TRACK
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

