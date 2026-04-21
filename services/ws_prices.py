```python
import websocket
import json
import threading
import streamlit as st

# Binance symbols
SYMBOL_MAP = {
    "BTC": "btcusdt",
    "ETH": "ethusdt",
    "BNB": "bnbusdt",
    "XRP": "xrpusdt",
    "SOL": "solusdt",
    "ADA": "adausdt",
    "DOGE": "dogeusdt",
    "TRX": "trxusdt",
    "MATIC": "maticusdt"
}

def start_ws():

    if "live_prices" not in st.session_state:
        st.session_state.live_prices = {}

    def on_message(ws, message):
        data = json.loads(message)

        if "data" in data:
            symbol = data["data"]["s"]   # BTCUSDT
            price = float(data["data"]["c"])

            # convert back to short symbol
            for k, v in SYMBOL_MAP.items():
                if v.upper() == symbol:
                    st.session_state.live_prices[k] = price

    def on_open(ws):
        streams = [f"{v}@ticker" for v in SYMBOL_MAP.values()]
        sub_msg = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": 1
        }
        ws.send(json.dumps(sub_msg))

    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws",
        on_open=on_open,
        on_message=on_message
    )

    ws.run_forever()


def start_ws_thread():
    if "ws_started" not in st.session_state:
        st.session_state.ws_started = True

        thread = threading.Thread(target=start_ws, daemon=True)
        thread.start()
```
