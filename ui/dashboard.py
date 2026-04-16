import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Services
from services.crypto_api import get_historical_data
from services.risk_engine import (
    run_risk_analysis,
    calculate_portfolio_risk,
    get_high_risk_assets
)
from services.forecast_engine import get_forecast_summary

# DB
from db.models import add_holding, get_holdings
st.write(df.head())
# UI Components
from ui.components import top_nav, section, metric_row

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

    page = top_nav()

    with st.spinner("Loading market data..."):
        df = load_data()

    if df.empty:
        st.error("Failed to load data")
        return

    # ================= DASHBOARD =================
    if page == "📊 Dashboard":

        section("📊 Market Overview")

        selected = st.multiselect(
            "Select Cryptos",
            df["Crypto"].unique(),
            default=df["Crypto"].unique()
        )

        f = df[df["Crypto"].isin(selected)].copy()

        # PRICE CHART
        st.plotly_chart(
            px.line(f, x="Date", y="Close", color="Crypto"),
            use_container_width=True
        )

        # RETURNS
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()
        st.plotly_chart(
            px.line(f, x="Date", y="Return", color="Crypto"),
            use_container_width=True
        )

        # VOLATILITY
        f["Vol"] = f.groupby("Crypto")["Return"].transform(lambda x: x.rolling(7).std())
        st.plotly_chart(
            px.line(f, x="Date", y="Vol", color="Crypto"),
            use_container_width=True
        )

        # CORRELATION
        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        st.plotly_chart(
            px.imshow(corr, text_auto=True),
            use_container_width=True
        )

    # ================= INVESTMENT =================
    elif page == "💰 Investment":

        section("💰 Smart Investment Allocation")

        amount = st.number_input("Investment Amount ($)", value=1000.0)
        risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])

        returns = df.groupby("Crypto").apply(
            lambda x: (x.Close.iloc[-1] - x.Close.iloc[0]) / x.Close.iloc[0]
        ).reset_index(name="Return")

        vol = df.groupby("Crypto")["Close"].std().reset_index(name="Vol")

        merged = returns.merge(vol, on="Crypto")

        if risk_level == "Low":
            merged["Score"] = 1 / merged["Vol"]
        elif risk_level == "Medium":
            merged["Score"] = merged["Return"] / merged["Vol"]
        else:
            merged["Score"] = merged["Return"]

        merged["Allocation %"] = merged["Score"] / merged["Score"].sum() * 100
        merged["Investment"] = merged["Allocation %"] / 100 * amount

        st.dataframe(merged)

        st.plotly_chart(
            px.pie(merged, names="Crypto", values="Investment"),
            use_container_width=True
        )

    # ================= RISK =================
    elif page == "⚠ Risk":

        section("⚠ Risk Analysis")

        risk_df = run_risk_analysis(df)
        st.dataframe(risk_df)

        # Portfolio risk
        portfolio_risk = calculate_portfolio_risk(df)

        metric_row([
            {"title": "Risk Level", "value": portfolio_risk["level"]},
            {"title": "Risk Score", "value": portfolio_risk["score"]}
        ])

        # High-risk alert
        alerts = get_high_risk_assets(df)

        if not alerts.empty:
            st.warning("⚠ High risk assets detected")
            st.dataframe(alerts)

    # ================= FORECAST =================
    elif page == "🔮 Forecast":

        section("🔮 Price Forecast")

        coin = st.selectbox("Select Crypto", df["Crypto"].unique())
        investment = st.number_input("Investment ($)", value=1000.0)
        days = st.slider("Forecast Days", 1, 30, 7)

        coin_df = df[df["Crypto"] == coin].copy()

        result = get_forecast_summary(coin_df, investment, days)

        if result:

            # METRICS
            metric_row([
                {"title": "Predicted Price", "value": f"${result['predicted_price']:.2f}"},
                {"title": "Expected Value", "value": f"${result['expected_value']:.2f}"},
                {"title": "Profit %", "value": f"{result['profit_pct']:.2f}%"}
            ])

            # CHART
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

    # ================= PORTFOLIO =================
    elif page == "👤 Portfolio":

        section("👤 Portfolio Manager")

        email = st.session_state.get("email")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        amount = st.number_input("Investment Amount", min_value=0.0)
        date = st.date_input("Purchase Date")

        if st.button("Add Investment"):
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
