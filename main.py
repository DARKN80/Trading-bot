import ccxt
import pandas as pd

# Connect to Bybit (read-only)
exchange = ccxt.bybit({
    "enableRateLimit": True
})

# Choose a coin and timeframe
symbol = "BTC/USDT"
timeframe = "5m"  # 5-minute candles
limit = 100       # last 100 candles

# Fetch historical OHLCV data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

# Convert to DataFrame for readability
df = pd.DataFrame(
    ohlcv,
    columns=["timestamp", "open", "high", "low", "close", "volume"]
)

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

print(df.tail())  # show last 5 entries
