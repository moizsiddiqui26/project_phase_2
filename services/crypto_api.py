def get_historical_data(days=120):

    import pandas as pd
    import time

    all_df = []

    for symbol, coin_id in TOP_10_COINS.items():

        try:
            url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"

            response = requests.get(url, params={
                "vs_currency": "usd",
                "days": days
            }, timeout=10)

            # 🔥 CHECK RESPONSE
            if response.status_code != 200:
                print(f"API Error {symbol}: {response.status_code}")
                continue

            data = response.json()

            # 🔥 SAFE CHECK
            if "prices" not in data or not data["prices"]:
                print(f"No data for {symbol}")
                continue

            temp = pd.DataFrame(data["prices"], columns=["timestamp", "Close"])
            temp["Date"] = pd.to_datetime(temp["timestamp"], unit="ms")
            temp["Crypto"] = symbol

            all_df.append(temp[["Date", "Crypto", "Close"]])

            time.sleep(1.2)  # 🔥 avoid rate limit

        except Exception as e:
            print(f"Error {symbol}:", e)
            continue

    # 🔥 FINAL CHECK
    if not all_df:
        print("⚠ No data fetched from API")
        return pd.DataFrame(columns=["Date", "Crypto", "Close"])

    return pd.concat(all_df)
