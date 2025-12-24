import ccxt
import pandas as pd
import time

# ------------------------------
# 1. Set up Bybit connection
# ------------------------------
exchange = ccxt.bybit({
    "enableRateLimit": True,  # auto-throttle requests
})

symbol = "BTC/USDT"    # coin to watch
timeframe = "5m"        # 5-minute candles
limit = 100             # last 100 candles

# ------------------------------
# 2. Main loop for continuous fetching
# ------------------------------
while True:
    try:
        # Fetch historical OHLCV data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        # Convert to a pandas DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Print the last 5 candles (for logs)
        print(df.tail())

        # Sleep to avoid hitting rate limits (adjustable)
        time.sleep(60)  # fetch every 60 seconds

    except ccxt.RateLimitExceeded as e:
        print("Rate limit hit, sleeping a bit...")
        time.sleep(10)

    except Exception as e:
        print("Unexpected error:", e)
        time.sleep(10)
