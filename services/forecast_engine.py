import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


# =========================
# PREPARE DATA
# =========================
def prepare_data(df: pd.DataFrame):
    """
    Prepare time-series data for ML model
    """
    df = df.sort_values("Date").reset_index(drop=True)
    df["t"] = np.arange(len(df))
    return df


# =========================
# TRAIN MODEL
# =========================
def train_model(df: pd.DataFrame):
    """
    Train Linear Regression model
    """
    X = df[["t"]]
    y = df["Close"]

    model = LinearRegression()
    model.fit(X, y)

    return model


# =========================
# FORECAST FUTURE PRICES
# =========================
def forecast_prices(df: pd.DataFrame, days: int = 7):
    """
    Forecast future prices for given days
    """

    if df.empty:
        return [], []

    df = prepare_data(df)

    model = train_model(df)

    # Future time steps
    future_t = np.arange(len(df), len(df) + days)

    future_prices = model.predict(future_t.reshape(-1, 1))

    # Future dates
    last_date = df["Date"].iloc[-1]
    future_dates = pd.date_range(last_date, periods=days + 1)[1:]

    return future_dates, future_prices


# =========================
# CALCULATE RETURNS
# =========================
def calculate_expected_return(current_price, predicted_price):
    """
    Calculate expected return %
    """
    return ((predicted_price - current_price) / current_price) * 100


# =========================
# FULL FORECAST SUMMARY
# =========================
def get_forecast_summary(df: pd.DataFrame, investment: float, days: int = 7):
    """
    Returns full forecast result:
    - predicted price
    - expected value
    - profit %
    """

    if df.empty:
        return None

    future_dates, future_prices = forecast_prices(df, days)

    current_price = df["Close"].iloc[-1]
    predicted_price = future_prices[-1]

    units = investment / current_price
    expected_value = units * predicted_price
    profit_pct = calculate_expected_return(current_price, predicted_price)

    return {
        "future_dates": future_dates,
        "future_prices": future_prices,
        "current_price": current_price,
        "predicted_price": predicted_price,
        "expected_value": expected_value,
        "profit_pct": profit_pct
    }
