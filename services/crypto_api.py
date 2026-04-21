import requests
import pandas as pd
import time

TOP_10_COINS = {
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

BASE_URL = "https://api.coingecko.com/api/v3"


# =========================
# LIVE PRICES
# =========================
def get_top_10_prices():
    try:
        ids = ",".join(TOP_10_COINS.values())

        res = requests.get(
            f"{BASE_URL}/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=10
        )

        return res.json()

    except:
        return {}


# =========================
# HISTORICAL DATA (CRITICAL FIX)
# =========================
def get_historical_data(days=90):

    all_data = []

    for symbol, coin_id in TOP_10_COINS.items():

        try:
            res = requests.get(
                f"{BASE_URL}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": days},
                timeout=10
            )

            if res.status_code != 200:
                continue

            data = res.json()

            if "prices" not in data:
                continue

            df = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
            df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["Crypto"] = symbol

            all_data.append(df[["Date", "Crypto", "Close"]])

            time.sleep(1)  # avoid rate limit

        except Exception as e:
            print("Error:", e)

    # 🔥 THIS IS THE FIX (NOT INSIDE LOOP)
    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
