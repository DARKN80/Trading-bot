# main.py
import ccxt
import pandas as pd
import time
import threading
from flask import Flask
import os

# ------------------------------
# 1. Flask server for Render
# ------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Trading bot is alive!"

def run_flask():
    # Render assigns a port via environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Run Flask in a separate thread
threading.Thread(target=run_flask).start()

# ------------------------------
# 2. Setup Bybit connection
# ------------------------------
exchange = ccxt.bybit({
    "enableRateLimit": True,  # avoid rate limit errors
})

symbol = "BTC/USDT"  # coin to watch
timeframe = "5m"
limit = 100

# ------------------------------
# 3. Continuous bot loop
# ------------------------------
while True:
    try:
        # Fetch historical OHLCV data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        # Convert to pandas DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Print last 5 candles for logs
        print(df.tail())

        # Sleep 60 seconds before next fetch
        time.sleep(60)

    except ccxt.RateLimitExceeded:
        print("Rate limit hit, sleeping 10 seconds...")
        time.sleep(10)

    except Exception as e:
        print("Unexpected error:", e)
        time.sleep(10)
