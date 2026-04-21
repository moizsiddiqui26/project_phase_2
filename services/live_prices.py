import requests
from concurrent.futures import ThreadPoolExecutor

SYMBOL_MAP = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "XRP": "XRPUSDT",
    "SOL": "SOLUSDT",
    "ADA": "ADAUSDT",
    "DOGE": "DOGEUSDT",
    "TRX": "TRXUSDT",
    "MATIC": "MATICUSDT"
}

BASE_URL = "https://api.binance.com/api/v3/ticker/price"


# =========================
# SINGLE FETCH
# =========================
def fetch_price(symbol):
    try:
        res = requests.get(f"{BASE_URL}?symbol={symbol}", timeout=2)
        if res.status_code == 200:
            data = res.json()
            return float(data["price"])
    except:
        return None


# =========================
# PARALLEL FETCH (FAST ⚡)
# =========================
def get_live_prices():

    prices = {}

    with ThreadPoolExecutor(max_workers=10) as executor:

        futures = {
            executor.submit(fetch_price, sym): name
            for name, sym in SYMBOL_MAP.items()
        }

        for future in futures:
            name = futures[future]
            price = future.result()

            if price is not None:
                prices[name] = price

    return prices
