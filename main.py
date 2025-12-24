import os
import time
import ccxt
import pandas as pd
import requests
import threading
from flask import Flask

# =====================
# Flask (Render keep-alive)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)

# Start Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

# =====================
# Telegram configuration
# =====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram not configured. Skipping message.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print("Telegram error:", e)

# =====================
# Exchange setup (Bybit)
# =====================
exchange = ccxt.bybit({"enableRateLimit": True})

TIMEFRAME = os.getenv("TIMEFRAME", "5m")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 60))  # seconds
VOL_THRESHOLD = float(os.getenv("VOL_THRESHOLD", 0.4))  # %

# =====================
# Load markets safely
# =====================
try:
    markets = exchange.load_markets()
except Exception as e:
    print("Error loading markets:", e)
    markets = {}

symbols = [
    s for s in markets
    if s.endswith("/USDT")
    and markets[s].get("active", False)
    and markets[s].get("spot", False)
][:15]  # limit scan count to avoid rate limits

send_message(f"📡 Scanner started\nWatching {len(symbols)} symbols\nTimeframe: {TIMEFRAME}")

# =====================
# Scanner loop
# =====================
backoff = 15

while True:
    try:
        best_symbol = None
        best_move = 0

        for symbol in symbols:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=10)
            df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

            change = ((df.iloc[-1]["close"] - df.iloc[-2]["close"]) / df.iloc[-2]["close"]) * 100

            if abs(change) > best_move:
                best_move = abs(change)
                best_symbol = symbol

            time.sleep(1.2)  # polite delay

        if best_symbol and best_move >= VOL_THRESHOLD:
            send_message(
                f"🚨 Market Alert\n"
                f"Symbol: {best_symbol}\n"
                f"Move: {best_move:.2f}%\n"
                f"Timeframe: {TIMEFRAME}"
            )

        backoff = 15
        time.sleep(FETCH_INTERVAL)

    except ccxt.RateLimitExceeded:
        print("Rate limit hit, backing off...")
        time.sleep(backoff)
        backoff = min(backoff * 2, 300)

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
