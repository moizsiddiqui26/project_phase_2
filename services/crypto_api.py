import requests
import pandas as pd
import time
from functools import lru_cache

# =========================
# CONFIG
# =========================
TOP_10_COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
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
# SAFE REQUEST HELPER
# =========================
def safe_request(url, params=None):
    try:
        res = requests.get(url, params=params, timeout=10)

        # ❌ Handle rate limit / bad response
        if res.status_code != 200:
            return None

        data = res.json()

        # ❌ Reject invalid API responses
        if not isinstance(data, dict):
            return None

        if "status" in data:
            return None

        return data

    except:
        return None


# =========================
# LIVE PRICES (CACHED)
# =========================
@lru_cache(maxsize=2)
def get_top_10_prices():

    ids = ",".join(TOP_10_COINS.values())

    data = safe_request(
        f"{BASE_URL}/simple/price",
        params={"ids": ids, "vs_currencies": "usd"}
    )

    if not data:
        return {}

    return data


# =========================
# HISTORICAL DATA (SAFE)
# =========================
@lru_cache(maxsize=2)
def get_historical_data(days=90):

    all_data = []

    for symbol, coin_id in TOP_10_COINS.items():

        data = safe_request(
            f"{BASE_URL}/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days}
        )

        if not data or "prices" not in data:
            continue

        df = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])

        df["Date"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["Crypto"] = symbol

        all_data.append(df[["Date", "Crypto", "Close"]])

        # ✅ Small delay (safe, not heavy)
        time.sleep(0.2)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
