# main.py
import ccxt
import pandas as pd
import time
import threading
from flask import Flask
from telegram import Bot
import os
import matplotlib.pyplot as plt

# ------------------------------
# 1. Flask server for Render
# ------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Trading bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

# ------------------------------
# 2. Telegram Bot Setup
# ------------------------------
TELEGRAM_TOKEN = "8201131169:AAGNp5VOkeTHj-fTjquUpDpoCk7wxbi4W4E"  # replace with your BotFather token
CHAT_ID = "7752955793"           # replace with your Telegram ID
bot = Bot(token=TELEGRAM_TOKEN)

def send_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print("Telegram send error:", e)

def send_chart(df, symbol):
    try:
        plt.figure(figsize=(6,4))
        plt.plot(df['timestamp'], df['close'], label='Close Price', color='blue')
        plt.title(f'{symbol} Price Chart')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("chart.png")
        plt.close()
        bot.send_photo(chat_id=CHAT_ID, photo=open("chart.png", "rb"))
    except Exception as e:
        print("Chart send error:", e)

# ------------------------------
# 3. Setup Bybit connection
# ------------------------------
exchange = ccxt.bybit({
    "enableRateLimit": True
})

symbol = "BTC/USDT"  # coin to watch
timeframe = "5m"
limit = 100

# ------------------------------
# 4. Main Bot Loop
# ------------------------------
while True:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Print last 5 candles in logs
        print(df.tail())

        # Telegram message for the last candle
        last = df.iloc[-1]
        message = (
            f"Symbol: {symbol}\n"
            f"Time: {last['timestamp']}\n"
            f"Open: {last['open']}\n"
            f"High: {last['high']}\n"
            f"Low: {last['low']}\n"
            f"Close: {last['close']}\n"
            f"Volume: {last['volume']}"
        )
        send_message(message)

        # Optional: send chart every N intervals (like every 5 minutes)
        if int(time.time()) % 300 < 60:  # every ~5 minutes
            send_chart(df, symbol)

        time.sleep(60)  # fetch every minute

    except ccxt.RateLimitExceeded:
        print("Rate limit hit, sleeping 10 seconds...")
        time.sleep(10)

    except Exception as e:
        print("Unexpected error:", e)
        time.sleep(10)
