import yfinance as yf
import requests
import os
import time

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 🔥 ここ変更（超重要）
TICKERS = [str(i) for i in range(1300, 9999)]

def send(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except:
        print("send error")

def fetch(ticker):
    for _ in range(2):
        try:
            df = yf.download(f"{ticker}.T", period="3mo", progress=False, threads=False)
            if df is not None and not df.empty:
                return df
        except:
            pass
        time.sleep(1)
    return None

def get_score(df):
    score = 0

    if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
        score += 10

    if df["Close"].iloc[-1] > df["Close"].mean():
        score += 10

    if df["Volume"].iloc[-1] > df["Volume"].mean():
        score += 10

    return score


results = []
count = 0

for t in TICKERS:
    df = fetch(t)

    if df is None or len(df) < 50:
        continue

    s = get_score(df)

    if s >= 20:
        results.append((t, s))

    count += 1

    # 🔥 API負荷軽減
    if count % 50 == 0:
        time.sleep(2)


# 上位だけ送る
results.sort(key=lambda x: x[1], reverse=True)
top = results[:10]

if top:
    msg = "【上位銘柄】\n"
    for r in top:
        msg += f"{r[0]} スコア:{r[1]}\n"
else:
    msg = "ヒットなし"

send(msg)
send("スキャン完了")