import yfinance as yf
import requests
import os
import time

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

TICKERS = [
    "7203","6758","9984","8306","9432",
    "7974","6861","6501","6098","4063"
]

def send(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except:
        print("Discord NG")


def fetch(ticker):
    for _ in range(3):
        try:
            df = yf.download(
                f"{ticker}.T",
                period="3mo",
                progress=False,
                threads=False
            )

            if df is not None and not df.empty:
                return df

        except:
            pass

        time.sleep(2)

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
fail_count = 0

for t in TICKERS:
    df = fetch(t)

    if df is None:
        fail_count += 1
        continue

    if len(df) < 30:
        continue

    s = get_score(df)

    if s >= 10:
        results.append((t, s))


# 👇 成功したものだけ使う
results.sort(key=lambda x: x[1], reverse=True)

msg = "【結果】\n"

for r in results:
    msg += f"{r[0]} スコア:{r[1]}\n"

msg += f"\n失敗銘柄: {fail_count}件"

send(msg)
send("完了")