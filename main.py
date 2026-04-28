import yfinance as yf
import requests
import os
import time
import random

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 🔥 銘柄数制限（まずは100〜200にする）
TICKERS = [str(i) for i in range(1300, 1500)]

def send(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except:
        pass

def fetch(ticker):
    try:
        df = yf.download(
            f"{ticker}.T",
            period="3mo",
            progress=False,
            threads=False
        )
        return df
    except:
        return None


results = []

for i, t in enumerate(TICKERS):

    df = fetch(t)

    if df is None or df.empty or len(df) < 30:
        continue

    score = 0

    if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
        score += 10

    if df["Volume"].iloc[-1] > df["Volume"].mean():
        score += 10

    if score >= 10:
        results.append((t, score))

    # 🔥 超重要：間引き
    time.sleep(random.uniform(1.0, 2.5))

    # 🔥 50件ごとに休憩
    if i % 50 == 0:
        time.sleep(5)


results.sort(key=lambda x: x[1], reverse=True)

msg = "【結果】\n"

for r in results[:10]:
    msg += f"{r[0]} スコア:{r[1]}\n"

send(msg)
send("完了")