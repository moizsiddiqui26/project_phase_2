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

# UI
from ui.components import top_nav


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

    # TOP NAV
    page = top_nav()

    # LOAD DATA
    with st.spinner("🚀 Loading crypto data..."):
        df = load_data()

    if df.empty:
        st.error("⚠ Failed to load data")
        return

    # =========================
    # 📊 DASHBOARD
    # =========================
    if page == "📊 Dashboard":

        st.subheader("📊 Market Overview")

        coins = st.multiselect(
            "Select Coins",
            df["Crypto"].unique(),
            default=df["Crypto"].unique()
        )

        f = df[df["Crypto"].isin(coins)].copy()

        # PRICE CHART
        st.plotly_chart(
            px.line(f, x="Date", y="Close", color="Crypto",
                    title="Price Trends"),
            use_container_width=True
        )

        # RETURNS
        f["Return"] = f.groupby("Crypto")["Close"].pct_change()

        st.plotly_chart(
            px.line(f, x="Date", y="Return", color="Crypto",
                    title="Returns"),
            use_container_width=True
        )

        # VOLATILITY
        f["Volatility"] = f.groupby("Crypto")["Return"].transform(
            lambda x: x.rolling(7).std()
        )

        st.plotly_chart(
            px.line(f, x="Date", y="Volatility", color="Crypto",
                    title="Volatility"),
            use_container_width=True
        )

        # CORRELATION
        pivot = f.pivot(index="Date", columns="Crypto", values="Close")
        corr = pivot.pct_change().corr()

        st.plotly_chart(
            px.imshow(corr, text_auto=True, title="Correlation Matrix"),
            use_container_width=True
        )

    # =========================
    # 💰 INVESTMENT
    # =========================
    elif page == "💰 Investment":

        st.subheader("💰 Smart Investment Allocation")

        amount = st.number_input("Investment ($)", value=1000.0)
        risk = st.selectbox("Risk Level", ["Low", "Medium", "High"])

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

        st.dataframe(m)

        st.plotly_chart(
            px.pie(m, names="Crypto", values="Investment",
                   title="Investment Distribution"),
            use_container_width=True
        )

    # =========================
    # ⚠ RISK
    # =========================
    elif page == "⚠ Risk":

        st.subheader("⚠ Risk Analysis")

        risk_df = run_risk_analysis(df)
        st.dataframe(risk_df)

        portfolio = calculate_portfolio_risk(df)

        st.metric("Portfolio Risk", portfolio["level"])
        st.metric("Risk Score", portfolio["score"])

    # =========================
    # 🔮 FORECAST
    # =========================
    elif page == "🔮 Forecast":

        st.subheader("🔮 Price Forecast")

        coin = st.selectbox("Select Coin", df["Crypto"].unique())
        amount = st.number_input("Investment ($)", value=1000.0)
        days = st.slider("Days", 1, 30, 7)

        coin_df = df[df["Crypto"] == coin]

        result = get_forecast_summary(coin_df, amount, days)

        if result:

            col1, col2, col3 = st.columns(3)

            col1.metric("Predicted Price",
                        f"${result['predicted_price']:.2f}")

            col2.metric("Expected Value",
                        f"${result['expected_value']:.2f}")

            col3.metric("Profit %",
                        f"{result['profit_pct']:.2f}%")

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

    # =========================
    # 👤 PORTFOLIO
    # =========================
    elif page == "👤 Portfolio":

        st.subheader("👤 Portfolio Manager")

        email = st.session_state.get("email")

        coin = st.selectbox("Crypto", df["Crypto"].unique())
        amount = st.number_input("Amount", min_value=0.0)
        date = st.date_input("Date")

        if st.button("Add Investment"):
            add_holding(email, coin, amount, str(date))
            st.success("Added successfully")

        data = get_holdings(email)

        if data:
            pdf = pd.DataFrame(data, columns=["Crypto", "Amount", "Date"])

            st.dataframe(pdf)

            st.plotly_chart(
                px.pie(pdf, names="Crypto", values="Amount",
                       title="Portfolio Distribution"),
                use_container_width=True
            )
        else:
            st.info("No investments yet")
