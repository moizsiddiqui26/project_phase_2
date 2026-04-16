import requests
import pandas as pd
import time
from config import COINGECKO_BASE_URL, TOP_10_COINS


# =========================
# GET TOP 10 LIVE PRICES
# =========================
def get_top_10_prices():
    """
    Fetch live prices for top 10 cryptocurrencies
    """
    try:
        ids = ",".join(TOP_10_COINS.values())

        url = f"{COINGECKO_BASE_URL}/simple/price"

        response = requests.get(url, params={
            "ids": ids,
            "vs_currencies": "usd"
        }, timeout=10)

        data = response.json()

        return data

    except Exception as e:
        print("Error fetching prices:", e)
        return {}


# =========================
# GET HISTORICAL DATA
# =========================
def get_historical_data(days=120):
    """
    Fetch historical price data for top 10 coins
    """
    all_df = []

    for symbol, coin_id in TOP_10_COINS.items():

        try:
            url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"

            response = requests.get(url, params={
                "vs_currency": "usd",
                "days": days
            }, timeout=10)

            data = response.json()

            if "prices" not in data:
                continue

            temp = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
            temp["Date"] = pd.to_datetime(temp["timestamp"], unit="ms")
            temp["Crypto"] = symbol

            all_df.append(temp[["Date", "Crypto", "Close"]])

            time.sleep(1)  # prevent rate limit

        except Exception as e:
            print(f"Error fetching {symbol}:", e)
            continue

    if not all_df:
        return pd.DataFrame(columns=["Date", "Crypto", "Close"])

    return pd.concat(all_df)


# =========================
# GET SINGLE COIN DATA
# =========================
def get_coin_data(coin_symbol, days=120):
    """
    Fetch historical data for a single coin
    """
    coin_id = TOP_10_COINS.get(coin_symbol)

    if not coin_id:
        return pd.DataFrame()

    try:
        url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"

        response = requests.get(url, params={
            "vs_currency": "usd",
            "days": days
        }, timeout=10)

        data = response.json()

        temp = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
        temp["Date"] = pd.to_datetime(temp["timestamp"], unit="ms")

        return temp[["Date", "Close"]]

    except Exception as e:
        print("Error:", e)
        return pd.DataFrame()


# =========================
# GET MARKET SUMMARY
# =========================
def get_market_summary():
    """
    Returns summary (latest price + change %)
    """
    try:
        ids = ",".join(TOP_10_COINS.values())

        url = f"{COINGECKO_BASE_URL}/coins/markets"

        response = requests.get(url, params={
            "vs_currency": "usd",
            "ids": ids
        }, timeout=10)

        data = response.json()

        summary = []

        for coin in data:
            summary.append({
                "name": coin["symbol"].upper(),
                "price": coin["current_price"],
                "change": coin["price_change_percentage_24h"]
            })

        return summary

    except Exception as e:
        print("Error fetching summary:", e)
        return []
