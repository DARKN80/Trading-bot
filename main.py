    app.run(host="0.0.0.0", port=port)

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()

# =====================
# Telegram
# =====================
TELEGRAM_TOKEN = os.getenv("8452796874:AAEMPhUfnSwgb63ZweDU1StMpKeYvsQlCcU")
CHAT_ID = "7752955793"

def send_message(text):
    if not TELEGRAM_TOKEN:
        print("Telegram token missing")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

# =====================
# Exchange
# =====================
exchange = ccxt.bybit({
    "enableRateLimit": True
})

TIMEFRAME = "5m"
FETCH_INTERVAL = 60  # seconds
VOL_THRESHOLD = 0.4  # %

# =====================
# Load markets once
# =====================
markets = exchange.load_markets()

symbols = [
    s for s in markets
    if s.endswith("/USDT")
    and markets[s]["active"]
    and markets[s]["spot"]
][:15]  # limit scan count

send_message(f"Scanner started\nWatching {len(symbols)} symbols")

# =====================
# Scanner loop
# =====================
while True:
    try:
        best = None
        best_move = 0

        for symbol in symbols:
            ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=10)
            df = pd.DataFrame(ohlcv, columns=["t","o","h","l","c","v"])

            change = ((df.iloc[-1]["c"] - df.iloc[-2]["c"]) / df.iloc[-2]["c"]) * 100

            if abs(change) > best_move:
                best_move = abs(change)
                best = (symbol, change)

            time.sleep(1.2)  # polite delay

        if best and best_move >= VOL_THRESHOLD:
            send_message(
                f"📈 Market Scanner Alert\n"
                f"Symbol: {best[0]}\n"
                f"Move: {best[1]:.2f}%\n"
                f"Timeframe: {TIMEFRAME}"
            )

        time.sleep(FETCH_INTERVAL)

    except ccxt.RateLimitExceeded:
        print("Rate limit hit, backing off")
        time.sleep(30)

    except Exception as e:
        print("Error:", e)
        time.sleep(20)
